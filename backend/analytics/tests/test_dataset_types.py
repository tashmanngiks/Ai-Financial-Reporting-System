"""Tests for nine-dataset-type selection, validation, prompts, and templates."""

from __future__ import annotations

from django.test import SimpleTestCase, TestCase

from analytics.api.uploads import (
    DATASET_TYPE_RULES,
    _infer_dataset_type,
    _validate_dataset_type,
)
from analytics.services.analysis_prompt_defaults import (
    ANNUAL_FINANCIAL_ANALYSIS_ID,
    ANNUAL_FINANCIAL_ANALYSIS_PROMPT,
    CREDIT_RISK_ANALYSIS_ID,
    FINANCIAL_INSTRUMENTS_ANALYSIS_ID,
    MONEY_MARKET_ANALYSIS_ID,
    WACC_ANALYSIS_ID,
    get_default_analysis_prompt_definitions,
)
from analytics.services.prompt_module_store import decompose_master_prompt_to_section_prompts
from analytics.services.report_prompt_registry import (
    DEFAULT_REPORT_PROMPT_CONFIG,
    get_report_prompt_registry,
)


EXPECTED_DATASET_TYPES = [
    'wacc',
    'money_market',
    'financial_instruments',
    'credit_risk',
    'financial_statements',
    'investment_portfolio',
    'market_macro',
    'valuation',
    'annual_financial',
]

ANNUAL_FINANCIAL_SECTIONS = [
    'executive_summary',
    'annual_financial_overview',
    'revenue_income_performance',
    'profitability_analysis',
    'financial_position_analysis',
    'asset_analysis',
    'liability_debt_analysis',
    'equity_capital_structure_analysis',
    'cash_flow_analysis',
    'working_capital_analysis',
    'financial_ratio_analysis',
    'year_over_year_trend_analysis',
    'financial_strength_stability',
    'financial_risks_weaknesses',
    'key_performance_drivers',
    'recommendations',
    'conclusion',
]


SINGLE_YEAR_ANNUAL = {
    'entity': 'Acme Corp',
    'financial_year': 2024,
    'income_statement': {
        'revenue': 1000,
        'cost_of_sales': 400,
        'gross_profit': 600,
        'operating_income': 250,
        'ebitda': 300,
        'ebit': 250,
        'finance_costs': 40,
        'profit_before_tax': 210,
        'tax_expense': 50,
        'net_income': 160,
    },
    'balance_sheet': {
        'total_assets': 2000,
        'current_assets': 800,
        'cash': 200,
        'receivables': 300,
        'inventory': 150,
        'total_liabilities': 900,
        'current_liabilities': 400,
        'borrowings': 500,
        'total_equity': 1100,
        'retained_earnings': 700,
    },
    'cash_flow': {
        'operating_cash_flow': 280,
        'investing_cash_flow': -120,
        'financing_cash_flow': -80,
        'capital_expenditure': 100,
        'free_cash_flow': 180,
        'net_change_in_cash': 80,
    },
}

MULTI_YEAR_ANNUAL = {
    'entity': 'Acme Corp',
    'annual_financial': [
        {
            'financial_year': 2022,
            'income_statement': {'revenue': 800, 'net_income': 100, 'ebitda': 200},
            'balance_sheet': {'total_assets': 1500, 'total_liabilities': 700, 'total_equity': 800, 'borrowings': 400},
            'cash_flow': {'operating_cash_flow': 180, 'free_cash_flow': 90},
        },
        {
            'financial_year': 2023,
            'income_statement': {'revenue': 900, 'net_income': 130, 'ebitda': 240},
            'balance_sheet': {'total_assets': 1700, 'total_liabilities': 750, 'total_equity': 950, 'borrowings': 420},
            'cash_flow': {'operating_cash_flow': 210, 'free_cash_flow': 110},
        },
        {
            'financial_year': 2024,
            'income_statement': {'revenue': 1000, 'net_income': 160, 'ebitda': 300},
            'balance_sheet': {'total_assets': 2000, 'total_liabilities': 900, 'total_equity': 1100, 'borrowings': 500},
            'cash_flow': {'operating_cash_flow': 280, 'free_cash_flow': 180},
        },
    ],
}

