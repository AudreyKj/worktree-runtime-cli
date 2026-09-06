import tempfile
import unittest
from pathlib import Path
from unittest import mock

from worktree_runtime import state


class StateTests(unittest.TestCase):
    def test_save_and_load_state(self):
        with tempfile.TemporaryDirectory() as directory:
            state_file = Path(directory, "state.json")
            with mock.patch.object(state, "STATE_FILE", state_file):
                state.save_state("/repo", {"api": 8000}, {"api": 123})
                loaded = state.load_state()

        self.assertEqual(
            loaded["/repo"],
            {"ports": {"api": 8000}, "pids": {"api": 123}},
        )


if __name__ == "__main__":
    unittest.main()
