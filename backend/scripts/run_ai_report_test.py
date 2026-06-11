import os
import sys
import json
from pathlib import Path

# Ensure Django project is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_analytics.settings_sqlite')

import django
django.setup()

from analytics.views import generate_comprehensive_ai_analysis

# Load sample financial data if available
root = Path(__file__).resolve().parents[2]
sample_path = root / 'sample_financial_data.json'
if sample_path.exists():
    data = json.loads(sample_path.read_text())
else:
    data = {
        "dashboard": {"bank_name": "Test Bank", "period": "2026-Q2"},
        "metrics": {"profitability": {"roa": 1.2, "roe": 8.5}},
        "accounts": []
    }

context = {
    'raw_financial_data': data,
    'bank_name': data.get('dashboard', {}).get('bank_name', 'Test Bank'),
    'data_period': data.get('dashboard', {}).get('period', '2026-Q2'),
    'user_prompt': 'Provide a concise executive summary and 3 recommendations.'
}

print('Running AI report generation test...')
try:
    result = generate_comprehensive_ai_analysis(context)
    print('Result keys:', list(result.keys()))
    if result.get('success') is False:
        print('AI reported error:', result.get('error'))
    else:
        sections = result.get('sections') or []
        print(f'Generated sections: {len(sections)}')
        if sections:
            print('First section title:', sections[0].get('title'))
            print('First section content preview:', str(sections[0].get('content'))[:500])
    sys.exit(0)
except Exception as e:
    print('Test failed with exception:', str(e))
    raise
