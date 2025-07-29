"""
Financial Advisor AI Module for CatatUang Bot
Provides intelligent financial recommendations and analysis
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

class FinancialAdvisor:
    def __init__(self):
        # Support multiple LLM providers
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY') 
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        
        # Default to free option if available
        self.selected_provider = self._select_provider()
        
    def _select_provider(self):
        """Select the best available LLM provider"""
        if self.groq_api_key:
            return 'groq'  # Fast and free
        elif self.gemini_api_key:
            return 'gemini'  # Good and has free tier
        elif self.openai_api_key:
            return 'openai'  # Premium option
        else:
            return 'local'  # Fallback to rule-based
    
    def get_transaction_advice(self, amount: float, category: str, description: str, user_data: Dict) -> str:
        """Get immediate advice when user inputs a transaction"""
        
        # Prepare context from user's financial data
        context = self._prepare_user_context(user_data)
        
        prompt = f"""
        Kamu adalah advisor keuangan yang ramah dan membantu. User baru saja input transaksi:
        
        Transaksi: {amount:,.0f} IDR untuk {category} - {description}
        
        Data keuangan user bulan ini:
        {context}
        
        Berikan 1 saran singkat (max 100 kata) yang:
        1. Positif dan memotivasi
        2. Actionable/bisa ditindaklanjuti  
        3. Relevan dengan kategori transaksi
        4. Gunakan emoji yang sesuai
        
        Format: 💡 Tips: [saran singkat]
        """
        
        return self._get_ai_response(prompt)
    
    def get_monthly_analysis(self, user_data: Dict) -> str:
        """Generate comprehensive monthly financial analysis"""
        
        context = self._prepare_detailed_context(user_data)
        
        prompt = f"""
        Analisis data keuangan user berikut dan berikan rekomendasi:
        
        {context}
        
        Berikan analisis dalam format:
        📊 ANALISIS KEUANGAN BULAN INI
        
        💰 Ringkasan:
        [ringkasan pendapatan vs pengeluaran]
        
        📈 Tren Pengeluaran:
        [kategori terbesar dan polanya]
        
        💡 Rekomendasi:
        [3 saran konkret untuk bulan depan]
        
        🎯 Target Hemat:
        [target realistis yang bisa dicapai]
        """
        
        return self._get_ai_response(prompt)
    
    def get_budget_recommendation(self, monthly_income: float, user_data: Dict) -> str:
        """Generate personalized budget recommendations"""
        
        prompt = f"""
        User memiliki penghasilan bulanan: {monthly_income:,.0f} IDR
        
        Berikan rekomendasi budget menggunakan prinsip 50/30/20 yang disesuaikan untuk Indonesia:
        
        Format response:
        💰 REKOMENDASI BUDGET BULANAN
        
        🏠 Kebutuhan Pokok (50%): {monthly_income*0.5:,.0f} IDR
        - Sewa/KPR, listrik, air, internet
        - Makanan pokok, transport kerja
        - Asuransi kesehatan
        
        🎯 Keinginan (30%): {monthly_income*0.3:,.0f} IDR  
        - Hiburan, nongkrong, hobi
        - Shopping non-esensial
        - Traveling
        
        💎 Tabungan & Investasi (20%): {monthly_income*0.2:,.0f} IDR
        - Emergency fund (6-12 bulan pengeluaran)
        - Investasi jangka panjang
        - Dana pensiun
        
        💡 Tips khusus berdasarkan penghasilan Anda:
        [saran spesifik untuk range income ini]
        """
        
        return self._get_ai_response(prompt)
    
    def _prepare_user_context(self, user_data: Dict) -> str:
        """Prepare concise context for quick transaction advice"""
        
        total_income = user_data.get('total_income', 0)
        total_expense = user_data.get('total_expense', 0)
        categories = user_data.get('categories', {})
        
        context = f"""
        Pemasukan bulan ini: {total_income:,.0f} IDR
        Pengeluaran bulan ini: {total_expense:,.0f} IDR
        Sisa budget: {total_income - total_expense:,.0f} IDR
        
        Top 3 kategori pengeluaran:
        """
        
        # Add top spending categories
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        for cat, amount in sorted_categories:
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            context += f"- {cat}: {amount:,.0f} IDR ({percentage:.1f}%)\n"
        
        return context
    
    def _prepare_detailed_context(self, user_data: Dict) -> str:
        """Prepare detailed context for comprehensive analysis"""
        
        # This would include more detailed spending patterns, trends, etc.
        # Implementation depends on your data structure
        return self._prepare_user_context(user_data)
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from selected AI provider"""
        
        try:
            if self.selected_provider == 'groq':
                return self._call_groq_api(prompt)
            elif self.selected_provider == 'gemini':
                return self._call_gemini_api(prompt)
            elif self.selected_provider == 'openai':
                return self._call_openai_api(prompt)
            else:
                return self._get_rule_based_advice(prompt)
                
        except Exception as e:
            print(f"AI API Error: {e}")
            return self._get_rule_based_advice(prompt)
    
    def _call_groq_api(self, prompt: str) -> str:
        """Call Groq API (Fast and Free)"""
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3-70b-8192",  # or "mixtral-8x7b-32768"
            "messages": [
                {
                    "role": "system", 
                    "content": "Kamu adalah financial advisor yang ramah, ahli keuangan Indonesia, dan memberikan saran praktis dengan bahasa yang mudah dipahami."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini API"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Kamu adalah financial advisor Indonesia yang ramah dan praktis.\n\n{prompt}"
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 500,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    
    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API"""
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Kamu adalah financial advisor Indonesia yang ramah, praktis, dan memberikan saran yang actionable."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    def _get_rule_based_advice(self, prompt: str) -> str:
        """Fallback rule-based advice when no AI API available"""
        
        advice_templates = [
            "💡 Tips: Catat terus pengeluaranmu untuk kontrol yang lebih baik!",
            "💡 Tips: Sisihkan 20% penghasilan untuk tabungan dan investasi.",
            "💡 Tips: Review pengeluaran mingguan untuk mencari area penghematan.",
            "💡 Tips: Buat emergency fund minimal 6 bulan pengeluaran.",
            "💡 Tips: Investasi rutin lebih baik daripada lump sum besar.",
        ]
        
        # Simple logic based on keywords in prompt
        if "makanan" in prompt.lower():
            return "💡 Tips: Coba meal prep untuk hemat pengeluaran makanan! Masak sendiri bisa hemat 30-50%."
        elif "transport" in prompt.lower():
            return "💡 Tips: Pertimbangkan transportasi umum atau carpooling untuk menghemat biaya transport."
        elif "entertainment" in prompt.lower() or "hiburan" in prompt.lower():
            return "💡 Tips: Set budget hiburan maksimal 10% dari income bulanan ya!"
        
        # Default advice
        import random
        return random.choice(advice_templates)

# Example usage functions
def get_transaction_insight(amount: float, category: str, description: str, user_financial_data: Dict) -> str:
    """Get AI-powered insight for a transaction"""
    advisor = FinancialAdvisor()
    return advisor.get_transaction_advice(amount, category, description, user_financial_data)

def get_monthly_financial_analysis(user_financial_data: Dict) -> str:
    """Get comprehensive monthly analysis"""
    advisor = FinancialAdvisor()
    return advisor.get_monthly_analysis(user_financial_data)

def get_personalized_budget(monthly_income: float, user_financial_data: Dict) -> str:
    """Get personalized budget recommendations"""
    advisor = FinancialAdvisor()
    return advisor.get_budget_recommendation(monthly_income, user_financial_data)
