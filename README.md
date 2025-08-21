# 🤖 CatatUang - AI-Powered Expense Tracker Bot

A serverless Telegram bot for automatic expense tracking with **AI-powered financial insights**. Deploy once, use forever! 🚀

## ✨ Features

- 🤖 **AI Financial Advisor** - Smart insights and recommendations powered by Gemini/Groq/OpenAI
- 📊 **Google Sheets Auto-Save** - Data automatically saved to your spreadsheet
- ⚡ **Serverless Architecture** - Zero server maintenance, pay-per-use
- 💰 **100% Free Deployment** - Telegram Bot API + Vercel free tier
- 📈 **Smart Reports & Analytics** - Comprehensive financial reporting
- 🎯 **Budget Planning** - AI-powered budget recommendations and feasibility checks
- 🔒 **Secure** - Your data stays in your Google Sheets


### Manual Installation

## 📋 Prerequisites

Before you start, you'll need:

1. **Telegram Account** - To create the bot
2. **Google Account** - For Google Sheets integration
3. **Vercel Account** - For free hosting
4. **AI API Key** - For smart financial insights (optional but recommended)

## 🛠️ Step-by-Step Setup

### Step 1: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Choose a name (e.g., "My Expense Tracker")
4. Choose a username (e.g., "@myexpense_bot")
5. **Save the bot token** - you'll need it later

### Step 2: Setup Google Sheets Integration

#### 2.1 Create Google Sheets
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. **Copy the Sheets ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit
   ```

#### 2.2 Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable **Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search "Google Sheets API" and enable it
4. Create Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
5. Generate Key:
   - Click on the created service account
   - Go to "Keys" tab > "Add Key" > "Create new key"
   - Choose **JSON** format and download

#### 2.3 Share Google Sheets
1. Open your Google Sheets
2. Click "Share" button
3. Add the service account email (from JSON file) as Editor
4. The email looks like: `your-service@project-name.iam.gserviceaccount.com`

#### 2.4 Encode Service Account Key
Convert your JSON key to base64:

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("path\to\your-key.json"))
```

**Linux/Mac:**
```bash
base64 -i your-key.json | tr -d '\n'
```

**Save this base64 string** - you'll need it for Vercel.

### Step 3: Get AI API Key (Optional but Recommended)

Choose one of these **FREE** options for AI features:

#### Option A: Groq (Recommended - Free & Fast)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Create new API key
4. Copy the key (starts with `gsk_`)

