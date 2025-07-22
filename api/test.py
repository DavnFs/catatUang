from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "CatatUang Telegram Bot is running!",
            "endpoint": "/api/telegram-webhook",
            "method": "POST"
        }
        
        self.wfile.write(json.dumps(response).encode())
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "Webhook endpoint is working!",
            "note": "This is a test response"
        }
        
        self.wfile.write(json.dumps(response).encode())