WACC_SAMPLE = {
    'wacc': 0.092,
    'cost_of_equity': 0.12,
    'cost_of_debt': 0.06,
    'tax_rate': 0.25,
    'capital_structure': {'equity_weight': 0.6, 'debt_weight': 0.4},
    'beta': 1.1,
    'risk_free_rate': 0.03,
    'market_risk_premium': 0.05,
}

MONEY_MARKET_SAMPLE = {
    'money_market': {
        'treasury_bills': 0.045,
        'commercial_paper': 0.05,
        'certificates_of_deposit': 0.048,
        'interbank_rates': 0.047,
        'repo_rates': 0.046,
        'liquidity': 'adequate',
    }
}

FINANCIAL_INSTRUMENTS_SAMPLE = {
    'financial_instruments': {
        'bonds': [{'name': 'Gov Bond', 'yield': 0.05}],
        'equities': [{'ticker': 'ABC', 'price': 12.5}],
        'derivatives': [{'type': 'option'}],
        'mutual_funds': [{'name': 'Growth Fund'}],
        'etf': [{'name': 'Market ETF'}],
        'commodities': [{'name': 'Gold'}],
    }
}

CREDIT_RISK_SAMPLE = {
    'credit_risk': {
        'credit_exposure': 5000000,
        'probability_of_default': 0.02,
        'loss_given_default': 0.45,
        'exposure_at_default': 4800000,
        'expected_loss': 43200,
        'counterparty': 'Borrower A',
        'default_risk': 'moderate',
    }
}

UNRELATED_SAMPLE = {
    'weather': {'temperature': 22, 'humidity': 40},
    'sports': {'team': 'None', 'score': 0},
}


class DatasetTypeRegistryTests(SimpleTestCase):
    def test_nine_dataset_types_registered(self):
        self.assertEqual(sorted(DATASET_TYPE_RULES.keys()), sorted(EXPECTED_DATASET_TYPES))

    def test_each_dataset_type_has_prompt_and_template(self):
        templates = DEFAULT_REPORT_PROMPT_CONFIG['templates']
        prompt_ids = {item['prompt_id'] for item in get_default_analysis_prompt_definitions()}
        for dataset_type, rule in DATASET_TYPE_RULES.items():
            self.assertIn(rule['prompt_id'], prompt_ids, dataset_type)
            self.assertIn(rule['template'], templates, dataset_type)
            self.assertTrue(rule['label'])
            self.assertGreaterEqual(len(rule['signals']), 2)


class DatasetValidationTests(SimpleTestCase):
    def test_annual_financial_single_year_accepted(self):
        ok, detected, error = _validate_dataset_type(SINGLE_YEAR_ANNUAL, 'annual_financial')
        self.assertTrue(ok)
        self.assertEqual(detected, 'annual_financial')
        self.assertIsNone(error)

    def test_annual_financial_multi_year_accepted(self):
        ok, detected, error = _validate_dataset_type(MULTI_YEAR_ANNUAL, 'annual_financial')
        self.assertTrue(ok)
        self.assertEqual(detected, 'annual_financial')
        self.assertIsNone(error)

    def test_unrelated_dataset_rejected_for_annual_financial(self):
        ok, detected, error = _validate_dataset_type(UNRELATED_SAMPLE, 'annual_financial')
        self.assertFalse(ok)
        self.assertIsNone(detected)
        self.assertIn('Unable to verify', error or '')

    def test_mismatch_rejects_wrong_selection(self):
        ok, detected, error = _validate_dataset_type(WACC_SAMPLE, 'money_market')
        self.assertFalse(ok)
        self.assertEqual(detected, 'wacc')
        self.assertIn('WACC', error or '')

    def test_existing_wacc_money_market_instruments_still_validate(self):
        for sample, dataset_type in (
            (WACC_SAMPLE, 'wacc'),
            (MONEY_MARKET_SAMPLE, 'money_market'),
            (FINANCIAL_INSTRUMENTS_SAMPLE, 'financial_instruments'),
            (CREDIT_RISK_SAMPLE, 'credit_risk'),
        ):
            ok, detected, error = _validate_dataset_type(sample, dataset_type)
            self.assertTrue(ok, f'{dataset_type}: {error}')
            self.assertEqual(detected, dataset_type)

    def test_invalid_dataset_type_rejected(self):
        ok, _, error = _validate_dataset_type(WACC_SAMPLE, 'not_a_type')
        self.assertFalse(ok)
        self.assertIn('Please select one dataset type', error or '')

    def test_infer_prefers_supported_type(self):
        self.assertEqual(_infer_dataset_type(WACC_SAMPLE), 'wacc')
        self.assertEqual(_infer_dataset_type(CREDIT_RISK_SAMPLE), 'credit_risk')
        self.assertEqual(_infer_dataset_type(SINGLE_YEAR_ANNUAL), 'annual_financial')


