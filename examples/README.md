# CatatUang Examples

Folder ini berisi contoh-contoh implementasi dan testing untuk CatatUang.

## 📁 Files

### `test_api.py`
Script Python untuk testing semua endpoint API secara comprehensive.

**Usage:**
```bash
pip install requests
python test_api.py
```

**Features:**
- Test basic webhook functionality
- Test WhatsApp Cloud API format
- Test Twilio webhook format  
- Test report generation
- Test CORS headers
- Stress testing
- Health check

### `whatsapp_bot.js`
WhatsApp bot menggunakan whatsapp-web.js yang otomatis forward pesan ke CatatUang API.

**Setup:**
```bash
npm init -y
npm install whatsapp-web.js qrcode-terminal axios
node whatsapp_bot.js
```

**Features:**
- Auto-forward expense messages ke API
- Generate dan kirim laporan
- Help command
- Error handling
- Graceful shutdown

### `credentials.json.example`
Template file untuk Google Service Account credentials.

**Usage:**
1. Download actual credentials dari Google Cloud Console
2. Copy format dari file ini
3. **NEVER commit actual credentials ke Git**

## 🧪 Testing Workflow

### 1. Local Testing
```bash
# Start local development
vercel dev

# Update test_api.py BASE_URL ke http://localhost:3000
python test_api.py
```

### 2. Production Testing
```bash
# Update test_api.py BASE_URL ke https://your-app.vercel.app
python test_api.py
```

### 3. WhatsApp Bot Testing
```bash
# Update WEBHOOK_URL di whatsapp_bot.js
node whatsapp_bot.js

# Scan QR code
# Send test messages: #jajan 15000 bakso
```

## 📱 WhatsApp Testing Messages

Copy-paste messages ini untuk testing:

```
#jajan 15000 bakso
#transport 25000 ojek ke kantor
#makan 30000 nasi padang
#kopi 12000 es kopi susu
#belanja 50000 groceries
#bensin 100000 isi tank
#gym 150000 membership
laporan
help
```

## 🔧 Environment Setup

Pastikan environment variables sudah diset:

```bash
GOOGLE_SHEETS_ID=your_sheets_id
GOOGLE_SERVICE_ACCOUNT_KEY=base64_encoded_credentials
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

## 📊 Expected Results

Setelah testing, Anda harus lihat:

1. **Google Sheets** - Data expense baru
2. **Console logs** - Success/error messages  
3. **WhatsApp replies** - Confirmation messages
4. **API responses** - JSON dengan status success

## 🚨 Troubleshooting

### Common Issues:

**"Connection failed"**
- Check BASE_URL/WEBHOOK_URL
- Verify Vercel deployment status
- Check internet connection

**"Google Sheets not configured"**  
- Verify environment variables
- Check service account permissions
- Ensure sheets is shared

**"WhatsApp auth failed"**
- Restart whatsapp_bot.js
- Re-scan QR code
- Check device WhatsApp status

### Debug Tips:

```bash
# Check Vercel logs
vercel logs --follow

# Test single endpoint
curl https://your-app.vercel.app/api/webhook

# Check environment variables
vercel env ls
```

---

Happy testing! 🚀
