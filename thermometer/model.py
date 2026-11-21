"""温度计：读数、零上零下与温差。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

MIN_CELSIUS = -30
MAX_CELSIUS = 50
KINDS: Tuple[str, ...] = ("read", "difference")


class ThermometerError(ValueError):
    """温度计相关的输入错误。"""


def check_temp(value: Any, name: str = "温度") -> int:
    """校验温度是 -30–50 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ThermometerError("%s必须是整数" % name)
    if value < MIN_CELSIUS or value > MAX_CELSIUS:
        raise ThermometerError(
            "%s必须在 %d–%d°C 之间：%d" % (name, MIN_CELSIUS, MAX_CELSIUS, value)
        )
    return value


def format_temp(value: int) -> str:
    """格式化为“-7°C”或“18°C”。"""
    return "%d°C" % check_temp(value)


def phase(value: int) -> str:
    """判断零上、零下还是零度。"""
    check_temp(value)
    if value > 0:
        return "零上"
    if value < 0:
        return "零下"
    return "零度"


def difference(start: int, end: int) -> int:
    """计算末温减初温，可为负数。"""
    check_temp(start, "初温")
    check_temp(end, "末温")
    return end - start


def difference_text(start: int, end: int) -> str:
    """把温差描述成“上升 / 下降 N°C”。"""
    delta = difference(start, end)
    if delta > 0:
        return "上升 %d°C" % delta
    if delta < 0:
        return "下降 %d°C" % abs(delta)
    return "没有变化"


@dataclass(frozen=True)
class ThermometerProblem:
    """一道温度计题：读数题 start == end，温差题 start != end。"""

    start: int
    end: int
    kind: str

    def __post_init__(self) -> None:
        check_temp(self.start, "初温")
        check_temp(self.end, "末温")
        if self.kind not in KINDS:
            raise ThermometerError("未知题型：%s" % self.kind)
        if self.kind == "read" and self.start != self.end:
            raise ThermometerError("读数题的起止温度必须相同")
        if self.kind == "difference" and self.start == self.end:
            raise ThermometerError("温差题的起止温度不能相同")

    @property
    def value(self) -> int:
        """读数题显示的温度；温差题显示末温。"""
        return self.end

    @property
    def prompt(self) -> str:
        if self.kind == "read":
            return "读出温度计上的温度"
        return "温度从 %s 变到 %s，变化了多少？" % (
            format_temp(self.start),
            format_temp(self.end),
        )

    @property
    def answer(self) -> str:
        if self.kind == "read":
            return "%s（%s）" % (format_temp(self.value), phase(self.value))
        return difference_text(self.start, self.end)


def generate_readings(
    count: int = 8,
    min_temp: int = MIN_CELSIUS,
    max_temp: int = MAX_CELSIUS,
    seed: Optional[int] = None,
) -> List[int]:
    """生成不重复的温度读数。"""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ThermometerError("题目数量必须是正整数")
    check_temp(min_temp, "最低温度")
    check_temp(max_temp, "最高温度")
    if min_temp > max_temp:
        raise ThermometerError("最低温度不能高于最高温度")
    available = max_temp - min_temp + 1
    if count > available:
        raise ThermometerError("温度范围内只有 %d 个取值" % available)
    rng = random.Random(seed)
    values = rng.sample(range(min_temp, max_temp + 1), count)
    return values


def generate_problems(
    count: int = 8,
    min_temp: int = -20,
    max_temp: int = 40,
    kinds: Sequence[str] = KINDS,
    seed: Optional[int] = None,
) -> List[ThermometerProblem]:
    """生成读数题与温差题。"""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ThermometerError("题目数量必须是正整数")
    if count > 30:
        raise ThermometerError("题目数量不能超过 30")
    check_temp(min_temp, "最低温度")
    check_temp(max_temp, "最高温度")
    if min_temp >= max_temp:
        raise ThermometerError("最低温度必须小于最高温度")
    chosen = tuple(kinds)
    if not chosen:
        raise ThermometerError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise ThermometerError("未知题型：%s" % kind)

    rng = random.Random(seed)
    readings = generate_readings(max(count, 2), min_temp, max_temp, seed)
    result: List[ThermometerProblem] = []
    seen = set()
    index = 0
    while len(result) < count:
        kind = rng.choice(chosen)
        if kind == "read":
            value = readings[index % len(readings)]
            index += 1
            key = ("read", value)
            if key in seen:
                continue
            seen.add(key)
            result.append(ThermometerProblem(value, value, "read"))
        else:
            first = rng.randint(min_temp, max_temp)
            second = rng.randint(min_temp, max_temp)
            if first == second:
                continue
            key = ("difference", first, second)
            if key in seen:
                continue
            seen.add(key)
            result.append(ThermometerProblem(first, second, "difference"))
    return result
