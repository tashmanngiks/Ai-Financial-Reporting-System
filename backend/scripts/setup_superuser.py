#!/usr/bin/env python3
"""Setup a superuser account for initial login."""
import os
import sys
from pathlib import Path

# Make project importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_analytics.settings_sqlite')

import django
django.setup()

from django.contrib.auth.models import User

# Delete existing admin if present
User.objects.filter(username='admin').delete()

# Create new superuser with known credentials
user = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='SecureAdmin123!'
)

print(f"✓ Superuser created successfully!")
print(f"  Username: admin")
print(f"  Password: SecureAdmin123!")
print(f"\nUse these credentials to log in.")
