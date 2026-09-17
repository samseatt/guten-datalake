"""Startup configuration and destructive test-database guard tests; no DB writes."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/database"))
from bootstrap_test_db import validate


class ConfigurationTests(unittest.TestCase):
    def test_missing_or_invalid_database_url_fails_without_exposing_credentials(self):
        for value in ("", "postgresql://user:secret_marker@localhost/db", "not_a_url_secret_marker"):
            with self.subTest(value=bool(value)):
                result = subprocess.run([sys.executable, "-B", "-c", "import app.database"],
                    cwd=ROOT, env=dict(os.environ, DATABASE_URL=value), capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("DATABASE_URL", result.stderr)
                self.assertNotIn("secret_marker", result.stderr)

    def test_database_guard_rejects_master_unrelated_and_unsafe_names(self):
        for name in ("", "guten_datalake", "vitaledge_test_1", "guten_test", "guten_x_test_a;drop", "guten_x_test_"+"a"*64):
            with self.subTest(name=name):
                with self.assertRaises(ValueError): validate(name)
        validate("guten_acceptance_test_abc123")
