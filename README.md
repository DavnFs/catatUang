# 🤖 CatatUang - Telegram Expense Tracker Bot

[![Deploy with Vercel](https://vercel.com/button)](http## 🤖 Cara Pakai

### Commands Telegram:
```
/start    - Mulai bot & lihat panduan
/help     - Bantuan lengkap  
/report   - Laporan hari ini
/week     - Laporan minggu ini
/month    - Laporan bulan ini
```

### Format Transaksi:
```
# Pengeluaran
50000 makanan nasi padang
25000 transport ojek ke kantor
15000 kopi es kopi susu

# Pemasukan (pakai tanda +)
+1000000 gaji salary bulan ini
+500000 bonus kinerja
```/new/clone?repository-url=https://github.com/yourusername/catatuang)

Bot Telegram serverless untuk mencatat pengeluaran otomatis. Deploy sekali, pakai selamanya! 🚀

## ✨ Fitur

- 🤖 **Telegram Bot Interface** - Chat natural untuk catat transaksi
- 📊 **Google Sheets Auto-Save** - Data tersimpan otomatis di spreadsheet  
- ⚡ **Serverless** - Zero server maintenance, pay per use
- � **100% Gratis** - Telegram Bot API gratis tanpa batas
- 📈 **Smart Reports** - Laporan via /report command
- 🔒 **Secure** - Environment variables yang aman

## 🚀 Quick Start

### ⚡ Super Quick Setup (Windows)
```bash
# Run auto setup script
powershell -ExecutionPolicy Bypass -File setup.ps1

# Or use deployment helper
deploy.bat
```

### ⚡ Super Quick Setup (Linux/Mac)
```bash
# Run auto setup script
chmod +x setup.sh
./setup.sh
```

### 📖 Manual Setup

#### 1. Deploy ke Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/catatuang)

Atau manual:
```bash
git clone https://github.com/yourusername/catatuang.git
cd catatuang
vercel --prod
```

#### 2. Setup Environment Variables

Di Vercel Dashboard → Settings → Environment Variables:

```bash
GOOGLE_SHEETS_ID=your_google_sheets_id
GOOGLE_SERVICE_ACCOUNT_KEY=base64_encoded_service_account_json  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

#### 3. Setup Google Sheets

1. **Buat Google Cloud Project** → Enable Google Sheets API
2. **Buat Service Account** → Download JSON credentials
3. **Encode ke Base64**: `base64 -i credentials.json | tr -d '\n'`
4. **Buat Google Sheets** → Share dengan service account email
5. **Copy Sheets ID** dari URL

### 4. Setup Telegram Bot

1. **Chat @BotFather** di Telegram
2. **Create bot**: `/newbot` → beri nama & username
3. **Copy token** dan set di environment variables
4. **Set webhook**: `https://your-app.vercel.app/api/telegram-webhook`

## � Documentation

| Document | Description |
|----------|-------------|
| [QUICK_START.md](QUICK_START.md) | ⚡ 15-minute setup guide |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | 📖 Complete step-by-step guide |
| [docs/setup.md](docs/setup.md) | 🔧 Technical setup details |
| [docs/api.md](docs/api.md) | 📡 API documentation |
| [docs/structure.md](docs/structure.md) | 🏗️ Project structure |
| [examples/README.md](examples/README.md) | 💡 Usage examples |

## 🛠️ Development Tools

| File | Purpose |
|------|---------|
| `setup.ps1` | Windows PowerShell auto-setup |
| `setup.sh` | Linux/Mac bash auto-setup |
| `deploy.bat` | Windows deployment helper |
| `encode_credentials.py` | Python script untuk encode service account |
| `encode_credentials.ps1` | PowerShell script untuk encode service account |
| `examples/test_api.py` | API testing script |
| `examples/telegram_bot_local.py` | Local Telegram bot untuk testing |

### 🔐 Quick Credential Setup

```bash
# Windows - Encode service account to base64
powershell -File encode_credentials.ps1

# Linux/Mac - Encode service account to base64  
python3 encode_credentials.py
```

## �📱 Cara Pakai

### Format WhatsApp:
```
#kategori jumlah keterangan
```

### Contoh:
```
#jajan 15000 bakso
#transport 25000 ojek ke kantor
#makan 30000 nasi padang
#kopi 12000 es kopi susu
```

## 🔗 API Endpoints

| Endpoint | Method | Fungsi |
|----------|--------|--------|
| `/api/telegram-webhook` | GET | Status check |
| `/api/telegram-webhook` | POST | Terima pesan Telegram |
| `/api/report` | GET | Generate laporan pengeluaran |

## 📊 Response Format

### Success Response:
```json
{
  "status": "success",
  "data": {
    "timestamp": "2025-01-22 10:30:00",
    "kategori": "jajan",
    "jumlah": 15000,
    "keterangan": "bakso"
  },
  "message": "✅ Berhasil mencatat: jajan Rp 15,000"
}
```

### Report Response:
```json
{
  "status": "success",
  "summary": {
    "total_expense": 125000,
    "total_transactions": 8,
    "categories": {
      "jajan": 45000,
      "transport": 50000,
      "kopi": 30000
    }
  },
  "recent_transactions": [...],
  "message": "Report generated with 8 transactions"
}
```

## 🛠️ Development

### Local Testing:
```bash
# Install Vercel CLI
npm i -g vercel

# Clone & setup
git clone https://github.com/yourusername/catatuang.git
cd catatuang

# Setup environment
vercel env pull .env.local

# Run locally
vercel dev
```

### Test Endpoints:
```bash
# Test webhook
curl -X POST http://localhost:3000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "#jajan 15000 bakso"}'

# Test report  
curl http://localhost:3000/api/report
```

## 🔧 Telegram Setup

### 1. Buat Bot di Telegram
1. Chat **@BotFather** di Telegram
2. Kirim `/newbot`
3. Beri nama bot: `CatatUang Bot`
4. Beri username: `@catatuang_yourname_bot`
5. Copy token yang diberikan

### 2. Set Webhook (Setelah Deploy)
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app.vercel.app/api/telegram-webhook"}'
```

### 3. Test Local Development
```bash
# Setup environment
cp .env.example .env.local
# Edit .env.local dengan credentials

# Install dependencies
pip install -r requirements.txt

# Run local bot untuk testing
python examples/telegram_bot_local.py
```
2. Get access token dari Meta for Developers  
3. Set webhook: `https://your-app.vercel.app/api/webhook`
4. Set verify token di environment variables

### Option 3: Provider Indonesia
- [Fonnte](https://fonnte.com/)
- [Wablas](https://wablas.com/)
- [Woowa](https://woowa.id/)

## 📈 Production Checklist

- [ ] ✅ Deploy to Vercel
- [ ] ✅ Setup Google Sheets + Service Account
- [ ] ✅ Configure environment variables
- [ ] ✅ Setup Telegram bot + webhook
- [ ] ✅ Test all endpoints
- [ ] ✅ Monitor logs di Vercel dashboard

## 🏗️ Architecture

```
🤖 Telegram → 🔗 Webhook → ⚡ Vercel Function → 📊 Google Sheets
```

**Flow:**
1. User kirim pesan `50000 makanan nasi padang` di Telegram
2. Telegram kirim webhook ke `/api/telegram-webhook`
3. Vercel function parse pesan → validate → save ke Google Sheets
4. Bot reply dengan konfirmasi

## 💡 Advanced Features

### Custom Categories:
Tambah kategori baru langsung pakai:
```
100000 gym membership bulanan
50000 gift kado ulang tahun
+2000000 freelance project selesai
```

### Smart Commands:
```
/report     - Hari ini
/week       - 7 hari terakhir  
/month      - Bulan ini
/categories - Lihat semua kategori
```

### Error Handling:
- Input validation
- Graceful error messages
- Comprehensive logging

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - silakan gunakan untuk personal maupun komersial.

## 🙋‍♂️ Support

- 📖 [Documentation](./docs/)
- 🐛 [Issues](https://github.com/yourusername/catatuang/issues)
- 💬 [Discussions](https://github.com/yourusername/catatuang/discussions)

## 🌟 Showcase

Sudah pakai CatatUang? Tag kami di sosial media!

**Made with ❤️ for automated expense tracking**

---

⭐ **Star this repo if it helps you!** ⭐
