import json
import os
import base64
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler
import gspread
from google.oauth2.service_account import Credentials
import requests

# Jakarta timezone (UTC+7)
JAKARTA_TZ = timezone(timedelta(hours=7))

def get_jakarta_time():
    """Get current time in Jakarta timezone (UTC+7)"""
    return datetime.now(JAKARTA_TZ)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle Telegram webhook"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            webhook_data = json.loads(post_data.decode('utf-8'))
            
            # Process Telegram webhook
            response = self._process_telegram_webhook(webhook_data)
            self._send_json_response(response)
            
        except Exception as e:
            self._send_error_response(500, f"Webhook error: {str(e)}")

    def do_GET(self):
        """Handle GET requests - for testing"""
        try:
            self._send_json_response({
                "status": "success",
                "message": "🤖 CatatUang Telegram Bot is running!",
                "timestamp": get_jakarta_time().isoformat(),
                "version": "1.0.0"
            })
                
        except Exception as e:
            self._send_error_response(500, f"Error: {str(e)}")

    def _process_telegram_webhook(self, data):
        """Process incoming Telegram webhook data"""
        try:
            # Extract message from Telegram webhook
            if 'message' in data:
                message = data['message']
                chat_id = message.get('chat', {}).get('id', '')
                user_id = message.get('from', {}).get('id', '')
                username = message.get('from', {}).get('username', 'unknown')
                first_name = message.get('from', {}).get('first_name', 'User')
                text = message.get('text', '')
                
                if text:
                    # Process the message
                    if text.startswith('/'):
                        result = self._process_command(text, chat_id, username, first_name)
                    else:
                        result = self._process_expense_message(text, f"{username}_{user_id}")
                    
                    # Send reply to Telegram
                    self._send_telegram_message(chat_id, result)
                    
                    return {
                        "status": "success",
                        "message": "Message processed",
                        "timestamp": get_jakarta_time().isoformat()
                    }
            
            return {"status": "success", "message": "No message to process"}
            
        except Exception as e:
            return {"status": "error", "message": f"Processing error: {str(e)}"}

    def _process_command(self, text, chat_id, username, first_name):
        """Process Telegram bot commands"""
        try:
            command = text.lower().split()[0]
            
            if command == '/start':
                return f"""👋 Halo {first_name}! Selamat datang di CatatUang Bot!

🤖 **Cara Pakai:**
• Tulis pengeluaran: `50000 makanan nasi padang`
• Tulis pemasukan: `+1000000 gaji salary`
• Lihat laporan: /report

📋 **Commands:**
/help - Bantuan lengkap
/report - Laporan hari ini
/week - Laporan minggu ini
/month - Laporan bulan ini
/categories - Daftar kategori

💡 **Contoh:**
`15000 transport ojek ke kantor`
`+500000 bonus kinerja`"""

            elif command == '/help':
                return """📚 **Panduan CatatUang Bot**

**Format Pengeluaran:**
`[jumlah] [kategori] [deskripsi]`

**Format Pemasukan:**
`+[jumlah] [kategori] [deskripsi]`

**Contoh:**
• `50000 makanan nasi padang`
• `25000 transport ojek`
• `+1000000 gaji salary`
• `+100000 bonus freelance`

**Commands:**
/start - Mulai bot
/report - Laporan hari ini
/week - Laporan minggu
/month - Laporan bulan
/categories - Kategori tersedia

💡 Pastikan format: angka spasi kategori spasi deskripsi"""

            elif command in ['/report', '/today']:
                return self._generate_report_summary('today')
                
            elif command == '/week':
                return self._generate_report_summary('week')
                
            elif command == '/month':
                return self._generate_report_summary('month')
                
            elif command == '/categories':
                return """📊 **Kategori Tersedia:**

**Pengeluaran:**
• makanan - Makanan & minuman
• transport - Transportasi
• belanja - Shopping
• hiburan - Entertainment
• kesehatan - Medis
• pendidikan - Edukasi
• lainnya - Kategori lain

**Pemasukan:**
• gaji - Salary
• bonus - Bonus/insentif
• freelance - Kerja sampingan
• investasi - Return investasi
• lainnya - Sumber lain

💡 Bisa juga pakai kategori custom!"""

            else:
                return f"❌ Command tidak dikenal: {command}\n\nKetik /help untuk panduan lengkap."
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"

    def _process_expense_message(self, text, user_id):
        """Process expense/income message and save to Google Sheets"""
        try:
            # Parse message: amount category description
            parts = text.strip().split(' ', 2)
            
            if len(parts) < 2:
                return "❌ Format salah!\n\n✅ Contoh yang benar:\n• `50000 makanan nasi padang`\n• `+1000000 gaji salary`\n\nKetik /help untuk panduan lengkap."
            
            amount_str = parts[0]
            kategori_input = parts[1].lower()
            deskripsi = parts[2] if len(parts) > 2 else ""
            
            # Standardize category with fuzzy matching
            kategori = self._standardize_category(kategori_input)
            suggestion_text = self._get_category_suggestion(kategori_input, kategori)
            
            # Parse amount (check for income with + prefix)
            is_income = amount_str.startswith('+')
            if is_income:
                amount_str = amount_str[1:]  # Remove + prefix
            
            try:
                amount = int(amount_str.replace(',', '').replace('.', ''))
            except ValueError:
                return "❌ Jumlah harus berupa angka!\n\n✅ Contoh: `50000 makanan nasi padang`"
            
            if amount <= 0:
                return "❌ Jumlah harus lebih dari 0!"
            
            # Get Jakarta time for the transaction
            jakarta_time = get_jakarta_time()
            
            # Save to Google Sheets
            success = self._save_to_sheets({
                'tanggal': jakarta_time.strftime('%Y-%m-%d %H:%M:%S'),
                'kategori': kategori,
                'deskripsi': deskripsi,
                'jumlah': amount if is_income else -amount,  # Negative for expenses
                'sumber': f"telegram_{user_id}",
                'tipe': 'pemasukan' if is_income else 'pengeluaran'
            })
            
            if success:
                tipe_emoji = "💰" if is_income else "💸"
                tipe_text = "Pemasukan" if is_income else "Pengeluaran"
                formatted_amount = f"Rp {amount:,}".replace(',', '.')
                
                return f"""{tipe_emoji} **{tipe_text} Tercatat!**

💵 Jumlah: {formatted_amount}
📂 Kategori: {kategori.title()}
📝 Deskripsi: {deskripsi}
📅 Waktu: {jakarta_time.strftime('%d/%m/%Y %H:%M')} WIB

✅ Data tersimpan di Google Sheets!{suggestion_text}"""
            else:
                return "❌ Gagal menyimpan data. Coba lagi dalam beberapa saat."
                
        except Exception as e:
            return f"❌ Error: {str(e)}\n\nKetik /help untuk format yang benar."

    def _standardize_category(self, input_category):
        """Standardize category with fuzzy matching and English translation"""
        input_category = input_category.lower().strip()
        
        # Standard categories (Indonesian)
        standard_categories = {
            'makanan': ['makanan', 'makan', 'food', 'eat', 'dining', 'snack', 'meal', 
                       'kuliner', 'restaurant', 'resto', 'cafe', 'warung', 'delivery',
                       'gofood', 'grabfood', 'ojol_food', 'takeaway', 'jajan'],
            'transport': ['transport', 'transportation', 'travel', 'ojek', 'grab', 'gojek',
                         'taxi', 'bus', 'angkot', 'motor', 'bensin', 'fuel', 'parking',
                         'parkir', 'tol', 'toll', 'uber', 'bike', 'sepeda', 'perjalanan'],
            'belanja': ['belanja', 'shopping', 'groceries', 'supermarket', 'mall', 'online',
                       'tokopedia', 'shopee', 'lazada', 'bukalapak', 'clothes', 'baju',
                       'elektronik', 'gadget', 'kosmetik', 'skincare', 'shop'],
            'kesehatan': ['kesehatan', 'health', 'dokter', 'doctor', 'obat', 'medicine',
                         'rumah_sakit', 'hospital', 'klinik', 'clinic', 'vitamin',
                         'medical', 'therapy', 'terapi', 'dental', 'gigi'],
            'hiburan': ['hiburan', 'entertainment', 'movie', 'cinema', 'bioskop', 'game',
                       'gaming', 'hobby', 'rekreasi', 'vacation', 'liburan', 'wisata',
                       'netflix', 'spotify', 'youtube', 'subscription', 'fun'],
            'pendidikan': ['pendidikan', 'education', 'sekolah', 'school', 'university',
                          'kuliah', 'kursus', 'course', 'training', 'buku', 'book',
                          'alat_tulis', 'stationery', 'laptop', 'belajar', 'study'],
            'utilitas': ['utilitas', 'utilities', 'listrik', 'electricity', 'air', 'water',
                        'internet', 'wifi', 'pulsa', 'credit', 'gas', 'pdam', 'pln',
                        'telepon', 'phone', 'tv_cable', 'indihome', 'bills'],
            'investasi': ['investasi', 'investment', 'saham', 'stock', 'reksadana',
                         'mutual_fund', 'crypto', 'bitcoin', 'ethereum', 'trading',
                         'deposito', 'deposit', 'obligasi', 'bond', 'gold', 'emas'],
            'gaji': ['gaji', 'salary', 'income', 'penghasilan', 'upah', 'wage', 'bonus',
                    'thr', 'allowance', 'tunjangan', 'honorarium', 'fee', 'freelance',
                    'komisi', 'commission', 'royalty', 'earnings'],
            'lainnya': ['lainnya', 'others', 'misc', 'miscellaneous', 'random', 'other',
                       'undefined', 'unknown', 'dll', 'etc', 'various']
        }
        
        # Exact match first
        for standard_cat, aliases in standard_categories.items():
            if input_category in aliases:
                return standard_cat
        
        # Fuzzy matching using simple similarity
        best_match = None
        best_score = 0
        
        for standard_cat, aliases in standard_categories.items():
            for alias in aliases:
                # Calculate similarity score
                score = self._calculate_similarity(input_category, alias)
                if score > best_score and score >= 0.6:  # 60% similarity threshold
                    best_score = score
                    best_match = standard_cat
        
        # If good match found, return it
        if best_match:
            return best_match
            
        # If no good match, return original
        return input_category
    
    def _calculate_similarity(self, str1, str2):
        """Calculate string similarity using simple character matching"""
        if len(str1) == 0 or len(str2) == 0:
            return 0
        
        # Convert to lowercase for comparison
        str1, str2 = str1.lower(), str2.lower()
        
        # If exact match
        if str1 == str2:
            return 1.0
        
        # Calculate character-based similarity
        set1, set2 = set(str1), set(str2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0
        
        # Jaccard similarity + length penalty for very different lengths
        jaccard = intersection / union
        length_diff = abs(len(str1) - len(str2)) / max(len(str1), len(str2))
        
        return jaccard * (1 - length_diff * 0.3)
    
    def _get_category_suggestion(self, original, corrected):
        """Get category suggestion if standardization changed the input"""
        if corrected != original.lower():
            return f"\n💡 *Kategori dikoreksi: '{original}' → '{corrected}'*"
        return ""

    def _save_to_sheets(self, data):
        """Save data to Google Sheets"""
        try:
            service_account_key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
            
            if not service_account_key or not sheets_id:
                return False
            
            # Parse credentials
            decoded_key = base64.b64decode(service_account_key).decode('utf-8')
            credentials_info = json.loads(decoded_key)
            
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
            client = gspread.authorize(credentials)
            sheet = client.open_by_key(sheets_id).sheet1
            
            # Append data
            row = [
                data['tanggal'],
                data['kategori'],
                data['deskripsi'],
                data['jumlah'],
                data['sumber']
            ]
            
            sheet.append_row(row)
            return True
            
        except Exception as e:
            print(f"Sheets error: {e}")
            return False

    def _generate_report_summary(self, period):
        """Generate expense report summary"""
        try:
            # Get data from report API endpoint
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data laporan."
            
            # Filter by period using Jakarta timezone
            jakarta_now = get_jakarta_time()
            
            if period == 'today':
                start_date = jakarta_now.strftime('%Y-%m-%d')
                filtered_data = [row for row in report_data if row.get('Tanggal', '').startswith(start_date)]
                title = "📊 **Laporan Hari Ini**"
            elif period == 'week':
                week_ago = (jakarta_now - timedelta(days=7)).strftime('%Y-%m-%d')
                filtered_data = [row for row in report_data if row.get('Tanggal', '') >= week_ago]
                title = "📊 **Laporan 7 Hari Terakhir**"
            elif period == 'month':
                month_start = jakarta_now.strftime('%Y-%m-01')
                filtered_data = [row for row in report_data if row.get('Tanggal', '') >= month_start]
                title = "📊 **Laporan Bulan Ini**"
            else:
                filtered_data = report_data
                title = "📊 **Laporan Keseluruhan**"
            
            if not filtered_data:
                return f"{title}\n\n📝 Belum ada transaksi dalam period ini."
            
            # Calculate summary
            total_income = sum(int(row.get('Jumlah', 0)) for row in filtered_data if int(row.get('Jumlah', 0)) > 0)
            total_expense = abs(sum(int(row.get('Jumlah', 0)) for row in filtered_data if int(row.get('Jumlah', 0)) < 0))
            balance = total_income - total_expense
            
            # Category breakdown
            categories = {}
            for row in filtered_data:
                cat = row.get('Kategori', 'lainnya')
                amount = int(row.get('Jumlah', 0))
                if amount < 0:  # Expense
                    categories[cat] = categories.get(cat, 0) + abs(amount)
            
            # Format response with Jakarta time
            result = f"""{title}
📅 {jakarta_now.strftime('%d/%m/%Y')} WIB

💰 **Ringkasan:**
• Pemasukan: Rp {total_income:,}
• Pengeluaran: Rp {total_expense:,}
• Saldo: Rp {balance:,}

📊 **Per Kategori:**"""
            
            for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                result += f"\n• {cat.title()}: Rp {amount:,}"
            
            result += f"\n\n📈 Total transaksi: {len(filtered_data)}"
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error generating report: {str(e)}"

    def _get_sheets_data(self):
        """Get data from Google Sheets"""
        try:
            service_account_key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
            
            if not service_account_key or not sheets_id:
                return None
            
            decoded_key = base64.b64decode(service_account_key).decode('utf-8')
            credentials_info = json.loads(decoded_key)
            
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
            client = gspread.authorize(credentials)
            sheet = client.open_by_key(sheets_id).sheet1
            
            return sheet.get_all_records()
            
        except Exception as e:
            print(f"Error getting sheets data: {e}")
            return None

    def _send_telegram_message(self, chat_id, text):
        """Send message to Telegram"""
        try:
            bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending telegram message: {e}")
            return False

    def _send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {
            "status": "error",
            "message": message,
            "timestamp": get_jakarta_time().isoformat()
        }
        self.wfile.write(json.dumps(error_response).encode())