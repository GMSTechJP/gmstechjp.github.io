#!/usr/bin/env python3
"""ノード図（node-example 等）の色の検証。

ガイドでは、ノードを色付きの箱（class="node node-inject" など）で並べて処理の流れを示す。
この箱は CSS のクラスで色を付けるため、次の2つの誤りが起きても HTML としては正しく、
フローの検証にもレビュー（ソースを文字として読むもの）にも引っかからない。描画して
初めて「読めない」と分かる。

1. 未定義のクラス: 使ったクラス（node-http-in 等）が、そのページの CSS に無い。
   箱に色が付かず、暗い背景の上に文字だけが並ぶ。
2. コントラスト不足: .node-* の規則で、文字色と背景色のコントラスト比が WCAG 2.x の
   AA 基準（4.5:1）を下回る。箱の文字は太字 14px で、「大きい文字」（太字 18.66px 以上）
   には当たらないため、緩い 3:1 ではなく 4.5:1 を使う。

色は、規則の中に直接書かれた16進（#rgb / #rrggbb）と white / black だけを解釈する。
それ以外の書き方（rgb() や変数）は判定できないので検査しない（見逃す方向にしか働かない）。
"""

import glob
import re
import sys

MIN_RATIO = 4.5
NAMED = {"white": "#ffffff", "black": "#000000"}

STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
NODE_CLASS = re.compile(r"\.(node-[A-Za-z0-9_-]+)")
CLASS_ATTR = re.compile(r'class="([^"]*)"')
BG = re.compile(r"background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3}\b|#[0-9a-fA-F]{6}\b)")
FG = re.compile(r"(?<![\w-])color\s*:\s*(#[0-9a-fA-F]{3}\b|#[0-9a-fA-F]{6}\b|white\b|black\b)")


def to_hex(value):
    value = NAMED.get(value.lower(), value.lower())
    if len(value) == 4:
        value = "#" + "".join(c * 2 for c in value[1:])
    return value


def luminance(hex_color):
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def line_of(src, pos):
    return src.count("\n", 0, pos) + 1


def check(path):
    src = open(path, encoding="utf-8").read()
    errors = []
    defined = set()

    for style in STYLE.finditer(src):
        css = style.group(1)
        for rule in RULE.finditer(css):
            selector, body = rule.group(1), rule.group(2)
            classes = NODE_CLASS.findall(selector)
            if not classes:
                continue
            defined.update(classes)
            bg, fg = BG.search(body), FG.search(body)
            if not (bg and fg):
                continue
            ratio = contrast(to_hex(bg.group(1)), to_hex(fg.group(1)))
            if ratio < MIN_RATIO:
                line = line_of(src, style.start(1) + rule.start())
                errors.append(
                    f"{path}:{line}: {selector.strip()} の文字色 {fg.group(1)} と背景色 "
                    f"{bg.group(1)} のコントラスト比が {ratio:.2f}（{MIN_RATIO} 以上が必要）"
                )

    for attr in CLASS_ATTR.finditer(src):
        tokens = attr.group(1).split()
        if "node" not in tokens:
            continue
        for token in tokens:
            if token.startswith("node-") and token not in defined:
                errors.append(
                    f"{path}:{line_of(src, attr.start())}: クラス {token} がこのページの "
                    f"CSS に定義されていない（箱に色が付かない）"
                )
    return errors


def main():
    paths = sys.argv[1:] or sorted(glob.glob("*.html"))
    errors = []
    for path in paths:
        errors.extend(check(path))
    for e in errors:
        print(e)
    print(f"\n{len(paths)} files checked, {len(errors)} problems found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