class AnnualFinancialPromptTests(SimpleTestCase):
    def test_annual_financial_master_prompt_registered(self):
        definitions = {item['prompt_id']: item for item in get_default_analysis_prompt_definitions()}
        annual = definitions[ANNUAL_FINANCIAL_ANALYSIS_ID]
        self.assertEqual(annual['recommended_sections'], ANNUAL_FINANCIAL_SECTIONS)
        self.assertIn('Annual Financial Master Prompt', ANNUAL_FINANCIAL_ANALYSIS_PROMPT)
        self.assertIn('Never invent', ANNUAL_FINANCIAL_ANALYSIS_PROMPT)

    def test_annual_financial_section_prompts_decompose(self):
        extracted = decompose_master_prompt_to_section_prompts(
            ANNUAL_FINANCIAL_ANALYSIS_PROMPT,
            ANNUAL_FINANCIAL_SECTIONS,
        )
        for section in ANNUAL_FINANCIAL_SECTIONS:
            self.assertIn(section, extracted)
            self.assertTrue(extracted[section].strip())

    def test_annual_financial_template_has_all_sections(self):
        template = DEFAULT_REPORT_PROMPT_CONFIG['templates']['annual_financial_report']
        self.assertEqual(template['sections'], ANNUAL_FINANCIAL_SECTIONS)

    def test_registry_resolves_annual_financial_template(self):
        registry = get_report_prompt_registry()
        options = registry.build_report_options({'template': 'annual_financial'})
        self.assertEqual(options['template'], 'annual_financial_report')
        self.assertEqual(options['sections'], ANNUAL_FINANCIAL_SECTIONS)

    def test_legacy_prompts_still_registered(self):
        prompt_ids = {item['prompt_id'] for item in get_default_analysis_prompt_definitions()}
        for prompt_id in (
            WACC_ANALYSIS_ID,
            MONEY_MARKET_ANALYSIS_ID,
            FINANCIAL_INSTRUMENTS_ANALYSIS_ID,
            CREDIT_RISK_ANALYSIS_ID,
        ):
            self.assertIn(prompt_id, prompt_ids)


class PromptPersistenceSmokeTests(TestCase):
    def test_ensure_prompt_defaults_seeds_annual_financial(self):
        from analytics.models import AnalysisPrompt
        from analytics.services.prompt_settings_store import (
            ensure_prompt_defaults,
            update_analysis_prompt_content,
        )

        ensure_prompt_defaults()
        prompt = AnalysisPrompt.objects.get(prompt_id=ANNUAL_FINANCIAL_ANALYSIS_ID)
        self.assertIn('Annual Financial', prompt.title)
        self.assertEqual(list(prompt.recommended_sections), ANNUAL_FINANCIAL_SECTIONS)

        updated = update_analysis_prompt_content(
            ANNUAL_FINANCIAL_ANALYSIS_ID,
            prompt.content + '\n# Custom Annual Note',
        )
        self.assertIn('Custom Annual Note', updated.content)

        reloaded = AnalysisPrompt.objects.get(prompt_id=ANNUAL_FINANCIAL_ANALYSIS_ID)
        self.assertIn('Custom Annual Note', reloaded.content)
