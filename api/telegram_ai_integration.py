"""
Integration module for Financial Advisor AI with existing Telegram Bot
"""
import json
from .financial_advisor import FinancialAdvisor, get_transaction_insight, get_monthly_financial_analysis, get_personalized_budget

class TelegramFinancialBot:
    def __init__(self):
        self.advisor = FinancialAdvisor()
    
    def get_enhanced_transaction_response(self, amount: float, category: str, description: str, 
                                        user_id: str, is_income: bool = False) -> str:
        """
        Get enhanced response with AI insights for transaction
        """
        # Get user's financial data (you'll need to implement this based on your data structure)
        user_data = self._get_user_financial_data(user_id)
        
        # Standard response first
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

        # Add AI insight if not income (for expenses, we give saving tips)
        if not is_income and self.advisor.selected_provider != 'local':
            try:
                ai_insight = self.advisor.get_transaction_advice(amount, category, description, user_data)
                return f"{standard_response}\n\n{ai_insight}"
            except Exception as e:
                print(f"AI insight error: {e}")
        
        return standard_response
    
    def _get_user_financial_data(self, user_id: str) -> dict:
        """
        Get user's financial data for the current month
        This should be implemented based on your Google Sheets data structure
        """
        # This is a placeholder - you'll need to implement based on your sheets structure
        # For now, return sample data
        return {
            'total_income': 3000000,  # Example data
            'total_expense': 1500000,
            'categories': {
                'makanan': 500000,
                'transport': 300000,
                'hiburan': 200000,
                'belanja': 400000,
                'utilitas': 100000
            },
            'daily_average': 50000,
            'transactions_count': 30
        }
    
    def get_ai_financial_analysis(self, user_id: str) -> str:
        """Get comprehensive AI-powered financial analysis"""
        try:
            user_data = self._get_user_financial_data(user_id)
            return self.advisor.get_monthly_analysis(user_data)
        except Exception as e:
            return f"❌ Gagal menganalisis data keuangan: {str(e)}"
    
    def get_ai_budget_recommendation(self, user_id: str, monthly_income: float = None) -> str:
        """Get AI-powered budget recommendations"""
        try:
            user_data = self._get_user_financial_data(user_id)
            
            # If income not provided, try to estimate from data
            if monthly_income is None:
                monthly_income = user_data.get('total_income', 3000000)  # Default estimate
            
            return self.advisor.get_budget_recommendation(monthly_income, user_data)
        except Exception as e:
            return f"❌ Gagal membuat rekomendasi budget: {str(e)}"
    
    def get_smart_category_suggestion(self, description: str) -> str:
        """Use AI to suggest better category based on description"""
        if self.advisor.selected_provider == 'local':
            return None  # Skip AI suggestion if no API available
            
        try:
            prompt = f"""
            Berdasarkan deskripsi transaksi: "{description}"
            
            Tentukan kategori yang paling tepat dari pilihan berikut:
            makanan, transport, belanja, kesehatan, hiburan, pendidikan, utilitas, investasi, gaji, lainnya
            
            Berikan hanya nama kategori, tanpa penjelasan tambahan.
            """
            
            response = self.advisor._get_ai_response(prompt)
            # Extract just the category name from response
            category = response.strip().lower()
            
            valid_categories = ['makanan', 'transport', 'belanja', 'kesehatan', 'hiburan', 
                              'pendidikan', 'utilitas', 'investasi', 'gaji', 'lainnya']
            
            if category in valid_categories:
                return category
                
        except Exception as e:
            print(f"AI category suggestion error: {e}")
        
        return None

# Additional command handlers for new AI features
def handle_advice_command(user_id: str) -> str:
    """Handle /advice command"""
    bot = TelegramFinancialBot()
    return bot.get_ai_financial_analysis(user_id)

def handle_budget_command(user_id: str, monthly_income: float = None) -> str:
    """Handle /budget command"""
    bot = TelegramFinancialBot()
    return bot.get_ai_budget_recommendation(user_id, monthly_income)

