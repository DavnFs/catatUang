# Setup Guide - CatatUang

## 📋 Prerequisites

- Google account untuk Google Sheets
- WhatsApp Business account atau provider API
- Vercel account (gratis)

## 🔧 Detailed Setup

### 1. Google Cloud Setup

#### A. Create Project & Enable APIs
```bash
1. Buka https://console.cloud.google.com/
2. Create New Project → "CatatUang" 
3. Navigate ke "APIs & Services" → "Library"
4. Enable: "Google Sheets API" dan "Google Drive API"
```

#### B. Create Service Account
```bash
1. IAM & Admin → Service Accounts → Create Service Account
2. Name: "catatuang-service"
3. Role: "Editor" (atau buat custom role)
4. Create Key → JSON → Download file
```

#### C. Encode Credentials
```bash
# Linux/Mac
base64 -i service-account.json | tr -d '\n'

# Windows PowerShell  
[Convert]::ToBase64String([IO.File]::ReadAllBytes("service-account.json"))

# Save output untuk environment variable
```

### 2. Google Sheets Setup

```bash
1. Buat Google Sheets baru
2. Copy ID dari URL: 
   https://docs.google.com/spreadsheets/d/[SHEETS_ID]/edit
3. Share sheets dengan service account email (dari JSON file)
4. Give "Editor" permission
```

### 3. Vercel Deployment

#### A. GitHub Method (Recommended)
```bash
1. Fork/clone repository ke GitHub
2. Connect ke Vercel account
3. Import project dari GitHub
4. Auto-deploy setup ✅
```

#### B. CLI Method
```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### 4. Environment Variables

Set di Vercel Dashboard → Project → Settings → Environment Variables:

```bash
# Required
GOOGLE_SHEETS_ID=1abc123def456ghi789jkl012mno345pqr678
GOOGLE_SERVICE_ACCOUNT_KEY=ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC...

# Optional (untuk WhatsApp verification)  
WHATSAPP_VERIFY_TOKEN=my_secret_token_123
```

### 5. WhatsApp Integration

#### Option A: Twilio (Easiest)
```bash
1. Daftar di https://www.twilio.com/
2. Console → Develop → Messaging → Try WhatsApp
3. Sandbox Settings:
   - Webhook URL: https://your-app.vercel.app/api/webhook
   - HTTP Method: POST
4. Test dengan kirim pesan ke Twilio sandbox number
```

#### Option B: WhatsApp Cloud API (Production)
```bash
1. Setup WhatsApp Business Account
2. Meta for Developers → Create App → WhatsApp
3. Get Permanent Access Token
4. Setup Webhook:
   - URL: https://your-app.vercel.app/api/webhook
   - Verify Token: (sama dengan WHATSAPP_VERIFY_TOKEN)
   - Subscribe to: messages
```

#### Option C: Provider Indonesia
**Fonnte:**
```bash
1. Daftar di https://fonnte.com/
2. Beli paket WhatsApp API
3. Webhook Settings:
   - URL: https://your-app.vercel.app/api/webhook
   - Method: POST
```

## 🧪 Testing

### 1. Test Endpoints
```bash
# Health check
curl https://your-app.vercel.app/api/webhook

# Test message processing
curl -X POST https://your-app.vercel.app/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "#jajan 15000 bakso"}'

# Test report
curl https://your-app.vercel.app/api/report
```

### 2. Test WhatsApp Integration
```bash
# Kirim pesan ke WhatsApp bot:
#jajan 15000 bakso
#transport 25000 ojek  
#makan 30000 nasi padang

# Check Google Sheets untuk data baru
# Check Vercel logs untuk debug
```

## 🚨 Troubleshooting

### Common Issues

**1. "Google Sheets not configured"**
```bash
Solution:
- Check GOOGLE_SHEETS_ID di environment variables
- Verify service account key format (base64)
- Ensure sheets shared dengan service account
```

**2. "Invalid service account key format"**  
```bash
Solution:
- Re-encode JSON ke base64
- Remove newlines: | tr -d '\n'
- Verify JSON structure valid
```

**3. "Permission denied"**
```bash
Solution:
- Share Google Sheets dengan service account email
- Give "Editor" permission, bukan "Viewer"
- Check service account roles di Google Cloud
```

**4. WhatsApp webhook tidak respond**
```bash
Solution:
- Verify webhook URL di provider settings
- Check WHATSAPP_VERIFY_TOKEN match
- Test manual dengan curl
- Check Vercel function logs
```

### Debug Tips

```bash
# Check Vercel logs
vercel logs --follow

# Test locally
vercel dev

# Check environment variables
vercel env ls
```

## 📊 Production Monitoring

### 1. Vercel Analytics
- Enable di Project Settings → Analytics
- Monitor function invocations & errors

### 2. Google Sheets Monitoring  
- Check data integrity
- Monitor API quota usage

### 3. WhatsApp Provider Monitoring
- Check webhook delivery success rate
- Monitor API limits

## 🔒 Security Best Practices

```bash
# Environment Variables
- Never commit .env files
- Use Vercel's secret management
- Rotate API keys periodically

# Access Control  
- Limit service account permissions
- Use specific Google Sheets sharing
- Implement rate limiting if needed

# Monitoring
- Enable Vercel function logs
- Monitor unusual activity
- Set up alerts for errors
```

## 📈 Scaling Considerations

### High Volume (>1000 requests/day)
```bash
- Consider upgrading Vercel plan
- Implement caching for reports
- Add rate limiting
- Monitor Google Sheets API limits
```

### Multiple Users
```bash
- Add user identification in webhook
- Separate sheets per user/team
- Implement access control
```

---

**Need help?** Open an issue di GitHub repository! 🚀
