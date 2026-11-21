"""温度计 SVG 与 A4 练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Optional, Sequence

from .model import (
    MAX_CELSIUS,
    MIN_CELSIUS,
    ThermometerError,
    ThermometerProblem,
)

_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 3mm; page-break-inside: avoid; }
.prompt { font-size: 13px; margin: 0 0 2mm; color: #323f4b; }
.answer-line { margin-top: 2mm; border-bottom: 1px dashed #9aa5b1; height: 22px; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #b02a37; padding-left: 3mm; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def _fmt(value: float) -> str:
    return ("%.2f" % value).rstrip("0").rstrip(".")


def render_thermometer(
    value: Optional[int] = None,
    low: int = MIN_CELSIUS,
    high: int = MAX_CELSIUS,
    size: int = 150,
) -> str:
    """绘制竖直温度计；value 为 None 时表示待读的空白温度计。"""
    if isinstance(size, bool) or not isinstance(size, int) or size < 100:
        raise ThermometerError("温度计尺寸必须是至少 100 的整数")
    if isinstance(low, bool) or not isinstance(low, int) or isinstance(high, bool) or not isinstance(high, int):
        raise ThermometerError("刻度范围必须是整数")
    if low < MIN_CELSIUS or high > MAX_CELSIUS or low >= high:
        raise ThermometerError("刻度范围必须在 -30–50 且 low < high")
    if value is not None:
        if value < low or value > high:
            raise ThermometerError("温度超出刻度范围：%d" % value)

    width = float(size)
    height = round(size * 3.1, 2)
    tube_x = width * 0.53
    tube_w = width * 0.17
    top = height * 0.08
    bottom = height * 0.79
    bulb_r = width * 0.17
    bulb_cy = bottom + bulb_r * 0.55

    def y_of(temp: int) -> float:
        ratio = (temp - low) / float(high - low)
        return bottom - ratio * (bottom - top)

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s" '
        'role="img" aria-label="温度计">' % (_fmt(width), _fmt(height), _fmt(width), _fmt(height)),
        "<title>温度计</title>",
        # 外管与球泡
        '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="#f8fafc" '
        'stroke="#323f4b" stroke-width="1.8"/>'
        % (
            _fmt(tube_x - tube_w / 2),
            _fmt(top),
            _fmt(tube_w),
            _fmt(bottom - top + 6),
            _fmt(tube_w / 2),
        ),
        '<circle cx="%s" cy="%s" r="%s" fill="#f8fafc" stroke="#323f4b" stroke-width="1.8"/>'
        % (_fmt(tube_x), _fmt(bulb_cy), _fmt(bulb_r)),
    ]

    # 水银：球泡始终有液体，柱高随温度变化。
    if value is None:
        parts.append(
            '<circle cx="%s" cy="%s" r="%s" fill="#cbd2d9" stroke="#9aa5b1"/>'
            % (_fmt(tube_x), _fmt(bulb_cy), _fmt(bulb_r * 0.72))
        )
        parts.append(
            '<text x="%s" y="%s" font-size="%s" fill="#616e7c" text-anchor="middle">?</text>'
            % (_fmt(tube_x), _fmt(bulb_cy + bulb_r * 0.2), _fmt(width * 0.18))
        )
    else:
        column_top = y_of(value)
        parts.append(
            '<circle cx="%s" cy="%s" r="%s" fill="#d64545" stroke="#a61b1b"/>'
            % (_fmt(tube_x), _fmt(bulb_cy), _fmt(bulb_r * 0.72))
        )
        column_h = max(0.0, bottom - column_top)
        if column_h > 0:
            parts.append(
                '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="#d64545"/>'
                % (
                    _fmt(tube_x - tube_w * 0.3),
                    _fmt(column_top),
                    _fmt(tube_w * 0.6),
                    _fmt(column_h + 6),
                    _fmt(tube_w * 0.3),
                )
            )

    # 刻度线与左侧数字。
    ticks: List[str] = ['<g stroke="#52606d" stroke-linecap="round">']
    labels: List[str] = ['<g font-size="%s" fill="#3e4c59" text-anchor="end">' % _fmt(max(8.0, width * 0.085))]
    for temp in range(low, high + 1):
        y = y_of(temp)
        if temp % 10 == 0:
            length, stroke_width = width * 0.13, 1.1
            labels.append(
                '<text x="%s" y="%s">%d</text>'
                % (_fmt(tube_x - tube_w / 2 - width * 0.17), _fmt(y + width * 0.03), temp)
            )
        elif temp % 5 == 0:
            length, stroke_width = width * 0.09, 0.8
        else:
            length, stroke_width = width * 0.05, 0.5
        ticks.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke-width="%s"/>'
            % (
                _fmt(tube_x - tube_w / 2),
                _fmt(y),
                _fmt(tube_x - tube_w / 2 - length),
                _fmt(y),
                stroke_width,
            )
        )
    ticks.append("</g>")
    labels.append("</g>")
    parts.extend(ticks)
    parts.extend(labels)
    parts.append("</svg>")
    return "\n".join(parts)


def render_worksheet(
    problems: Sequence[ThermometerProblem],
    title: str = "温度计练习",
    answers: bool = False,
) -> str:
    """生成可打印的温度计练习纸。"""
    items = list(problems)
    if not items:
        raise ThermometerError("至少需要一道题")
    for item in items:
        if not isinstance(item, ThermometerProblem):
            raise ThermometerError("题目必须是 ThermometerProblem")

    cards: List[str] = []
    for index, item in enumerate(items, 1):
        if item.kind == "read":
            figure = render_thermometer(item.value)
        else:
            figure = render_thermometer(item.end)
        cards.append(
            '<div class="card">\n<p class="prompt">%d. %s</p>\n%s\n'
            '<div class="answer-line"></div>\n</div>'
            % (index, html.escape(item.prompt), figure)
        )

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="grid">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        rows = []
        for index, item in enumerate(items, 1):
            rows.append(
                "<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
                % (index, html.escape(item.prompt), html.escape(item.answer))
            )
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)
