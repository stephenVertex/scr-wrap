#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# ///

"""Tests for the agent-facing ``scr-wrap prime`` command."""

import os
import subprocess
import tempfile
import unittest


SCR_WRAP = os.path.join(os.path.dirname(__file__), "scr-wrap")


class TestPrimeCommand(unittest.TestCase):
    def _run(self, *args, cwd=None):
        return subprocess.run(
            [SCR_WRAP, *args],
            capture_output=True,
            text=True,
            cwd=cwd,
        )

    def test_prime_prints_compact_agent_guide_without_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self._run("prime", cwd=tmpdir)
            files_created = os.listdir(tmpdir)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(files_created, [])
        for section in ("What it does", "Command surface", "Conventions and gotchas"):
            self.assertIn(section, result.stdout)
        for option in ("--out-dir", "--frame", "--numbered", "--from-clipboard"):
            self.assertIn(option, result.stdout)
        self.assertNotIn("Input file(s) required", result.stdout)

    def test_prime_does_not_replace_normal_help(self):
        result = self._run("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: scr-wrap", result.stdout)
        self.assertIn("--numbered STUB", result.stdout)


if __name__ == "__main__":
    unittest.main()
