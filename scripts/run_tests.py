"""Run the integration suite, retaining text and machine-readable results."""
import json
import os
from pathlib import Path
import sys
import time
import unittest
import uuid

root = Path(__file__).resolve().parents[1]
os.chdir(root)
artifacts = Path(os.environ.get("TEST_ARTIFACTS_DIR") or root / "test-results" / (time.strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8])).resolve()
artifacts.mkdir(parents=True, exist_ok=True)
os.environ["TEST_ARTIFACTS_DIR"] = str(artifacts)
started = time.monotonic()
with (artifacts / "api-results.txt").open("w") as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.discover(str(root / "tests")))
summary = dict(tests=result.testsRun, failures=[dict(test=str(t), detail=d) for t,d in result.failures],
               errors=[dict(test=str(t), detail=d) for t,d in result.errors], skipped=[str(t) for t,_ in result.skipped],
               seconds=round(time.monotonic()-started, 2), passed=result.wasSuccessful())
(artifacts / "api-results.json").write_text(json.dumps(summary, indent=2) + "\n")
print((artifacts / "api-results.txt").read_text())
print(f"API reports: {artifacts}")
sys.exit(0 if result.wasSuccessful() else 1)