def handle_tips_command(category: str = None) -> str:
    """Handle /tips command"""
    advisor = FinancialAdvisor()
    
    if category:
        prompt = f"""
        Berikan 5 tips praktis untuk menghemat pengeluaran kategori {category} dalam konteks Indonesia.
        
        Format:
        💡 TIPS HEMAT {category.upper()}
        
        1. [tip pertama]
        2. [tip kedua] 
        3. [tip ketiga]
        4. [tip keempat]
        5. [tip kelima]
        
        Setiap tip harus actionable dan realistis untuk orang Indonesia.
        """
    else:
        prompt = """
        Berikan 5 tips umum pengelolaan keuangan untuk orang Indonesia.
        
        Format:
        💰 TIPS KEUANGAN SMART
        
        1. [tip pertama]
        2. [tip kedua]
        3. [tip ketiga] 
        4. [tip keempat]
        5. [tip kelima]
        
        Focus pada tips yang praktis dan mudah diterapkan.
        """
    
    try:
        return advisor._get_ai_response(prompt)
    except Exception as e:
        return """💰 TIPS KEUANGAN SMART

1. 💎 Sisihkan 20% penghasilan untuk tabungan dan investasi
2. 🏠 Batasi pengeluaran kebutuhan pokok maksimal 50% income
3. 📊 Catat semua pengeluaran untuk kontrol yang lebih baik
4. 🚨 Buat emergency fund minimal 6 bulan pengeluaran
5. 📈 Mulai investasi dari sekarang, walau jumlah kecil

💡 Konsistensi lebih penting daripada jumlah besar!"""

def handle_goals_command(user_id: str, goal_amount: float = None, goal_description: str = "") -> str:
    """Handle /goals command"""
    if goal_amount is None:
        return """🎯 SET FINANCIAL GOALS

Gunakan format: `/goals [jumlah] [deskripsi]`

**Contoh:**
• `/goals 10000000 emergency fund`
• `/goals 50000000 beli motor`
• `/goals 5000000 liburan bali`

💡 Goals yang clear dan terukur lebih mudah dicapai!"""
    
    advisor = FinancialAdvisor()
    
    prompt = f"""
    User ingin menabung {goal_amount:,.0f} IDR untuk {goal_description}.
    
    Berikan rencana menabung yang realistis dengan asumsi penghasilan menengah Indonesia (3-5 juta/bulan).
    
    Format:
    🎯 RENCANA MENCAPAI GOAL
    
    💰 Target: {goal_amount:,.0f} IDR - {goal_description}
    
    📅 Timeline Options:
    • 6 bulan: [jumlah per bulan] IDR/bulan
    • 12 bulan: [jumlah per bulan] IDR/bulan  
    • 24 bulan: [jumlah per bulan] IDR/bulan
    
    💡 Tips Mencapai Goal:
    [3 tips praktis]
    
    🚀 Action Plan:
    [langkah konkret yang bisa dimulai hari ini]
    """
    
    try:
        return advisor._get_ai_response(prompt)
    except Exception as e:
        # Fallback calculation
        monthly_6 = goal_amount / 6
        monthly_12 = goal_amount / 12
        monthly_24 = goal_amount / 24
        
        return f"""🎯 RENCANA MENCAPAI GOAL

💰 Target: Rp {goal_amount:,.0f} - {goal_description}

📅 Timeline Options:
• 6 bulan: Rp {monthly_6:,.0f}/bulan
• 12 bulan: Rp {monthly_12:,.0f}/bulan
• 24 bulan: Rp {monthly_24:,.0f}/bulan

💡 Tips Mencapai Goal:
1. Set auto transfer ke rekening terpisah
2. Kurangi 1-2 kebiasaan pengeluaran kecil
3. Cari sumber income tambahan

🚀 Mulai hari ini, jangan tunda lagi!"""
