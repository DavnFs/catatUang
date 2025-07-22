from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Test GET request"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Check environment variables
        env_status = {
            "telegram_token": "✅" if os.getenv('TELEGRAM_BOT_TOKEN') else "❌ MISSING",
            "google_sheets_id": "✅" if os.getenv('GOOGLE_SHEETS_ID') else "❌ MISSING", 
            "google_key": "✅" if os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY') else "❌ MISSING"
        }
        
        response = {
            "status": "ok",
            "message": "Telegram webhook endpoint is running!",
            "environment_variables": env_status,
            "endpoint": "/api/telegram-webhook-minimal",
            "note": "This is the minimal version for testing"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
        
    def do_POST(self):
        """Handle minimal Telegram webhook"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            webhook_data = json.loads(post_data.decode('utf-8'))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ok",
                "message": "Webhook received successfully!",
                "received_data": webhook_data,
                "note": "Minimal webhook handler - not processing yet"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "message": str(e),
                "endpoint": "/api/telegram-webhook-minimal"
            }
            
            self.wfile.write(json.dumps(error_response).encode())
