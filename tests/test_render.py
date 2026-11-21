"""温度计与练习纸渲染测试。"""

import unittest

from thermometer.model import ThermometerError, ThermometerProblem
from thermometer.render import render_thermometer, render_worksheet


class ThermometerSvgTest(unittest.TestCase):
    def test_root(self):
        svg = render_thermometer()
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("温度计", svg)

    def test_tick_count(self):
        svg = render_thermometer()
        self.assertEqual(svg.count("<line"), 81)

    def test_label_count(self):
        svg = render_thermometer(-10)
        self.assertEqual(svg.count("<text"), 9)

    def test_question_mark(self):
        svg = render_thermometer()
        self.assertIn(">?<", svg)
        self.assertEqual(svg.count("<text"), 10)

    def test_mercury_present(self):
        svg = render_thermometer(20)
        self.assertIn("#d64545", svg)
        self.assertNotIn(">?<", svg)

    def test_negative_value(self):
        svg = render_thermometer(-30)
        self.assertIn("#d64545", svg)

    def test_custom_size(self):
        svg = render_thermometer(0, size=200)
        self.assertIn('width="200"', svg)

    def test_custom_range(self):
        svg = render_thermometer(10, low=-10, high=20)
        self.assertEqual(svg.count("<line"), 31)

    def test_value_out_of_range(self):
        with self.assertRaises(ThermometerError):
            render_thermometer(40, low=-10, high=20)

    def test_invalid_size(self):
        with self.assertRaises(ThermometerError):
            render_thermometer(size=50)

    def test_invalid_range(self):
        with self.assertRaises(ThermometerError):
            render_thermometer(low=0, high=0)

    def test_range_beyond_scale(self):
        with self.assertRaises(ThermometerError):
            render_thermometer(low=-50, high=20)

    def test_non_int_range(self):
        with self.assertRaises(ThermometerError):
            render_thermometer(low=-1.5, high=20)


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.problems = [
            ThermometerProblem(8, 8, "read"),
            ThermometerProblem(-3, 5, "difference"),
            ThermometerProblem(-15, -15, "read"),
        ]

    def test_document(self):
        page = render_worksheet(self.problems)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertIn("温度计练习", page)
        self.assertTrue(page.endswith("</html>"))

    def test_card_count(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('class="card"'), 3)

    def test_answers(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("上升 8°C", page)

    def test_no_answers(self):
        page = render_worksheet(self.problems, answers=False)
        self.assertNotIn("参考答案", page)

    def test_custom_title(self):
        page = render_worksheet(self.problems, title="认识温度")
        self.assertIn("<title>认识温度</title>", page)

    def test_empty(self):
        with self.assertRaises(ThermometerError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(ThermometerError):
            render_worksheet([("8", "read")])

    def test_escaping(self):
        page = render_worksheet(self.problems, title="<b>温度</b>")
        self.assertNotIn("<b>温度</b>", page)
        self.assertIn("&lt;b&gt;", page)


if __name__ == "__main__":
    unittest.main()
