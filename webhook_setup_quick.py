#!/usr/bin/env python3
"""
Quick script untuk set Telegram webhook setelah deploy Vercel
"""

import requests

def set_webhook_quick():
    print("🤖 CatatUang - Set Telegram Webhook")
    print("=" * 40)
    
    # Input dari user
    bot_token = input("Bot Token dari @BotFather: ").strip()
    vercel_url = input("Vercel URL (contoh: catatuang-xxx.vercel.app): ").strip()
    
    # Clean URL
    if not vercel_url.startswith('http'):
        vercel_url = f"https://{vercel_url}"
    
    webhook_url = f"{vercel_url}/api/telegram-webhook"
    
    print(f"\n🔗 Setting webhook: {webhook_url}")
    
    # Set webhook
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    try:
        response = requests.post(api_url, json={'url': webhook_url})
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook berhasil diset!")
            
            # Get bot info
            bot_response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
            bot_info = bot_response.json()
            
            if bot_info.get('ok'):
                username = bot_info['result'].get('username')
                print(f"\n🎯 Bot siap digunakan!")
                print(f"📱 Search di Telegram: @{username}")
                print(f"🚀 Kirim /start untuk test")
                print(f"💰 Test transaksi: 50000 makanan nasi padang")
            
        else:
            print(f"❌ Error: {result.get('description')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    set_webhook_quick()
