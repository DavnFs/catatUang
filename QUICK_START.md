# ⚡ Quick Start Guide - CatatUang Telegram Bot

Panduan cepat untuk setup CatatUang Telegram Bot dalam 10 menit.

## 🎯 Langkah Cepat (10 menit)

### 1. Prerequisites (1 menit)
- [x] Akun Google
- [x] Akun Vercel (gratis)
- [x] Akun Telegram

### 2. Setup Telegram Bot (2 menit)

**a. Buat Bot di Telegram:**
1. Chat **@BotFather** di Telegram
2. Kirim `/newbot`
3. Beri nama: "CatatUang Bot"
4. Beri username: "@catatuang_yourname_bot"
5. **Copy token** yang diberikan

### 3. Setup Google Sheets (3 menit)

**a. Buat Google Sheets:**
1. Buka https://sheets.google.com
2. New Spreadsheet
3. Rename: "CatatUang Database"
4. Header row: `Tanggal | Kategori | Deskripsi | Jumlah | Sumber`

**b. Setup API:**
1. https://console.cloud.google.com → New Project
2. APIs & Services → Enable APIs:
   - Google Sheets API ✅
   - Google Drive API ✅

**c. Service Account:**
1. IAM & Admin → Service Accounts → Create
2. Name: `catatuang-service`
3. Role: Editor
4. Create Key → JSON → Download
5. Share Sheets dengan email service account

### 4. Deploy ke Vercel (3 menit)

**a. Fork/Clone Repository:**
```bash
git clone https://github.com/username/catatuang.git
cd catatuang
```

**b. Deploy:**
```bash
npm install -g vercel
vercel login
vercel
```

**c. Environment Variables:**
Di Vercel Dashboard → Project → Settings → Environment Variables:

| Variable | Value | Description |
|----------|--------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Base64 dari JSON file | Credentials Google Sheets API |
| `GOOGLE_SHEETS_ID` | ID dari URL Sheets | Target spreadsheet |
| `TELEGRAM_BOT_TOKEN` | Token dari @BotFather | Bot authentication |

### 5. Setup Webhook & Test (2 menit)

**a. Set Webhook:**
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app.vercel.app/api/telegram-webhook"}'
```

**b. Test Bot:**
1. Search bot di Telegram: `@catatuang_yourname_bot`
2. Kirim `/start`
3. Test transaksi: `50000 makanan nasi padang`
4. Test laporan: `/report`

## 🎉 Done!

Bot Telegram sudah siap! 🚀

**Format Pesan:**
```
# Pengeluaran
50000 makanan nasi padang
25000 transport ojek

# Pemasukan 
+1000000 gaji salary
+500000 bonus

# Commands
/start /help /report /week /month
```

##  Troubleshooting

| Error | Solution |
|-------|----------|
| Google Sheets not configured | Check environment variables |
| Invalid bot token | Check TELEGRAM_BOT_TOKEN |
| Python runtime error | Check vercel.json config |
| Bot not responding | Check webhook URL & verify token |

## 📱 Mobile URLs

Setelah deploy, bookmark URL ini:

- **View Report:** `https://your-app.vercel.app/api/report`
- **Bot Status:** `https://your-app.vercel.app/api/telegram-webhook` 
- **Google Sheets:** Link direct ke sheets

## 🎉 Ready to Use!

Your CatatUang Telegram Bot is ready! 

**Next Steps:**
- Customize categories in `api/telegram-webhook.py`
- Add more commands & features
- Setup monitoring & backups
- Invite family/team to use bot

---

Need help? Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.
