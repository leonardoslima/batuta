import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'orchestrate.py'
spec = importlib.util.spec_from_file_location('account_plans_runner', SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class AccountPlansTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.policy = self.root / 'policy.json'
        self.now = dt.datetime.now(dt.timezone.utc)
        patch = mock.patch.dict(os.environ, {'CODEX_HOME': str(self.root / 'codex')})
        patch.start()
        self.addCleanup(patch.stop)

    def configure(self, plan='small', **extra):
        account = {'plan': plan, 'source': 'user', 'observedAt': self.now.isoformat(),
                   'confirmed': True, **extra}
        (self.root / runner.USER_PRICES_FILE).write_text(json.dumps({
            'billing': {'codex': 'subscription'}, 'accounts': {'codex': account}}), encoding='utf-8')

    def reading(self, plan=None, percent=20):
        value = {'provider': 'codex', 'source': 'fixture', 'observedAt': self.now.isoformat(),
                 'windows': {'5h': {'usedPercent': percent,
                     'resetsAt': (self.now + dt.timedelta(hours=2)).isoformat()}}}
        if plan:
            value['accountObservation'] = {'plan': plan, 'source': 'fixture',
                                           'observedAt': self.now.isoformat()}
        runner.save_usage(self.policy, value)

    def test_legacy_billing_and_unknown_account(self):
        (self.root / runner.USER_PRICES_FILE).write_text(
            json.dumps({'billing': {'codex': 'subscription'}}), encoding='utf-8')
        account = runner.models_payload(self.policy)['providers']['codex']['account']
        self.assertIsNone(account['plan'])
        self.assertEqual(account['billing'], 'subscription')
        self.assertIn('plan', account['missing'])

    def test_configuration_is_exposed_without_turning_price_into_capacity(self):
        self.configure(price={'amount': 20, 'currency': 'USD', 'period': 'month'},
                       extraUsageEnabled=True, extraUsageAuthorized=False,
                       consumption='preserve', models=['example-model'])
        account = runner.usage_payload(self.policy, refresh=False)['providers']['codex']['account']
        self.assertEqual(account['plan'], 'small')
        self.assertEqual(account['price']['amount'], 20)
        self.assertFalse(account['extraUsageAuthorized'])
        self.assertEqual(account['limits'], {})
        self.assertEqual(account['consumption'], 'preserve')

    def test_codex_discovers_only_explicit_plan_type_and_does_not_write_preferences(self):
        folder = self.root / 'codex' / 'sessions' / '2026' / '10' / '29'
        folder.mkdir(parents=True)
        event = {'timestamp': self.now.isoformat(), 'payload': {'rate_limits': {
            'plan_type': 'example-plan', 'primary': {'used_percent': 20,
            'window_minutes': 300, 'resets_at': (self.now + dt.timedelta(hours=2)).timestamp()}}}}
        path = folder / 'rollout-example.jsonl'
        path.write_text(json.dumps(event), encoding='utf-8')
        account = runner.usage_payload(self.policy)['providers']['codex']['account']
        self.assertEqual(account['plan'], 'example-plan')
        self.assertFalse(account['confirmed'])
        self.assertIsNone(account['price'])
        self.assertFalse((self.root / runner.USER_PRICES_FILE).exists())
        del event['payload']['rate_limits']['plan_type']
        path.write_text(json.dumps(event), encoding='utf-8')
        self.assertNotIn('accountObservation', runner.codex_quota())

    def test_conflicting_observation_preserves_confirmed_preferences(self):
        self.configure()
        self.reading('large')
        account = runner.usage_payload(self.policy, refresh=False)['providers']['codex']['account']
        self.assertTrue(account['conflict'])
        self.assertEqual(account['configuredPlan'], 'small')
        self.assertEqual(account['plan'], 'large')
        self.assertEqual(runner.load_prices(self.policy)['accounts']['codex']['plan'], 'small')

    def test_invalid_account_values_fail_at_boundary(self):
        for bad in [dict(price={'amount': -1, 'currency': 'USD', 'period': 'month'}),
                    dict(extraUsageAuthorized='yes'), dict(models='all'),
                    dict(observedAt='yesterday'), dict(consumption='unlimited')]:
            with self.subTest(bad=bad):
                self.configure(**bad)
                with self.assertRaises(runner.PlanError):
                    runner.load_prices(self.policy)

    def test_forecast_does_not_reuse_samples_after_plan_change(self):
        self.configure()
        self.reading()
        context = runner.saved_usage(self.policy)['codex']['accountContext']
        samples = [{'provider': 'codex', 'model': 'test', 'workers': 1,
                    'observedAt': self.now.isoformat(), 'perWorker': {'5h': 10},
                    'accountContext': context} for _ in range(2)]
        runner.save_quota_samples(self.policy, samples)
        workers = [{'id': 'a', 'provider': 'codex', 'model': 'test'}]
        def projection():
            usage = runner.usage_payload(self.policy, refresh=False)
            return runner.quota_forecast(workers, self.policy, usage)[0]['codex']['windows']['5h']['projectedPercent']
        self.assertEqual(projection(), 10)
        self.configure('large')
        self.assertIsNone(projection())

    def test_no_sample_is_recorded_across_a_plan_change(self):
        self.configure()
        self.reading(percent=20)
        before = runner.saved_usage(self.policy)
        self.configure('large')
        self.now += dt.timedelta(minutes=1)
        self.reading(percent=30)
        samples = runner.quota_samples([{'id': 'a', 'provider': 'codex', 'model': 'test'}],
            [{'id': 'a', 'status': 'done'}], before, runner.saved_usage(self.policy),
            self.now - dt.timedelta(minutes=1))
        self.assertEqual(samples, [])

    def test_preview_explains_account_and_unverified_model(self):
        self.configure(models=['allowed'], extraUsageEnabled=True)
        preview = runner.preview_usage_cost([{'id': 'a', 'provider': 'codex',
            'model': 'other', 'estimatedPromptTokens': 10}], self.policy)
        self.assertEqual(preview['accounts']['codex']['plan'], 'small')
        self.assertTrue(any('other' in warning for warning in preview['warnings']))
        self.assertTrue(any('extra' in warning.lower() for warning in preview['warnings']))

    def test_refreshing_identical_reading_does_not_relabel_its_original_plan(self):
        self.configure()
        self.reading(percent=20)
        before = runner.saved_usage(self.policy)['codex']
        self.configure('large')
        self.reading(percent=20)
        self.assertEqual(runner.saved_usage(self.policy)['codex']['accountContext'], before['accountContext'])
        self.now += dt.timedelta(minutes=1)
        self.reading(percent=40)
        samples = runner.quota_samples([{'id': 'a', 'provider': 'codex', 'model': 'test'}],
            [{'id': 'a', 'status': 'done'}], {'codex': before}, runner.saved_usage(self.policy),
            self.now - dt.timedelta(minutes=1))
        self.assertEqual(samples, [])

    def test_missing_plan_in_later_reading_preserves_conflict_and_evidence_age(self):
        self.configure(models=['old-plan-model'], extraUsageAuthorized=True)
        self.reading('large')
        original = runner.saved_usage(self.policy)['codex']['accountObservation']
        self.now += dt.timedelta(minutes=35)
        self.reading(percent=21)
        usage = runner.usage_payload(self.policy, refresh=False, now=self.now)
        account = usage['providers']['codex']['account']
        self.assertEqual(account['plan'], 'large')
        self.assertTrue(account['conflict'])
        self.assertEqual(account['models'], [])
        self.assertFalse(account['extraUsageAuthorized'])
        self.assertTrue(account['observationStale'])
        self.assertEqual(runner.saved_usage(self.policy)['codex']['accountObservation'], original)

    def test_forecast_requires_reading_from_current_context(self):
        self.configure()
        self.reading()
        self.configure('large')
        current = runner.usage_payload(self.policy, refresh=False)['providers']['codex']['accountContext']
        runner.save_quota_samples(self.policy, [{'provider': 'codex', 'model': 'test',
            'workers': 1, 'observedAt': self.now.isoformat(), 'accountContext': current,
            'perWorker': {'5h': 10}} for _ in range(2)])
        workers = [{'id': 'a', 'provider': 'codex', 'model': 'test'}]
        usage = runner.usage_payload(self.policy, refresh=False)
        forecast, _ = runner.quota_forecast(workers, self.policy, usage)
        self.assertIsNone(forecast['codex']['windows']['5h']['projectedPercent'])

    def test_context_ignores_date_and_consumption_preference(self):
        self.configure()
        self.reading()
        initial = runner.usage_payload(self.policy, refresh=False)['providers']['codex']['accountContext']
        self.now += dt.timedelta(minutes=1)
        self.configure(consumption='preserve')
        current = runner.usage_payload(self.policy, refresh=False)['providers']['codex']['accountContext']
        self.assertEqual(current, initial)


if __name__ == '__main__':
    unittest.main()
