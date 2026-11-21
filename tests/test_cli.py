"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from thermometer.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_phase_positive(self):
        code, out, _ = run(["phase", "12"])
        self.assertEqual(code, 0)
        self.assertIn("零上", out)

    def test_phase_negative(self):
        code, out, _ = run(["phase", "-8"])
        self.assertEqual(code, 0)
        self.assertIn("零下", out)

    def test_phase_zero(self):
        code, out, _ = run(["phase", "0"])
        self.assertEqual(code, 0)
        self.assertIn("零度", out)

    def test_phase_invalid(self):
        code, _, err = run(["phase", "88"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_diff(self):
        code, out, _ = run(["diff", "-3", "9"])
        self.assertEqual(code, 0)
        self.assertIn("上升 12°C", out)

    def test_diff_down(self):
        code, out, _ = run(["diff", "9", "-3"])
        self.assertEqual(code, 0)
        self.assertIn("下降 12°C", out)

    def test_show_stdout(self):
        code, out, _ = run(["show", "15"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)

    def test_show_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "temp.svg"
            code, out, _ = run(["show", "-5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "read,guess"])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_empty_kind(self):
        code, _, err = run(["sheet", "--kinds", " , "])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_bad_range(self):
        code, _, err = run(["sheet", "--min", "10", "--max", "10"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_output_dir(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "out" / "sheet.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
