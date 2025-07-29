# 🤖 Panduan Implementasi AI Financial Advisor

## 📋 Overview

Panduan ini akan membantu Anda menambahkan fitur AI Financial Advisor ke CatatUang bot yang sudah ada. Fitur ini akan memberikan:

- ✨ **Insight real-time** saat input transaksi
- 📊 **Analisis keuangan bulanan** yang cerdas  
- 💰 **Rekomendasi budget** personal
- 🎯 **Goal setting** dan tracking
- 💡 **Tips hemat** berdasarkan pola pengeluaran

## 🚀 Quick Implementation Steps

### 1. **Pilih Provider AI (Gratis vs Berbayar)**

| Provider | Cost | Quality | Speed | Free Tier |
|----------|------|---------|-------|-----------|
| **Groq** | FREE | Good | Very Fast | ✅ Unlimited |
| **Gemini** | FREE | Good | Fast | ✅ 60 req/min |
| **OpenAI** | PAID | Best | Medium | ❌ $5 minimum |

**Rekomendasi:** Mulai dengan **Groq** (gratis unlimited) atau **Gemini** (gratis).

### 2. **Get API Key**

#### Option A: Groq (Recommended - Free & Fast)
1. Daftar di: https://console.groq.com
2. Buat API key baru
3. Copy API key yang dihasilkan

#### Option B: Google Gemini (Free Tier)  
1. Buka: https://ai.google.dev/
2. Get API key
3. Copy API key

#### Option C: OpenAI (Paid Premium)
1. Daftar di: https://platform.openai.com
2. Add billing method
3. Create API key

### 3. **Setup Environment Variables**

Tambahkan ke Vercel environment variables atau `.env` file:

```bash
# Pilih salah satu atau lebih (untuk fallback)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional configurations
AI_INSIGHTS_ENABLED=true
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.7
```

### 4. **Update Requirements**

Tambahkan dependency ke `requirements.txt`:

```txt
# Existing dependencies
gspread
google-auth
requests

# New AI dependencies  
openai>=1.0.0  # For OpenAI API
google-generativeai>=0.3.0  # For Gemini API
# No extra dependency needed for Groq (uses OpenAI-compatible API)
```

### 5. **Integrate AI ke Telegram Bot**

#### A. Update telegram-webhook.py

Tambahkan import di bagian atas file:

```python
# Add these imports
from .telegram_ai_integration import (
    TelegramFinancialBot, 
    handle_advice_command,
    handle_budget_command, 
    handle_tips_command,
    handle_goals_command
)
```

#### B. Update _process_expense_message method

Replace existing method dengan versi AI-enhanced:

```python
def _process_expense_message(self, text, user_id):
    """Process expense/income message with AI insights"""
    try:
        # ... existing parsing logic ...
        
        # Use AI-enhanced response
        ai_bot = TelegramFinancialBot()
        return ai_bot.get_enhanced_transaction_response(
            amount=amount,
            category=kategori, 
            description=deskripsi,
            user_id=user_id,
            is_income=is_income
        )
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

#### C. Add new AI commands

Update `_process_command` method:

```python
def _process_command(self, text, chat_id, username, first_name, user_id=None):
    """Process commands with new AI features"""
    try:
        command = text.lower().split()[0]
        args = text.split()[1:] if len(text.split()) > 1 else []
        
        # ... existing commands ...
        
        # NEW AI COMMANDS
        elif command == '/advice':
            return handle_advice_command(f"{username}_{user_id}")
            
        elif command == '/budget':
            monthly_income = float(args[0]) if args else None
            return handle_budget_command(f"{username}_{user_id}", monthly_income)
            
        elif command == '/tips':
            category = args[0] if args else None
            return handle_tips_command(category)
            
        elif command == '/goals':
            if len(args) >= 2:
                goal_amount = float(args[0])
                goal_desc = ' '.join(args[1:])
                return handle_goals_command(f"{username}_{user_id}", goal_amount, goal_desc)
            else:
                return handle_goals_command(f"{username}_{user_id}")
        
        # ... rest of existing commands ...
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### 6. **Update Help Command**

Tambahkan commands baru ke `/help`:

