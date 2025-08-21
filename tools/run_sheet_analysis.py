import os
import base64
import json
import sys
from pathlib import Path

# Ensure repository root is on sys.path so `from api...` imports work when running the script
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Try to import Google API libraries; if missing, we will print an actionable message later
GOOGLE_LIBS_AVAILABLE = True
try:
    from google.oauth2.service_account import Credentials
    import gspread
except Exception:
    GOOGLE_LIBS_AVAILABLE = False

from api.financial_advisor import FinancialAdvisor


def safe_int(v):
    try:
        return int(v)
    except Exception:
        try:
            s = str(v).replace(',', '').replace('.', '')
            return int(float(s))
        except Exception:
            return 0


def main():
    if not GOOGLE_LIBS_AVAILABLE:
        print('Missing Google API libraries (gspread/google-auth).')
        print('Install them with: pip install -r requirements.txt')
        return

    key_b64 = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    sheet_id = os.environ.get('GOOGLE_SHEETS_ID')
    if not key_b64 or not sheet_id:
        print('Missing GOOGLE_SERVICE_ACCOUNT_KEY or GOOGLE_SHEETS_ID in environment.')
        return

    try:
        key_json = base64.b64decode(key_b64).decode('utf-8')
        cred_info = json.loads(key_json)
    except Exception as e:
        print('Failed to decode GOOGLE_SERVICE_ACCOUNT_KEY:', e)
        return

    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    try:
        creds = Credentials.from_service_account_info(cred_info, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        rows = sheet.get_all_records()
    except Exception as e:
        print('Error fetching sheet:', e)
        return

    total_income = 0
    total_expense = 0
    categories = {}
    transactions = []

    for r in rows:
        # tolerant key names
        jumlah = r.get('Jumlah') if 'Jumlah' in r else r.get('jumlah', 0)
        jumlah = safe_int(jumlah)
        kategori = r.get('Kategori') or r.get('kategori') or 'lainnya'
        des = r.get('Deskripsi') or r.get('Keterangan') or r.get('deskripsi') or ''
        tanggal = r.get('Tanggal') or r.get('tanggal') or ''

        if jumlah > 0:
            total_income += jumlah
        else:
            total_expense += abs(jumlah)
            categories[kategori] = categories.get(kategori, 0) + abs(jumlah)

        transactions.append({'kategori': kategori, 'jumlah': jumlah, 'des': des, 'tanggal': tanggal})

    carry_over = safe_int(os.environ.get('CARRY_OVER_BALANCE', 0))

    user_data = {
        'total_income': total_income,
        'total_expense': total_expense,
        'carry_over_balance': carry_over,
        'categories': categories,
        'transactions_count': len(transactions),
        'historical_spending_pattern': [],
        'avg_monthly_expense': total_expense,
        'months_with_data': 1
    }

    advisor = FinancialAdvisor()

    print('\n=== MONTHLY ANALYSIS ===\n')
    try:
        print(advisor.get_monthly_analysis(user_data))
    except Exception as e:
        print('Error running monthly analysis:', e)

    if transactions:
        last = transactions[-1]
        amt = abs(last['jumlah'])
        cat = last['kategori'] or 'lainnya'
        desc = last['des'] or last['tanggal'] or 'transaksi terbaru'

        print('\n=== ADVICE FOR LAST TRANSACTION ===\n')
        try:
            print(advisor.get_transaction_advice(amt, cat, desc, user_data))
        except Exception as e:
            print('Error running transaction advice:', e)


if __name__ == '__main__':
    main()
