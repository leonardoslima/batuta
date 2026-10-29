import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('research_defaults_runner',
    Path(__file__).resolve().parents[1] / 'scripts' / 'orchestrate.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ResearchDefaultsTest(unittest.TestCase):
    def test_unconfigured_profiles_do_not_select_model_or_effort(self):
        data = runner.parse_playbooks_yaml(runner.bundled_playbooks_path().read_text(encoding='utf-8'))
        for tier in data['tiers'].values():
            for choice in tier.values():
                self.assertEqual(choice, {}, 'A tier must be resolved from research, not a bundled model or effort')
        for profile in data['profiles'].values():
            self.assertNotIn('tiers', profile)
        for book in data['playbooks'].values():
            for phase in book['phases']:
                self.assertNotIn('model', phase)
                self.assertNotIn('effort', phase)
                self.assertNotIn('provider', phase)
                for rule in phase.get('rules', []):
                    self.assertNotIn('model', rule['use'])
                    self.assertNotIn('effort', rule['use'])
                    self.assertNotIn('provider', rule['use'])
                    conditions = rule['if'] if isinstance(rule['if'], list) else [rule['if']]
                    self.assertFalse(any(condition.startswith(('claude-', 'codex-')) for condition in conditions))

    def test_unconfigured_worker_has_no_hidden_reasoning_downgrade(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with mock.patch.object(runner, 'effective_playbooks_path', return_value=runner.bundled_playbooks_path()):
                raw = {'version': 1, 'strategy': 'economy', 'workers': [{
                    'id': 'one', 'provider': 'codex', 'cwd': folder, 'task': 'Inspect a file.'}]}
                worker = runner.validate_plan(raw, root/'plan.json', policy_path=root/'policy.json')['workers'][0]
                self.assertIsNone(worker['model'])
                self.assertIsNone(worker['effort'])

    def test_local_price_table_is_not_presented_as_live_research(self):
        with tempfile.TemporaryDirectory() as folder:
            payload = runner.models_payload(Path(folder)/'policy.json')
            self.assertFalse(payload['pricingEvidence']['networkChecked'])
            self.assertTrue(payload['pricingEvidence']['requiresOfficialResearch'])


if __name__ == '__main__':
    unittest.main()
