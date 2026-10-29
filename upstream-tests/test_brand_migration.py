import importlib.util
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "orchestrate.py"
SPEC = importlib.util.spec_from_file_location("orchestrate_brand_migration", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class BrandMigrationTests(unittest.TestCase):
    def test_migrates_saved_configuration_without_overwriting_new_files(self):
        with tempfile.TemporaryDirectory() as folder, mock.patch.dict(os.environ, {
            "APPDATA": folder,
            "ORQUESTRADOR_ORCHESTRATE_POLICY": "",
            "ALETHE_ORCHESTRATE_POLICY": "",
        }):
            legacy = Path(folder) / "Alethe"
            legacy.mkdir()
            (legacy / "alethe-orchestrate.json").write_text('{"onboarded":true}', encoding="utf-8")
            (legacy / "alethe-playbooks.yaml").write_text("profile: base\n", encoding="utf-8")
            (legacy / "alethe-prices.json").write_text('{"billing":{"codex":"subscription"}}', encoding="utf-8")
            (legacy / "alethe-usage.json").write_text('{"providers":{"codex":{}}}', encoding="utf-8")
            (legacy / "alethe-playbooks.html").write_text("<html>antigo</html>", encoding="utf-8")
            (legacy / "orchestrations").mkdir()
            (legacy / "orchestrations" / "modes.json").write_text('{"everywhere":null}', encoding="utf-8")
            current = Path(folder) / "Orquestrador"
            current.mkdir()
            (current / "orquestrador-prices.json").write_text('{"billing":{"codex":"api"}}', encoding="utf-8")

            policy = runner.default_policy_path()

            self.assertEqual(policy, current / "orquestrador-orchestrate.json")
            self.assertEqual(policy.read_text(encoding="utf-8"), '{"onboarded":true}')
            self.assertEqual((current / "orquestrador-playbooks.yaml").read_text(encoding="utf-8"), "profile: base\n")
            self.assertEqual((current / "orquestrador-prices.json").read_text(encoding="utf-8"), '{"billing":{"codex":"api"}}')
            self.assertEqual((current / "orquestrador-usage.json").read_text(encoding="utf-8"), '{"providers":{"codex":{}}}')
            self.assertEqual((current / "orquestrador-playbooks.html").read_text(encoding="utf-8"), "<html>antigo</html>")
            self.assertEqual((current / "orchestrations" / "modes.json").read_text(encoding="utf-8"), '{"everywhere":null}')
            self.assertTrue((legacy / "alethe-orchestrate.json").is_file())

    def test_doctor_first_run_copies_saved_files_and_keeps_the_legacy_folder(self):
        with tempfile.TemporaryDirectory() as folder, mock.patch.dict(os.environ, {
            "APPDATA": folder,
            "ORQUESTRADOR_ORCHESTRATE_POLICY": "",
            "ALETHE_ORCHESTRATE_POLICY": "",
        }):
            legacy = Path(folder) / "Alethe"
            legacy.mkdir()
            for basename, content in {
                "orchestrate.json": '{"version":1}',
                "playbooks.yaml": "version: 1\n",
                "prices.json": '{"models":{}}',
                "usage.json": '{"providers":{}}',
                "playbooks.html": "<html></html>",
            }.items():
                (legacy / f"alethe-{basename}").write_text(content, encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runner.main(["doctor"])
            self.assertEqual(code, 0)
            self.assertIsInstance(json.loads(output.getvalue()), dict)
            current = Path(folder) / "Orquestrador"
            for basename in ("orchestrate.json", "playbooks.yaml", "prices.json", "usage.json", "playbooks.html"):
                self.assertEqual(
                    (current / f"orquestrador-{basename}").read_bytes(),
                    (legacy / f"alethe-{basename}").read_bytes(),
                )

    def test_new_environment_override_wins_and_legacy_override_remains_available(self):
        with tempfile.TemporaryDirectory() as folder:
            new_path = Path(folder) / "new.json"
            legacy_path = Path(folder) / "old.json"
            with mock.patch.dict(os.environ, {
                "ORQUESTRADOR_ORCHESTRATE_POLICY": str(new_path),
                "ALETHE_ORCHESTRATE_POLICY": str(legacy_path),
            }):
                self.assertEqual(runner.default_policy_path(), new_path)
            with mock.patch.dict(os.environ, {
                "ORQUESTRADOR_ORCHESTRATE_POLICY": "",
                "ALETHE_ORCHESTRATE_POLICY": str(legacy_path),
            }):
                self.assertEqual(runner.default_policy_path(), legacy_path)

    def test_new_home_and_playbooks_environment_variables_take_priority(self):
        with tempfile.TemporaryDirectory() as folder:
            current = Path(folder) / "current"
            legacy = Path(folder) / "legacy"
            with mock.patch.dict(os.environ, {
                "ORQUESTRADOR_ORCHESTRATE_HOME": str(current),
                "ALETHE_ORCHESTRATE_HOME": str(legacy),
                "ORQUESTRADOR_ORCHESTRATE_PLAYBOOKS": str(current / "playbooks.yaml"),
                "ALETHE_ORCHESTRATE_PLAYBOOKS": str(legacy / "playbooks.yaml"),
            }):
                self.assertEqual(runner.orchestrations_home(), current)
                self.assertEqual(runner.user_playbooks_path(current / "policy.json"), current / "playbooks.yaml")
            with mock.patch.dict(os.environ, {
                "ORQUESTRADOR_ORCHESTRATE_HOME": "",
                "ALETHE_ORCHESTRATE_HOME": str(legacy),
                "ORQUESTRADOR_ORCHESTRATE_PLAYBOOKS": "",
                "ALETHE_ORCHESTRATE_PLAYBOOKS": str(legacy / "playbooks.yaml"),
            }):
                self.assertEqual(runner.orchestrations_home(), legacy)
                self.assertEqual(runner.user_playbooks_path(current / "policy.json"), legacy / "playbooks.yaml")


if __name__ == "__main__":
    unittest.main()
