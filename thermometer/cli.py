"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    MAX_CELSIUS,
    MIN_CELSIUS,
    ThermometerError,
    difference_text,
    format_temp,
    generate_problems,
    phase,
)
from .render import render_thermometer, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="thermometer",
        description="温度计：-30~50°C 读数、零上零下与温差练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸 HTML")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--min", dest="min_temp", type=int, default=-20, help="最低温度，默认 -20")
    sheet.add_argument("--max", dest="max_temp", type=int, default=40, help="最高温度，默认 40")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument(
        "--kinds",
        default=",".join(KINDS),
        help="题型，用逗号分隔：read（读数）、difference（温差）",
    )
    sheet.add_argument("--title", default="温度计练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    show = subparsers.add_parser("show", help="输出单个温度计 SVG")
    show.add_argument("temp", type=int, help="温度（%d–%d）" % (MIN_CELSIUS, MAX_CELSIUS))
    show.add_argument("--size", type=int, default=150, help="宽度，默认 150")
    show.add_argument("-o", "--output", default=None, help="输出文件")

    phase_parser = subparsers.add_parser("phase", help="判断零上或零下")
    phase_parser.add_argument("temp", type=int, help="温度")

    diff_parser = subparsers.add_parser("diff", help="计算温差")
    diff_parser.add_argument("start", type=int, help="初温")
    diff_parser.add_argument("end", type=int, help="末温")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise ThermometerError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "phase":
            print("%s 是%s" % (format_temp(args.temp), phase(args.temp)))
            return 0
        if args.command == "diff":
            print(difference_text(args.start, args.end))
            return 0
        if args.command == "show":
            _write_output(render_thermometer(args.temp, size=args.size), args.output)
            return 0
        problems = generate_problems(
            args.count, args.min_temp, args.max_temp, _parse_kinds(args.kinds), args.seed
        )
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except ThermometerError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
