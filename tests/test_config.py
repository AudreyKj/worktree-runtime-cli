import tempfile
import unittest
from pathlib import Path
from unittest import mock

from worktree_runtime import config


class ConfigTests(unittest.TestCase):
    def load(self, contents):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, ".worktree-runtime.yml")
            path.write_text(contents)
            with mock.patch.object(config, "CONFIG_FILE", path):
                return config.load_config()

    def test_loads_valid_config(self):
        loaded = self.load(
            """
ports:
  api:
    start: 8000
    end: 8010
commands:
  api: python -m http.server
"""
        )
        self.assertEqual(loaded["ports"]["api"]["start"], 8000)

    def test_rejects_mismatched_services(self):
        with self.assertRaisesRegex(ValueError, "same services"):
            self.load(
                """
ports:
  api:
    start: 8000
    end: 8010
commands:
  web: npm run dev
"""
            )

    def test_rejects_invalid_port_range(self):
        with self.assertRaisesRegex(ValueError, "valid start/end range"):
            self.load(
                """
ports:
  api:
    start: 9000
    end: 8000
commands:
  api: python -m http.server
"""
            )


if __name__ == "__main__":
    unittest.main()
