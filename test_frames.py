#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow"]
# ///

"""Tests for scr-wrap --frame styles."""

import os
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCR_WRAP = os.path.join(os.path.dirname(__file__), "scr-wrap")


class TestFrameStyles(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.input_path = os.path.join(self.tmpdir, "input.png")
        img = Image.new("RGB", (800, 600), "red")
        img.save(self.input_path)

    def tearDown(self):
        for root, dirs, files in os.walk(self.tmpdir, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(self.tmpdir)

    def _run(self, *args, expect_ok=True):
        cmd = [SCR_WRAP, self.input_path] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if expect_ok:
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}\nstdout: {result.stdout}")
        return result

    def _size(self, filename):
        with Image.open(os.path.join(self.tmpdir, filename)) as img:
            return img.size

    def test_frame_default_same_as_omitted(self):
        out_default = os.path.join(self.tmpdir, "default.png")
        out_omitted = os.path.join(self.tmpdir, "omitted.png")
        self._run("-o", out_default, "--frame", "default")
        self._run("-o", out_omitted)
        self.assertEqual(self._size("default.png"), self._size("omitted.png"))
        self.assertEqual(self._size("default.png"), (800, 696))

    def test_frame_mac(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--frame", "mac")
        self.assertEqual(self._size("out.png"), (800, 696))

    def test_frame_browser_dark(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--frame", "browser-dark")
        self.assertEqual(self._size("out.png"), (800, 696))

    def test_frame_window(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--frame", "window")
        self.assertEqual(self._size("out.png"), (800, 696))

    def test_frame_no_browser_ignores_frame(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--no-browser", "--frame", "mac")
        self.assertEqual(self._size("out.png"), (800, 600))

    def test_frame_invalid_choice_rejected(self):
        result = self._run("--frame", "nonexistent", expect_ok=False)
        self.assertNotEqual(result.returncode, 0)

    def test_frame_out_dir_naming(self):
        outdir = os.path.join(self.tmpdir, "outdir")
        img2 = os.path.join(self.tmpdir, "img2.png")
        img = Image.new("RGB", (200, 100), "blue")
        img.save(img2)
        self._run(self.input_path, img2, "--out-dir", outdir, "--frame", "mac")
        expected1 = os.path.join(outdir, "input.mac.png")
        expected2 = os.path.join(outdir, "img2.mac.png")
        self.assertTrue(os.path.exists(expected1), f"Missing {expected1}")
        self.assertTrue(os.path.exists(expected2), f"Missing {expected2}")

    def test_frame_all_styles_produce_valid_output(self):
        for style in ["default", "mac", "browser-dark", "window"]:
            out = os.path.join(self.tmpdir, f"{style}.png")
            self._run("-o", out, "--frame", style)
            with Image.open(out) as img:
                self.assertEqual(img.size, (800, 696), f"Wrong size for {style}: {img.size}")


if __name__ == "__main__":
    unittest.main()
