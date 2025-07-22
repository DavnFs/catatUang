# 🚀 CatatUang - Panduan Setup Lengkap

Panduan step-by-step untuk setup project CatatUang dari awal hingga production.

## 📋 Daftar Isi

1. [Persyaratan Sistem](#persyaratan-sistem)
2. [Setup Lokal](#setup-lokal)
3. [Konfigurasi Google Sheets](#konfigurasi-google-sheets)
4. [Setup WhatsApp Integration](#setup-whatsapp-integration)
5. [Deploy ke Vercel](#deploy-ke-vercel)
6. [Testing & Troubleshooting](#testing--troubleshooting)
7. [Maintenance](#maintenance)

## 📌 Persyaratan Sistem

### Yang Dibutuhkan:
- Node.js (v16+) dan npm
- Python 3.7+
- Git
- Akun Google (untuk Google Sheets API)
- Akun Vercel (untuk hosting)
- Akun WhatsApp Business API (opsional, untuk production)

### Tools Development:
- VS Code atau editor lainnya
- Terminal/Command Prompt
- Browser untuk testing

## 🔧 Setup Lokal

### 1. Clone Repository

```bash
# Clone dari GitHub (jika sudah diupload)
git clone https://github.com/username/catatuang.git
cd catatuang

# Atau download ZIP dan extract
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (untuk development tools)
npm install
```

### 3. Setup Environment Variables

Buat file `.env.local` di root folder:

```bash
# Copy template
cp examples/credentials.json.example .env.local
```

Edit `.env.local`:
```env
# Google Sheets Configuration
GOOGLE_SERVICE_ACCOUNT_KEY=<base64_encoded_service_account_json>
GOOGLE_SHEETS_ID=<your_google_sheets_id>

# WhatsApp Configuration (opsional)
WHATSAPP_TOKEN=<your_whatsapp_token>
WHATSAPP_VERIFY_TOKEN=<your_verify_token>

# Development
NODE_ENV=development
```

## 📊 Konfigurasi Google Sheets

### 1. Buat Google Sheets

1. Buka [Google Sheets](https://sheets.google.com)
2. Buat spreadsheet baru
3. Rename menjadi "CatatUang Database"
4. Buat header di baris pertama:
   ```
   A1: Tanggal
   B1: Kategori  
   C1: Deskripsi
   D1: Jumlah
   E1: Sumber
   ```

### 2. Setup Google Cloud Project

1. Buka [Google Cloud Console](https://console.cloud.google.com)
2. Buat project baru atau pilih existing
3. Enable APIs:
   - Google Sheets API
   - Google Drive API

### 3. Create Service Account

1. Navigate ke "IAM & Admin" > "Service Accounts"
2. Klik "Create Service Account"
3. Isi detail:
   - Name: `catatuang-service`
   - Description: `Service account for CatatUang app`
4. Grant roles:
   - Editor (atau Google Sheets API permissions)
5. Create key:
   - Key type: JSON
   - Download file JSON

### 4. Share Google Sheets

1. Buka Google Sheets yang sudah dibuat
2. Klik "Share"
3. Add email service account (dari JSON file)
4. Permission: Editor
5. Copy Sheets ID dari URL:
   ```
   https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit
   ```

### 5. Encode Service Account

**Option 1: Gunakan Helper Script (Recommended)**

Windows:
```powershell
# Drag & drop file JSON ke script ini
powershell -File encode_credentials.ps1

# Atau dengan path langsung
powershell -File encode_credentials.ps1 "C:\path\to\service-account.json"
```

Linux/Mac:
```bash
# Interactive mode
python3 encode_credentials.py

# Atau dengan path langsung
python3 encode_credentials.py ./service-account.json
```

**Option 2: Manual Encoding**

```bash
# Linux/Mac
base64 -i path/to/service-account.json

# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("path\to\service-account.json"))

# Atau gunakan online base64 encoder
```

Copy hasil encoding ke environment variable `GOOGLE_SERVICE_ACCOUNT_KEY`.

## 📱 Setup WhatsApp Integration

### Option 1: WhatsApp Business API (Production)

1. Daftar di [Meta for Developers](https://developers.facebook.com)
2. Create App > Business
3. Add WhatsApp Product
4. Setup:
   - Phone number
   - Webhook URL: `https://your-app.vercel.app/api/webhook`
   - Verify token: buat token random
5. Get access token dari dashboard

### Option 2: WhatsApp Web (Development)

Gunakan library seperti `whatsapp-web.js` (lihat `examples/whatsapp_bot.js`):

```bash
cd examples
npm install whatsapp-web.js qrcode-terminal
node whatsapp_bot.js
```

### 3. Test Integration

```bash
# Test webhook endpoint
curl -X POST http://localhost:3000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"from":"1234567890","body":{"text":"belanja 50000 makanan di warteg"}}]}'
```

## 🚀 Deploy ke Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login Vercel

```bash
vercel login
```

### 3. Configure Project

```bash
# Di root folder project
vercel

# Ikuti prompts:
# ? Set up and deploy "catatuang"? Y
# ? In which directory is your code located? ./
# ? Want to override the settings? Y
# ? What's your build command? (leave empty)
# ? What's your output directory? (leave empty)
# ? What's your install command? pip install -r requirements.txt
```

### 4. Set Environment Variables

```bash
# Via CLI
vercel env add GOOGLE_SERVICE_ACCOUNT_KEY
vercel env add GOOGLE_SHEETS_ID
vercel env add WHATSAPP_TOKEN
vercel env add WHATSAPP_VERIFY_TOKEN

# Atau via Vercel Dashboard:
# 1. Buka project di vercel.com
# 2. Settings > Environment Variables
# 3. Add variables satu per satu
```

### 5. Deploy

```bash
vercel --prod
```

### 6. Setup Custom Domain (Opsional)

1. Buka Vercel Dashboard
2. Project Settings > Domains
3. Add domain yang sudah dimiliki
4. Configure DNS records

## 🧪 Testing & Troubleshooting

### 1. Test Local Development

```bash
# Install vercel dev untuk local testing
npm install -g vercel
vercel dev

# Test endpoints
curl http://localhost:3000/api/webhook
curl http://localhost:3000/api/report
```

### 2. Test API Endpoints

```bash
# Test webhook
python examples/test_api.py

# Atau manual test
curl -X GET https://your-app.vercel.app/api/report
```

### 3. Common Issues

#### Google Sheets Error
```
Error: Google Sheets not configured
```
**Solution:** Check environment variables dan pastikan service account sudah di-share ke sheets.

#### WhatsApp Connection Error
```
Error: Invalid webhook token
```
**Solution:** Pastikan `WHATSAPP_VERIFY_TOKEN` sama dengan yang di Meta Dashboard.

#### Vercel Deploy Error
```
Error: Python runtime not found
```
**Solution:** Pastikan `vercel.json` sudah benar dan `requirements.txt` ada.

### 4. Debug Logs

```bash
# Vercel function logs
vercel logs

# Real-time logs
vercel logs --follow
```

## 🔄 Maintenance

### 1. Update Dependencies

```bash
# Update Python packages
pip list --outdated
pip install --upgrade package_name

# Update requirements.txt
pip freeze > requirements.txt
```

### 2. Backup Data

```bash
# Export Google Sheets data
python -c "
import gspread
# ... script untuk export data
"
```

### 3. Monitor Usage

1. Vercel Dashboard > Analytics
2. Google Cloud Console > API Usage
3. WhatsApp Business > Analytics

### 4. Security Updates

- Rotate service account keys every 90 days
- Update webhook tokens
- Review permissions regularly

## 📚 Resources

- [Dokumentasi API](docs/api.md)
- [Struktur Project](docs/structure.md)
- [Setup Detail](docs/setup.md)
- [Examples](examples/README.md)

## 🆘 Support

Jika mengalami masalah:

1. Check troubleshooting di atas
2. Lihat logs di Vercel Dashboard
3. Buat issue di GitHub repository
4. Contact developer

---

**Status:** ✅ Project siap production  
**Version:** 1.0.0  
**Last Updated:** Juli 2025
