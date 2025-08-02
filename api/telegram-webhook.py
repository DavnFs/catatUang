import json
import os
import base64
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler
import gspread
from google.oauth2.service_account import Credentials
import requests

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import AI integration
try:
    from api.financial_advisor import FinancialAdvisor
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False
    print("AI integration not available, using standard responses")

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
                        result = self._process_command(text, chat_id, username, first_name, user_id)
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

    def _process_command(self, text, chat_id, username, first_name, user_id=None):
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
                ai_section = ""
                if AI_ENABLED:
                    ai_section = """
**🤖 AI Financial Advisor (with Historical Analysis):**
/tips - Tips hemat umum
/advice - Analisis keuangan personal dengan data historis
/budget [income] - Rekomendasi budget berdasarkan pola pengeluaran historis
/goals [jumlah] [deskripsi] - Set financial goals
/budgetcheck [jumlah] [hari] - Cek kelayakan budget untuk periode tertentu
/dailyplan [budget_harian] - Rencana pengeluaran harian

"""
                
                return f"""📚 **Panduan CatatUang Bot**

**Format Pengeluaran:**
`[jumlah] [kategori] [deskripsi]`

**Format Pemasukan:**
`+[jumlah] [kategori] [deskripsi]`

**Contoh:**
• `50000 makanan nasi padang`
• `25000 transport ojek`
• `+1000000 gaji salary`
• `+100000 bonus freelance`

**📊 Laporan Dasar:**
/start - Mulai bot
/report - Laporan hari ini
/week - Laporan minggu
/month - Laporan bulan
/yearly - Laporan tahun ini
/categories - Kategori tersedia

**💰 Income & Balance:**
/income [jumlah] - Tambah pemasukan manual
/balance - Lihat saldo & overview dengan carry-over analysis
/expenses - Laporan pengeluaran saja

**🔧 Transaction Management:**
/recent - Lihat 10 transaksi terbaru
/delete [nomor] - Hapus transaksi (gunakan nomor dari /recent)
/edit [nomor] [jumlah] [kategori] [deskripsi] - Edit transaksi

{ai_section}**📈 Analytics & Insights:**
/trends - Trend pengeluaran bulanan
/analytics - Analisis mendalam
/breakdown - Breakdown per kategori dengan %
/patterns - Pola pengeluaran harian/mingguan
/compare - Perbandingan bulan ini vs lalu

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
            
            elif command == '/trends':
                return self._generate_trends_analysis()
                
            elif command == '/analytics':
                return self._generate_analytics_summary()
                
            elif command == '/breakdown':
                return self._generate_category_breakdown()
                
            elif command == '/patterns':
                return self._generate_spending_patterns()
                
            elif command == '/yearly':
                return self._generate_report_summary('year')
                
            elif command == '/compare':
                return self._generate_comparison_report()
                
            elif command == '/income':
                # Parse income amount if provided
                parts = text.split()
                if len(parts) >= 2:
                    try:
                        amount = int(parts[1].replace(',', '').replace('.', ''))
                        return self._add_manual_income(amount, f"{username}_{user_id}")
                    except ValueError:
                        return "❌ Format salah! Gunakan: `/income 1000000` atau `/income 1000000 uang jajan dari ortu`"
                else:
                    return """💰 **Manual Income Entry**

**Format:**
`/income [jumlah]` - Tambah pemasukan cepat
`/income [jumlah] [deskripsi]` - Dengan deskripsi

**Contoh:**
• `/income 500000` - Pemasukan Rp 500.000
• `/income 1000000 uang jajan dari ortu`
• `/income 2000000 THR lebaran`

💡 Untuk pemasukan rutin, gunakan format biasa: `+1000000 gaji salary`"""
                
            elif command == '/balance':
                return self._get_current_balance()
                
            elif command == '/expenses':
                return self._generate_expenses_only_report()

            # AI Commands (if enabled)
            elif command == '/tips' and AI_ENABLED:
                return self._get_ai_tips()
                
            elif command == '/advice' and AI_ENABLED:
                return self._get_ai_advice(f"{username}_{user_id}")
                
            elif command == '/budget' and AI_ENABLED:
                args = text.split()[1:] if len(text.split()) > 1 else []
                monthly_income = float(args[0]) if args else None
                return self._get_ai_budget(f"{username}_{user_id}", monthly_income)
                
            elif command == '/goals' and AI_ENABLED:
                args = text.split()[1:] if len(text.split()) > 1 else []
                if len(args) >= 2:
                    goal_amount = float(args[0])
                    goal_desc = ' '.join(args[1:])
                    return self._set_financial_goal(f"{username}_{user_id}", goal_amount, goal_desc)
                else:
                    return self._show_goals_help()
                    
            elif command == '/budgetcheck' and AI_ENABLED:
                args = text.split()[1:] if len(text.split()) > 1 else []
                if len(args) >= 2:
                    budget_amount = float(args[0])
                    duration_days = int(args[1])
                    return self._check_budget_feasibility(f"{username}_{user_id}", budget_amount, duration_days)
                else:
                    return self._show_budgetcheck_help()
                    
            elif command == '/dailyplan' and AI_ENABLED:
                args = text.split()[1:] if len(text.split()) > 1 else []
                if args:
                    daily_budget = float(args[0])
                    return self._get_daily_spending_plan(daily_budget)
                else:
                    return self._show_dailyplan_help()
                    
            elif command == '/recent':
                return self._show_recent_transactions(f"{username}_{user_id}")
                
            elif command == '/delete':
                args = text.split()[1:] if len(text.split()) > 1 else []
                if args:
                    try:
                        row_number = int(args[0])
                        return self._delete_transaction(f"{username}_{user_id}", row_number)
                    except ValueError:
                        return "❌ Format salah! Gunakan: `/delete [nomor]`\n\nContoh: `/delete 3`\n\nLihat nomor transaksi dengan `/recent`"
                else:
                    return """🗑️ **Hapus Transaksi**

**Format:**
`/delete [nomor]` - Hapus transaksi berdasarkan nomor

**Cara pakai:**
1. Ketik `/recent` untuk lihat transaksi terbaru
2. Catat nomor transaksi yang mau dihapus
3. Ketik `/delete [nomor]`

**Contoh:**
• `/delete 3` - Hapus transaksi nomor 3
• `/delete 1` - Hapus transaksi terbaru

⚠️ **Peringatan:** Transaksi yang dihapus tidak bisa dikembalikan!"""
                
            elif command == '/edit':
                args = text.split()[1:] if len(text.split()) > 1 else []
                if len(args) >= 4:
                    try:
                        row_number = int(args[0])
                        new_amount = args[1]
                        new_category = args[2]
                        new_description = ' '.join(args[3:])
                        return self._edit_transaction(f"{username}_{user_id}", row_number, new_amount, new_category, new_description)
                    except ValueError:
                        return "❌ Format salah! Nomor transaksi harus berupa angka."
                else:
                    return """✏️ **Edit Transaksi**

**Format:**
`/edit [nomor] [jumlah_baru] [kategori_baru] [deskripsi_baru]`

