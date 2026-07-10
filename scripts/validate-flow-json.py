#!/usr/bin/env python3
"""サンプルフロー JSON の検証。

利用者はコピーボタン経由でフローを受け取る。コピーボタンは DOM の textContent を
読むため、ブラウザが解釈してしまうマークアップ（<html>, <style>, <a> など）が
flow-json ブロックに生のまま置かれていると、タグが消えた文字列が配布される。
破損しても JSON としては valid なままなので、json.loads だけでは検出できない。

そこで「ソースに書いた JSON」と「利用者が受け取る JSON」を突き合わせる。
"""

import glob
import html
import json
import re
import sys
from html.parser import HTMLParser

OPEN_TAG = '<div class="flow-json">'
MARKUP = re.compile(r"</?[A-Za-z][^>\s]*|<!\w+|<\?\w+")


def iter_blocks(src):
    """flow-json ブロックの中身を、div のネストを数えながら取り出す。"""
    for m in re.finditer(re.escape(OPEN_TAG), src):
        i, depth = m.end(), 1
        for t in re.finditer(r"<(/?)div\b", src[i:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                yield m.start(), src[i : i + t.start()]
                break


class TextContent(HTMLParser):
    """ブラウザの Node.textContent を再現する。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    @classmethod
    def of(cls, markup):
        parser = cls()
        parser.feed(markup)
        parser.close()
        return "".join(parser.parts)


def check(path):
    src = open(path, encoding="utf-8").read()
    errors = []

    for offset, raw in iter_blocks(src):
        line = src.count("\n", 0, offset) + 1
        intended = html.unescape(raw)
        delivered = TextContent.of(raw)

        if delivered != intended:
            lost = ", ".join(MARKUP.findall(raw)[:3])
            errors.append(
                f"{path}:{line}: コピー時にマークアップが失われる。"
                f"生タグを HTML エスケープすること（例: {lost}）"
            )
            continue

        try:
            flow = json.loads(delivered)
        except json.JSONDecodeError as e:
            errors.append(f"{path}:{line}: JSON がパースできない: {e}")
            continue

        if not isinstance(flow, list):
            errors.append(f"{path}:{line}: フローは配列でなければならない")
            continue

        ids = {n.get("id") for n in flow if isinstance(n, dict)}
        for node in flow:
            if not isinstance(node, dict) or "id" not in node or "type" not in node:
                errors.append(f"{path}:{line}: id / type を持たないノードがある")
                break
            for port in node.get("wires") or []:
                for target in port:
                    if target not in ids:
                        errors.append(
                            f"{path}:{line}: ノード {node['id']} の接続先 "
                            f"{target} がフロー内に存在しない"
                        )

    return errors


def main():
    targets = sys.argv[1:] or sorted(glob.glob("*.html"))
    errors = []
    checked = 0

    for path in targets:
        if OPEN_TAG not in open(path, encoding="utf-8").read():
            continue
        checked += 1
        errors.extend(check(path))

    for e in errors:
        print(e)
    print(f"\n{checked} files checked, {len(errors)} problems found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
