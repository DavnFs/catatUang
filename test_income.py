import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import importlib.util

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the modules to test
from api.financial_advisor import FinancialAdvisor

# Import telegram_webhook module using importlib due to hyphen in filename
spec = importlib.util.spec_from_file_location("telegram_webhook", 
                                             os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                         "api", "telegram-webhook.py"))
telegram_webhook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telegram_webhook)

class TestIncomeFeature(unittest.TestCase):
    
    def test_income_transaction_advice(self):
        """Test that FinancialAdvisor.get_transaction_advice provides appropriate advice for income"""
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
    
    def test_process_income_message(self):
        """Test that telegram_webhook._process_income_message correctly processes income messages"""
        # Create a mock handler instance
        handler = telegram_webhook.handler()
        
        # Mock the necessary methods
        handler.get_user_data = MagicMock(return_value={
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        })
        handler.add_income = MagicMock(return_value=True)
        handler.get_transaction_advice = MagicMock(return_value="Advice for income")
        
        # Test processing an income message
        with patch.object(handler, 'send_message') as mock_send_message:
            handler._process_income_message("+500000 gaji gaji tambahan", "user123")
            
            # Assert that the message was processed correctly
            handler.add_income.assert_called_once()
            handler.get_transaction_advice.assert_called_once()
            mock_send_message.assert_called()
    
    def test_income_category_detection(self):
        """Test that telegram_webhook._process_income_message correctly detects income categories"""
        # Create a mock handler instance
        handler = telegram_webhook.handler()
        
        # Mock the necessary methods
        handler.get_user_data = MagicMock(return_value={
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        })
        handler.add_income = MagicMock(return_value=True)
        handler.get_transaction_advice = MagicMock(return_value="Advice for income")
        
        # Test with different income categories
        with patch.object(handler, 'send_message'):
            # Test with 'gaji' category
            handler._process_income_message("+3000000 gaji gaji bulanan", "user123")
            handler.add_income.assert_called_with("user123", 3000000, "gaji", "gaji bulanan")
            
            # Test with 'bonus' category
            handler.add_income.reset_mock()
            handler._process_income_message("+1000000 bonus bonus tahunan", "user123")
            handler.add_income.assert_called_with("user123", 1000000, "bonus", "bonus tahunan")
            
            # Test with 'lainnya' category
            handler.add_income.reset_mock()
            handler._process_income_message("+500000 lainnya penjualan barang", "user123")
            handler.add_income.assert_called_with("user123", 500000, "lainnya", "penjualan barang")

if __name__ == '__main__':
    unittest.main()