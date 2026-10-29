"""Offline onboarding through public commands; approval is a fixture step, not NLP."""
import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("onboarding_flow_runner", ROOT / "scripts" / "orchestrate.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class OnboardingFlowTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="onboarding-offline-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.policy = self.root / "policy.json"
        self.codex = self.root / "codex"
        self.codex.mkdir()
        self.prices = self.root / runner.USER_PRICES_FILE
        self.playbooks = self.root / runner.USER_PLAYBOOKS_FILE
        self.now = dt.datetime.now(dt.timezone.utc)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.dict(os.environ, {
            "CODEX_HOME": str(self.codex),
            "ORQUESTRADOR_ORCHESTRATE_HOME": str(self.root / "home"),
            "ALETHE_ORCHESTRATE_HOME": str(self.root / "home"),
            "ORQUESTRADOR_ORCHESTRATE_POLICY": str(self.policy),
            "ALETHE_ORCHESTRATE_POLICY": str(self.policy),
            "ORQUESTRADOR_ORCHESTRATE_PLAYBOOKS": str(self.playbooks),
            "ALETHE_ORCHESTRATE_PLAYBOOKS": str(self.playbooks),
        }))
        # Replace the bundled price source with deterministic, explicitly fictitious data.
        bundled_prices = self.root / "fixture-prices.json"
        self.write(bundled_prices, {"version": 1, "currency": "USD", "unit": "per 1M tokens",
            "models": {"claude/fixture-alternative": self.price(2, 6)}})
        self.stack.enter_context(mock.patch.object(runner, "PRICES_FILE", str(bundled_prices)))
        self.probe = self.stack.enter_context(mock.patch.object(runner, "probe_provider", side_effect=self.fake_probe))
        self.auth = self.stack.enter_context(mock.patch.object(runner, "provider_logged_in", return_value=None))
        self.stack.enter_context(mock.patch.object(runner.shutil, "which", side_effect=lambda name: str(self.root / (name + ".fake")) if name in ("codex", "claude") else None))
        self.process = self.stack.enter_context(mock.patch.object(runner.subprocess, "run", side_effect=AssertionError("No CLI execution during onboarding")))
        self.launch = self.stack.enter_context(mock.patch.object(runner.subprocess, "Popen", side_effect=AssertionError("No worker launch during onboarding")))
        self.socket = self.stack.enter_context(mock.patch("socket.socket", side_effect=AssertionError("Offline fixture: network forbidden")))

    def fake_probe(self, provider):
        installed = provider in ("codex", "claude")
        executable = str(self.root / (provider + ".fake")) if installed else None
        return {"provider": provider, "installed": installed, "executable": executable,
            "launch": [executable] if installed else None, "version": "fixture-only" if installed else None,
            "capabilities": runner.PROVIDER_CAPABILITIES[provider]}

    def price(self, input_price, output_price):
        return {"input": input_price, "output": output_price, "asOf": self.now.date().isoformat(),
            "source": "https://fixtures.invalid/pricing"}

    def write(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*") if path.is_file()}

    def call(self, *args, success=True, as_json=True):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.main([str(arg) for arg in args])
        self.assertEqual(code, 0 if success else 2, err.getvalue())
        return json.loads(out.getvalue()) if as_json and success else out.getvalue()

    def read(self, command):
        return self.call(command, "--policy", self.policy)

    def plan(self, provider="codex", **extra):
        path = self.root / "plan.json"
        self.write(path, {"version": 1, "strategy": "economy", "workers": [{
            "id": "inspect", "provider": provider, "cwd": str(self.root),
            "task": "Inspect the supplied offline fixture.", **extra}]})
        return path

    def preview(self, path):
        result = self.call("validate", path, "--policy", self.policy)
        self.assertTrue(result["valid"])
        preview = self.call("dry-run", path, "--policy", self.policy)
        self.assertTrue(preview["dryRun"])
        self.process.assert_not_called()
        self.launch.assert_not_called()
        self.socket.assert_not_called()
        return preview

    def cache(self, model="fixture-new-model", days_old=0, metadata=True):
        entry = {"slug": model, "visibility": "list"}
        if metadata:
            entry.update(default_reasoning_level="low", supported_reasoning_levels=[
                {"effort": "low"}, {"effort": "high"}, {"effort": "max"}])
        self.write(self.codex / "models_cache.json", {"fetched_at": (self.now - dt.timedelta(days=days_old)).isoformat(), "models": [entry]})

    def approve_and_configure(self, model="fixture-new-model", price=True):
        # Explicit test-script approval: only now may the fixture persist proposed choices.
        self.call("playbook", "--init", "--policy", self.policy, as_json=False)
        text = self.playbooks.read_text(encoding="utf-8")
        self.assertIn("    codex: {}", text)
        self.playbooks.write_text(text.replace("    codex: {}", "    codex: { model: " + model + ", effort: high }", 1), encoding="utf-8")
        self.write(self.prices, {"models": {"codex/" + model: self.price(3, 9)} if price else {},
            "billing": {"codex": "subscription", "claude": "api"},
            "accounts": {"codex": {"plan": "fixture-plan", "source": "offline-user-fixture",
                "observedAt": self.now.isoformat(), "confirmed": True, "models": [model],
                "extraUsageEnabled": True, "extraUsageAuthorized": False, "consumption": "preserve"}}})
        return self.call("policy", "set", "economy", "--file", self.policy,
            "--backend", "skill", "--provider-switch", "never", "--provider-order", "claude", "codex",
            "--conserve-providers", "codex", "--max-workers", "2", "--max-concurrent", "1", "--max-calls", "2")

    def test_initial_discovery_is_read_only_then_approved_choices_are_reloaded(self):
        self.cache()
        path = self.plan()
        before = self.snapshot()
        doctor = self.read("doctor")
        self.assertFalse(doctor["policy"]["exists"])
        self.assertFalse(doctor["policy"]["configured"])
        self.assertEqual(doctor["installedProviders"], [p for p in runner.BUILTIN_PROVIDERS if p in ("codex", "claude")])
        self.assertTrue(all(p["loggedIn"] is None for p in doctor["providers"]))
        models = self.read("models")
        candidate = next(m for m in models["providers"]["codex"]["models"] if m["model"] == "fixture-new-model")
        self.assertTrue(candidate["priceMissing"])
        self.assertEqual(candidate["supportedEfforts"], ["low", "high", "max"])
        self.assertIn("fixture-new-model", models["providers"]["codex"]["discovery"]["candidates"])
        unconfigured = self.preview(path)["workers"][0]
        self.assertIsNone(unconfigured["model"])
        self.assertIsNone(unconfigured["effort"])
        self.assertEqual(self.snapshot(), before)

        self.approve_and_configure()
        persisted = self.snapshot()
        self.assertTrue(self.read("doctor")["policy"]["configured"])
        saved = self.call("policy", "show", "--file", self.policy)["policy"]
        self.assertEqual(saved, json.loads(self.policy.read_text(encoding="utf-8")))
        self.assertEqual(saved["providerSwitch"], "never")
        reloaded = self.read("models")
        candidate = next(m for m in reloaded["providers"]["codex"]["models"] if m["model"] == "fixture-new-model")
        self.assertEqual((candidate["input"], candidate["output"]), (3, 9))
        self.assertFalse(reloaded["pricingEvidence"]["networkChecked"])
        self.assertTrue(reloaded["pricingEvidence"]["requiresOfficialResearch"])
        self.assertEqual(candidate["source"], "https://fixtures.invalid/pricing")
        preview = self.preview(path)
        worker = preview["workers"][0]
        self.assertEqual((worker["provider"], worker["model"], worker["effort"]), ("codex", "fixture-new-model", "high"))
        self.assertFalse(worker["switched"])
        self.assertEqual(preview["budget"]["maxCalls"], 2)
        self.assertEqual(preview["maxConcurrent"], 1)
        self.assertAlmostEqual(worker["listPriceEstimateUsd"], worker["estimatedPromptTokens"] * 3 / 1_000_000)
        self.assertEqual(preview["accounts"]["codex"]["plan"], "fixture-plan")
        self.assertFalse(preview["accounts"]["codex"]["extraUsageAuthorized"])
        self.assertEqual(self.snapshot(), persisted)

    def test_reconfiguration_preserves_explicit_restrictions_and_refuses_overwrite(self):
        self.cache()
        self.approve_and_configure()
        previous = json.loads(self.policy.read_text(encoding="utf-8"))
        choices = (self.prices.read_bytes(), self.playbooks.read_bytes())
        self.read("doctor")
        self.read("models")
        self.call("playbook", "--init", "--policy", self.policy, success=False, as_json=False)
        updated = self.call("policy", "set", "--file", self.policy, "--max-calls", "1")["policy"]
        expected = {**previous, "budget": {**previous["budget"], "maxCalls": 1}}
        self.assertEqual(updated, expected)
        self.assertEqual((self.prices.read_bytes(), self.playbooks.read_bytes()), choices)
        preview = self.preview(self.plan())
        self.assertEqual(preview["budget"]["maxCalls"], 1)
        self.assertEqual(preview["workers"][0]["model"], "fixture-new-model")
        self.assertEqual(preview["workers"][0]["effort"], "high")
        auto = self.preview(self.plan("auto"))["workers"][0]
        self.assertEqual(auto["provider"], "claude")
        self.assertIsNone(auto["model"])
        self.assertIsNone(auto["effort"])

    def test_new_unpriced_model_and_supported_effort_survive_persistence(self):
        self.cache()
        self.approve_and_configure(price=False)
        models = self.read("models")["providers"]["codex"]
        new = next(m for m in models["models"] if m["model"] == "fixture-new-model")
        self.assertTrue(new["discovered"])
        self.assertTrue(new["priceMissing"])
        self.assertIn("high", new["supportedEfforts"])
        self.assertIn("confirmed-account", new["inventorySources"])
        preview = self.preview(self.plan())
        self.assertEqual(preview["workers"][0]["model"], "fixture-new-model")
        self.assertEqual(preview["workers"][0]["effort"], "high")
        self.assertIsNone(preview["workers"][0]["listPriceEstimateUsd"])
        self.assertIsNone(preview["totals"]["listPriceEstimateUsd"])

    def test_missing_or_stale_cache_and_optional_unknowns_do_not_invent_access(self):
        for state in ("missing", "stale"):
            with self.subTest(cache=state):
                if state == "stale":
                    self.cache(days_old=3, metadata=False)
                path = self.plan()
                before = self.snapshot()
                doctor = self.read("doctor")
                self.assertTrue(doctor["policy"]["valid"])
                models = self.read("models")
                codex = models["providers"]["codex"]
                self.assertTrue(codex["discovery"]["stale"])
                self.assertFalse(codex["discovery"]["accountAccessVerified"])
                self.assertIsNone(codex["account"]["plan"])
                self.assertIsNone(codex["account"]["price"])
                self.assertEqual(codex["account"]["limits"], {})
                if state == "missing":
                    self.assertIsNone(codex["discovery"]["observedAt"])
                    self.assertEqual(codex["discovery"]["candidates"], [])
                else:
                    self.assertIn("fixture-new-model", codex["discovery"]["candidates"])
                    model = next(m for m in codex["models"] if m["model"] == "fixture-new-model")
                    self.assertEqual(model["supportedEfforts"], [])
                    self.assertIsNone(model["defaultEffort"])
                preview = self.preview(path)
                self.assertIsNone(preview["totals"]["listPriceEstimateUsd"])
                self.assertTrue(doctor["usage"]["providers"]["codex"]["missing"])
                self.assertEqual(self.snapshot(), before)

    def test_alternative_provider_and_custom_cli_preview_without_execution(self):
        self.call("policy", "set", "economy", "--file", self.policy, "--provider-order", "claude", "codex", "--provider-switch", "ask")
        self.call("playbook", "--init", "--policy", self.policy, as_json=False)
        text = self.playbooks.read_text(encoding="utf-8")
        self.playbooks.write_text(text.replace("    claude: {}", "    claude: { model: fixture-alternative, effort: high }", 1), encoding="utf-8")
        before = self.snapshot()
        models = self.read("models")["providers"]["claude"]
        priced = next(m for m in models["models"] if m["model"] == "fixture-alternative")
        self.assertFalse(priced["discovered"])
        self.assertNotIn("fixture-alternative", models["discovery"]["candidates"])
        self.assertIsNone(models["account"]["plan"])
        self.assertEqual(self.snapshot(), before)
        alternative = self.preview(self.plan("auto"))["workers"][0]
        self.assertEqual((alternative["provider"], alternative["model"], alternative["effort"]), ("claude", "fixture-alternative", "high"))
        custom = self.preview(self.plan("custom", command=sys.executable,
            args=["fixture_cli.py", "--model", "custom-fixture", "--effort", "max"], outputFormat="text"))["workers"][0]
        self.assertEqual((custom["provider"], custom["model"], custom["effort"]), ("custom", "custom-fixture", "max"))
        self.assertEqual(custom["command"], Path(sys.executable).stem)
        self.assertIsNone(custom["listPriceEstimateUsd"])


if __name__ == "__main__":
    unittest.main()
