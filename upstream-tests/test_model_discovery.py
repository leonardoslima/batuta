import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('discovery_runner',
    Path(__file__).resolve().parents[1] / 'scripts' / 'orchestrate.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ModelDiscoveryTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.policy = self.root / 'policy.json'
        self.codex = self.root / 'codex'
        self.codex.mkdir()
        patch = mock.patch.dict(os.environ, {'CODEX_HOME': str(self.codex)})
        patch.start()
        self.addCleanup(patch.stop)
        self.now = dt.datetime.now(dt.timezone.utc)

    def cache(self, models, fetched_at=None):
        (self.codex / 'models_cache.json').write_text(json.dumps({
            'fetched_at': fetched_at or self.now.isoformat(), 'models': models}), encoding='utf-8')

    def test_unpriced_terra_remains_a_candidate_with_its_efforts(self):
        self.cache([{'slug': 'gpt-6.1-terra', 'display_name': 'GPT-6.1 Terra',
            'visibility': 'list', 'default_reasoning_level': 'low',
            'supported_reasoning_levels': [{'effort': 'low'}, {'effort': 'high'}, {'effort': 'max'}]}])
        provider = runner.models_payload(self.policy, now=self.now)['providers']['codex']
        terra = next(m for m in provider['models'] if m['model'] == 'gpt-6.1-terra')
        self.assertTrue(terra['discovered'])
        self.assertTrue(terra['priceMissing'])
        self.assertEqual(terra['supportedEfforts'], ['low', 'high', 'max'])
        self.assertIn('gpt-6.1-terra', provider['discovery']['candidates'])
        self.assertIn('codex-cache', terra['inventorySources'])

    def test_price_catalog_is_not_account_discovery(self):
        self.cache([])
        provider = runner.models_payload(self.policy)['providers']['codex']
        priced = next(m for m in provider['models'] if not m['missing'])
        self.assertFalse(priced['discovered'])
        self.assertNotIn(priced['model'], provider['discovery']['candidates'])
        self.assertIn('prices', priced['inventorySources'])

    def test_hidden_models_are_not_presented_as_visible_candidates(self):
        self.cache([{'slug': 'example-hidden', 'visibility': 'hide'},
                    {'slug': 'example-visible', 'visibility': 'list'}])
        provider = runner.models_payload(self.policy)['providers']['codex']
        self.assertNotIn('example-hidden', provider['discovery']['candidates'])
        self.assertIn('example-visible', provider['discovery']['candidates'])

    def test_cache_freshness_and_origin_are_explicit(self):
        self.cache([{'slug': 'example'}], (self.now-dt.timedelta(days=2)).isoformat())
        discovery = runner.models_payload(self.policy, now=self.now)['providers']['codex']['discovery']
        self.assertTrue(discovery['stale'])
        self.assertEqual(discovery['source'], str(self.codex / 'models_cache.json'))
        self.assertFalse(discovery['accountAccessVerified'])

    def test_confirmed_account_models_are_included_without_price(self):
        (self.root / runner.USER_PRICES_FILE).write_text(json.dumps({'accounts': {'codex': {
            'models': ['example-account-only'], 'confirmed': True,
            'source': 'user', 'observedAt': self.now.isoformat()}}}), encoding='utf-8')
        provider = runner.models_payload(self.policy)['providers']['codex']
        model = next(m for m in provider['models'] if m['model'] == 'example-account-only')
        self.assertTrue(model['discovered'])
        self.assertIn('confirmed-account', model['inventorySources'])
        self.assertIn('example-account-only', provider['discovery']['candidates'])


if __name__ == '__main__':
    unittest.main()
