"""温度读数、分类与出题测试。"""

import unittest
from dataclasses import FrozenInstanceError

from thermometer.model import (
    KINDS,
    MAX_CELSIUS,
    MIN_CELSIUS,
    ThermometerError,
    ThermometerProblem,
    check_temp,
    difference,
    difference_text,
    format_temp,
    generate_problems,
    generate_readings,
    phase,
)


def expected_phase(value):
    if value > 0:
        return "零上"
    if value < 0:
        return "零下"
    return "零度"


class GeneratedPhaseTest(unittest.TestCase):
    """逐度覆盖 -30–50°C 的零上 / 零下判断。"""


def _make_phase_test(value):
    def test(self):
        self.assertEqual(phase(value), expected_phase(value))

    test.__doc__ = "%d°C 的冷热状态" % value
    return test


for _value in range(MIN_CELSIUS, MAX_CELSIUS + 1):
    setattr(GeneratedPhaseTest, "test_temp_%03d" % (_value + 30), _make_phase_test(_value))


class CheckTempTest(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(check_temp(MIN_CELSIUS), MIN_CELSIUS)
        self.assertEqual(check_temp(MAX_CELSIUS), MAX_CELSIUS)

    def test_too_cold(self):
        with self.assertRaises(ThermometerError):
            check_temp(-31)

    def test_too_hot(self):
        with self.assertRaises(ThermometerError):
            check_temp(51)

    def test_bool(self):
        with self.assertRaises(ThermometerError):
            check_temp(True)

    def test_float(self):
        with self.assertRaises(ThermometerError):
            check_temp(18.5)

    def test_string(self):
        with self.assertRaises(ThermometerError):
            check_temp("-3")

    def test_custom_name(self):
        with self.assertRaisesRegex(ThermometerError, "末温"):
            check_temp(99, "末温")


class FormatTest(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(format_temp(18), "18°C")

    def test_zero(self):
        self.assertEqual(format_temp(0), "0°C")

    def test_negative(self):
        self.assertEqual(format_temp(-7), "-7°C")

    def test_invalid(self):
        with self.assertRaises(ThermometerError):
            format_temp(-40)


class DifferenceTest(unittest.TestCase):
    def test_up(self):
        self.assertEqual(difference(-5, 7), 12)

    def test_down(self):
        self.assertEqual(difference(10, 3), -7)

    def test_same(self):
        self.assertEqual(difference(5, 5), 0)

    def test_invalid_start(self):
        with self.assertRaises(ThermometerError):
            difference(-40, 0)

    def test_invalid_end(self):
        with self.assertRaises(ThermometerError):
            difference(0, 60)

    def test_text_up(self):
        self.assertEqual(difference_text(-5, 7), "上升 12°C")

    def test_text_down(self):
        self.assertEqual(difference_text(10, 3), "下降 7°C")

    def test_text_same(self):
        self.assertEqual(difference_text(3, 3), "没有变化")


class ProblemTest(unittest.TestCase):
    def test_read_problem(self):
        problem = ThermometerProblem(8, 8, "read")
        self.assertEqual(problem.prompt, "读出温度计上的温度")
        self.assertEqual(problem.answer, "8°C（零上）")
        self.assertEqual(problem.value, 8)

    def test_negative_read(self):
        problem = ThermometerProblem(-12, -12, "read")
        self.assertEqual(problem.answer, "-12°C（零下）")

    def test_difference_prompt(self):
        problem = ThermometerProblem(-4, 6, "difference")
        self.assertEqual(problem.prompt, "温度从 -4°C 变到 6°C，变化了多少？")
        self.assertEqual(problem.answer, "上升 10°C")

    def test_read_requires_same(self):
        with self.assertRaises(ThermometerError):
            ThermometerProblem(1, 2, "read")

    def test_difference_requires_change(self):
        with self.assertRaises(ThermometerError):
            ThermometerProblem(2, 2, "difference")

    def test_bad_kind(self):
        with self.assertRaises(ThermometerError):
            ThermometerProblem(1, 1, "guess")

    def test_out_of_range(self):
        with self.assertRaises(ThermometerError):
            ThermometerProblem(-40, -40, "read")

    def test_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            ThermometerProblem(1, 1, "read").start = 2


class ReadingGenerationTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_readings(6, seed=1)), 6)

    def test_unique(self):
        values = generate_readings(10, seed=2)
        self.assertEqual(len(set(values)), len(values))

    def test_deterministic(self):
        self.assertEqual(generate_readings(5, seed=3), generate_readings(5, seed=3))

    def test_bounds(self):
        for value in generate_readings(10, -5, 5, seed=4):
            self.assertGreaterEqual(value, -5)
            self.assertLessEqual(value, 5)

    def test_invalid_count(self):
        for bad in (0, -2, 2.5, True, "4"):
            with self.assertRaises(ThermometerError):
                generate_readings(bad)

    def test_range_too_small(self):
        with self.assertRaises(ThermometerError):
            generate_readings(5, 0, 3)

    def test_low_above_high(self):
        with self.assertRaises(ThermometerError):
            generate_readings(2, 10, -10)

    def test_out_of_bounds(self):
        with self.assertRaises(ThermometerError):
            generate_readings(2, -40, 0)


class ProblemGenerationTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(8, seed=1)), 8)

    def test_deterministic(self):
        self.assertEqual(generate_problems(6, seed=9), generate_problems(6, seed=9))

    def test_unique(self):
        items = generate_problems(10, seed=5)
        keys = {(item.kind, item.start, item.end) for item in items}
        self.assertEqual(len(keys), len(items))

    def test_read_only(self):
        items = generate_problems(6, kinds=("read",), seed=2)
        for item in items:
            self.assertEqual(item.kind, "read")

    def test_difference_only(self):
        items = generate_problems(6, kinds=("difference",), seed=2)
        for item in items:
            self.assertEqual(item.kind, "difference")

    def test_invalid_count(self):
        for bad in (0, -1, True, 2.5):
            with self.assertRaises(ThermometerError):
                generate_problems(bad)

    def test_too_many(self):
        with self.assertRaises(ThermometerError):
            generate_problems(31)

    def test_invalid_bounds(self):
        with self.assertRaises(ThermometerError):
            generate_problems(2, 20, 20)
        with self.assertRaises(ThermometerError):
            generate_problems(2, -40, 0)

    def test_empty_kinds(self):
        with self.assertRaises(ThermometerError):
            generate_problems(2, kinds=())

    def test_unknown_kind(self):
        with self.assertRaises(ThermometerError):
            generate_problems(2, kinds=("read", "guess"))

    def test_all_kinds_known(self):
        for item in generate_problems(8, seed=12):
            self.assertIn(item.kind, KINDS)


if __name__ == "__main__":
    unittest.main()
