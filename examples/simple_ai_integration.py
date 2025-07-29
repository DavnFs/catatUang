"""
Simple AI Integration Example for CatatUang Bot
This is a minimal implementation to get started with AI features
"""
import os
import requests
import json

def get_simple_financial_advice(amount: float, category: str, user_spending_pattern: dict = None) -> str:
    """
    Simple function to get AI financial advice
    This can be called from your existing telegram bot
    """
    
    # Check if we have any AI API key
    groq_key = os.getenv('GROQ_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not any([groq_key, gemini_key, openai_key]):
        # Fallback to simple rule-based advice
        return get_rule_based_advice(amount, category)
    
    # Use the first available API
    if groq_key:
        return call_groq_api(amount, category, groq_key, user_spending_pattern)
    elif gemini_key:
        return call_gemini_api(amount, category, gemini_key, user_spending_pattern) 
    elif openai_key:
        return call_openai_api(amount, category, openai_key, user_spending_pattern)
    
    return get_rule_based_advice(amount, category)

def call_groq_api(amount: float, category: str, api_key: str, user_data: dict = None) -> str:
    """Call Groq API for financial advice"""
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple context
        context = ""
        if user_data:
            total_expense = user_data.get('total_expense', 0)
            if total_expense > 0:
                context = f"Total pengeluaran bulan ini: Rp {total_expense:,.0f}"
        
        prompt = f"""
        User baru saja mencatat pengeluaran:
        - Jumlah: Rp {amount:,.0f}
        - Kategori: {category}
        {context}
        
        Berikan 1 tips singkat untuk kategori {category} dalam 1 kalimat.
        Gunakan bahasa Indonesia yang friendly dan emoji yang sesuai.
        Mulai dengan "💡 Tips: "
        """
        
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": "Kamu adalah financial advisor ramah yang memberikan tips praktis untuk orang Indonesia."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        advice = result['choices'][0]['message']['content'].strip()
        
        # Ensure it starts with the emoji
        if not advice.startswith('💡'):
            advice = f"💡 Tips: {advice}"
            
        return advice
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return get_rule_based_advice(amount, category)

def call_gemini_api(amount: float, category: str, api_key: str, user_data: dict = None) -> str:
    """Call Google Gemini API for financial advice"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        context = ""
        if user_data:
            total_expense = user_data.get('total_expense', 0)
            if total_expense > 0:
                context = f"Total pengeluaran bulan ini: Rp {total_expense:,.0f}"
        
        prompt = f"""
        User baru mencatat pengeluaran Rp {amount:,.0f} untuk kategori {category}.
        {context}
        
        Berikan 1 tips singkat hemat untuk kategori {category} dalam bahasa Indonesia.
        Gunakan emoji dan maksimal 20 kata.
        Format: "💡 Tips: [saran singkat]"
        """
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 100,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        advice = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if not advice.startswith('💡'):
            advice = f"💡 Tips: {advice}"
            
        return advice
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return get_rule_based_advice(amount, category)

def call_openai_api(amount: float, category: str, api_key: str, user_data: dict = None) -> str:
    """Call OpenAI API for financial advice"""
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        context = ""
        if user_data:
            total_expense = user_data.get('total_expense', 0)
            if total_expense > 0:
                context = f"Total pengeluaran bulan ini: Rp {total_expense:,.0f}"
        
        prompt = f"""
        User mencatat pengeluaran Rp {amount:,.0f} untuk {category}.
        {context}
        
        Berikan tips singkat untuk kategori {category} dalam bahasa Indonesia.
        Maksimal 15 kata, gunakan emoji.
        Format: "💡 Tips: [saran]"
        """
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Kamu financial advisor Indonesia yang memberikan tips praktis singkat."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        advice = result['choices'][0]['message']['content'].strip()
        
        if not advice.startswith('💡'):
            advice = f"💡 Tips: {advice}"
            
        return advice
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return get_rule_based_advice(amount, category)

def get_rule_based_advice(amount: float, category: str) -> str:
    """Fallback rule-based advice when AI APIs are not available"""
    
    category_tips = {
        'makanan': [
            "💡 Tips: Coba meal prep untuk hemat 30-50% pengeluaran makanan! 🍱",
            "💡 Tips: Masak di rumah lebih sehat dan hemat daripada beli terus! 👨‍🍳",
            "💡 Tips: Beli bahan makanan di pasar tradisional lebih murah! 🛒"
        ],
        'transport': [
            "💡 Tips: Pertimbangkan naik kendaraan umum untuk rute rutin! 🚌",
            "💡 Tips: Jalan kaki atau sepeda untuk jarak dekat, sehat dan hemat! 🚶‍♂️",
            "💡 Tips: Gunakan app transport untuk compare harga dan promo! 📱"
        ],
        'hiburan': [
            "💡 Tips: Set budget hiburan maksimal 10% dari income bulanan! 🎬",
            "💡 Tips: Cari aktivitas gratis seperti jogging di taman! 🏃‍♂️",
            "💡 Tips: Manfaatkan promo dan diskon untuk entertainment! 🎟️"
        ],
        'belanja': [
            "💡 Tips: Buat list belanja dan stick to it, jangan impulse buying! 📝",
            "💡 Tips: Compare harga online vs offline sebelum beli! 💻",
            "💡 Tips: Tunggu sale untuk barang non-urgent! 🏷️"
        ],
        'kesehatan': [
            "💡 Tips: Investasi kesehatan sekarang lebih murah dari sakit nanti! 💪",
            "💡 Tips: Rutin olahraga dan makan sehat untuk cegah penyakit! 🥗",
            "💡 Tips: Gunakan BPJS untuk healthcare yang terjangkau! 🏥"
        ]
    }
    
    import random
    
    # Get category-specific tip or default
    tips = category_tips.get(category.lower(), [
        "💡 Tips: Catat semua pengeluaran untuk kontrol finansial yang lebih baik! 📊",
        "💡 Tips: Review pengeluaran bulanan dan cari area untuk berhemat! 🔍",
        "💡 Tips: Sisihkan 20% income untuk tabungan dan investasi! 💰"
    ])
    
    return random.choice(tips)

# Example usage in your existing telegram bot:
def enhanced_transaction_response(amount: float, category: str, description: str, is_income: bool = False) -> str:
    """
    Enhanced response that includes AI advice
    You can integrate this into your existing _process_expense_message function
    """
    
    # Your existing response format
    tipe_emoji = "💰" if is_income else "💸"
    tipe_text = "Pemasukan" if is_income else "Pengeluaran"
    formatted_amount = f"Rp {amount:,}".replace(',', '.')
    
    from datetime import datetime, timezone, timedelta
    JAKARTA_TZ = timezone(timedelta(hours=7))
    jakarta_time = datetime.now(JAKARTA_TZ)
    
    standard_response = f"""{tipe_emoji} **{tipe_text} Tercatat!**

💵 Jumlah: {formatted_amount}
📂 Kategori: {category.title()}
📝 Deskripsi: {description}
📅 Waktu: {jakarta_time.strftime('%d/%m/%Y %H:%M')} WIB

✅ Data tersimpan di Google Sheets!"""

    # Add AI insight for expenses only
    if not is_income:
        try:
            # You can pass user spending data here if available
            user_data = {'total_expense': 1500000}  # Example
            ai_advice = get_simple_financial_advice(amount, category, user_data)
            return f"{standard_response}\n\n{ai_advice}"
        except:
            pass
    
    return standard_response

# Quick test function
if __name__ == "__main__":
    # Test the AI advice function
    print("Testing AI advice:")
    advice = get_simple_financial_advice(50000, "makanan")
    print(advice)
    
    print("\nTesting enhanced response:")
    response = enhanced_transaction_response(75000, "transport", "ojek ke kantor")
    print(response)
