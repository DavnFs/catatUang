import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the modules to test
from api.financial_advisor import FinancialAdvisor

class TestFinancialAdvisor(unittest.TestCase):
    
    def test_get_transaction_advice_expense(self):
        """Test that get_transaction_advice provides appropriate advice for expenses"""
        # Setup mock user data
        user_data = {
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        }
        
        # Create an instance of FinancialAdvisor
        advisor = FinancialAdvisor()
        
        # Mock the AI response
        mock_response = """💡 Tips:
🍽️ Pengeluaran makanan sebesar Rp 100.000 masih dalam batas wajar (10% dari pengeluaran bulanan).
🛒 Pertimbangkan untuk memasak di rumah lebih sering untuk menghemat pengeluaran makanan.
💰 Dengan saldo yang cukup, tetap bijak dalam pengeluaran untuk mencapai target tabungan."""
        
        # Test with an expense transaction
        with patch.object(advisor, '_get_ai_response', return_value=mock_response):
            advice = advisor.get_transaction_advice(
                amount=100000,
                category='makanan',
                description='makan siang',
                user_data=user_data
            )
        
        # Assert that the advice contains expense-specific recommendations
        self.assertEqual(advice, mock_response)
        self.assertIn("Pengeluaran makanan", advice)
        self.assertIn("memasak di rumah", advice)
    
    def test_get_transaction_advice_income(self):
        """Test that get_transaction_advice provides appropriate advice for income"""
        # Setup mock user data
        user_data = {
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        }
        
        # Create an instance of FinancialAdvisor
        advisor = FinancialAdvisor()
        
        # Mock the AI response
        mock_response = """💡 Tips:
💰 Pemasukan tambahan sebesar Rp 500.000 meningkatkan saldo bulanan Anda.
📊 Pertimbangkan untuk mengalokasikan 50% ke tabungan dan 50% untuk kebutuhan.
🏦 Dengan saldo yang meningkat, Anda bisa mempertimbangkan investasi jangka panjang."""
        
        # Test with an income transaction
        with patch.object(advisor, '_get_ai_response', return_value=mock_response):
            advice = advisor.get_transaction_advice(
                amount=500000,
                category='gaji',
                description='gaji tambahan',
                user_data=user_data
            )
        
        # Assert that the advice contains income-specific recommendations
        self.assertEqual(advice, mock_response)
        self.assertIn("Pemasukan tambahan", advice)
        self.assertIn("tabungan", advice)
        self.assertIn("investasi", advice)
    
    def test_get_budget_recommendation(self):
        """Test that get_budget_recommendation provides appropriate budget recommendations"""
        # Setup mock user data
        user_data = {
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        }
        
        # Create an instance of FinancialAdvisor
        advisor = FinancialAdvisor()
        
        # Mock the AI response
        mock_response = """💡 Rekomendasi Budget Bulanan:

🍽️ Makanan: Rp 1.500.000 (30% dari pendapatan)
🚗 Transport: Rp 750.000 (15% dari pendapatan)
🏠 Sewa/Cicilan: Rp 1.250.000 (25% dari pendapatan)
💊 Kesehatan: Rp 250.000 (5% dari pendapatan)
🎭 Hiburan: Rp 500.000 (10% dari pendapatan)
💰 Tabungan: Rp 750.000 (15% dari pendapatan)"""
        
        # Test the budget recommendation
        with patch.object(advisor, '_get_ai_response', return_value=mock_response):
            recommendation = advisor.get_budget_recommendation(user_data)
        
        # Assert that the recommendation contains appropriate budget categories
        self.assertEqual(recommendation, mock_response)
        self.assertIn("Rekomendasi Budget Bulanan", recommendation)
        self.assertIn("Makanan", recommendation)
        self.assertIn("Transport", recommendation)
        self.assertIn("Tabungan", recommendation)
    
    def test_check_budget_feasibility(self):
        """Test that check_budget_feasibility provides appropriate feasibility assessment"""
        # Setup mock user data and budget
        user_data = {
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        }
        
        budget = {
            'makanan': 1500000,
            'transport': 750000,
            'sewa': 1250000,
            'kesehatan': 250000,
            'hiburan': 500000,
            'tabungan': 750000
        }
        
        # Create an instance of FinancialAdvisor
        advisor = FinancialAdvisor()
        
        # Mock the AI response
        mock_response = """✅ Budget Anda Realistis!

📊 Total Budget: Rp 5.000.000
💰 Total Pendapatan: Rp 5.000.000

💡 Analisis:
- Budget seimbang dengan pendapatan (100%)
- Alokasi tabungan 15% sudah baik (minimal 10%)
- Pengeluaran makanan 30% masih wajar (ideal 20-30%)
- Biaya sewa/cicilan 25% ideal (batas aman 30%)

🎯 Saran:
- Pertahankan disiplin mengikuti budget ini
- Pantau kategori makanan agar tidak melebihi batas
- Pertimbangkan meningkatkan tabungan jika ada pendapatan tambahan"""
        
        # Test the budget feasibility
        with patch.object(advisor, '_get_ai_response', return_value=mock_response):
            assessment = advisor.check_budget_feasibility(budget, user_data)
        
        # Assert that the assessment contains appropriate feasibility information
        self.assertEqual(assessment, mock_response)
        self.assertIn("Budget Anda Realistis", assessment)
        self.assertIn("Total Budget", assessment)
        self.assertIn("Total Pendapatan", assessment)
        self.assertIn("Analisis", assessment)
    
    def test_get_daily_spending_plan(self):
        """Test that get_daily_spending_plan provides appropriate daily spending plan"""
        # Setup mock user data
        user_data = {
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000,
            'remaining_days': 15
        }
        
        # Create an instance of FinancialAdvisor
        advisor = FinancialAdvisor()
        
        # Mock the AI response
        mock_response = """💡 Rencana Pengeluaran Harian:

📅 Sisa hari dalam bulan ini: 15 hari
💰 Sisa saldo bulan ini: Rp 3.000.000
💸 Budget harian yang aman: Rp 200.000/hari

🍽️ Makanan: maks. Rp 60.000/hari
🚗 Transport: maks. Rp 30.000/hari
☕ Minuman/Snack: maks. Rp 20.000/hari
🎭 Hiburan: maks. Rp 40.000/hari
💊 Kebutuhan mendadak: Rp 50.000/hari

💡 Tips:
- Siapkan bekal dari rumah untuk hemat makan siang
- Gunakan transportasi umum jika memungkinkan
- Batasi pembelian impulsif
- Sisihkan Rp 30.000/hari untuk tabungan"""
        
        # Test the daily spending plan
        with patch.object(advisor, '_get_ai_response', return_value=mock_response):
            plan = advisor.get_daily_spending_plan(user_data)
        
        # Assert that the plan contains appropriate daily spending information
        self.assertEqual(plan, mock_response)
        self.assertIn("Rencana Pengeluaran Harian", plan)
        self.assertIn("Sisa hari dalam bulan ini", plan)
        self.assertIn("Budget harian yang aman", plan)
        self.assertIn("Tips", plan)
    
    def test_get_monthly_analysis(self):
        """Test that get_monthly_analysis provides appropriate monthly analysis"""
        # Setup mock user data
        user_data = {
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000,
            'previous_month': {
                'total_income': 4800000,
                'total_expense': 2200000,
                'categories': {'makanan': 1200000, 'transport': 600000, 'hiburan': 400000}
            }
        }
        
        # Create an instance of FinancialAdvisor
        advisor = FinancialAdvisor()
        
        # Mock the AI response
        mock_response = """📊 Analisis Keuangan Bulanan:

💰 Pendapatan: Rp 5.000.000 (+4.2% dari bulan lalu)
💸 Pengeluaran: Rp 2.000.000 (-9.1% dari bulan lalu)
💼 Saldo: Rp 3.000.000 (+15.4% dari bulan lalu)

📈 Perubahan Kategori:
- Makanan: Rp 1.000.000 (-16.7% 👍)
- Transport: Rp 500.000 (-16.7% 👍)
- Hiburan: Rp 500.000 (+25% 👎)

💡 Insight:
- Pengeluaran makanan dan transport menurun, pertahankan!
- Pengeluaran hiburan meningkat, perlu diperhatikan
- Rasio tabungan 60% sangat baik (ideal >20%)

🎯 Rekomendasi:
- Pertahankan pola pengeluaran makanan dan transport
- Evaluasi pengeluaran hiburan yang meningkat
- Pertimbangkan investasi dengan kelebihan saldo
- Tetapkan target tabungan minimal 25% dari pendapatan"""
        
        # Test the monthly analysis
        with patch.object(advisor, '_get_ai_response', return_value=mock_response):
            analysis = advisor.get_monthly_analysis(user_data)
        
        # Assert that the analysis contains appropriate monthly analysis information
        self.assertEqual(analysis, mock_response)
        self.assertIn("Analisis Keuangan Bulanan", analysis)
        self.assertIn("Pendapatan", analysis)
        self.assertIn("Pengeluaran", analysis)
        self.assertIn("Perubahan Kategori", analysis)
        self.assertIn("Insight", analysis)
        self.assertIn("Rekomendasi", analysis)

if __name__ == '__main__':
    unittest.main()