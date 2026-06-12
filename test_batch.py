#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow"]
# ///

"""Tests for scr-wrap batch processing (--out-dir, summary, naming)."""

import os
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCR_WRAP = os.path.join(os.path.dirname(__file__), "scr-wrap")


class TestBatchProcessing(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.outdir = os.path.join(self.tmpdir, "outdir")
        self.img1 = os.path.join(self.tmpdir, "img1.png")
        self.img2 = os.path.join(self.tmpdir, "img2.png")
        img = Image.new("RGB", (800, 600), "red")
        img.save(self.img1)
        img = Image.new("RGB", (800, 600), "blue")
        img.save(self.img2)

    def tearDown(self):
        for root, dirs, files in os.walk(self.tmpdir, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(self.tmpdir)

    def _run(self, *args, expect_ok=True):
        cmd = [SCR_WRAP] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if expect_ok:
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        return result

    def test_out_dir_creates_directory(self):
        self.assertFalse(os.path.exists(self.outdir))
        self._run(self.img1, self.img2, "--out-dir", self.outdir)
        self.assertTrue(os.path.exists(self.outdir))

    def test_out_dir_consistent_naming(self):
        self._run(self.img1, self.img2, "--out-dir", self.outdir)
        expected1 = os.path.join(self.outdir, "img1.wrapped.png")
        expected2 = os.path.join(self.outdir, "img2.wrapped.png")
        self.assertTrue(os.path.exists(expected1), f"Missing {expected1}")
        self.assertTrue(os.path.exists(expected2), f"Missing {expected2}")

    def test_out_dir_no_browser_suffix(self):
        self._run(self.img1, self.img2, "--out-dir", self.outdir, "--no-browser")
        expected1 = os.path.join(self.outdir, "img1.effects.png")
        expected2 = os.path.join(self.outdir, "img2.effects.png")
        self.assertTrue(os.path.exists(expected1), f"Missing {expected1}")
        self.assertTrue(os.path.exists(expected2), f"Missing {expected2}")

    def test_summary_line_for_batch(self):
        result = self._run(self.img1, self.img2, "--out-dir", self.outdir)
        self.assertIn("Batch summary:", result.stdout)
        self.assertIn("2/2 processed", result.stdout)
        self.assertIn("bytes", result.stdout)

    def test_no_summary_for_single_input(self):
        result = self._run(self.img1, "--out-dir", self.outdir)
        self.assertNotIn("Batch summary:", result.stdout)

    def test_o_with_multi_input_fails(self):
        result = self._run(self.img1, self.img2, "-o", os.path.join(self.tmpdir, "out.png"), expect_ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cannot specify -o", result.stdout)

    def test_o_and_out_dir_together_fails(self):
        result = self._run(self.img1, "-o", os.path.join(self.tmpdir, "out.png"), "--out-dir", self.outdir, expect_ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cannot use -o and --out-dir", result.stdout)

    def test_default_naming_without_out_dir(self):
        self._run(self.img1, self.img2)
        expected1 = os.path.join(self.tmpdir, "img1.wrapped.png")
        expected2 = os.path.join(self.tmpdir, "img2.wrapped.png")
        self.assertTrue(os.path.exists(expected1), f"Missing {expected1}")
        self.assertTrue(os.path.exists(expected2), f"Missing {expected2}")

    def test_default_summary_without_out_dir(self):
        result = self._run(self.img1, self.img2)
        self.assertIn("Batch summary:", result.stdout)
        self.assertIn("2/2 processed", result.stdout)


if __name__ == "__main__":
    unittest.main()
