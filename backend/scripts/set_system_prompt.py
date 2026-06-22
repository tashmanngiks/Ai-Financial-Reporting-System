#!/usr/bin/env python3
"""CLI to view and update the persisted system prompt template.

Usage examples:
  python backend/scripts/set_system_prompt.py --show
  python backend/scripts/set_system_prompt.py --file ./template.txt
  python backend/scripts/set_system_prompt.py --text "New template..."
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
import os

# Make project importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_analytics.settings_sqlite')

import django
django.setup()

from analytics.services.report_prompt_registry import get_report_prompt_registry


def main() -> int:
    parser = argparse.ArgumentParser(description='View or update the system prompt template')
    parser.add_argument('--show', action='store_true', help='Print the current persisted template')
    parser.add_argument('--file', '-f', help='Path to a file containing the new template')
    parser.add_argument('--text', '-t', help='Template text (use quotes)')
    args = parser.parse_args()

    registry = get_report_prompt_registry()
    config = registry.load()
    current = config.get('system_prompt_template')

    if args.show and not (args.file or args.text):
        if current:
            print(current)
            return 0
        print('<no template persisted>')
        return 0

    if not args.file and not args.text:
        parser.print_help()
        return 2

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f'File not found: {path}', file=sys.stderr)
            return 3
        new_template = path.read_text(encoding='utf-8')
    else:
        new_template = args.text

    config['system_prompt_template'] = new_template
    saved = registry.save(config)
    print('Saved system_prompt_template to', registry.config_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
