#!/usr/bin/env python3
"""データの並びの図（rd- で始まるクラス）が、共有スタイルで描かれるかを調べる。

図の部品は css/register-diagram.css で描く。次の2つの誤りは、図が崩れても
HTML としては正しく、ソースを読むレビューでは気づきにくい。

- rd- のクラスを使っているのに、ページが css/register-diagram.css を読み込んでいない
  （マス目が描かれず、文字が横に並ぶだけになる）
- css/register-diagram.css に無い rd- のクラスを使っている（打ち間違いなど）

    python3 scripts/check-register-diagram.py

終了コード: 0 = 問題なし、1 = 問題がある。
"""

import glob
import os
import posixpath
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = "css/register-diagram.css"


def same_file(href):
    """href が CSS を指すか。./ や ?v=2 などの付いた書き方も同じファイルとみなす。"""
    if not href:
        return False
    path = re.split(r"[?#]", href.strip(), maxsplit=1)[0]
    return posixpath.normpath(path) == CSS


class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.classes = {}  # rd- のクラス → 最初に現れた行
        self.links = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        rel = (a.get("rel") or "").lower().split()
        # 代替のスタイルシート（alternate）は、既定では読み込まれない
        if tag == "link" and "stylesheet" in rel and "alternate" not in rel and same_file(a.get("href")):
            self.links = True
        for c in (a.get("class") or "").split():
            if c.startswith("rd-"):
                self.classes.setdefault(c, self.getpos()[0])


def main():
    css_path = os.path.join(ROOT, CSS)
    if not os.path.exists(css_path):
        print(f"{CSS} が無い")
        return 1
    with open(css_path, encoding="utf-8") as f:
        css = re.sub(r"/\*.*?\*/", "", f.read(), flags=re.S)
    defined = set(re.findall(r"\.(rd-[A-Za-z0-9_-]+)", css))

    pages = sorted(glob.glob(os.path.join(ROOT, "*.html")))
    problems = []
    for path in pages:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            # フロー JSON などの文字列の中のクラスを数えないよう、HTML として解析する
            scan = Scan()
            scan.feed(f.read())
        if scan.classes and not scan.links:
            problems.append(f'{name}: rd- のクラスを使っているのに <link rel="stylesheet" href="{CSS}"> を読み込んでいない')
        for c, line in sorted(scan.classes.items(), key=lambda x: x[1]):
            if c not in defined:
                problems.append(f"{name}:{line}: {c} は {CSS} に無い")
    for p in problems:
        print(p)
    print(f"\n{len(pages)} pages checked, {len(problems)} problems found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
