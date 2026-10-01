#!/usr/bin/env python3
"""ノード図（node-example 等）の色の検証。

ガイドでは、ノードを色付きの箱（class="node node-inject" など）で並べて処理の流れを示す。
この箱は CSS のクラスで色を付けるため、次の誤りが起きても HTML としては正しく、
フローの検証にもレビュー（ソースを文字として読むもの）にも引っかからない。描画して
初めて「読めない」と分かる。

1. 未定義のクラス: 使ったクラス（node-http-in 等）が、そのページの CSS に無い。
   箱に色が付かず、暗い背景の上に文字だけが並ぶ。別の規則の中に入れ子で書いた規則は、
   その規則の子孫にしか効かないため、定義として数えない。
2. コントラスト不足: 文字色と背景色のコントラスト比が WCAG 2.x の AA 基準（4.5:1）を
   下回る。箱の文字は太字 14px で、「大きい文字」（太字 18.66px 以上）には当たらないため、
   緩い 3:1 ではなく 4.5:1 を使う。.node-* の規則と、箱に付けたインライン style
   （規則の色を上書きする場合）の両方を検査する。
3. 箱を opacity で薄くしている: 下の背景と混ざって読みにくくなるため、色で表現する。

色は、16進（#rgb / #rrggbb）と white / black だけを解釈する。次は検査しない
（いずれも見逃す方向にしか働かない）。
- rgb() や CSS 変数など、上記以外の書き方の色
- 背景色か文字色の片方しか決まらない箱（もう片方は継承で決まり、静的には分からない）
"""

import glob
import re
import sys

MIN_RATIO = 4.5
NAMED = {"white": "#ffffff", "black": "#000000"}

STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
NODE_CLASS = re.compile(r"\.(node-[A-Za-z0-9_-]+)")
TAG = re.compile(r"<[A-Za-z][^>]*>")
CLASS_ATTR = re.compile(r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
STYLE_ATTR = re.compile(r"""\bstyle\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
COLOR = r"(#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|\bwhite\b|\bblack\b)"
BG_DECL = re.compile(r"(?<![\w-])background(?:-color)?\s*:([^;]*)", re.I)
FG_DECL = re.compile(r"(?<![\w-])color\s*:([^;]*)", re.I)
OPACITY = re.compile(r"(?<![\w-])opacity\s*:\s*([0-9.]+)", re.I)


def to_hex(value):
    value = NAMED.get(value.lower(), value.lower())
    if len(value) == 4:
        value = "#" + "".join(c * 2 for c in value[1:])
    return value


def first_color(decl_re, text):
    """宣言の値に含まれる最初の色を返す（省略記法 background: url(..) #fff にも対応）。"""
    found = None
    for m in decl_re.finditer(text):
        c = re.search(COLOR, m.group(1), re.I)
        if c:
            found = to_hex(c.group(1))  # 後の宣言が勝つ
    return found


def luminance(hex_color):
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def css_rules(css):
    """(セレクタ, 直下の宣言, 有効か) を返す。

    有効とは、祖先がすべて @media などのアットルールであること。通常の規則の中に
    入れ子で書いた規則は、その規則の子孫にしか効かないため有効としない。
    コメントは位置を保つため同じ長さの空白に置き換える。
    """
    css = CSS_COMMENT.sub(lambda m: " " * len(m.group(0)), css)
    rules = []
    stack = []  # [セレクタ, 直下の宣言のかけら, 開始位置]
    start = 0
    for i, ch in enumerate(css):
        if ch == "{":
            prelude = css[start:i]
            if stack:
                stack[-1][1].append(prelude)
            stack.append([prelude.strip(), [], i])
            start = i + 1
        elif ch == "}":
            if not stack:
                start = i + 1
                continue
            selector, parts, pos = stack.pop()
            parts.append(css[start:i])
            effective = all(s.startswith("@") for s, _, _ in stack)
            if not selector.startswith("@"):
                rules.append((selector, ";".join(parts), effective, pos))
            start = i + 1
        elif ch == ";" and stack:
            stack[-1][1].append(css[start:i + 1])
            start = i + 1
    return rules


def line_of(src, pos):
    return src.count("\n", 0, pos) + 1


def check(path):
    src = open(path, encoding="utf-8").read()
    errors = []
    defined = set()
    class_colors = {}  # .node-x 単独セレクタの色（インライン上書きの判定に使う）

    for style in STYLE.finditer(src):
        for selector, body, effective, pos in css_rules(style.group(1)):
            classes = NODE_CLASS.findall(selector)
            if not classes or not effective:
                continue
            defined.update(classes)
            bg, fg = first_color(BG_DECL, body), first_color(FG_DECL, body)
            for sel in (s.strip() for s in selector.split(",")):
                m = re.fullmatch(r"\.(node-[A-Za-z0-9_-]+)", sel)
                if m:
                    old = class_colors.get(m.group(1), (None, None))
                    class_colors[m.group(1)] = (bg or old[0], fg or old[1])
            if bg and fg:
                ratio = contrast(bg, fg)
                if ratio < MIN_RATIO:
                    errors.append(
                        f"{path}:{line_of(src, style.start(1) + pos)}: {selector} の文字色 {fg} と"
                        f"背景色 {bg} のコントラスト比が {ratio:.2f}（{MIN_RATIO} 以上が必要）"
                    )

    for tag in TAG.finditer(src):
        cm = CLASS_ATTR.search(tag.group(0))
        if not cm:
            continue
        tokens = (cm.group(1) or cm.group(2) or "").split()
        if "node" not in tokens:
            continue
        line = line_of(src, tag.start())
        node_classes = [t for t in tokens if t.startswith("node-")]
        for token in node_classes:
            if token not in defined:
                errors.append(
                    f"{path}:{line}: クラス {token} がこのページの CSS に定義されていない"
                    f"（箱に色が付かない）"
                )
        sm = STYLE_ATTR.search(tag.group(0))
        if not sm:
            continue
        inline = sm.group(1) or sm.group(2) or ""
        op = OPACITY.search(inline)
        if op and float(op.group(1)) < 1:
            errors.append(
                f"{path}:{line}: ノードの箱を opacity: {op.group(1)} で薄くしている"
                f"（背景と混ざって読みにくくなる。色で表現する）"
            )
        ibg, ifg = first_color(BG_DECL, inline), first_color(FG_DECL, inline)
        if not (ibg or ifg):
            continue
        cbg = cfg = None
        for token in node_classes:
            b, f = class_colors.get(token, (None, None))
            cbg, cfg = b or cbg, f or cfg
        bg, fg = ibg or cbg, ifg or cfg
        if bg and fg:
            ratio = contrast(bg, fg)
            if ratio < MIN_RATIO:
                errors.append(
                    f"{path}:{line}: インライン style で上書きした箱の文字色 {fg} と背景色 {bg} の"
                    f"コントラスト比が {ratio:.2f}（{MIN_RATIO} 以上が必要）"
                )
    return errors


def main():
    paths = sys.argv[1:] or sorted(glob.glob("*.html"))
    if not paths:
        # 実行場所の誤りなどで1件も検査しないまま成功扱いになるのを防ぐ
        print("検査対象の HTML が見つからない")
        return 1
    errors = []
    for path in paths:
        errors.extend(check(path))
    for e in errors:
        print(e)
    print(f"\n{len(paths)} files checked, {len(errors)} problems found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
