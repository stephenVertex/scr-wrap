#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow"]
# ///

"""Tests for scr-wrap --numbered flag (scr-rename numbering integration)."""

import os
import subprocess
import sys
import tempfile
import time
import unittest

from PIL import Image


SCR_WRAP = os.path.join(os.path.dirname(__file__), "scr-wrap")


class TestNumberedOutput(unittest.TestCase):
    def setUp(self):
        self.orig_cwd = os.getcwd()
        self.tmpdir = tempfile.mkdtemp()
        self.outdir = os.path.join(self.tmpdir, "numbered_out")
        self.img1 = os.path.join(self.tmpdir, "img1.png")
        self.img2 = os.path.join(self.tmpdir, "img2.png")
        self.img3 = os.path.join(self.tmpdir, "img3.png")
        img = Image.new("RGB", (400, 300), "red")
        img.save(self.img1)
        time.sleep(0.05)
        img = Image.new("RGB", (400, 300), "blue")
        img.save(self.img2)
        time.sleep(0.05)
        img = Image.new("RGB", (400, 300), "green")
        img.save(self.img3)

    def tearDown(self):
        os.chdir(self.orig_cwd)
        for root, dirs, files in os.walk(self.tmpdir, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(self.tmpdir)

    def _run(self, *args, cwd=None, expect_ok=True):
        cmd = [SCR_WRAP] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        if expect_ok:
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        return result

    def test_numbered_naming_with_out_dir(self):
        self._run(self.img1, self.img2, "--numbered", "shot", "--out-dir", self.outdir)
        self.assertTrue(os.path.exists(os.path.join(self.outdir, "shot-1.png")))
        self.assertTrue(os.path.exists(os.path.join(self.outdir, "shot-2.png")))

    def test_numbered_naming_without_out_dir(self):
        self._run(self.img1, self.img2, "--numbered", "capture", cwd=self.tmpdir)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "capture-1.png")))
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "capture-2.png")))

    def test_numbered_mtime_ordering(self):
        self._run(self.img1, self.img2, self.img3, "--numbered", "screen", "--out-dir", self.outdir)
        img1_mtime = os.path.getmtime(self.img1)
        img2_mtime = os.path.getmtime(self.img2)
        img3_mtime = os.path.getmtime(self.img3)
        self.assertLess(img1_mtime, img2_mtime)
        self.assertLess(img2_mtime, img3_mtime)

        shot1_path = os.path.join(self.outdir, "screen-1.png")
        shot2_path = os.path.join(self.outdir, "screen-2.png")
        shot3_path = os.path.join(self.outdir, "screen-3.png")
        self.assertTrue(os.path.exists(shot1_path))
        self.assertTrue(os.path.exists(shot2_path))
        self.assertTrue(os.path.exists(shot3_path))

        with Image.open(shot1_path) as s1:
            self.assertEqual(s1.getpixel((200, 200)), (255, 0, 0))
        with Image.open(shot2_path) as s2:
            self.assertEqual(s2.getpixel((200, 200)), (0, 0, 255))
        with Image.open(shot3_path) as s3:
            self.assertEqual(s3.getpixel((200, 200)), (0, 128, 0))

    def test_numbered_no_zero_padding(self):
        self._run(self.img1, self.img2, "--numbered", "s", "--out-dir", self.outdir)
        self.assertTrue(os.path.exists(os.path.join(self.outdir, "s-1.png")))
        self.assertTrue(os.path.exists(os.path.join(self.outdir, "s-2.png")))
        self.assertFalse(os.path.exists(os.path.join(self.outdir, "s-01.png")))
        self.assertFalse(os.path.exists(os.path.join(self.outdir, "s-02.png")))

    def test_numbered_single_input(self):
        self._run(self.img1, "--numbered", "single", "--out-dir", self.outdir)
        self.assertTrue(os.path.exists(os.path.join(self.outdir, "single-1.png")))

    def test_numbered_batch_summary(self):
        result = self._run(self.img1, self.img2, "--numbered", "batch", "--out-dir", self.outdir)
        self.assertIn("Batch summary:", result.stdout)
        self.assertIn("2/2 processed", result.stdout)

    def test_numbered_with_o_fails(self):
        result = self._run(
            self.img1, "--numbered", "fail", "-o", os.path.join(self.tmpdir, "out.png"),
            expect_ok=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cannot use -o and --numbered", result.stdout)

    def test_numbered_with_no_browser(self):
        self._run(self.img1, self.img2, "--numbered", "nbf", "--no-browser", "--out-dir", self.outdir)
        p1 = os.path.join(self.outdir, "nbf-1.png")
        p2 = os.path.join(self.outdir, "nbf-2.png")
        self.assertTrue(os.path.exists(p1))
        self.assertTrue(os.path.exists(p2))
        with Image.open(p1) as img:
            self.assertEqual(img.size, (400, 300))


if __name__ == "__main__":
    unittest.main()
