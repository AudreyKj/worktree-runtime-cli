import unittest
from unittest import mock

from worktree_runtime import runtime


class RuntimeTests(unittest.TestCase):
    def test_service_port_variable(self):
        self.assertEqual(runtime.service_port_variable("api-server"), "API_SERVER_PORT")

    @mock.patch.object(runtime.subprocess, "Popen")
    def test_start_project_sets_port_environment(self, popen):
        runtime.start_project(
            "python -m server",
            8000,
            {"api-server": 8000, "web": 5000},
        )

        _, kwargs = popen.call_args
        self.assertEqual(kwargs["env"]["PORT"], "8000")
        self.assertEqual(kwargs["env"]["API_SERVER_PORT"], "8000")
        self.assertEqual(kwargs["env"]["WEB_PORT"], "5000")
        self.assertTrue(kwargs["start_new_session"])


if __name__ == "__main__":
    unittest.main()
