#!/usr/bin/env python3
"""表のあるページが、表の列幅を整えるスクリプト（js/table-fit.js）を読み込んでいるか調べる。

表は幅 100% の自動レイアウトのため、説明文のような長い列があると、項目名のような
短い列まで少しずつ縮められ、あと数文字分の幅が足りずに折り返す。js/table-fit.js は
描画後に列の幅を測り、短い列を 1 行に保つ。読み込みを忘れても表示は崩れず、
折り返しが戻るだけなので、見た目の確認では気づきにくい。

    python3 scripts/check-table-fit.py

終了コード: 0 = すべて読み込んでいる、1 = 読み込んでいないページがある。
"""

import glob
import os
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = "js/table-fit.js"


class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = 0
        self.loads = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self.tables += 1
        elif tag == "script" and a.get("src") == SCRIPT and "defer" in a:
            self.loads = True


def main():
    pages = sorted(glob.glob(os.path.join(ROOT, "*.html")))
    if not os.path.exists(os.path.join(ROOT, SCRIPT)):
        print(f"{SCRIPT} が無い")
        return 1
    missing = []
    for path in pages:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        # フロー JSON などの文字列の中の <table> を数えないよう、HTML として解析する
        scan = Scan()
        scan.feed(text)
        if scan.tables and not scan.loads:
            missing.append(os.path.basename(path))
    for name in missing:
        print(f'{name}: 表があるのに <script src="{SCRIPT}" defer></script> を読み込んでいない')
    print(f"\n{len(pages)} pages checked, {len(missing)} problems found")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