```python
elif command == '/help':
    return f"""🤖 **CatatUang Bot - Panduan Lengkap**

📝 **Format Transaksi:**
• `50000 makanan nasi padang` - Pengeluaran
• `+1000000 gaji salary` - Pemasukan  

📊 **Laporan:**
/report - Laporan hari ini
/week - Laporan minggu ini  
/month - Laporan bulan ini
/balance - Saldo saat ini

🤖 **AI Financial Advisor:**
/advice - Analisis keuangan personal
/budget [income] - Rekomendasi budget bulanan
/tips [kategori] - Tips hemat berdasarkan kategori
/goals [jumlah] [deskripsi] - Set target financial

💡 **Contoh AI Commands:**
• `/advice` - Analisis pengeluaran bulan ini
• `/budget 5000000` - Budget untuk income 5 juta
• `/tips makanan` - Tips hemat makanan
• `/goals 10000000 emergency fund` - Set goal

📱 **Lainnya:**
/categories - Daftar kategori
/help - Panduan ini"""
```

## 🔧 Advanced Configuration

### Custom Data Integration

Untuk mendapatkan insight yang lebih akurat, implement `_get_user_financial_data()` method:

```python
def _get_user_financial_data(self, user_id: str) -> dict:
    """Get user's actual financial data from Google Sheets"""
    try:
        # Query Google Sheets for user's current month data
        sheet = self._get_sheets_client()
        
        # Calculate monthly totals, categories, etc.
        # This depends on your sheets structure
        
        return {
            'total_income': calculated_income,
            'total_expense': calculated_expense,
            'categories': category_breakdown,
            'daily_average': daily_avg,
            'transactions_count': count
        }
    except Exception as e:
        # Return fallback data
        return {
            'total_income': 3000000,
            'total_expense': 1500000,
            'categories': {},
            'daily_average': 50000,
            'transactions_count': 30
        }
```

### Error Handling

AI akan secara otomatis fallback ke rule-based responses jika API gagal.

### Cost Management

- **Groq**: Gratis unlimited ✅
- **Gemini**: 60 requests/menit gratis ✅  
- **OpenAI**: ~$0.001 per request 💰

## 🧪 Testing

Test commands baru:

```
/advice
/budget 4000000  
/tips makanan
/goals 5000000 motor baru
50000 makanan nasi padang
+1000000 gaji bulanan
```

## 🚀 Deployment

### Vercel Deployment

1. Update environment variables di Vercel dashboard
2. Deploy updated code:

```bash
vercel --prod
```

### Local Testing

```bash
# Install new dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_groq_key"

# Test locally
vercel dev
```

## 📈 Expected Results

Setelah implementasi:

**Before:**
```
User: 50000 makanan nasi padang
Bot: ✅ Pengeluaran tercatat! Rp 50.000 - makanan
```

**After:**  
```
User: 50000 makanan nasi padang  
Bot: ✅ Pengeluaran tercatat! Rp 50.000 - makanan

💡 Tips: Pengeluaran makanan Anda bulan ini sudah 45% dari income. 
Coba meal prep 2-3x seminggu untuk hemat Rp 300rb/bulan! 🍱
```

**New Commands:**
```
User: /advice
Bot: 📊 ANALISIS KEUANGAN BULAN INI
💰 Ringkasan: Income Rp 4.5jt, Expense Rp 2.8jt (62%)
📈 Tren: Makanan 35%, Transport 20%, Hiburan 15%  
💡 Rekomendasi: [AI-generated personal advice]
```

## 🎯 Next Steps

1. ✅ Setup API key (5 menit)
2. ✅ Update environment variables (2 menit)  
3. ✅ Integrate code (15 menit)
4. ✅ Test new features (5 menit)
5. ✅ Deploy to production (2 menit)

Total implementation time: **~30 menit** 🚀

## 💡 Pro Tips

- Mulai dengan Groq API (gratis, cepat)
- Test di local environment dulu
- Monitor API usage untuk cost control
- Bisa kombinasi multiple AI providers untuk redundancy
- AI insights akan makin akurat seiring bertambahnya data user

Happy coding! 🎉
