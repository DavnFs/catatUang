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

**📊 Laporan Dasar:**
/start - Mulai bot
/report - Laporan hari ini
/week - Laporan minggu
/month - Laporan bulan
/yearly - Laporan tahun ini
/categories - Kategori tersedia

**� Income & Balance:**
/income [jumlah] - Tambah pemasukan manual
/balance - Lihat saldo & overview
/expenses - Laporan pengeluaran saja

**�📈 Analytics & Insights:**
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
        """Get current balance and financial overview"""
        try:
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data balance."
            
            jakarta_now = get_jakarta_time()
            
            # All time totals
            total_income = sum(int(row.get('Jumlah', 0)) for row in report_data if int(row.get('Jumlah', 0)) > 0)
            total_expense = sum(abs(int(row.get('Jumlah', 0))) for row in report_data if int(row.get('Jumlah', 0)) < 0)
            net_balance = total_income - total_expense
            
            # This month
            current_month = jakarta_now.strftime('%Y-%m')
            current_month_data = [row for row in report_data if row.get('Tanggal', '').startswith(current_month)]
            
            month_income = sum(int(row.get('Jumlah', 0)) for row in current_month_data if int(row.get('Jumlah', 0)) > 0)
            month_expense = sum(abs(int(row.get('Jumlah', 0))) for row in current_month_data if int(row.get('Jumlah', 0)) < 0)
            month_balance = month_income - month_expense
            
            # Balance status
            balance_emoji = "💚" if net_balance > 0 else "🔴" if net_balance < 0 else "⚖️"
            month_emoji = "💚" if month_balance > 0 else "🔴" if month_balance < 0 else "⚖️"
            
            result = f"""💼 **Current Balance Overview**
📅 {jakarta_now.strftime('%d/%m/%Y %H:%M')} WIB

{balance_emoji} **Total Balance:** Rp {net_balance:,}
• Total Pemasukan: Rp {total_income:,}
• Total Pengeluaran: Rp {total_expense:,}
• Transaksi: {len(report_data)}

{month_emoji} **Bulan Ini ({current_month}):**
• Pemasukan: Rp {month_income:,}
• Pengeluaran: Rp {month_expense:,}
• Saldo bulan ini: Rp {month_balance:,}
• Transaksi: {len(current_month_data)}"""

            # Add insights
            if total_income == 0:
                result += f"\n\n💡 **Tip:** Belum ada pemasukan tercatat. Gunakan `/income [jumlah]` untuk menambah pemasukan dari orang tua."
            elif month_income == 0:
                result += f"\n\n💡 **Info:** Belum ada pemasukan bulan ini. Total pengeluaran: Rp {month_expense:,}"
            
            # Spending rate if there's income
            if total_income > 0:
                spending_rate = (total_expense / total_income) * 100
                if spending_rate > 100:
                    result += f"\n\n⚠️ **Warning:** Pengeluaran melebihi pemasukan ({spending_rate:.1f}%)"
                elif spending_rate > 80:
                    result += f"\n\n⚠️ **Caution:** Spending rate tinggi ({spending_rate:.1f}%)"
                else:
                    result += f"\n\n✅ **Good:** Spending rate sehat ({spending_rate:.1f}%)"
            
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