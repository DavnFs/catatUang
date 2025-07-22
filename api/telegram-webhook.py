import json
import os
import base64
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import gspread
from google.oauth2.service_account import Credentials
import requests


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
                "timestamp": datetime.now().isoformat(),
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
                        "timestamp": datetime.now().isoformat()
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
            kategori = parts[1].lower()
            deskripsi = parts[2] if len(parts) > 2 else ""
            
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
            
            # Save to Google Sheets
            success = self._save_to_sheets({
                'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
📅 Waktu: {datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Data tersimpan di Google Sheets!"""
            else:
                return "❌ Gagal menyimpan data. Coba lagi dalam beberapa saat."
                
        except Exception as e:
            return f"❌ Error: {str(e)}\n\nKetik /help untuk format yang benar."

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
            from datetime import datetime, timedelta
            
            report_data = self._get_sheets_data()
            if not report_data:
                return "❌ Tidak bisa mengambil data laporan."
            
            # Filter by period
            now = datetime.now()
            if period == 'today':
                start_date = now.strftime('%Y-%m-%d')
                filtered_data = [row for row in report_data if row.get('Tanggal', '').startswith(start_date)]
                title = "📊 **Laporan Hari Ini**"
            elif period == 'week':
                week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                filtered_data = [row for row in report_data if row.get('Tanggal', '') >= week_ago]
                title = "📊 **Laporan 7 Hari Terakhir**"
            elif period == 'month':
                month_start = now.strftime('%Y-%m-01')
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
            
            # Format response
            result = f"""{title}
📅 {now.strftime('%d/%m/%Y')}

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
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(error_response).encode())
