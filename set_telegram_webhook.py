#!/usr/bin/env python3
"""
Script untuk setup webhook Telegram Bot
Usage: python set_telegram_webhook.py
"""

import os
import requests
import sys

def set_webhook():
    # Get environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    webhook_url = input("Enter your Vercel app URL (e.g., https://your-app.vercel.app): ").strip()
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        print("Please set your bot token in .env file")
        return False
    
    if not webhook_url:
        print("❌ Webhook URL required!")
        return False
    
    if not webhook_url.startswith('http'):
        webhook_url = f"https://{webhook_url}"
    
    webhook_endpoint = f"{webhook_url}/api/telegram-webhook"
    
    print(f"🤖 Setting webhook for bot...")
    print(f"📡 Webhook URL: {webhook_endpoint}")
    
    # Set webhook
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    payload = {
        'url': webhook_endpoint,
        'drop_pending_updates': True
    }
    
    try:
        response = requests.post(api_url, json=payload)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook berhasil diset!")
            print(f"📋 Description: {result.get('description', 'Success')}")
            
            # Get webhook info
            info_response = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
            webhook_info = info_response.json()
            
            if webhook_info.get('ok'):
                info = webhook_info['result']
                print(f"\n📊 Webhook Info:")
                print(f"   URL: {info.get('url')}")
                print(f"   Pending updates: {info.get('pending_update_count', 0)}")
                if info.get('last_error_message'):
                    print(f"   Last error: {info.get('last_error_message')}")
            
            print(f"\n🎯 Next steps:")
            print(f"1. Search your bot in Telegram: @{get_bot_username(bot_token)}")
            print(f"2. Send /start to test")
            print(f"3. Try: 50000 makanan nasi padang")
            
            return True
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def get_bot_username(bot_token):
    """Get bot username"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        result = response.json()
        if result.get('ok'):
            return result['result'].get('username', 'unknown')
    except:
        pass
    return 'your_bot'

def delete_webhook():
    """Delete webhook (for testing local bot)"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        return False
    
    try:
        response = requests.post(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook deleted!")
            print("Now you can run local bot with: python examples/telegram_bot_local.py")
            return True
        else:
            print(f"❌ Error: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Make sure TELEGRAM_BOT_TOKEN is set in environment.")
    
    print("🤖 Telegram Bot Webhook Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'delete':
        delete_webhook()
        return
    
    print("\nOptions:")
    print("1. Set webhook (for production)")
    print("2. Delete webhook (for local testing)")
    print("3. Check current webhook")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        set_webhook()
    elif choice == '2':
        delete_webhook()
    elif choice == '3':
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if bot_token:
            try:
                response = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
                result = response.json()
                if result.get('ok'):
                    info = result['result']
                    print(f"\n📊 Current Webhook:")
                    print(f"   URL: {info.get('url', 'Not set')}")
                    print(f"   Pending updates: {info.get('pending_update_count', 0)}")
                    if info.get('last_error_message'):
                        print(f"   Last error: {info.get('last_error_message')}")
                else:
                    print(f"❌ Error: {result.get('description')}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ TELEGRAM_BOT_TOKEN not found!")
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()
