#!/usr/bin/env python3
"""
Local Telegram Bot untuk Testing CatatUang
Gunakan ini untuk development sebelum deploy ke production
"""

import os
import json
import requests
from datetime import datetime
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    """Send message to Telegram chat"""
    url = f"{API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def get_updates(offset=None):
    """Get updates from Telegram"""
    url = f"{API_URL}/getUpdates"
    params = {'timeout': 10}
    if offset:
        params['offset'] = offset
    
    response = requests.get(url, params=params)
    return response.json()

def process_message(message):
    """Process incoming message"""
    chat_id = message['chat']['id']
    user = message['from']
    text = message.get('text', '')
    
    print(f"Message from {user.get('first_name', 'Unknown')}: {text}")
    
    # Simulate webhook processing
    webhook_data = {
        'message': {
            'chat': {'id': chat_id},
            'from': user,
            'text': text
        }
    }
    
    # Process with local webhook logic
    try:
        # Import webhook handler
        import sys
        sys.path.append('../api')
        # from telegram_webhook import handler
        
        # Simple local processing for testing
        if text.startswith('/start'):
            response_text = f"""👋 Halo! Selamat datang di CatatUang Bot!

🤖 **Cara Pakai:**
• Tulis pengeluaran: `50000 makanan nasi padang`
• Tulis pemasukan: `+1000000 gaji salary`
• Lihat laporan: /report

📋 **Commands:**
/help - Bantuan lengkap
/report - Laporan hari ini
/categories - Daftar kategori

💡 **Contoh:**
`15000 transport ojek ke kantor`
`+500000 bonus kinerja`"""
            
        elif text.startswith('/help'):
            response_text = """📚 **Panduan CatatUang Bot**

**Format Pengeluaran:**
`[jumlah] [kategori] [deskripsi]`

**Format Pemasukan:**
`+[jumlah] [kategori] [deskripsi]`

**Commands:**
/start - Mulai bot
/report - Laporan hari ini
/categories - Kategori tersedia

💡 **Contoh:**
• `50000 makanan nasi padang`
• `+1000000 gaji salary`"""
            
        elif text.startswith('/'):
            response_text = f"Command: {text}\n\n✅ Bot berfungsi! Deploy ke Vercel untuk fitur lengkap."
            
        else:
            # Simple expense parsing
            try:
                parts = text.strip().split(' ', 2)
                if len(parts) >= 2:
                    amount = parts[0]
                    category = parts[1]
                    description = parts[2] if len(parts) > 2 else ""
                    
                    is_income = amount.startswith('+')
                    amount_clean = amount.replace('+', '').replace(',', '')
                    
                    tipe = "💰 Pemasukan" if is_income else "💸 Pengeluaran"
                    response_text = f"""{tipe} Tercatat! ✅

💵 Jumlah: Rp {amount_clean}
📂 Kategori: {category.title()}
📝 Deskripsi: {description}
📅 Waktu: {datetime.now().strftime('%d/%m/%Y %H:%M')}

🚀 Deploy ke Vercel untuk save ke Google Sheets!"""
                else:
                    response_text = "❌ Format salah!\n\n✅ Contoh: `50000 makanan nasi padang`"
            except:
                response_text = "❌ Format tidak valid. Ketik /help untuk panduan."
        
        send_message(chat_id, response_text)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        # Fallback to simple echo
        send_message(chat_id, f"Echo: {text}")

def main():
    """Main bot loop"""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Set your bot token in .env file")
        return
    
    print("🤖 CatatUang Telegram Bot started!")
    print("Bot token:", BOT_TOKEN[:10] + "...")
    
    # Get bot info
    try:
        response = requests.get(f"{API_URL}/getMe")
        bot_info = response.json()
        if bot_info['ok']:
            bot = bot_info['result']
            print(f"Bot name: {bot['first_name']}")
            print(f"Username: @{bot['username']}")
        else:
            print("❌ Invalid bot token!")
            return
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        return
    
    print("\n📱 Waiting for messages...")
    print("Send /start to your bot to test!")
    print("Press Ctrl+C to stop\n")
    
    offset = None
    
    try:
        while True:
            try:
                # Get updates
                updates = get_updates(offset)
                
                if updates['ok']:
                    for update in updates['result']:
                        offset = update['update_id'] + 1
                        
                        if 'message' in update:
                            process_message(update['message'])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n👋 Stopping bot...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n👋 Bot stopped!")

if __name__ == "__main__":
    main()