**Cara pakai:**
1. Ketik `/recent` untuk lihat transaksi terbaru
2. Catat nomor transaksi yang mau diedit
3. Ketik `/edit` dengan data baru

**Contoh:**
• `/edit 3 75000 makanan dinner dengan teman`
• `/edit 1 +1200000 gaji salary bulan ini`

💡 **Tips:** Untuk pemasukan, tambahkan tanda `+` di depan jumlah"""

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
                # Use AI-enhanced response if available
                if AI_ENABLED and os.getenv('AI_INSIGHTS_ENABLED', 'true').lower() == 'true':
                    try:
                        # Get AI insight for the transaction
                        advisor = FinancialAdvisor()
                        user_data = self._get_user_financial_data(user_id)
                        
                        ai_tip = advisor.get_transaction_advice(
                            amount=amount,
                            category=kategori,
                            description=deskripsi,
                            user_data=user_data
                        )
                        
                        # Format AI-enhanced response
                        tipe_emoji = "💰" if is_income else "💸"
                        tipe_text = "Pemasukan" if is_income else "Pengeluaran"
                        formatted_amount = f"Rp {amount:,}".replace(',', '.')
                        
                        return f"""{tipe_emoji} **{tipe_text} Tercatat!**

💵 Jumlah: {formatted_amount}
📂 Kategori: {kategori.title()}
📝 Deskripsi: {deskripsi}
📅 Waktu: {jakarta_time.strftime('%d/%m/%Y %H:%M')} WIB

✅ Data tersimpan di Google Sheets!

