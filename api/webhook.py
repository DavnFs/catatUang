import json
import os
import base64
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import gspread
from google.oauth2.service_account import Credentials


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle WhatsApp webhook verification"""
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query)
        
        # WhatsApp verification
        verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', '')
        challenge = params.get('hub.challenge', [None])[0]
        token = params.get('hub.verify_token', [None])[0]
        mode = params.get('hub.mode', [None])[0]
        
        if mode == 'subscribe' and token == verify_token:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(challenge.encode())
            return
        
        # Default response
        self._send_json_response({
            "status": "ok",
            "message": "CatatUang Webhook Ready! 🚀",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })

    def do_POST(self):
        """Handle incoming WhatsApp messages"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_error_response(400, "Invalid JSON payload")
                return
            
            result = self._process_webhook(data)
            self._send_json_response(result)
            
        except Exception as e:
            self._send_error_response(500, f"Server error: {str(e)}")

    def _process_webhook(self, data):
        """Process different webhook formats"""
        try:
            # Format 1: Direct message (testing)
            if 'text' in data:
                return self._process_expense_message(data['text'])
            
            # Format 2: WhatsApp Cloud API
            if 'entry' in data:
                for entry in data['entry']:
                    for change in entry.get('changes', []):
                        if change.get('field') == 'messages':
                            messages = change.get('value', {}).get('messages', [])
                            for message in messages:
                                if message.get('type') == 'text':
                                    text = message.get('text', {}).get('body', '')
                                    if text.startswith('#'):
                                        return self._process_expense_message(text)
            
            # Format 3: Twilio
            if 'Body' in data:
                text = data['Body']
                if text.startswith('#'):
                    return self._process_expense_message(text)
            
            return {"status": "ok", "message": "No action needed"}
            
        except Exception as e:
            return {"status": "error", "message": f"Processing error: {str(e)}"}

    def _process_expense_message(self, text):
        """Parse and save expense data"""
        try:
            if not text.startswith('#'):
                return {"status": "error", "message": "Format harus diawali dengan '#'"}
            
            parts = text[1:].split(' ', 2)
            if len(parts) < 2:
                return {"status": "error", "message": "Format: #kategori jumlah keterangan"}
            
            kategori = parts[0].lower().strip()
            try:
                jumlah = int(parts[1])
            except ValueError:
                return {"status": "error", "message": "Jumlah harus berupa angka"}
            
            keterangan = parts[2].strip() if len(parts) > 2 else ""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to Google Sheets
            save_result = self._save_to_sheets(timestamp, kategori, jumlah, keterangan)
            
            if save_result['success']:
                return {
                    "status": "success",
                    "data": {
                        "timestamp": timestamp,
                        "kategori": kategori,
                        "jumlah": jumlah,
                        "keterangan": keterangan
                    },
                    "message": f"✅ Berhasil mencatat: {kategori} Rp {jumlah:,}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Gagal simpan: {save_result['error']}"
                }
                
        except Exception as e:
            return {"status": "error", "message": f"Error: {str(e)}"}

    def _save_to_sheets(self, timestamp, kategori, jumlah, keterangan):
        """Save data to Google Sheets"""
        try:
            service_account_key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
            
            if not service_account_key or not sheets_id:
                return {"success": False, "error": "Google Sheets not configured"}
            
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
            
            # Ensure header exists
            try:
                header = sheet.row_values(1)
                if not header or header != ["Tanggal", "Kategori", "Jumlah", "Keterangan"]:
                    sheet.insert_row(["Tanggal", "Kategori", "Jumlah", "Keterangan"], 1)
            except:
                sheet.insert_row(["Tanggal", "Kategori", "Jumlah", "Keterangan"], 1)
            
            sheet.append_row([timestamp, kategori, jumlah, keterangan])
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

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
