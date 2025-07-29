import requests
import json
import time

# Configuration
BASE_URL = "https://your-app.vercel.app"  # Replace with your Vercel URL
# BASE_URL = "http://localhost:3000"  # For local testing

def test_webhook_basic():
    """Test basic webhook functionality"""
    print("🧪 Testing webhook endpoint...")
    
    test_cases = [
        {"text": "#jajan 15000 bakso", "expected": "success"},
        {"text": "#transport 25000 ojek", "expected": "success"},
        {"text": "#makan 30000 nasi padang", "expected": "success"},
        {"text": "jajan 15000 bakso", "expected": "error"},  # Missing #
        {"text": "#jajan", "expected": "error"},  # Missing amount
        {"text": "#jajan abc bakso", "expected": "error"},  # Invalid amount
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/api/webhook",
                json=test_case,
                timeout=10
            )
            result = response.json()
            
            status = result.get('status')
            message = result.get('message', 'No message')
            
            if status == test_case['expected']:
                print(f"✅ Test {i}: {test_case['text'][:20]}... → {status}")
            else:
                print(f"❌ Test {i}: Expected {test_case['expected']}, got {status}")
                print(f"   Message: {message}")
                
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
    
    print()

def test_whatsapp_cloud_api_format():
    """Test WhatsApp Cloud API webhook format"""
    print("☁️ Testing WhatsApp Cloud API format...")
    
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550559999",
                                "phone_number_id": "123456789"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": "6281234567890"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "6281234567890",
                                    "id": "wamid.xxx",
                                    "timestamp": "1642000000",
                                    "text": {"body": "#kopi 12000 es kopi susu"},
                                    "type": "text"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/webhook", json=webhook_data)
        result = response.json()
        print(f"✅ WhatsApp Cloud API: {result.get('message', result)}")
    except Exception as e:
        print(f"❌ WhatsApp Cloud API test failed: {e}")
    
    print()

def test_twilio_format():
    """Test Twilio webhook format"""
    print("📞 Testing Twilio format...")
    
    twilio_data = {
        "Body": "#belanja 50000 groceries",
        "From": "whatsapp:+6281234567890",
        "To": "whatsapp:+14155238886",
        "MessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "AccountSid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/webhook", json=twilio_data)
        result = response.json()
        print(f"✅ Twilio format: {result.get('message', result)}")
    except Exception as e:
        print(f"❌ Twilio test failed: {e}")
    
    print()

def test_report_endpoint():
    """Test report generation"""
    print("📊 Testing report endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/report", timeout=15)
        result = response.json()
        
        if result.get('status') == 'success':
            summary = result.get('summary', {})
            print(f"✅ Report generated successfully!")
            print(f"   Total Expense: Rp {summary.get('total_expense', 0):,}")
            print(f"   Total Transactions: {summary.get('total_transactions', 0)}")
            print(f"   Categories: {list(summary.get('categories', {}).keys())}")
        else:
            print(f"⚠️ Report error: {result.get('message', result)}")
            
    except Exception as e:
        print(f"❌ Report test failed: {e}")
    
    print()

def test_verification():
    """Test WhatsApp verification"""
    print("🔐 Testing webhook verification...")
    
    try:
        # Test verification endpoint
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'test_token',
            'hub.challenge': 'test_challenge_123'
        }
        
        response = requests.get(f"{BASE_URL}/api/webhook", params=params)
        
        if response.status_code == 200:
            if response.text == 'test_challenge_123':
                print("✅ Verification with correct token: Success")
            else:
                print("⚠️ Verification returned unexpected response")
        else:
            print(f"⚠️ Verification failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Verification test failed: {e}")
    
    print()

def test_cors():
    """Test CORS headers"""
    print("🌐 Testing CORS...")
    
    try:
        response = requests.options(f"{BASE_URL}/api/report")
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'Not found')
        print(f"✅ CORS header: {cors_header}")
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
    
    print()

def stress_test():
    """Simple stress test"""
    print("⚡ Running stress test (10 concurrent requests)...")
    
    import concurrent.futures
    import threading
    
    def send_request(i):
        try:
            response = requests.post(
                f"{BASE_URL}/api/webhook",
                json={"text": f"#test {1000 * i} stress test {i}"},
                timeout=10
            )
            return f"Request {i}: {response.status_code}"
        except Exception as e:
            return f"Request {i}: Failed - {e}"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_request, i) for i in range(1, 11)]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(f"   {result}")
    
    print()

def health_check():
    """Basic health check"""
    print("🏥 Health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/webhook", timeout=5)
        if response.status_code == 200:
            print("✅ Service is healthy")
        else:
            print(f"⚠️ Service returned {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print()

if __name__ == "__main__":
    print("🚀 CatatUang API Testing Suite")
    print("=" * 50)
    print(f"🌐 Testing: {BASE_URL}")
    print()
    
    # Run all tests
    health_check()
    test_verification()
    test_webhook_basic()
    test_whatsapp_cloud_api_format()
    test_twilio_format()
    test_cors()
    test_report_endpoint()
    
    # Optional stress test (uncomment if needed)
    # stress_test()
    
    print("✅ Testing completed!")
    print()
    print("📝 Next steps:")
    print("1. Check your Google Sheets for new test data")
    print("2. Update BASE_URL with your actual Vercel URL")
    print("3. Setup WhatsApp webhook with this URL:")
    print(f"   {BASE_URL}/api/webhook")
    print("4. Test with real WhatsApp messages!")
    print()
    print("🎉 Happy expense tracking!")