#### Option B: Google Gemini (Free Tier)
1. Go to [ai.google.dev](https://ai.google.dev)
2. Get API key for free
3. Copy the key (starts with `AIza`)

#### Option C: OpenAI (Paid)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Add billing method (minimum $5)
3. Create API key
4. Copy the key (starts with `sk-`)

### Step 4: Deploy to Vercel

#### 4.1 Fork This Repository
1. Click "Fork" button on this GitHub repository
2. Clone to your GitHub account

#### 4.2 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Import your forked repository
5. **Don't deploy yet** - we need to add environment variables first

#### 4.3 Add Environment Variables
In Vercel dashboard, go to your project settings > Environment Variables and add:

**Required Variables:**
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GOOGLE_SHEETS_ID=your_google_sheets_id
GOOGLE_SERVICE_ACCOUNT_KEY=your_base64_encoded_service_account_key
```

**AI Variables (choose one):**
```bash
# Option A: Groq (Free)
GROQ_API_KEY=gsk_your_groq_api_key

# Option B: Gemini (Free tier)
GEMINI_API_KEY=AIza_your_gemini_api_key

# Option C: OpenAI (Paid)
OPENAI_API_KEY=sk-your_openai_api_key
```

**Optional Variables:**
```bash
AI_INSIGHTS_ENABLED=true
NODE_ENV=production
```

#### 4.4 Deploy
1. Click "Deploy" in Vercel
2. Wait for deployment to complete
3. Copy your Vercel app URL (e.g., `https://your-app.vercel.app`)

### Step 5: Setup Telegram Webhook

1. Open your browser and go to:
   ```
   https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook?url={YOUR_VERCEL_URL}/api/telegram-webhook
   ```
   
   Replace:
   - `{YOUR_BOT_TOKEN}` with your actual bot token
   - `{YOUR_VERCEL_URL}` with your Vercel app URL

2. You should see: `{"ok":true,"result":true,"description":"Webhook was set"}`

### Step 6: Test Your Bot

1. Open Telegram and find your bot
2. Send `/start` to begin
3. Try logging an expense: `50000 makanan nasi padang`
4. Check your Google Sheets - the data should appear!

## 💬 How to Use

### Basic Commands
```
/start    - Start the bot and see guide
/help     - Complete help guide
/report   - Today's report
/week     - This week's report
/month    - This month's report
```

### Recording Transactions
```
# Expenses
50000 makanan nasi padang
25000 transport ojek to office
15000 coffee morning coffee

# Income (use + prefix)
+1000000 gaji monthly salary
+500000 bonus performance bonus
```

### 🤖 AI-Powered Features

#### Smart Insights on Every Transaction
When you log an expense, get instant AI-powered tips:
```
User: 50000 makanan nasi padang
Bot: ✅ Expense recorded! Rp 50,000 - Food
     💡 Tips: Try meal prep to save 30-50% on food expenses! 🍱
```

#### AI Financial Commands
```
/tips                           - General financial tips
/advice                         - Personal financial analysis
/budget [monthly_income]        - Budget recommendations
/goals [amount] [description]   - Set financial goals
/budgetcheck [amount] [days]    - Check budget feasibility
/dailyplan [daily_budget]       - Daily spending plan
```

#### Example AI Interactions
```
/budgetcheck 500000 14
→ Analyzes if 500k is enough for 14 days

/dailyplan 75000
→ Creates spending plan for 75k per day

/budget 4000000
→ Monthly budget advice for 4M income

/goals 10000000 emergency fund
→ Plan to save 10M for emergency fund
```

## 📊 Supported Categories

**Expenses:** makanan, transport, belanja, hiburan, kesehatan, pendidikan, utilitas, lainnya

**Income:** gaji, bonus, freelance, investasi, lainnya

The bot automatically categorizes your transactions using fuzzy matching!

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Your Telegram bot token from @BotFather |
| `GOOGLE_SHEETS_ID` | ✅ | Your Google Sheets ID from the URL |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | ✅ | Base64 encoded service account JSON |
| `GROQ_API_KEY` | ⭐ | Groq API key for AI features (free) |
| `GEMINI_API_KEY` | ⭐ | Google Gemini API key for AI features (free tier) |
| `OPENAI_API_KEY` | ⭐ | OpenAI API key for AI features (paid) |
| `AI_INSIGHTS_ENABLED` | ❌ | Enable/disable AI features (default: true) |

⭐ = Recommended (choose one for AI features)

### Google Sheets Format

The bot automatically creates columns:
- **Tanggal** - Transaction date/time
- **Kategori** - Category (auto-detected)
- **Deskripsi** - Transaction description
- **Jumlah** - Amount (negative for expenses, positive for income)
- **Sumber** - Source (telegram_username)
- **Tipe** - Type (pengeluaran/pemasukan)

## 🚀 Advanced Features

### AI Provider Fallback
The bot automatically falls back to rule-based advice if AI APIs are unavailable, ensuring reliability.

### Smart Category Detection
Uses fuzzy matching to automatically categorize transactions:
- `gofood` → `makanan`
- `ojek` → `transport`
- `netflix` → `hiburan`

### Multi-language Support
Supports both Indonesian and English transaction descriptions.

## 🔒 Security & Privacy

- **Your data stays yours** - Everything is stored in your own Google Sheets
- **Secure API communication** - All API calls use HTTPS
- **No data collection** - We don't store or access your financial data
- **Open source** - Full transparency, inspect the code yourself

## 💰 Cost Breakdown

- **Telegram Bot API**: 100% Free
- **Vercel Hosting**: Free tier (sufficient for personal use)
- **Google Sheets API**: Free tier (sufficient for personal use)
- **AI APIs**:
  - Groq: 100% Free ✅
  - Gemini: Free tier (60 requests/minute) ✅
  - OpenAI: ~$0.001 per request 💰

**Total monthly cost for most users: $0** 🎉

## 🛠️ Troubleshooting

### Bot not responding?
1. Check if webhook is set correctly
2. Verify Vercel deployment is successful
3. Check environment variables are set

### Transactions not saving?
1. Verify Google Sheets ID is correct
2. Check if service account has edit access
3. Ensure service account key is properly encoded

### AI features not working?
1. Verify AI API key is correct
2. Check if API key has proper permissions
3. Bot will fall back to rule-based advice if AI fails

### Common Issues

**"Error 400: Bad Request"**
- Bot token is incorrect
- Check TELEGRAM_BOT_TOKEN environment variable

**"Error 403: Forbidden"**
- Service account doesn't have access to sheets
- Re-share your Google Sheets with service account email

**"AI insights not showing"**
- Check if AI_INSIGHTS_ENABLED=true
- Verify AI API key is working
- Check Vercel function logs for errors

## 🔄 Updates

To update your bot with new features:
1. Pull latest changes from this repository
2. Redeploy on Vercel
3. New features will be automatically available

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Questions**: Check existing issues or create new one
- **Feature Requests**: Open an issue with "enhancement" label

## 📜 License

MIT License - feel free to use, modify, and distribute.

## 🙏 Contributing

We welcome contributions! Please feel free to submit pull requests.

---


Deploy your own CatatUang bot today and take control of your finances with AI-powered insights! 🚀

## 🧪 Local Testing Tool (FinancialAdvisor)

You can test the AI FinancialAdvisor logic locally without Telegram using the CLI tool:

```
python tools/test_financial_advisor.py transaction --amount 50000 --category makanan --desc "sarapan nasi uduk"
python tools/test_financial_advisor.py monthly
python tools/test_financial_advisor.py budget --income 4000000
python tools/test_financial_advisor.py budgetcheck --amount 500000 --days 14
python tools/test_financial_advisor.py dailyplan --daily 75000
```

It will auto-detect the available AI provider (Groq, Gemini, OpenAI) based on your `.env`. If none available, it falls back to rule-based tips.

### Mengganti model Groq

Jika ingin menggunakan model Groq lain (mis. gpt-120b-oss), atau cek model yang tersedia dengan 
```
curl https://api.groq.com/openai/v1/models \
     -H "Authorization: Bearer $GROQ_API_KEY"  ///isi dengan api key anda

```

tambahkan variabel lingkungan `GROQ_MODEL` di `.env`:

```
GROQ_MODEL=gpt-oss-120b
GROQ_API_KEY=gsk_...
```

Tool sudah membaca `GROQ_MODEL` dan akan memakai model tersebut saat memanggil Groq API.

