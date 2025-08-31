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

class TestExpenseFeature(unittest.TestCase):
    
    def test_expense_transaction_advice(self):
        """Test that FinancialAdvisor.get_transaction_advice provides appropriate advice for expenses"""
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
    
    def test_process_expense_message(self):
        """Test that telegram_webhook._process_expense_message correctly processes expense messages"""
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
        handler.add_expense = MagicMock(return_value=True)
        handler.get_transaction_advice = MagicMock(return_value="Advice for expense")
        
        # Test processing an expense message
        with patch.object(handler, 'send_message') as mock_send_message:
            handler._process_expense_message("100000 makanan makan siang", "user123")
            
            # Assert that the message was processed correctly
            handler.add_expense.assert_called_once()
            handler.get_transaction_advice.assert_called_once()
            mock_send_message.assert_called()
    
    def test_expense_category_detection(self):
        """Test that telegram_webhook._process_expense_message correctly detects expense categories"""
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
        handler.add_expense = MagicMock(return_value=True)
        handler.get_transaction_advice = MagicMock(return_value="Advice for expense")
        
        # Test with different expense categories
        with patch.object(handler, 'send_message'):
            # Test with 'makanan' category
            handler._process_expense_message("50000 makanan sarapan", "user123")
            handler.add_expense.assert_called_with("user123", 50000, "makanan", "sarapan")
            
            # Test with 'transport' category
            handler.add_expense.reset_mock()
            handler._process_expense_message("25000 transport ojek", "user123")
            handler.add_expense.assert_called_with("user123", 25000, "transport", "ojek")
            
            # Test with 'hiburan' category
            handler.add_expense.reset_mock()
            handler._process_expense_message("75000 hiburan nonton", "user123")
            handler.add_expense.assert_called_with("user123", 75000, "hiburan", "nonton")

if __name__ == '__main__':
    unittest.main()