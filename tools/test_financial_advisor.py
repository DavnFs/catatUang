"""CLI Testing Tool for FinancialAdvisor

Run various test scenarios against the FinancialAdvisor without Telegram.
Usage:
  python tools/test_financial_advisor.py --mode transaction --amount 50000 --category makanan --desc "sarapan nasi uduk"
  python tools/test_financial_advisor.py --mode monthly
  python tools/test_financial_advisor.py --mode budget --income 4000000
  python tools/test_financial_advisor.py --mode budgetcheck --amount 500000 --days 14
  python tools/test_financial_advisor.py --mode dailyplan --daily 75000

Environment variables (put in .env):
  GROQ_API_KEY=...
  GEMINI_API_KEY=...
  OPENAI_API_KEY=...

If no API key present or API fails, falls back to rule-based advice.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict

# Ensure project root is in path when running directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.financial_advisor import FinancialAdvisor

# Sample dummy user financial data for testing
SAMPLE_USER_DATA: Dict = {
    "total_income": 5_000_000,
    "total_expense": 3_450_000,
    "categories": {
        "makanan": 1_200_000,
        "transport": 500_000,
        "hiburan": 300_000,
        "belanja": 250_000,
    },
    "carry_over_balance": 1_000_000,
    "effective_balance": 2_550_000,
    "avg_monthly_expense": 3_400_000,
    "months_with_data": 6,
    "historical_spending_pattern": [3_600_000, 3_500_000, 3_400_000],
    "transactions_count": 128,
    "current_month_balance": 1_550_000,
    "total_income_all_time": 30_000_000,
    "total_expense_all_time": 20_350_000,
    "first_transaction_date": "2025-02-01",
}


def run_transaction(args):
    advisor = FinancialAdvisor()
    print(f"Provider terpilih: {advisor.selected_provider}\n")
    result = advisor.get_transaction_advice(args.amount, args.category, args.desc, SAMPLE_USER_DATA)
    print(result)


def run_monthly(_: argparse.Namespace):
    advisor = FinancialAdvisor()
    print(f"Provider terpilih: {advisor.selected_provider}\n")
    result = advisor.get_monthly_analysis(SAMPLE_USER_DATA)
    print(result)


def run_budget(args):
    advisor = FinancialAdvisor()
    print(f"Provider terpilih: {advisor.selected_provider}\n")
    result = advisor.get_budget_recommendation(args.income, SAMPLE_USER_DATA)
    print(result)


def run_budget_check(args):
    advisor = FinancialAdvisor()
    print(f"Provider terpilih: {advisor.selected_provider}\n")
    result = advisor.check_budget_feasibility(args.amount, args.days, SAMPLE_USER_DATA)
    print(result)


def run_daily_plan(args):
    advisor = FinancialAdvisor()
    print(f"Provider terpilih: {advisor.selected_provider}\n")
    result = advisor.get_daily_spending_plan(args.daily, args.priorities)
    print(result)


def main():
    parser = argparse.ArgumentParser(description="Test FinancialAdvisor outputs")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_tr = sub.add_parser("transaction", help="Test single transaction advice")
    p_tr.add_argument("--amount", type=float, required=True)
    p_tr.add_argument("--category", type=str, required=True)
    p_tr.add_argument("--desc", type=str, required=True)
    p_tr.set_defaults(func=run_transaction)

    p_month = sub.add_parser("monthly", help="Test monthly analysis")
    p_month.set_defaults(func=run_monthly)

    p_budget = sub.add_parser("budget", help="Test budget recommendation")
    p_budget.add_argument("--income", type=float, required=True)
    p_budget.set_defaults(func=run_budget)

    p_bcheck = sub.add_parser("budgetcheck", help="Test budget feasibility check")
    p_bcheck.add_argument("--amount", type=float, required=True)
    p_bcheck.add_argument("--days", type=int, required=True)
    p_bcheck.set_defaults(func=run_budget_check)

    p_daily = sub.add_parser("dailyplan", help="Test daily spending plan")
    p_daily.add_argument("--daily", type=float, required=True)
    p_daily.add_argument("--priorities", nargs="*", default=None)
    p_daily.set_defaults(func=run_daily_plan)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
