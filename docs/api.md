# API Documentation - CatatUang

## Base URL
```
Production: https://your-app.vercel.app
Local: http://localhost:3000
```

## Authentication
Tidak ada authentication required untuk endpoints publik. WhatsApp verification menggunakan `WHATSAPP_VERIFY_TOKEN`.

---

## Endpoints

### 1. Webhook Verification
**GET** `/api/webhook`

WhatsApp provider akan call endpoint ini untuk verifikasi webhook.

#### Query Parameters:
- `hub.mode` (string): "subscribe"
- `hub.verify_token` (string): Token untuk verifikasi
- `hub.challenge` (string): Challenge yang harus di-return

#### Response:
```
200 OK
Content-Type: text/plain

{challenge_value}
```

#### Error Response:
```json
{
  "status": "ok",
  "message": "CatatUang Webhook Ready! 🚀",
  "timestamp": "2025-01-22T10:30:00Z",
  "version": "1.0.0"
}
```

---

### 2. Process WhatsApp Message  
**POST** `/api/webhook`

Endpoint utama untuk memproses pesan WhatsApp dari berbagai provider.

#### Request Body:

**Format 1: Direct Message (Testing)**
```json
{
  "text": "#jajan 15000 bakso"
}
```

**Format 2: WhatsApp Cloud API**
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "field": "messages",
          "value": {
            "messages": [
              {
                "from": "6281234567890",
                "id": "wamid.xxx",
                "timestamp": "1642000000",
                "text": {
                  "body": "#jajan 15000 bakso"
                },
                "type": "text"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

**Format 3: Twilio**
```json
{
  "Body": "#jajan 15000 bakso",
  "From": "whatsapp:+6281234567890",
  "To": "whatsapp:+14155238886"
}
```

#### Response:

**Success:**
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

**Error:**
```json
{
  "status": "error", 
  "message": "Format harus diawali dengan '#'"
}
```

#### Input Format:
```
#kategori jumlah keterangan
```

**Contoh:**
- `#jajan 15000 bakso` 
- `#transport 25000 ojek ke kantor`
- `#makan 30000 nasi padang`

---

### 3. Generate Report
**GET** `/api/report`

Generate laporan pengeluaran dari Google Sheets.

#### Response:

**Success:**
```json
{
  "status": "success",
  "timestamp": "2025-01-22T10:30:00Z",
  "summary": {
    "total_expense": 125000,
    "total_transactions": 8,
    "categories": {
      "jajan": 45000,
      "transport": 50000,
      "makan": 30000
    },
    "category_counts": {
      "jajan": 3,
      "transport": 2, 
      "makan": 3
    },
    "monthly_breakdown": {
      "2025-01": 125000
    }
  },
  "recent_transactions": [
    {
      "Tanggal": "2025-01-22 10:30:00",
      "Kategori": "jajan",
      "Jumlah": 15000,
      "Keterangan": "bakso"
    }
  ],
  "message": "Report generated with 8 transactions"
}
```

**Error:**
```json
{
  "status": "error",
  "message": "Google Sheets not configured"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid JSON atau format |
| 500 | Internal Server Error |

## Error Messages

### Input Validation Errors:
- `"Format harus diawali dengan '#'"`
- `"Format: #kategori jumlah keterangan"`  
- `"Jumlah harus berupa angka"`

### System Errors:
- `"Google Sheets not configured"`
- `"Invalid service account key format"`
- `"Processing error: {details}"`

---

## Rate Limits

- **Vercel Free**: 100GB-hours/month
- **Google Sheets API**: 300 requests/minute/project
- **WhatsApp API**: Tergantung provider

---

## Headers

### Request Headers:
```
Content-Type: application/json
```

### Response Headers:
```
Content-Type: application/json
Access-Control-Allow-Origin: *
```

---

## Testing

### cURL Examples:

**Test webhook:**
```bash
curl -X POST https://your-app.vercel.app/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "#jajan 15000 bakso"}'
```

**Test report:**
```bash
curl https://your-app.vercel.app/api/report
```

**Test verification:**
```bash
curl "https://your-app.vercel.app/api/webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=test123"
```

### JavaScript Examples:

**Send expense:**
```javascript
const response = await fetch('https://your-app.vercel.app/api/webhook', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: '#jajan 15000 bakso'
  })
});

const result = await response.json();
console.log(result);
```

**Get report:**
```javascript
const response = await fetch('https://your-app.vercel.app/api/report');
const report = await response.json();
console.log(report.summary);
```

---

## Webhook Security

### WhatsApp Cloud API Verification:
```javascript
// Verify signature (optional)
const crypto = require('crypto');

function verifySignature(payload, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  
  return hash === signature;
}
```

### IP Whitelist (Optional):
```javascript
// Twilio IPs untuk whitelist
const twilio_ips = [
  '54.172.60.0',
  '54.244.51.0',
  // ... dll
];
```

---

**Last Updated:** 2025-01-22
