# thermometer

[![CI](https://github.com/eastyou/thermometer/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/thermometer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

把温度计画成 SVG，覆盖 -30–50°C：既能出“读温度”题，也能出“从 -4°C 变到 6°C，变化了多少”的温差题，生成可打印的 A4 练习纸。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 生成 8 道读数 / 温差混合练习，附答案
thermometer sheet --count 8 --answers -o sheet.html

# 只出零下读数题
thermometer sheet --kinds read --min -30 --max 0 -o below.html

# 输出单个 15°C 的温度计 SVG
thermometer show 15 -o temp.svg

# 判断零上零下与计算温差
thermometer phase -8
thermometer diff -4 6
# 上升 10°C
```

## 功能

- -30–50°C 竖直温度计，1°/5°/10° 三级刻度
- 水银柱随温度升降，零下同样可读
- 读数题与温差题，题目去重、支持随机种子复现
- 温差自动判断上升 / 下降，并给出变化量
- 输出 A4 打印样式，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
