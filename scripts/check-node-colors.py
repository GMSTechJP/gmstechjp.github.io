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
   検査するのは箱のインライン style の opacity で、.node-* の規則側の opacity は見ない。

CSS は、ページの <style> と、<link rel="stylesheet"> で読み込むサイト内のファイル
（css/node-diagram.css など）の両方を読む。共有の CSS は箱の色を
.node-example .node-inject のように図の中だけに効かせ、文字色は .node-example .node に
まとめて書いているため、箱の色はクラスごとに背景色と文字色を集めてから判定する
（クラスが文字色を決めていなければ、この共通の文字色を使う）。

箱の色は、クラスごとに、詳細度と出現順（<link> と <style> の HTML 内の順）で
カスケードを再現して解決する。次は再現しない（見逃しや誤検出の方向に働きうる）。
- ブラウザの暗黙の終了タグ（閉じていない <p> や <li>）。箱が図の中にあるかの判定は
  タグの対応だけで行う
- 図の中だけに効く規則（.node-example .node-x）と、図の外にも効く規則の両方があるとき、
  図の外の箱にも図の中の色を当てはめる

色は、16進（#rgb / #rrggbb）と white / black だけを解釈する。次は検査しない
（いずれも見逃す方向にしか働かない）。
- rgb() や CSS 変数など、上記以外の書き方の色
- 背景色か文字色の片方しか決まらない箱（もう片方は継承で決まり、静的には分からない）
"""

import glob
import os
import re
import sys
from html.parser import HTMLParser

MIN_RATIO = 4.5
NAMED = {"white": "#ffffff", "black": "#000000"}

HREF = re.compile(r"""\bhref\s*=\s*["']([^"']+)["']""", re.I)
# 箱の色を決める単独のセレクタ（.node-x、または図の中だけに効かせた .node-example .node-x）
BOX_SELECTOR = re.compile(r"(?:\.node-example\s+)?\.(node-[A-Za-z0-9_-]+)")
# 箱すべてに効く文字色のセレクタ
BASE_SELECTORS = {".node", ".node-example .node"}
NODE_CLASS = re.compile(r"\.(node-[A-Za-z0-9_-]+)")
COLOR = r"(#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|\bwhite\b|\bblack\b)"
BG_DECL = re.compile(r"(?<![\w-])background(?:-color)?\s*:([^;]*)", re.I)
FG_DECL = re.compile(r"(?<![\w-])color\s*:([^;]*)", re.I)
OPACITY = re.compile(r"(?<![\w-])opacity\s*:\s*([^;!]*)", re.I)


def opacity_value(text):
    """宣言中の opacity を 0〜1 の数で返す。無い・解釈できないときは None。"""
    found = None
    for m in OPACITY.finditer(text):
        raw = m.group(1).strip()
        try:
            found = float(raw[:-1]) / 100 if raw.endswith("%") else float(raw)
        except ValueError:
            continue
    return found


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


def mask_css(css):
    """コメントと文字列の中身を空白に置き換える（位置は保つ）。

    content: "}" のように文字列やコメントに括弧があると、括弧の対応がずれて
    以降の規則を読み違えるため、構文として数えないようにする。
    要素のインライン style の値にも使い、コメントや文字列の中の opacity・色を数えない。
    """
    out = list(css)
    i, n = 0, len(css)
    while i < n:
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        elif css[i] in "\"'":
            quote, i = css[i], i + 1
            while i < n and css[i] != quote and css[i] != "\n":
                if css[i] == "\\":
                    out[i] = " "
                    i += 1
                    if i >= n:
                        break
                out[i] = " "
                i += 1
            i += 1
        else:
            i += 1
    return "".join(out)


class NodeTags(HTMLParser):
    """class に "node" を含む要素の (行, class の語, style, node-example の中か) を集める。"""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
            "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []
        self.stack = []  # (タグ名, node-example か)

    def in_diagram(self):
        return any(is_diagram for _, is_diagram in self.stack)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tokens = (attrs.get("class") or "").split()
        if "node" in tokens:
            self.found.append((self.getpos()[0], tokens, attrs.get("style") or "",
                               self.in_diagram()))
        if tag not in self.VOID:
            self.stack.append((tag, "node-example" in tokens))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID and self.stack:
            self.stack.pop()

    def handle_endtag(self, tag):
        # 閉じ忘れがあっても、対応する開きタグまで戻す
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def css_rules(css):
    """(セレクタ, 直下の宣言, 有効か) を返す。

    有効とは、祖先がすべて @media などのアットルールであること。通常の規則の中に
    入れ子で書いた規則は、その規則の子孫にしか効かないため有効としない。
    """
    css = mask_css(css)
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


def specificity(selector):
    """セレクタの詳細度 (ID, クラス・属性・疑似クラス, 要素・疑似要素) を返す（:not() などは近似）。"""
    sel = re.sub(r"\[[^\]]*\]", ".a", selector)  # 属性セレクタはクラスと同じ重み
    ids = len(re.findall(r"#[\w-]+", sel))
    pseudo_el = len(re.findall(r"::[\w-]+", sel))
    sel = re.sub(r"::[\w-]+", "", sel)
    classes = len(re.findall(r"\.[\w-]+|:[\w-]+", sel))
    elements = len(re.findall(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)", sel)) + pseudo_el
    return (ids, classes, elements)


def line_of(src, pos):
    return src.count("\n", 0, pos) + 1


def check(path):
    src = open(path, encoding="utf-8").read()
    errors = []
    defined = set()
    # 箱の色の候補。プロパティごとに (詳細度, 出現順, 色, 位置) を集め、カスケードと同じく
    # 詳細度が高いもの、同じなら後に出たものを採る
    box_bg = {}  # クラス名 -> 候補のリスト
    box_fg = {}
    base_fg = []  # 箱すべてに効く文字色（.node / .node-example .node）の候補
    unscoped = set()  # 図の外でも効きうる書き方（.node-example で始まらない）で定義されたクラス
    order = 0

    # <link> と <style> を HTML 内の出現順に読む（後のものが同じ詳細度の規則に勝つ）
    sheets = []  # (表示名, CSS の本文, ファイル内での本文の開始位置, 行番号を数えるファイルの中身)
    for m in re.finditer(r"<link\b[^>]*>|<style[^>]*>(.*?)</style>", src, re.S | re.I):
        if m.group(0).lower().startswith("<style"):
            sheets.append((path, m.group(1), m.start(1), src))
            continue
        tag = m.group(0)
        href = HREF.search(tag)
        if "stylesheet" not in tag.lower() or not href or re.match(r"[a-z]+:|//", href.group(1)):
            continue
        css_path = os.path.normpath(os.path.join(os.path.dirname(path), href.group(1)))
        if not os.path.exists(css_path):
            errors.append(f"{path}:{line_of(src, m.start())}: 読み込む CSS {href.group(1)} が無い")
            continue
        css = open(css_path, encoding="utf-8").read()
        sheets.append((css_path, css, 0, css))

    for where, css, offset, whole in sheets:
        for selector, body, effective, pos in css_rules(css):
            if not effective:
                continue
            bg, fg = first_color(BG_DECL, body), first_color(FG_DECL, body)
            loc = f"{where}:{line_of(whole, offset + pos)}"
            for sel in (x.strip() for x in selector.split(",")):
                order += 1
                spec = specificity(sel)
                if sel in BASE_SELECTORS:
                    if fg:
                        base_fg.append((spec, order, fg, loc))
                    continue
                classes = NODE_CLASS.findall(sel)
                if not classes:
                    continue
                defined.update(classes)
                if not sel.startswith(".node-example"):
                    unscoped.update(classes)
                m = BOX_SELECTOR.fullmatch(sel)
                if m:
                    # 箱の色を決めるセレクタ。クラスごとに集めて、あとでまとめて判定する
                    if bg:
                        box_bg.setdefault(m.group(1), []).append((spec, order, bg, loc))
                    if fg:
                        box_fg.setdefault(m.group(1), []).append((spec, order, fg, loc))
                elif bg and fg:
                    # 箱の色を決めるもの以外（.node-card .node-x など）は、規則の中だけで判定する
                    ratio = contrast(bg, fg)
                    if ratio < MIN_RATIO:
                        errors.append(
                            f"{loc}: {sel} の文字色 {fg} と"
                            f"背景色 {bg} のコントラスト比が {ratio:.2f}（{MIN_RATIO} 以上が必要）"
                        )

    def winner(candidates):
        return max(candidates, key=lambda c: (c[0], c[1])) if candidates else None

    # 箱の色は、クラスごとに背景色と文字色を解決してから判定する。文字色は、そのクラスの
    # 規則と、箱すべてに効く規則のうち、カスケードで勝つものを使う
    class_colors = {}  # クラス名 -> (背景色, 文字色)（インライン上書きの判定に使う）
    for name in sorted(set(box_bg) | set(box_fg)):
        b = winner(box_bg.get(name, []))
        f = winner(box_fg.get(name, []) + base_fg)
        class_colors[name] = (b and b[2], f and f[2])
        if b and f:
            ratio = contrast(b[2], f[2])
            if ratio < MIN_RATIO:
                errors.append(
                    f"{b[3]}: .{name} の文字色 {f[2]} と背景色 {b[2]} の"
                    f"コントラスト比が {ratio:.2f}（{MIN_RATIO} 以上が必要）"
                )
    common_fg = winner(base_fg)
    common_fg = common_fg and common_fg[2]

    parser = NodeTags()
    parser.feed(src)
    parser.close()
    for line, tokens, inline, in_diagram in parser.found:
        node_classes = [t for t in tokens if t.startswith("node-")]
        for token in node_classes:
            if token in defined and not in_diagram and token not in unscoped:
                errors.append(
                    f"{path}:{line}: クラス {token} の箱が node-example の外にある"
                    f"（共有の CSS は図の中だけに効くため、箱に色が付かない）"
                )
            if token not in defined:
                errors.append(
                    f"{path}:{line}: クラス {token} がこのページの CSS に定義されていない"
                    f"（箱に色が付かない）"
                )
        if not inline:
            continue
        inline = mask_css(inline)  # コメントや文字列の中の opacity・色を数えない
        op = opacity_value(inline)
        if op is not None and op < 1:
            errors.append(
                f"{path}:{line}: ノードの箱を opacity: {op:g} で薄くしている"
                f"（背景と混ざって読みにくくなる。色で表現する）"
            )
        ibg, ifg = first_color(BG_DECL, inline), first_color(FG_DECL, inline)
        if not (ibg or ifg):
            continue
        cbg = cfg = None
        for token in node_classes:
            b, f = class_colors.get(token, (None, None))
            cbg, cfg = b or cbg, f or cfg
        bg, fg = ibg or cbg, ifg or cfg or common_fg
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