{ai_tip}{suggestion_text}"""
                    except Exception as e:
                        print(f"AI response error: {e}")
                        # Fall back to standard response
                        pass
                
                # Standard response (fallback)
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
            elif period == 'year':
                year_start = jakarta_now.strftime('%Y-01-01')
                filtered_data = [row for row in report_data if row.get('Tanggal', '') >= year_start]
                title = "📊 **Laporan Tahun Ini**"
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

    def _generate_trends_analysis(self):
        """Generate monthly trends analysis"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data untuk analisis trend."
            
            # Group by month
            monthly_data = {}
            for row in report_data:
                date_str = row.get('Tanggal', '')
                if date_str:
                    try:
                        month = date_str[:7]  # YYYY-MM
                        amount = int(row.get('Jumlah', 0))
                        
                        if month not in monthly_data:
                            monthly_data[month] = {'income': 0, 'expense': 0}
                        
                        if amount > 0:
                            monthly_data[month]['income'] += amount
                        else:
                            monthly_data[month]['expense'] += abs(amount)
                    except:
                        continue
            
            if not monthly_data:
                return "📈 **Trend Analysis**\n\n📝 Belum ada data untuk analisis trend."
            
            # Sort by month and calculate trends
            sorted_months = sorted(monthly_data.keys())[-6:]  # Last 6 months
            
            result = "📈 **Trend Analysis - 6 Bulan Terakhir**\n\n"
            
            prev_expense = None
            for month in sorted_months:
                data = monthly_data[month]
                expense = data['expense']
                income = data['income']
                balance = income - expense
                
                # Calculate trend
                trend_emoji = ""
                if prev_expense is not None:
                    if expense > prev_expense:
                        pct_change = ((expense - prev_expense) / prev_expense) * 100
                        trend_emoji = f" 📈 +{pct_change:.1f}%"
                    elif expense < prev_expense:
                        pct_change = ((prev_expense - expense) / prev_expense) * 100
                        trend_emoji = f" 📉 -{pct_change:.1f}%"
                    else:
                        trend_emoji = " ➡️ 0%"
                
                result += f"**{month}:**\n"
                result += f"• Pengeluaran: Rp {expense:,}{trend_emoji}\n"
                result += f"• Pemasukan: Rp {income:,}\n"
                result += f"• Saldo: Rp {balance:,}\n\n"
                
                prev_expense = expense
            
            # Add average
            avg_expense = sum(monthly_data[m]['expense'] for m in sorted_months) / len(sorted_months)
            avg_income = sum(monthly_data[m]['income'] for m in sorted_months) / len(sorted_months)
            
            result += f"📊 **Rata-rata Bulanan:**\n"
            result += f"• Pengeluaran: Rp {avg_expense:,.0f}\n"
            result += f"• Pemasukan: Rp {avg_income:,.0f}\n"
            result += f"• Saldo: Rp {(avg_income - avg_expense):,.0f}"
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error generating trends: {str(e)}"

    def _generate_analytics_summary(self):
        """Generate comprehensive analytics summary"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data untuk analytics."
            
            jakarta_now = get_jakarta_time()
            
            # Current month data
            current_month = jakarta_now.strftime('%Y-%m')
            current_month_data = [row for row in report_data if row.get('Tanggal', '').startswith(current_month)]
            
            # Previous month data
            prev_month_date = jakarta_now.replace(day=1) - timedelta(days=1)
            prev_month = prev_month_date.strftime('%Y-%m')
            prev_month_data = [row for row in report_data if row.get('Tanggal', '').startswith(prev_month)]
            
            # Calculate metrics
            curr_expense = sum(abs(int(row.get('Jumlah', 0))) for row in current_month_data if int(row.get('Jumlah', 0)) < 0)
            prev_expense = sum(abs(int(row.get('Jumlah', 0))) for row in prev_month_data if int(row.get('Jumlah', 0)) < 0)
            
            curr_income = sum(int(row.get('Jumlah', 0)) for row in current_month_data if int(row.get('Jumlah', 0)) > 0)
            prev_income = sum(int(row.get('Jumlah', 0)) for row in prev_month_data if int(row.get('Jumlah', 0)) > 0)
            
            # Calculate percentages
            expense_change = ((curr_expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else 0
            income_change = ((curr_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
            
            # Top categories this month
            categories = {}
            for row in current_month_data:
                if int(row.get('Jumlah', 0)) < 0:  # Expenses only
                    cat = row.get('Kategori', 'lainnya')
                    categories[cat] = categories.get(cat, 0) + abs(int(row.get('Jumlah', 0)))
            
            # Average transaction
            avg_transaction = curr_expense / len(current_month_data) if current_month_data else 0
            
            # Days into month
            days_passed = jakarta_now.day
            days_in_month = 31  # Approximation
            daily_avg = curr_expense / days_passed if days_passed > 0 else 0
            projected_monthly = daily_avg * days_in_month
            
            result = f"🔬 **Analytics Summary - {current_month}**\n\n"
            
            result += f"📊 **Perbandingan Bulan Lalu:**\n"
            expense_emoji = "📈" if expense_change > 0 else "📉" if expense_change < 0 else "➡️"
            income_emoji = "📈" if income_change > 0 else "📉" if income_change < 0 else "➡️"
            
            result += f"• Pengeluaran: {expense_emoji} {expense_change:+.1f}%\n"
            result += f"• Pemasukan: {income_emoji} {income_change:+.1f}%\n\n"
            
            result += f"💰 **Proyeksi Bulan Ini:**\n"
            result += f"• Rata-rata harian: Rp {daily_avg:,.0f}\n"
            result += f"• Proyeksi total: Rp {projected_monthly:,.0f}\n"
            result += f"• Progress: {(days_passed/days_in_month)*100:.1f}%\n\n"
            
            result += f"🎯 **Top 3 Kategori:**\n"
            sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
            for i, (cat, amount) in enumerate(sorted_cats, 1):
                percentage = (amount / curr_expense * 100) if curr_expense > 0 else 0
                result += f"{i}. {cat.title()}: Rp {amount:,} ({percentage:.1f}%)\n"
            
            result += f"\n📈 **Statistik:**\n"
            result += f"• Rata-rata transaksi: Rp {avg_transaction:,.0f}\n"
            result += f"• Total transaksi: {len(current_month_data)}\n"
            
            if curr_income > 0:
                result += f"• Saving rate: {((curr_income - curr_expense) / curr_income * 100):.1f}%"
            else:
                result += f"• Total pengeluaran tanpa pemasukan: Rp {curr_expense:,}\n"
                result += f"💡 *Gunakan /income untuk tambah pemasukan*"
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error generating analytics: {str(e)}"

    def _generate_category_breakdown(self):
        """Generate detailed category breakdown with percentages"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data untuk breakdown."
            
            jakarta_now = get_jakarta_time()
            current_month = jakarta_now.strftime('%Y-%m')
            current_month_data = [row for row in report_data if row.get('Tanggal', '').startswith(current_month)]
            
            # Separate income and expenses
            expense_categories = {}
            income_categories = {}
            total_expense = 0
            total_income = 0
            
            for row in current_month_data:
                amount = int(row.get('Jumlah', 0))
                cat = row.get('Kategori', 'lainnya')
                
                if amount < 0:  # Expense
                    expense_amount = abs(amount)
                    expense_categories[cat] = expense_categories.get(cat, 0) + expense_amount
                    total_expense += expense_amount
                else:  # Income
                    income_categories[cat] = income_categories.get(cat, 0) + amount
                    total_income += amount
            
            result = f"📊 **Category Breakdown - {current_month}**\n\n"
            
            # Expense breakdown
            if expense_categories:
                result += f"💸 **Pengeluaran (Total: Rp {total_expense:,}):**\n"
                sorted_expenses = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)
                
                for cat, amount in sorted_expenses:
                    percentage = (amount / total_expense * 100) if total_expense > 0 else 0
                    bar = self._create_progress_bar(percentage)
                    result += f"• {cat.title()}: Rp {amount:,} ({percentage:.1f}%)\n"
                    result += f"  {bar}\n"
                
                result += "\n"
            
            # Income breakdown
            if income_categories:
                result += f"💰 **Pemasukan (Total: Rp {total_income:,}):**\n"
                sorted_income = sorted(income_categories.items(), key=lambda x: x[1], reverse=True)
                
                for cat, amount in sorted_income:
                    percentage = (amount / total_income * 100) if total_income > 0 else 0
                    bar = self._create_progress_bar(percentage)
                    result += f"• {cat.title()}: Rp {amount:,} ({percentage:.1f}%)\n"
                    result += f"  {bar}\n"
            
            # Summary
            balance = total_income - total_expense
            result += f"\n💼 **Summary:**\n"
            result += f"• Net Balance: Rp {balance:,}\n"
            
            if total_income > 0:
                result += f"• Expense Ratio: {(total_expense/total_income*100):.1f}%\n"
                result += f"• Savings Rate: {(balance/total_income*100):.1f}%"
            else:
                result += f"• Total Pengeluaran: Rp {total_expense:,}\n"
                result += f"💡 *Belum ada pemasukan tercatat. Gunakan /income untuk menambah.*"
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error generating breakdown: {str(e)}"

    def _generate_spending_patterns(self):
        """Analyze spending patterns by day of week and time"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data untuk analisis pattern."
            
            # Filter last 30 days
            jakarta_now = get_jakarta_time()
            thirty_days_ago = (jakarta_now - timedelta(days=30)).strftime('%Y-%m-%d')
            recent_data = [row for row in report_data if row.get('Tanggal', '') >= thirty_days_ago]
            
            # Analyze by day of week
            day_spending = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Mon-Sun
            day_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
            
            # Analyze by hour
            hour_spending = {}
            
            for row in recent_data:
                amount = int(row.get('Jumlah', 0))
                if amount < 0:  # Only expenses
                    date_str = row.get('Tanggal', '')
                    try:
                        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        weekday = dt.weekday()
                        hour = dt.hour
                        
                        day_spending[weekday] += abs(amount)
                        hour_spending[hour] = hour_spending.get(hour, 0) + abs(amount)
                    except:
                        continue
            
            result = f"🔍 **Spending Patterns - 30 Hari Terakhir**\n\n"
            
            # Day of week analysis
            total_weekly = sum(day_spending.values())
            if total_weekly > 0:
                result += f"📅 **Pengeluaran per Hari:**\n"
                
                # Find highest and lowest spending days
                max_day = max(day_spending, key=day_spending.get)
                min_day = min(day_spending, key=day_spending.get)
                
                for day_idx, day_name in enumerate(day_names):
                    amount = day_spending[day_idx]
                    percentage = (amount / total_weekly * 100) if total_weekly > 0 else 0
                    
                    emoji = "🔥" if day_idx == max_day else "💤" if day_idx == min_day else "📊"
                    bar = self._create_progress_bar(percentage, 10)
                    
                    result += f"{emoji} {day_name}: Rp {amount:,} ({percentage:.1f}%)\n"
                    result += f"   {bar}\n"
            
            # Hour analysis - peak hours
            if hour_spending:
                peak_hours = sorted(hour_spending.items(), key=lambda x: x[1], reverse=True)[:3]
                result += f"\n⏰ **Peak Spending Hours:**\n"
                
                for hour, amount in peak_hours:
                    time_str = f"{hour:02d}:00-{hour+1:02d}:00"
                    result += f"• {time_str}: Rp {amount:,}\n"
            
            # Weekend vs Weekday
            weekday_total = sum(day_spending[i] for i in range(5))  # Mon-Fri
            weekend_total = sum(day_spending[i] for i in range(5, 7))  # Sat-Sun
            
            if weekday_total + weekend_total > 0:
                weekday_avg = weekday_total / 5
                weekend_avg = weekend_total / 2
                
                result += f"\n📊 **Weekday vs Weekend:**\n"
                result += f"• Rata-rata weekday: Rp {weekday_avg:,.0f}\n"
                result += f"• Rata-rata weekend: Rp {weekend_avg:,.0f}\n"
                
                if weekend_avg > weekday_avg:
                    diff = ((weekend_avg - weekday_avg) / weekday_avg * 100)
                    result += f"• Weekend {diff:+.1f}% lebih tinggi 🎉"
                else:
                    diff = ((weekday_avg - weekend_avg) / weekend_avg * 100)
                    result += f"• Weekday {diff:+.1f}% lebih tinggi 💼"
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error analyzing patterns: {str(e)}"

    def _generate_comparison_report(self):
        """Compare current month with previous month"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data untuk perbandingan."
            
            jakarta_now = get_jakarta_time()
            
            # Current month
            current_month = jakarta_now.strftime('%Y-%m')
            current_data = [row for row in report_data if row.get('Tanggal', '').startswith(current_month)]
            
            # Previous month
            prev_month_date = jakarta_now.replace(day=1) - timedelta(days=1)
            prev_month = prev_month_date.strftime('%Y-%m')
            prev_data = [row for row in report_data if row.get('Tanggal', '').startswith(prev_month)]
            
            def analyze_month(data):
                income = sum(int(row.get('Jumlah', 0)) for row in data if int(row.get('Jumlah', 0)) > 0)
                expense = sum(abs(int(row.get('Jumlah', 0))) for row in data if int(row.get('Jumlah', 0)) < 0)
                
                categories = {}
                for row in data:
                    if int(row.get('Jumlah', 0)) < 0:
                        cat = row.get('Kategori', 'lainnya')
                        categories[cat] = categories.get(cat, 0) + abs(int(row.get('Jumlah', 0)))
                
                return {
                    'income': income,
                    'expense': expense,
                    'balance': income - expense,
                    'transactions': len(data),
                    'categories': categories
                }
            
            curr_analysis = analyze_month(current_data)
            prev_analysis = analyze_month(prev_data)
            
            result = f"⚖️ **Perbandingan Bulan**\n"
            result += f"📅 {prev_month} vs {current_month}\n\n"
            
            # Income comparison
            income_change = ((curr_analysis['income'] - prev_analysis['income']) / prev_analysis['income'] * 100) if prev_analysis['income'] > 0 else 0
            income_emoji = "📈" if income_change > 0 else "📉" if income_change < 0 else "➡️"
            
            result += f"💰 **Pemasukan:**\n"
            result += f"• Bulan lalu: Rp {prev_analysis['income']:,}\n"
            result += f"• Bulan ini: Rp {curr_analysis['income']:,}\n"
            result += f"• Perubahan: {income_emoji} {income_change:+.1f}%\n\n"
            
            # Expense comparison
            expense_change = ((curr_analysis['expense'] - prev_analysis['expense']) / prev_analysis['expense'] * 100) if prev_analysis['expense'] > 0 else 0
            expense_emoji = "📈" if expense_change > 0 else "📉" if expense_change < 0 else "➡️"
            
            result += f"💸 **Pengeluaran:**\n"
            result += f"• Bulan lalu: Rp {prev_analysis['expense']:,}\n"
            result += f"• Bulan ini: Rp {curr_analysis['expense']:,}\n"
            result += f"• Perubahan: {expense_emoji} {expense_change:+.1f}%\n\n"
            
            # Balance comparison
            balance_change = curr_analysis['balance'] - prev_analysis['balance']
            balance_emoji = "📈" if balance_change > 0 else "📉" if balance_change < 0 else "➡️"
            
            result += f"💼 **Saldo:**\n"
            result += f"• Bulan lalu: Rp {prev_analysis['balance']:,}\n"
            result += f"• Bulan ini: Rp {curr_analysis['balance']:,}\n"
            result += f"• Selisih: {balance_emoji} Rp {balance_change:+,}\n\n"
            
            # Category changes
            result += f"📊 **Perubahan Kategori Terbesar:**\n"
            category_changes = {}
            
            for cat in set(list(curr_analysis['categories'].keys()) + list(prev_analysis['categories'].keys())):
                curr_amount = curr_analysis['categories'].get(cat, 0)
                prev_amount = prev_analysis['categories'].get(cat, 0)
                change = curr_amount - prev_amount
                
                if prev_amount > 0:
                    pct_change = (change / prev_amount) * 100
                    category_changes[cat] = (change, pct_change)
            
            # Show top 3 increases and decreases
            increases = sorted([(k, v) for k, v in category_changes.items() if v[0] > 0], 
                             key=lambda x: x[1][0], reverse=True)[:2]
            decreases = sorted([(k, v) for k, v in category_changes.items() if v[0] < 0], 
                             key=lambda x: x[1][0])[:2]
            
            for cat, (change, pct) in increases:
                result += f"📈 {cat.title()}: +Rp {change:,} (+{pct:.1f}%)\n"
            
            for cat, (change, pct) in decreases:
                result += f"📉 {cat.title()}: Rp {change:,} ({pct:.1f}%)\n"
            
            # Summary insight
            if expense_change < -5:
                result += f"\n🎉 **Insight:** Pengeluaran turun signifikan bulan ini!"
            elif expense_change > 10:
                result += f"\n⚠️ **Warning:** Pengeluaran naik cukup tinggi bulan ini."
            elif abs(income_change) > 15:
                result += f"\n💡 **Insight:** Ada perubahan besar di pemasukan bulan ini."
            else:
                result += f"\n✅ **Insight:** Pola keuangan relatif stabil."
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error generating comparison: {str(e)}"

    def _create_progress_bar(self, percentage, length=15):
        """Create a visual progress bar"""
        filled = int(percentage / 100 * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
        
    def _add_manual_income(self, amount, user_id, description=""):
        """Add manual income entry for irregular income"""
        try:
            if amount <= 0:
                return "❌ Jumlah harus lebih dari 0!"
            
            # Get Jakarta time for the transaction
            jakarta_time = get_jakarta_time()
            
            # Default description for manual income
            if not description:
                description = "pemasukan manual"
            
            # Save to Google Sheets
            success = self._save_to_sheets({
                'tanggal': jakarta_time.strftime('%Y-%m-%d %H:%M:%S'),
                'kategori': 'lainnya',  # Default category for manual income
                'deskripsi': description,
                'jumlah': amount,  # Positive for income
                'sumber': f"telegram_{user_id}",
                'tipe': 'pemasukan'
            })
            
            if success:
                formatted_amount = f"Rp {amount:,}".replace(',', '.')
                
                return f"""💰 **Pemasukan Tercatat!**

💵 Jumlah: {formatted_amount}
📂 Kategori: Lainnya
📝 Deskripsi: {description}
📅 Waktu: {jakarta_time.strftime('%d/%m/%Y %H:%M')} WIB

✅ Data tersimpan di Google Sheets!

💡 *Tip: Untuk pemasukan dengan kategori spesifik, gunakan format: `+{amount} gaji salary`*"""
            else:
                return "❌ Gagal menyimpan data. Coba lagi dalam beberapa saat."
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _get_current_balance(self):
        """Get current balance and financial overview with carry-over analysis"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data balance."
            
            jakarta_now = get_jakarta_time()
            current_month = jakarta_now.strftime('%Y-%m')
            
            # All time totals
            total_income = sum(int(row.get('Jumlah', 0)) for row in report_data if int(row.get('Jumlah', 0)) > 0)
            total_expense = sum(abs(int(row.get('Jumlah', 0))) for row in report_data if int(row.get('Jumlah', 0)) < 0)
            net_balance = total_income - total_expense
            
            # This month
            current_month_data = [row for row in report_data if row.get('Tanggal', '').startswith(current_month)]
            month_income = sum(int(row.get('Jumlah', 0)) for row in current_month_data if int(row.get('Jumlah', 0)) > 0)
            month_expense = sum(abs(int(row.get('Jumlah', 0))) for row in current_month_data if int(row.get('Jumlah', 0)) < 0)
            month_balance = month_income - month_expense
            
            # Calculate carry-over from previous months
            previous_data = [row for row in report_data if not row.get('Tanggal', '').startswith(current_month)]
            previous_income = sum(int(row.get('Jumlah', 0)) for row in previous_data if int(row.get('Jumlah', 0)) > 0)
            previous_expense = sum(abs(int(row.get('Jumlah', 0))) for row in previous_data if int(row.get('Jumlah', 0)) < 0)
            carry_over_balance = previous_income - previous_expense
            
            # Balance status
            balance_emoji = "💚" if net_balance > 0 else "🔴" if net_balance < 0 else "⚖️"
            month_emoji = "💚" if month_balance > 0 else "🔴" if month_balance < 0 else "⚖️"
            carry_over_emoji = "💰" if carry_over_balance > 0 else "🔴" if carry_over_balance < 0 else "⚖️"
            
            result = f"""💼 **Balance Overview with Carry-Over Analysis**
📅 {jakarta_now.strftime('%d/%m/%Y %H:%M')} WIB

{balance_emoji} **TOTAL BALANCE:** Rp {net_balance:,}

{carry_over_emoji} **CARRY-OVER dari bulan lalu:** Rp {carry_over_balance:,}
• Total pemasukan sebelumnya: Rp {previous_income:,}
• Total pengeluaran sebelumnya: Rp {previous_expense:,}

{month_emoji} **BULAN INI ({current_month}):**
• Pemasukan: Rp {month_income:,}
• Pengeluaran: Rp {month_expense:,}
• Saldo bulan ini: Rp {month_balance:,}
• Transaksi: {len(current_month_data)}

💡 **SALDO EFEKTIF:** Rp {carry_over_balance + month_balance:,}
(Carry-over + Saldo bulan ini)"""

            # Add insights based on carry-over
            if carry_over_balance > 0:
                result += f"\n\n✅ **Good:** Anda memiliki saldo positif dari bulan-bulan sebelumnya!"
                if month_expense > 0:
                    months_sustainable = carry_over_balance / (month_expense / jakarta_now.day * 30) if jakarta_now.day > 0 else 0
                    result += f"\n💰 **Sustainability:** Dengan carry-over, bisa bertahan {months_sustainable:.1f} bulan lagi"
            elif carry_over_balance < 0:
                result += f"\n\n⚠️ **Caution:** Ada deficit Rp {abs(carry_over_balance):,} dari bulan-bulan sebelumnya"
            else:
                result += f"\n\n📊 **Info:** Ini adalah bulan pertama tracking atau saldo carry-over = 0"
            
            # Add income recommendation if needed
            if month_income == 0:
                result += f"\n\n💡 **Tip:** Belum ada pemasukan bulan ini. Gunakan `/income [jumlah]` untuk mencatat pemasukan."
            
            # AI advice prompt
            result += f"\n\n🤖 **Ingin analisis AI?** Gunakan `/advice` untuk mendapat insight mendalam berdasarkan data historis Anda!"
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error getting balance: {str(e)}"
    
    def _generate_expenses_only_report(self):
        """Generate report focusing on expenses only (useful when income is irregular)"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data expenses."
            
            jakarta_now = get_jakarta_time()
            
            # Filter expenses only
            expense_data = [row for row in report_data if int(row.get('Jumlah', 0)) < 0]
            
            if not expense_data:
                return "📊 **Expense Report**\n\n📝 Belum ada pengeluaran tercatat."
            
            # This month expenses
            current_month = jakarta_now.strftime('%Y-%m')
            month_expenses = [row for row in expense_data if row.get('Tanggal', '').startswith(current_month)]
            
            month_total = sum(abs(int(row.get('Jumlah', 0))) for row in month_expenses)
            all_time_total = sum(abs(int(row.get('Jumlah', 0))) for row in expense_data)
            
            # Category breakdown this month
            categories = {}
            for row in month_expenses:
                cat = row.get('Kategori', 'lainnya')
                amount = abs(int(row.get('Jumlah', 0)))
                categories[cat] = categories.get(cat, 0) + amount
            
            # Daily average this month
            days_passed = jakarta_now.day
            daily_avg = month_total / days_passed if days_passed > 0 else 0
            
            result = f"""📊 **Expense Report - {current_month}**
📅 {jakarta_now.strftime('%d/%m/%Y')} WIB

💸 **Pengeluaran Bulan Ini:**
• Total: Rp {month_total:,}
• Rata-rata harian: Rp {daily_avg:,.0f}
• Transaksi: {len(month_expenses)}

📈 **All Time:**
• Total pengeluaran: Rp {all_time_total:,}
• Total transaksi: {len(expense_data)}

📊 **Top Kategori Bulan Ini:**"""
            
            sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
            for i, (cat, amount) in enumerate(sorted_cats, 1):
                percentage = (amount / month_total * 100) if month_total > 0 else 0
                bar = self._create_progress_bar(percentage, 10)
                result += f"\n{i}. {cat.title()}: Rp {amount:,} ({percentage:.1f}%)"
                result += f"\n   {bar}"
            
            # Projected monthly spending
            days_in_month = 31  # Approximation
            projected = daily_avg * days_in_month
            
            result += f"\n\n📈 **Proyeksi Bulan Ini:**"
            result += f"\n• Estimasi total: Rp {projected:,.0f}"
            result += f"\n• Progress: {(days_passed/days_in_month)*100:.1f}%"
            
            # Add income reminder
            result += f"\n\n💡 **Tip:** Gunakan `/income [jumlah]` untuk mencatat pemasukan dari orang tua"
            
            return result.replace(',', '.')
            
        except Exception as e:
            return f"❌ Error generating expense report: {str(e)}"

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

    # AI Command Handlers
    def _get_ai_tips(self):
        """Get general financial tips from AI"""
        try:
            from api.financial_advisor import FinancialAdvisor
            advisor = FinancialAdvisor()
            
            prompt = """
            Berikan 5 tips keuangan umum yang praktis untuk orang Indonesia.
            
            Format:
            💰 TIPS KEUANGAN SMART
            
            1. [tip pertama]
            2. [tip kedua]
            3. [tip ketiga]
            4. [tip keempat]
            5. [tip kelima]
            
            Setiap tip harus actionable dan mudah diterapkan.
            """
            
            response = advisor._get_ai_response(prompt)
            return response
            
        except Exception as e:
            return """💰 TIPS KEUANGAN SMART

1. 💎 Sisihkan 20% penghasilan untuk tabungan dan investasi
2. 🏠 Batasi pengeluaran kebutuhan pokok maksimal 50% income  
3. 📊 Catat semua pengeluaran untuk kontrol yang lebih baik
4. 🚨 Buat emergency fund minimal 6 bulan pengeluaran
5. 📈 Mulai investasi dari sekarang, walau jumlah kecil

💡 Konsistensi lebih penting daripada jumlah besar!"""

    def _get_ai_advice(self, user_id):
        """Get AI-powered financial analysis with historical data"""
        try:
            from api.financial_advisor import FinancialAdvisor
            advisor = FinancialAdvisor()
            
            # Get REAL user data with historical analysis
            user_data = self._get_user_financial_data(user_id, include_historical=True)
            
            # If no data available, provide helpful message
            if user_data['total_income'] == 0 and user_data['total_expense'] == 0 and user_data['carry_over_balance'] == 0:
                return """🤖 **AI Financial Analysis**

📝 Belum ada data transaksi untuk dianalisis.

💡 **Untuk mendapatkan AI advice yang akurat:**
1. Mulai catat pemasukan: `+1000000 gaji salary`
2. Catat pengeluaran: `50000 makanan nasi padang`  
3. Gunakan /advice lagi setelah ada beberapa transaksi

🎯 **AI akan menganalisis:**
• Pola pengeluaran Anda
• Saldo carry-over dari bulan lalu
• Trend spending historis
• Rekomendasi budget yang realistis"""
            
            return advisor.get_monthly_analysis(user_data)
            
        except Exception as e:
            return f"❌ Gagal menganalisis data keuangan: {str(e)}"

    def _get_ai_budget(self, user_id, monthly_income):
        """Get AI budget recommendations with historical context"""
        try:
            from api.financial_advisor import FinancialAdvisor
            advisor = FinancialAdvisor()
            
            if monthly_income is None:
                return """💰 SET BUDGET RECOMMENDATION

Gunakan format: `/budget [penghasilan_bulanan]`

**Contoh:**
• `/budget 4000000` - Budget untuk penghasilan 4 juta
• `/budget 6500000` - Budget untuk penghasilan 6.5 juta

💡 Saya akan berikan rekomendasi budget berdasarkan prinsip 50/30/20 dan pola pengeluaran historis Anda!"""
            
            # Get real user data with historical context
            user_data = self._get_user_financial_data(user_id, include_historical=True)
            user_data['total_income'] = monthly_income  # Override with provided income
            
            return advisor.get_budget_recommendation(monthly_income, user_data)
            
        except Exception as e:
            return f"❌ Gagal membuat rekomendasi budget: {str(e)}"

    def _set_financial_goal(self, user_id, goal_amount, goal_description):
        """Set financial goals with AI recommendations"""
        try:
            from api.financial_advisor import FinancialAdvisor
            advisor = FinancialAdvisor()
            
            prompt = f"""
            User ingin menabung {goal_amount:,.0f} IDR untuk {goal_description}.
            
            Berikan rencana menabung yang realistis dengan asumsi penghasilan menengah Indonesia (3-5 juta/bulan).
            
            Format:
            🎯 RENCANA MENCAPAI GOAL
            
            💰 Target: {goal_amount:,.0f} IDR - {goal_description}
            
            📅 Timeline Options:
            • 6 bulan: [jumlah per bulan] IDR/bulan
            • 12 bulan: [jumlah per bulan] IDR/bulan  
            • 24 bulan: [jumlah per bulan] IDR/bulan
            
            💡 Tips Mencapai Goal:
            [3 tips praktis]
            
            🚀 Action Plan:
            [langkah konkret yang bisa dimulai hari ini]
            """
            
            return advisor._get_ai_response(prompt)
            
        except Exception as e:
            # Fallback calculation
            monthly_6 = goal_amount / 6
            monthly_12 = goal_amount / 12
            monthly_24 = goal_amount / 24
            
            return f"""🎯 RENCANA MENCAPAI GOAL

💰 Target: Rp {goal_amount:,.0f} - {goal_description}

📅 Timeline Options:
• 6 bulan: Rp {monthly_6:,.0f}/bulan
• 12 bulan: Rp {monthly_12:,.0f}/bulan
• 24 bulan: Rp {monthly_24:,.0f}/bulan

💡 Tips Mencapai Goal:
1. Set auto transfer ke rekening terpisah
2. Kurangi 1-2 kebiasaan pengeluaran kecil
3. Cari sumber income tambahan

🚀 Mulai hari ini, jangan tunda lagi!"""

    def _show_goals_help(self):
        """Show help for goals command"""
        return """🎯 SET FINANCIAL GOALS

Gunakan format: `/goals [jumlah] [deskripsi]`

**Contoh:**
• `/goals 10000000 emergency fund`
• `/goals 50000000 beli motor`
• `/goals 5000000 liburan bali`

💡 Goals yang clear dan terukur lebih mudah dicapai!"""

    def _check_budget_feasibility(self, user_id: str, budget_amount: float, duration_days: int):
        """Check if budget is feasible for given duration"""
        try:
            from api.financial_advisor import FinancialAdvisor
            advisor = FinancialAdvisor()
            
            # Get user's spending data for context
            user_data = self._get_user_spending_data(user_id)
            
            return advisor.check_budget_feasibility(budget_amount, duration_days, user_data)
            
        except Exception as e:
            # Fallback calculation
            daily_budget = budget_amount / duration_days
            
            return f"""💰 ANALISIS BUDGET {duration_days} HARI

💵 Total Budget: Rp {budget_amount:,.0f}
📅 Durasi: {duration_days} hari  
🎯 Budget Harian: Rp {daily_budget:,.0f}

✅ KELAYAKAN:
{'✅ Cukup untuk kebutuhan dasar' if daily_budget >= 50000 else '⚠️ Agak ketat, perlu hemat' if daily_budget >= 30000 else '❌ Sangat ketat, butuh strategi khusus'}

📊 REKOMENDASI ALOKASI HARIAN:
🍽️ Makanan: Rp {daily_budget*0.4:,.0f} (40%)
🚗 Transport: Rp {daily_budget*0.2:,.0f} (20%)  
🎯 Lain-lain: Rp {daily_budget*0.3:,.0f} (30%)
💎 Cadangan: Rp {daily_budget*0.1:,.0f} (10%)

💡 TIPS HEMAT:
1. Masak sendiri untuk hemat 40-50% budget makanan
2. Gunakan transport umum jika memungkinkan
3. Hindari pembelian impulsif

⚠️ PERINGATAN:
Sisihkan minimal 10% untuk emergency!"""

    def _get_daily_spending_plan(self, daily_budget: float):
        """Get daily spending plan"""
        try:
            from api.financial_advisor import FinancialAdvisor
            advisor = FinancialAdvisor()
            
            return advisor.get_daily_spending_plan(daily_budget)
            
        except Exception as e:
            return f"""📅 RENCANA PENGELUARAN HARIAN
💰 Budget: Rp {daily_budget:,.0f}

🎯 ALOKASI SMART:
🍽️ Makanan (3x sehari): Rp {daily_budget*0.45:,.0f} (45%)
🚗 Transport: Rp {daily_budget*0.25:,.0f} (25%)
☕ Jajan/Minuman: Rp {daily_budget*0.15:,.0f} (15%)
🎯 Lain-lain: Rp {daily_budget*0.10:,.0f} (10%)
💎 Tabungan: Rp {daily_budget*0.05:,.0f} (5%)

💡 STRATEGI HEMAT:
1. Bawa bekal dari rumah 2-3x seminggu
2. Batasi jajan maksimal budget yang ditentukan
3. Catat setiap pengeluaran real-time

📱 TRACKING HARIAN:
Kirim transaksi ke bot: "15000 makan siang ayam geprek" """

    def _show_budgetcheck_help(self):
        """Show help for budget check command"""
        return """💰 CEK KELAYAKAN BUDGET

Gunakan format: `/budgetcheck [jumlah] [hari]`

**Contoh:**
• `/budgetcheck 500000 14` - Cek budget 500rb untuk 14 hari
• `/budgetcheck 1000000 30` - Cek budget 1 juta untuk 30 hari
• `/budgetcheck 200000 7` - Cek budget 200rb untuk 1 minggu

💡 Saya akan analisis apakah budget tersebut cukup dan berikan tips pengeluaran harian!"""

    def _show_dailyplan_help(self):
        """Show help for daily plan command"""
        return """📅 RENCANA PENGELUARAN HARIAN

Gunakan format: `/dailyplan [budget_harian]`

**Contoh:**
• `/dailyplan 50000` - Rencana untuk budget 50rb/hari
• `/dailyplan 75000` - Rencana untuk budget 75rb/hari
• `/dailyplan 100000` - Rencana untuk budget 100rb/hari

💡 Saya akan buatkan alokasi smart dan tips hemat untuk budget harian Anda!"""

    def _get_user_spending_data(self, user_id: str) -> dict:
        """Get user's spending data for context from Google Sheets"""
        try:
            # Get REAL data from Google Sheets
            financial_data = self._get_user_financial_data(user_id)
            
            # Calculate daily average from real data
            current_day = get_jakarta_time().day
            daily_average = financial_data['total_expense'] / current_day if current_day > 0 else 0
            
            return {
                'daily_average': daily_average,
                'total_expense': financial_data['total_expense'],
                'categories': financial_data['categories']
            }
        except Exception as e:
            print(f"Error getting user spending data: {e}")
            # Fallback to minimal data
            return {
                'daily_average': 0,
                'total_expense': 0,
                'categories': {}
            }
    
    def _get_user_financial_data(self, user_id, include_historical=True):
        """Get user's financial data for AI analysis with historical data support"""
        try:
            # Get data from Google Sheets
            report_data = self._get_sheets_data()
            if not report_data:
                return self._get_empty_financial_data()
            
            jakarta_now = get_jakarta_time()
            current_month = jakarta_now.strftime('%Y-%m')
            
            if include_historical:
                # Include ALL historical data for better analysis
                all_data = report_data
                monthly_data = [row for row in report_data if row.get('Tanggal', '').startswith(current_month)]
                
                # Calculate historical totals (all time)
                total_income_all = sum(int(row.get('Jumlah', 0)) for row in all_data if int(row.get('Jumlah', 0)) > 0)
                total_expense_all = sum(abs(int(row.get('Jumlah', 0))) for row in all_data if int(row.get('Jumlah', 0)) < 0)
                
                # Calculate current month totals
                current_income = sum(int(row.get('Jumlah', 0)) for row in monthly_data if int(row.get('Jumlah', 0)) > 0)
                current_expense = sum(abs(int(row.get('Jumlah', 0))) for row in monthly_data if int(row.get('Jumlah', 0)) < 0)
                
                # Calculate carry-over balance from previous months
                previous_data = [row for row in all_data if not row.get('Tanggal', '').startswith(current_month)]
                previous_income = sum(int(row.get('Jumlah', 0)) for row in previous_data if int(row.get('Jumlah', 0)) > 0)
                previous_expense = sum(abs(int(row.get('Jumlah', 0))) for row in previous_data if int(row.get('Jumlah', 0)) < 0)
                carry_over_balance = previous_income - previous_expense
                
                # Current month categories
                current_categories = {}
                for row in monthly_data:
                    if int(row.get('Jumlah', 0)) < 0:  # Expenses only
                        cat = row.get('Kategori', 'lainnya')
                        current_categories[cat] = current_categories.get(cat, 0) + abs(int(row.get('Jumlah', 0)))
                
                # Historical spending patterns (last 3 months for trend analysis)
                last_3_months = []
                for i in range(1, 4):  # Last 3 months
                    target_date = (jakarta_now.replace(day=1) - timedelta(days=i*30))
                    target_month = target_date.strftime('%Y-%m')
                    month_data = [row for row in all_data if row.get('Tanggal', '').startswith(target_month)]
                    month_expense = sum(abs(int(row.get('Jumlah', 0))) for row in month_data if int(row.get('Jumlah', 0)) < 0)
                    last_3_months.append(month_expense)
                
                # Average monthly spending from historical data
                avg_monthly_expense = sum(last_3_months) / len(last_3_months) if last_3_months else 0
                
                return {
                    'total_income': current_income,
                    'total_expense': current_expense,
                    'categories': current_categories,
                    'transactions_count': len(monthly_data),
                    # Historical data for better AI analysis
                    'carry_over_balance': carry_over_balance,
                    'total_income_all_time': total_income_all,
                    'total_expense_all_time': total_expense_all,
                    'current_month_balance': current_income - current_expense,
                    'effective_balance': carry_over_balance + (current_income - current_expense),
                    'historical_spending_pattern': last_3_months,
                    'avg_monthly_expense': avg_monthly_expense,
                    'months_with_data': self._count_months_with_data(all_data),
                    'first_transaction_date': self._get_first_transaction_date(all_data)
                }
            else:
                # Legacy mode - current month only
                monthly_data = [row for row in report_data if row.get('Tanggal', '').startswith(current_month)]
                
                total_income = sum(int(row.get('Jumlah', 0)) for row in monthly_data if int(row.get('Jumlah', 0)) > 0)
                total_expense = sum(abs(int(row.get('Jumlah', 0))) for row in monthly_data if int(row.get('Jumlah', 0)) < 0)
                
                categories = {}
                for row in monthly_data:
                    if int(row.get('Jumlah', 0)) < 0:  # Expenses only
                        cat = row.get('Kategori', 'lainnya')
                        categories[cat] = categories.get(cat, 0) + abs(int(row.get('Jumlah', 0)))
                
                return {
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'categories': categories,
                    'transactions_count': len(monthly_data),
                    'carry_over_balance': 0,  # Not calculated in legacy mode
                    'effective_balance': total_income - total_expense
                }
                
        except Exception as e:
            print(f"Error getting user financial data: {e}")
            return self._get_empty_financial_data()
    
    def _get_empty_financial_data(self):
        """Return empty financial data structure"""
        return {
            'total_income': 0, 
            'total_expense': 0, 
            'categories': {}, 
            'transactions_count': 0,
            'carry_over_balance': 0,
            'effective_balance': 0
        }
    
    def _show_recent_transactions(self, user_id):
        """Show recent transactions for the user"""
        try:
            # Get Google Sheets data
            service_account_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
            sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            
            if not service_account_key or not sheets_id:
                return "❌ Konfigurasi Google Sheets tidak tersedia."
            
            decoded_key = base64.b64decode(service_account_key).decode('utf-8')
            credentials_info = json.loads(decoded_key)
            
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
            client = gspread.authorize(credentials)
            sheet = client.open_by_key(sheets_id).sheet1
            
            # Get all data
            all_data = sheet.get_all_values()
            if len(all_data) <= 1:  # Only header or empty
                return "📝 Belum ada transaksi yang tercatat."
            
            # Filter user's data and get last 10 transactions
            user_transactions = []
            for i, row in enumerate(all_data[1:], start=2):  # Skip header, start from row 2
                if len(row) >= 5 and row[4] == user_id:  # Check sumber column
                    user_transactions.append({
                        'row_number': i,
                        'date': row[0],
                        'category': row[1],
                        'description': row[2],
                        'amount': row[3]
                    })
            
            if not user_transactions:
                return "📝 Belum ada transaksi Anda yang tercatat."
            
            # Get last 10 transactions
            recent_transactions = user_transactions[-10:]
            
            response = "📝 **Transaksi Terbaru Anda:**\n\n"
            
            for i, trans in enumerate(reversed(recent_transactions), 1):
                amount_formatted = f"{float(trans['amount']):,.0f}" if trans['amount'].replace('-', '').replace('+', '').isdigit() else trans['amount']
                amount_symbol = "💰" if trans['amount'].startswith('+') or float(trans['amount']) > 0 else "💸"
                
                response += f"**{i}.** {amount_symbol} {amount_formatted} IDR\n"
                response += f"   📂 {trans['category'].title()} | 📅 {trans['date']}\n"
                response += f"   📝 {trans['description']}\n"
                response += f"   🔢 Row: {trans['row_number']}\n\n"
            
            response += "💡 **Cara pakai:**\n"
            response += "• `/delete [nomor]` - Hapus transaksi\n"
            response += "• `/edit [nomor] [jumlah] [kategori] [deskripsi]` - Edit transaksi\n\n"
            response += "⚠️ Gunakan nomor Row untuk delete/edit"
            
            return response
            
        except Exception as e:
            return f"❌ Error mengambil data transaksi: {str(e)}"
    
    def _delete_transaction(self, user_id, row_number):
        """Delete a specific transaction"""
        try:
            # Get Google Sheets data
            service_account_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
            sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            
            if not service_account_key or not sheets_id:
                return "❌ Konfigurasi Google Sheets tidak tersedia."
            
            decoded_key = base64.b64decode(service_account_key).decode('utf-8')
            credentials_info = json.loads(decoded_key)
            
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
            client = gspread.authorize(credentials)
            sheet = client.open_by_key(sheets_id).sheet1
            
            # Get specific row data to verify ownership
            try:
                row_data = sheet.row_values(row_number)
                if len(row_data) < 5:
                    return f"❌ Transaksi tidak ditemukan di row {row_number}."
                
                # Check if transaction belongs to user
                if row_data[4] != user_id:
                    return "❌ Anda hanya bisa menghapus transaksi milik Anda sendiri."
                
                # Show transaction details before deletion
                amount = row_data[3]
                category = row_data[1]
                description = row_data[2]
                date = row_data[0]
                
                # Delete the row
                sheet.delete_rows(row_number)
                
                amount_formatted = f"{float(amount):,.0f}" if amount.replace('-', '').replace('+', '').isdigit() else amount
                
                return f"""✅ **Transaksi berhasil dihapus!**

🗑️ **Yang dihapus:**
💰 Jumlah: {amount_formatted} IDR
📂 Kategori: {category.title()}
📝 Deskripsi: {description}
📅 Tanggal: {date}

💡 Gunakan `/recent` untuk melihat transaksi terbaru."""
                
            except Exception as e:
                return f"❌ Row {row_number} tidak ditemukan atau tidak valid: {str(e)}"
                
        except Exception as e:
            return f"❌ Error menghapus transaksi: {str(e)}"
    
    def _edit_transaction(self, user_id, row_number, new_amount, new_category, new_description):
        """Edit a specific transaction"""
        try:
            # Get Google Sheets data
            service_account_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
            sheets_id = os.getenv('GOOGLE_SHEETS_ID')
            
            if not service_account_key or not sheets_id:
                return "❌ Konfigurasi Google Sheets tidak tersedia."
            
            decoded_key = base64.b64decode(service_account_key).decode('utf-8')
            credentials_info = json.loads(decoded_key)
            
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
            client = gspread.authorize(credentials)
            sheet = client.open_by_key(sheets_id).sheet1
            
            # Get specific row data to verify ownership
            try:
                row_data = sheet.row_values(row_number)
                if len(row_data) < 5:
                    return f"❌ Transaksi tidak ditemukan di row {row_number}."
                
                # Check if transaction belongs to user
                if row_data[4] != user_id:
                    return "❌ Anda hanya bisa mengedit transaksi milik Anda sendiri."
                
                # Store old values for confirmation
                old_amount = row_data[3]
                old_category = row_data[1]
                old_description = row_data[2]
                
                # Process new amount (handle + prefix for income)
                is_income = new_amount.startswith('+')
                clean_amount = new_amount.replace('+', '').replace(',', '').replace('.', '')
                
                try:
                    amount_value = int(clean_amount)
                    final_amount = f"+{amount_value}" if is_income else str(-abs(amount_value))
                except ValueError:
                    return "❌ Jumlah harus berupa angka. Contoh: `75000` atau `+1000000`"
                
                # Standardize category
                standardized_category = self._standardize_category(new_category.lower())
                
                # Update the transaction
                current_date = get_jakarta_time().strftime('%Y-%m-%d %H:%M:%S')
                
                # Update specific cells
                sheet.update_cell(row_number, 1, current_date)  # Update timestamp
                sheet.update_cell(row_number, 2, standardized_category)  # Category
                sheet.update_cell(row_number, 3, new_description)  # Description
                sheet.update_cell(row_number, 4, final_amount)  # Amount
                # Keep user_id (column 5) unchanged
                
                old_amount_formatted = f"{float(old_amount):,.0f}" if old_amount.replace('-', '').replace('+', '').isdigit() else old_amount
                new_amount_formatted = f"{float(final_amount):,.0f}" if final_amount.replace('-', '').replace('+', '').isdigit() else final_amount
                
                return f"""✅ **Transaksi berhasil diedit!**

🔄 **Perubahan:**

**SEBELUM:**
💰 {old_amount_formatted} IDR
📂 {old_category.title()}
📝 {old_description}

**SESUDAH:**
💰 {new_amount_formatted} IDR
📂 {standardized_category.title()}
📝 {new_description}
📅 {current_date}

💡 Gunakan `/recent` untuk melihat transaksi terbaru."""
                
            except Exception as e:
                return f"❌ Row {row_number} tidak ditemukan atau tidak valid: {str(e)}"
                
        except Exception as e:
            return f"❌ Error mengedit transaksi: {str(e)}"
    
    def _count_months_with_data(self, data):
        """Count number of months that have transaction data"""
        months = set()
        for row in data:
            date_str = row.get('Tanggal', '')
            if date_str:
                try:
                    month = date_str[:7]  # YYYY-MM
                    months.add(month)
                except:
                    continue
        return len(months)
    
    def _get_first_transaction_date(self, data):
        """Get the date of first transaction for tenure calculation"""
        if not data:
            return None
        
        dates = []
        for row in data:
            date_str = row.get('Tanggal', '')
            if date_str:
                try:
                    dates.append(date_str)
                except:
                    continue
        
        return min(dates) if dates else None

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