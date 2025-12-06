import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import importlib.util
from datetime import datetime, timedelta

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import report module using importlib
spec = importlib.util.spec_from_file_location("report", 
                                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                          "api", "report.py"))
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)

# Import telegram_webhook module using importlib due to hyphen in filename
spec = importlib.util.spec_from_file_location("telegram_webhook", 
                                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                          "api", "telegram-webhook.py"))
telegram_webhook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telegram_webhook)

class TestReportFeature(unittest.TestCase):
    
    def setUp(self):
        # Create mock request, client_address, and server for BaseHTTPRequestHandler
        mock_request = MagicMock()
        mock_client_address = ('127.0.0.1', 12345)
        mock_server = MagicMock()
        
        # Patch the handler's __init__ method to avoid requiring HTTP request objects
        with patch('http.server.BaseHTTPRequestHandler.__init__', return_value=None):
            self.handler = telegram_webhook.handler(mock_request, mock_client_address, mock_server)
        
        # Mock data for testing - format as dictionaries like sheet.get_all_records()
        self.mock_data = [
            {'Tanggal': '2023-06-01', 'Jenis': 'expense', 'Jumlah': '-50000', 'Kategori': 'makanan', 'Deskripsi': 'makan siang'},
            {'Tanggal': '2023-06-01', 'Jenis': 'expense', 'Jumlah': '-25000', 'Kategori': 'transport', 'Deskripsi': 'ojek'},
            {'Tanggal': '2023-06-02', 'Jenis': 'expense', 'Jumlah': '-75000', 'Kategori': 'hiburan', 'Deskripsi': 'nonton'},
            {'Tanggal': '2023-06-02', 'Jenis': 'income', 'Jumlah': '1000000', 'Kategori': 'gaji', 'Deskripsi': 'gaji bulanan'},
            {'Tanggal': '2023-06-03', 'Jenis': 'expense', 'Jumlah': '-30000', 'Kategori': 'makanan', 'Deskripsi': 'sarapan'},
            {'Tanggal': '2023-06-03', 'Jenis': 'expense', 'Jumlah': '-20000', 'Kategori': 'transport', 'Deskripsi': 'bensin'}
        ]
        
        # Mock current date for testing
        self.mock_date = datetime(2023, 6, 3, 15, 30, 0)
        
        # Add the _get_sheets_data method to the handler for testing
        self.handler._get_sheets_data = MagicMock(return_value=self.mock_data)
    
    def test_daily_report(self):
        """Test that daily report generates correctly"""
        # Mock the get_jakarta_time function to return our fixed date
        with patch.object(telegram_webhook, 'get_jakarta_time', return_value=self.mock_date):
            # Generate daily report
            report_text = self.handler._generate_report_summary('today')
            
            # Assert that the report contains expected information
            self.assertIn('Laporan Hari Ini', report_text)
            self.assertIn('03/06/2023', report_text)
            self.assertIn('Rp 50.000', report_text)  # Total daily expense
            self.assertIn('Makanan', report_text)
            self.assertIn('Transport', report_text)
    
    def test_weekly_report(self):
        """Test that weekly report generates correctly"""
        # Mock the get_jakarta_time function to return our fixed date
        with patch.object(telegram_webhook, 'get_jakarta_time', return_value=self.mock_date):
            # Generate weekly report
            report_text = self.handler._generate_report_summary('week')
            
            # Assert that the report contains expected information
            self.assertIn('Laporan 7 Hari Terakhir', report_text)
            self.assertIn('03/06/2023', report_text)
            self.assertIn('Rp 1.000.000', report_text)  # Total income
            self.assertIn('Rp 200.000', report_text)   # Total expenses
    
    def test_monthly_report(self):
        """Test that monthly report generates correctly"""
        # Mock the get_jakarta_time function to return our fixed date
        with patch.object(telegram_webhook, 'get_jakarta_time', return_value=self.mock_date):
            # Generate monthly report
            report_text = self.handler._generate_report_summary('month')
            
            # Assert that the report contains expected information
            self.assertIn('Laporan Bulan Ini', report_text)
            self.assertIn('03/06/2023', report_text)
            self.assertIn('Rp 1.000.000', report_text)  # Total income
            self.assertIn('Rp 200.000', report_text)   # Total expenses
            self.assertIn('Makanan', report_text)
            self.assertIn('Transport', report_text)
            self.assertIn('Hiburan', report_text)
    
    def test_expenses_report(self):
        """Test that expenses-only report generates correctly"""
        # Mock the get_jakarta_time function to return our fixed date
        with patch.object(telegram_webhook, 'get_jakarta_time', return_value=self.mock_date):
            # Generate expenses report
            report_text = self.handler._generate_expenses_only_report()
            
            # Assert that the report contains expected information
            self.assertIn('Expense Report', report_text)
            self.assertIn('Rp 200.000', report_text)  # Total expenses
            self.assertIn('Makanan: Rp 80.000', report_text)
            self.assertIn('Transport: Rp 45.000', report_text)
            self.assertIn('Hiburan: Rp 75.000', report_text)
    
    def test_current_balance(self):
        """Test that current balance report generates correctly"""
        # Generate current balance report
        report_text = self.handler._get_current_balance()
        
        # Assert that the report contains expected information
        self.assertIn('Balance Overview', report_text)
        self.assertIn('Rp 800.000', report_text)  # Expected balance (1000000 - 200000)
        self.assertIn('pemasukan', report_text)
        self.assertIn('pengeluaran', report_text)

if __name__ == '__main__':
    unittest.main()