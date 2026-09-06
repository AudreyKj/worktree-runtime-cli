import unittest
from unittest import mock

from worktree_runtime import cli


class CliTests(unittest.TestCase):
    def test_partial_startup_failure_stops_started_processes(self):
        config = {
            "ports": {
                "frontend": {"start": 5000, "end": 5010},
                "backend": {"start": 8080, "end": 8090},
            },
            "commands": {
                "frontend": "frontend-command",
                "backend": "backend-command",
            },
        }
        frontend_process = mock.Mock(pid=123)

        with (
            mock.patch.object(cli, "load_config", return_value=config),
            mock.patch.object(
                cli.worktrees, "detect_current_worktree", return_value="/repo"
            ),
            mock.patch.object(cli.ports, "allocate_port", side_effect=[5000, 8080]),
            mock.patch.object(
                cli.runtime,
                "start_project",
                side_effect=[frontend_process, OSError("could not start")],
            ),
            mock.patch.object(cli.runtime, "stop_projects") as stop_projects,
        ):
            with self.assertRaisesRegex(OSError, "could not start"):
                cli.run()

        stop_projects.assert_called_once_with({"frontend": frontend_process})


if __name__ == "__main__":
    unittest.main()
