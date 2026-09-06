import unittest
from unittest import mock

from worktree_runtime import ports


class PortTests(unittest.TestCase):
    def setUp(self):
        ports.allocated_ports.clear()
        ports.claimed_ports.clear()

    def test_allocates_first_available_port(self):
        with mock.patch.object(
            ports, "is_port_available", side_effect=[False, True]
        ):
            allocated = ports.allocate_port("/repo", "api", 8000, 8001)

        self.assertEqual(allocated, 8001)

    def test_does_not_allocate_same_port_twice(self):
        with mock.patch.object(ports, "is_port_available", return_value=True):
            first = ports.allocate_port("/repo", "api", 8000, 8001)
            second = ports.allocate_port("/repo", "web", 8000, 8001)

        self.assertEqual((first, second), (8000, 8001))

    def test_raises_when_range_is_exhausted(self):
        with mock.patch.object(ports, "is_port_available", return_value=False):
            with self.assertRaisesRegex(RuntimeError, "No available ports"):
                ports.allocate_port("/repo", "api", 8000, 8001)


if __name__ == "__main__":
    unittest.main()
