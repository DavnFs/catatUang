"""
Financial Advisor AI Module for CatatUang Bot
Provides intelligent financial recommendations and analysis
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

class FinancialAdvisor:
    def __init__(self):
        # Support multiple LLM providers
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY') #in this project i use gemeni, because easy and reliable
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
        """Generate personalized budget recommendations with historical context"""
        
        # Extract historical data for better recommendations
        carry_over_balance = user_data.get('carry_over_balance', 0)
        avg_monthly_expense = user_data.get('avg_monthly_expense', 0)
        historical_pattern = user_data.get('historical_spending_pattern', [])
        months_with_data = user_data.get('months_with_data', 0)
        current_expense = user_data.get('total_expense', 0)
        
        # Build historical context for AI
        historical_context = ""
        if months_with_data > 0 and avg_monthly_expense > 0:
            historical_context = f"""
        
        DATA HISTORICAL USER:
        - Rata-rata pengeluaran bulanan: {avg_monthly_expense:,.0f} IDR
        - Saldo carry-over: {carry_over_balance:,.0f} IDR
        - Data tersedia untuk: {months_with_data} bulan
        - Pengeluaran bulan ini: {current_expense:,.0f} IDR
        """
        
        if len(historical_pattern) >= 2:
            trend = "menurun" if historical_pattern[0] > historical_pattern[-1] else "meningkat"
            historical_context += f"- Trend pengeluaran: {trend} dalam 3 bulan terakhir\n"
        
        prompt = f"""
        User memiliki penghasilan bulanan: {monthly_income:,.0f} IDR
        {historical_context}
        
        Berikan rekomendasi budget yang REALISTIS berdasarkan pola pengeluaran historis user, menggunakan prinsip 50/30/20 yang disesuaikan:
        
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
        
        💡 ANALISIS BERDASARKAN HISTORICAL DATA:
        [Bandingkan dengan pola pengeluaran historis user. Apakah budget ini realistis? Ada saldo carry-over yang perlu dipertimbangkan?]
        
        🎯 REKOMENDASI KHUSUS:
        [Saran spesifik berdasarkan trend pengeluaran dan saldo carry-over user]
        """
        
        return self._get_ai_response(prompt)
    
    def check_budget_feasibility(self, budget_amount: float, duration_days: int, user_data: Dict = None) -> str:
        """Check if a budget is feasible for a specific duration and provide daily spending advice"""
        
        daily_budget = budget_amount / duration_days
        
        # Get user's typical spending pattern if available
        context = ""
        if user_data:
            avg_daily = user_data.get('daily_average', 0)
            if avg_daily > 0:
                context = f"Rata-rata pengeluaran harian Anda biasanya: {avg_daily:,.0f} IDR"
        
        prompt = f"""
        User bertanya apakah budget {budget_amount:,.0f} IDR cukup untuk hidup selama {duration_days} hari.
        
        Budget per hari: {daily_budget:,.0f} IDR
        {context}
        
        Analisis dan berikan rekomendasi dalam format:
        
        💰 ANALISIS BUDGET {duration_days} HARI
        
        💵 Total Budget: {budget_amount:,.0f} IDR
        📅 Durasi: {duration_days} hari
        🎯 Budget Harian: {daily_budget:,.0f} IDR
        
        ✅ KELAYAKAN:
        [Apakah budget ini realistis? Cukup/kurang/berlebih dan kenapa]
        
        📊 REKOMENDASI ALOKASI HARIAN:
        🍽️ Makanan: [jumlah] IDR ({daily_budget*0.4:.0f} IDR - 40%)
        🚗 Transport: [jumlah] IDR ({daily_budget*0.2:.0f} IDR - 20%)
        🎯 Lain-lain: [jumlah] IDR ({daily_budget*0.3:.0f} IDR - 30%)
        💎 Cadangan: [jumlah] IDR ({daily_budget*0.1:.0f} IDR - 10%)
        
        💡 TIPS HEMAT:
        [3 tips praktis untuk mengoptimalkan budget ini]
        
        ⚠️ PERINGATAN:
        [Hal-hal yang perlu diwaspadai dengan budget ini]
        """
        
        return self._get_ai_response(prompt)
    
    def get_daily_spending_plan(self, daily_budget: float, priorities: List[str] = None) -> str:
        """Generate daily spending plan based on budget"""
        
        if not priorities:
            priorities = ["makanan", "transport", "kebutuhan_pokok"]
        
        prompt = f"""
        User memiliki budget harian {daily_budget:,.0f} IDR dan ingin rencana pengeluaran.
        
        Prioritas pengeluaran: {', '.join(priorities)}
        
        Berikan rencana dalam format:
        
        📅 RENCANA PENGELUARAN HARIAN
        💰 Budget: {daily_budget:,.0f} IDR
        
        🎯 ALOKASI SMART:
        🍽️ Makanan (sarapan + makan siang + makan malam): {daily_budget*0.45:.0f} IDR
        🚗 Transport (PP kerja/aktivitas): {daily_budget*0.25:.0f} IDR
        ☕ Jajan/Minuman: {daily_budget*0.15:.0f} IDR
        🎯 Lain-lain (darurat/tak terduga): {daily_budget*0.10:.0f} IDR
        💎 Sisa untuk tabung: {daily_budget*0.05:.0f} IDR
        
        💡 STRATEGI HEMAT:
        [Tips konkret untuk stay within budget]
        
        📱 TRACKING HARIAN:
        [Cara simple track pengeluaran per hari]
        """
        
        return self._get_ai_response(prompt)
    
    def _prepare_user_context(self, user_data: Dict) -> str:
        """Prepare user context with historical data for better AI analysis"""
        
        total_income = user_data.get('total_income', 0)
        total_expense = user_data.get('total_expense', 0)
        categories = user_data.get('categories', {})
        
        # New historical data fields
        carry_over_balance = user_data.get('carry_over_balance', 0)
        effective_balance = user_data.get('effective_balance', 0)
        avg_monthly_expense = user_data.get('avg_monthly_expense', 0)
        months_with_data = user_data.get('months_with_data', 0)
        historical_pattern = user_data.get('historical_spending_pattern', [])
        
        context = f"""
        BULAN INI:
        - Pemasukan: {total_income:,.0f} IDR
        - Pengeluaran: {total_expense:,.0f} IDR
        - Saldo bulan ini: {total_income - total_expense:,.0f} IDR
        
        HISTORICAL DATA:
        - Saldo carry-over dari bulan lalu: {carry_over_balance:,.0f} IDR
        - Total saldo efektif: {effective_balance:,.0f} IDR
        - Rata-rata pengeluaran bulanan: {avg_monthly_expense:,.0f} IDR
        - Data tersedia untuk: {months_with_data} bulan
        """
        
        # Add spending trend analysis if historical data available
        if len(historical_pattern) >= 2:
            trend_direction = "naik" if historical_pattern[0] > historical_pattern[-1] else "turun"
            context += f"- Trend pengeluaran: {trend_direction} dalam 3 bulan terakhir\n"
        
        context += "\nTop 3 kategori pengeluaran bulan ini:\n"        # Add top spending categories
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        for cat, amount in sorted_categories:
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            context += f"- {cat}: {amount:,.0f} IDR ({percentage:.1f}%)\n"
        
        return context
    
    def _prepare_detailed_context(self, user_data: Dict) -> str:
        """Prepare comprehensive detailed context for in-depth analysis"""
        
        total_income = user_data.get('total_income', 0)
        total_expense = user_data.get('total_expense', 0)
        categories = user_data.get('categories', {})
        transactions_count = user_data.get('transactions_count', 0)
        
        # Historical data
        carry_over_balance = user_data.get('carry_over_balance', 0)
        effective_balance = user_data.get('effective_balance', 0)
        current_month_balance = user_data.get('current_month_balance', 0)
        total_income_all_time = user_data.get('total_income_all_time', 0)
        total_expense_all_time = user_data.get('total_expense_all_time', 0)
        avg_monthly_expense = user_data.get('avg_monthly_expense', 0)
        months_with_data = user_data.get('months_with_data', 0)
        historical_pattern = user_data.get('historical_spending_pattern', [])
        first_transaction_date = user_data.get('first_transaction_date', '')
        
        context = f"""
        DATA KEUANGAN LENGKAP:
        
        BULAN BERJALAN:
        - Pemasukan bulan ini: {total_income:,.0f} IDR
        - Pengeluaran bulan ini: {total_expense:,.0f} IDR
        - Saldo bulan ini: {current_month_balance:,.0f} IDR
        - Jumlah transaksi: {transactions_count}
        
        HISTORICAL OVERVIEW:
        - Saldo dari bulan-bulan sebelumnya: {carry_over_balance:,.0f} IDR
        - Total saldo efektif saat ini: {effective_balance:,.0f} IDR
        - Total pemasukan all-time: {total_income_all_time:,.0f} IDR
        - Total pengeluaran all-time: {total_expense_all_time:,.0f} IDR
        - Rata-rata pengeluaran per bulan: {avg_monthly_expense:,.0f} IDR
        - Data tersedia untuk: {months_with_data} bulan
        """
        
        if first_transaction_date:
            context += f"- Mulai tracking sejak: {first_transaction_date}\n"
        
        # Historical spending pattern analysis
        if len(historical_pattern) >= 2:
            context += f"\nTREND PENGELUARAN (3 bulan terakhir):\n"
            for i, amount in enumerate(historical_pattern):
                context += f"- Bulan {i+1} lalu: {amount:,.0f} IDR\n"
            
            # Calculate trend
            if historical_pattern[0] > historical_pattern[-1]:
                trend_pct = ((historical_pattern[0] - historical_pattern[-1]) / historical_pattern[-1]) * 100
                context += f"- Trend: MENURUN {trend_pct:.1f}% (bagus!)\n"
            else:
                trend_pct = ((historical_pattern[-1] - historical_pattern[0]) / historical_pattern[0]) * 100
                context += f"- Trend: NAIK {trend_pct:.1f}% (perlu perhatian)\n"
        
        # Spending ratio analysis
        if effective_balance != 0:
            if carry_over_balance > 0:
                sustainability_months = carry_over_balance / avg_monthly_expense if avg_monthly_expense > 0 else 0
                context += f"\nANALISIS SUSTAINABILITY:\n"
                context += f"- Dengan saldo carry-over, bisa bertahan {sustainability_months:.1f} bulan lagi\n"
            
            if total_income > 0:
                expense_ratio = (total_expense / total_income) * 100
                context += f"- Expense ratio bulan ini: {expense_ratio:.1f}%\n"
        
        context += "\nBREAKDOWN KATEGORI BULAN INI:\n"        # Detailed category breakdown
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        for cat, amount in sorted_categories:
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            context += f"- {cat.title()}: {amount:,.0f} IDR ({percentage:.1f}%)\n"
        
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
        """Call Google Gemini API with fast timeout"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
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
        
        try:
            response = requests.post(url, json=data, timeout=5)  # Reduced timeout to 5 seconds
            response.raise_for_status()
            
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
            
        except requests.exceptions.Timeout:
            print("⚠️ Gemini API timeout - falling back to rule-based advice")
            raise Exception("API timeout")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Gemini API error: {e} - falling back to rule-based advice")
            raise Exception(f"API error: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error with Gemini: {e} - falling back to rule-based advice")
            raise Exception(f"Unexpected error: {e}")
    
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
