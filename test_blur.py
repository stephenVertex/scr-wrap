#!/usr/bin/env python3
"""Tests for scr-wrap --blur region blurring."""

import os
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCR_WRAP = os.path.join(os.path.dirname(__file__), "scr-wrap")


class TestBlurRegion(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.input_path = os.path.join(self.tmpdir, "input.png")
        # Create a solid-color image so blur is easy to detect
        img = Image.new("RGB", (400, 300), "red")
        img.save(self.input_path)

    def tearDown(self):
        for f in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)

    def _run(self, *args, expect_ok=True):
        cmd = [SCR_WRAP, self.input_path] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if expect_ok:
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        return result

    def _open(self, filename):
        return Image.open(os.path.join(self.tmpdir, filename))

    def test_single_blur_region(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--blur", "50,50,100,100")
        with self._open("out.png") as img:
            # The blurred region should differ from the original red
            px = img.load()
            # Pixel inside blur region should be less saturated / different from red
            # Because we blurred a solid red image, the region stays red-ish but softens.
            # We just verify the command succeeds and image is produced.
            self.assertEqual(img.size, (400, 396))  # 400x300 + 96px frame

    def test_multiple_blur_regions(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--blur", "10,10,20,20", "--blur", "200,100,50,50")
        with self._open("out.png") as img:
            self.assertEqual(img.size, (400, 396))

    def test_blur_no_browser(self):
        out = os.path.join(self.tmpdir, "out.png")
        self._run("-o", out, "--no-browser", "--blur", "50,50,100,100")
        with self._open("out.png") as img:
            self.assertEqual(img.size, (400, 300))

    def test_blur_clamps_to_image_bounds(self):
        out = os.path.join(self.tmpdir, "out.png")
        # Region partially outside image bounds should still work
        self._run("-o", out, "--blur", "350,250,100,100")
        with self._open("out.png") as img:
            self.assertEqual(img.size, (400, 396))

    def test_invalid_blur_format(self):
        out = os.path.join(self.tmpdir, "out.png")
        result = self._run("-o", out, "--blur", "50,50", expect_ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid blur region format", result.stderr)

    def test_blur_negative_width(self):
        out = os.path.join(self.tmpdir, "out.png")
        result = self._run("-o", out, "--blur", "50,50,-10,10", expect_ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid blur region format", result.stderr)

    def test_blur_changes_pixels(self):
        out = os.path.join(self.tmpdir, "out.png")
        # Create an image with a distinct color block to blur
        img = Image.new("RGB", (400, 300), "white")
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 150, 150], fill="black")
        img.save(self.input_path)

        # Blur region larger than the black rectangle so white pixels are included in the blur
        self._run("-o", out, "--no-browser", "--blur", "40,40,120,120")
        with self._open("out.png") as img:
            px = img.load()
            # Pixel at the edge of the black rectangle inside the blur region
            # should be gray-ish after blurring because white pixels are mixed in
            r, g, b = px[50, 100]
            # Blurred black on white edges should produce gray
            self.assertTrue(any(c > 0 for c in (r, g, b)), "Blurred edge should not be pure black")
            self.assertTrue(any(c < 255 for c in (r, g, b)), "Blurred edge should not be pure white")


if __name__ == "__main__":
    unittest.main()
