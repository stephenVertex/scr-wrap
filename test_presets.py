#!/usr/bin/env python3
"""Tests for scr-wrap --preset sizing."""

import os
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCR_WRAP = os.path.join(os.path.dirname(__file__), "scr-wrap")


class TestPresetSizing(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.input_path = os.path.join(self.tmpdir, "input.png")
        img = Image.new("RGB", (800, 600), "red")
        img.save(self.input_path)

    def tearDown(self):
        for f in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)

    def _run(self, *args):
        cmd = [SCR_WRAP, self.input_path] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

    def _size(self, filename):
        with Image.open(os.path.join(self.tmpdir, filename)) as img:
            return img.size

    def test_preset_x(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--preset", "x")
        self.assertEqual(self._size("out.png"), (1600, 900))

    def test_preset_linkedin(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--preset", "linkedin")
        self.assertEqual(self._size("out.png"), (1200, 627))

    def test_preset_og(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--preset", "og")
        self.assertEqual(self._size("out.png"), (1200, 630))

    def test_preset_square(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--preset", "square")
        self.assertEqual(self._size("out.png"), (1080, 1080))

    def test_preset_thumb(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--preset", "thumb")
        self.assertEqual(self._size("out.png"), (400, 300))

    def test_preset_with_background(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--preset", "square", "-b", "gradient")
        self.assertEqual(self._size("out.png"), (1080, 1080))

    def test_preset_no_browser(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--preset", "og", "--no-browser")
        self.assertEqual(self._size("out.png"), (1200, 630))

    def test_no_preset_uses_original_size(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out)
        # 800x600 + 96px frame height = 800x696
        self.assertEqual(self._size("out.png"), (800, 696))


if __name__ == "__main__":
    unittest.main()
