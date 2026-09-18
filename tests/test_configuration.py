"""Startup configuration and destructive test-database guard tests; no DB writes."""
import os
from pathlib import Path
import subprocess
import tempfile
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

    def test_secret_file_configuration_and_conflicting_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "database_url"
            path.write_text("postgresql+asyncpg://guten_app:test_secret@postgres/guten_compose_test_local\n")
            env = dict(os.environ, DATABASE_URL="", DATABASE_URL_FILE=str(path))
            result = subprocess.run([sys.executable, "-B", "-c", "from app.database import parsed_url; assert parsed_url.database == 'guten_compose_test_local'"], cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            env["DATABASE_URL"] = "postgresql+asyncpg:///guten_other_test_db"
            result = subprocess.run([sys.executable, "-B", "-c", "import app.database"], cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not both", result.stderr)
            self.assertNotIn("test_secret", result.stderr)

    def test_bad_tls_ca_and_conflicting_url_options_fail_closed(self):
        base = "postgresql+asyncpg://user:secret_marker@postgres/guten_test"
        for url, ca, message in ((base, "/no/such/ca.crt", "Could not load DATABASE_SSL_CA_FILE"),
                                 (base + "?ssl=disable", "/no/such/ca.crt", "SSL URL options")):
            result = subprocess.run([sys.executable, "-B", "-c", "import app.database"],
                cwd=ROOT, env=dict(os.environ, DATABASE_URL=url, DATABASE_URL_FILE="",
                                  DATABASE_SSL_CA_FILE=ca), capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)
            self.assertNotIn("secret_marker", result.stderr)
