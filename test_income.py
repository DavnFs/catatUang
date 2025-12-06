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
        # Create mock request, client_address, and server for BaseHTTPRequestHandler
        mock_request = MagicMock()
        mock_client_address = ('127.0.0.1', 12345)
        mock_server = MagicMock()
        
        # Patch the handler's __init__ method to avoid requiring HTTP request objects
        with patch('http.server.BaseHTTPRequestHandler.__init__', return_value=None):
            handler = telegram_webhook.handler(mock_request, mock_client_address, mock_server)
        
        # Mock the necessary methods
        handler._get_user_financial_data = MagicMock(return_value={
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'makanan': 1000000, 'transport': 500000, 'hiburan': 500000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        })
        handler._save_to_sheets = MagicMock(return_value=True)
        handler._calculate_daily_spending_pattern = MagicMock(return_value={})
        handler._get_remaining_days_in_month = MagicMock(return_value=15)
        handler._calculate_daily_budget = MagicMock(return_value=100000)
        handler._generate_personalized_advice = MagicMock(return_value="Advice for income")
        
        # Test processing an income message
        with patch.object(handler, '_send_telegram_message') as mock_send_message:
            result = handler._process_expense_message("+500000 gaji gaji tambahan", "user123")
            
            # Assert that the message was processed correctly
            handler._save_to_sheets.assert_called_once()
            handler._get_user_financial_data.assert_called_once()
            
            # Check that a successful result was returned (which indicates the message would be sent)
            self.assertIsNotNone(result)
            self.assertIn("Tercatat", result)
    
    def test_income_category_detection(self):
        """Test that telegram_webhook._process_income_message correctly detects income categories"""
        # Create mock request, client_address, and server for BaseHTTPRequestHandler
        mock_request = MagicMock()
        mock_client_address = ('127.0.0.1', 12345)
        mock_server = MagicMock()
        
        # Patch the handler's __init__ method to avoid requiring HTTP request objects
        with patch('http.server.BaseHTTPRequestHandler.__init__', return_value=None):
            handler = telegram_webhook.handler(mock_request, mock_client_address, mock_server)
        
        # Mock the necessary methods
        handler._get_user_financial_data = MagicMock(return_value={
            'total_income': 5000000,
            'total_expense': 2000000,
            'categories': {'gaji': 3000000, 'bisnis': 2000000},
            'transactions_count': 15,
            'carry_over_balance': 1000000,
            'effective_balance': 4000000
        })
        handler._save_to_sheets = MagicMock(return_value=True)
        handler._calculate_daily_spending_pattern = MagicMock(return_value={})
        handler._get_remaining_days_in_month = MagicMock(return_value=15)
        handler._calculate_daily_budget = MagicMock(return_value=100000)
        handler._generate_personalized_advice = MagicMock(return_value="Advice for income")
        
        # Test with different income categories
        # Test processing an income message with category detection
        with patch.object(handler, '_send_telegram_message'):
            # Test with 'gaji' category
            handler._process_expense_message("+3000000 gaji gaji bulanan", "user123")
            
            # Check that save_to_sheets was called with correct category
            handler._save_to_sheets.assert_called()
            args, kwargs = handler._save_to_sheets.call_args
            saved_data = args[0]
            self.assertEqual(saved_data['kategori'], 'gaji')
            self.assertEqual(saved_data['jumlah'], 3000000)  # Positive for income

if __name__ == '__main__':
    unittest.main()