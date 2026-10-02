#!/usr/bin/env python3
"""Dashboard 2.0 のフローが CLAUDE.md「Dashboard 2.0 のフロー」の決まりを守っているかを検査する。

Dashboard 2.0 では、/dashboard にダッシュボード設定ノード（ui-base）が2つ以上あると、
先に作られた1つのページしか配信されない。利用者がサイトの複数のフローを読み込んでも
ページが消えないよう、サイトの Dashboard 2.0 のフローはすべて1つの ui-base を共有する。
この状態は、次の決まりがすべて成り立つときに保たれる。

1. ui-base はブロックに1つだけで、ID は共有 ID（SHARED_BASE）
2. ui-base を参照する欄（"ui"）は、空でなければ共有 ID を指す
3. 設定ノードは ui-base → ui-theme → ui-page → ui-group の順に並ぶ
   （エディタの「コピーを読み込み」では依存順の並べ替えが働かず、参照先より先に追加された
   設定ノードは参照先の利用者として登録されない。使用中のページやテーマが「未使用」と
   表示され、案内に従って削除されてしまう）
4. ID が、サイト内の他のどのフローとも重ならない。例外は共有 ui-base と、
   中身が同一の公式テーマ（ALLOWED_SHARED）だけ
   （ID が1つでも重なると、エディタは通知を出し、利用者は「コピーを読み込み」を選ぶ。
   このとき、まだ存在しない設定ノードには新しい ID が振られる。最初に読み込んだ
   Dashboard 2.0 のフローでこれが起きると、ui-base が共有 ID で作られず、2つに分かれる）
5. ページのパスがサイト全体で一意（ページを共有すると、コピーの読み込みで同じパスの
   ページが別 ID で2つできる。決まり4によりページの ID は共有されないので、パスの重複を見る）
6. Dashboard 2.0 のガイド（nodered-dashboard2-*.html）に、複数のフローを読み込むときの案内がある

決まり4・5は、サイト内のどのフローをどの順で読み込んでも ui-base が1つに保たれることの
十分条件である（2026-10-02、各 Dashboard フローの前に他の全フローを1つずつ読み込む
模擬と、エディタ本体での読み込みで確認した）。

フロー JSON は validate-flow-json.py と同じ方法で取り出し、利用者がコピーで受け取る文字列を
検査する。JSON として読めないブロックは validate-flow-json.py が報告するので、ここでは飛ばす。
決まり4・5はファイルをまたぐため、常にサイトの全 HTML を対象にする。
"""

import fnmatch
import glob
import importlib.util
import json
import os
import sys
from collections import defaultdict
from html.parser import HTMLParser

SHARED_BASE = "c2e1aa56f50f03bd"
# 中身が同一であれば、複数のフローで共有してよい公式テーマ（CLAUDE.md の例外一覧と同じ）
ALLOWED_SHARED = {"129e99574def90a3", "afa24cae12543ca5", "c2ff5ba1f92a0f0e"}
CONFIG_RANK = {"ui-base": 0, "ui-theme": 1, "ui-page": 2, "ui-group": 3}
GUIDE_GLOB = "nodered-dashboard2-*.html"
NOTICE = "📌 複数のフローを読み込むとき"

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("validate_flow_json", os.path.join(_here, "validate-flow-json.py"))
_vfj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vfj)


def load_blocks(paths):
    """全ファイルの flow-json ブロックを (path, line, nodes, start) で返す。
    同じ行に複数のブロックが並ぶこともあるので、ブロックの区別には開始位置（start）を使う"""
    blocks = []
    root = os.path.dirname(_here)
    for full in paths:
        src = open(full, encoding="utf-8").read()
        path = os.path.relpath(full, root)  # 表示はリポジトリからの相対パス
        # validate-flow-json.py の CLASS_ATTR による事前の絞り込みは使わない。
        # 二重引用符の class 属性にしか合わず、class='flow-json' のブロックを静かに取りこぼすため。
        # ブロックの判定は HTMLParser（属性の引用符の種類に依存しない）だけに任せる
        parser = _vfj.FlowJsonExtractor(src)
        parser.feed(src)
        parser.close()
        for b in parser.blocks:
            try:
                nodes = json.loads(b["delivered"])
            except ValueError:
                continue
            if isinstance(nodes, list):
                nodes = [n for n in nodes if isinstance(n, dict) and "id" in n]
                blocks.append((path, b["line"], nodes, b["start"]))
    return blocks


def is_dashboard(nodes):
    # ui-base を書き忘れたフローも検査の対象にするため、Dashboard 2.0 のノード（ui- で始まる型）の有無で判定する
    return any(str(n.get("type", "")).startswith("ui-") for n in nodes)


def check_block(path, line, nodes):
    """決まり1〜3（ブロック単体で判定できるもの）"""
    errors = []
    at = f"{path}:{line}"
    bases = [n for n in nodes if n.get("type") == "ui-base"]
    if len(bases) != 1:
        errors.append(f"{at}: ui-base が {len(bases)} 個ある（1つにして共有 ID {SHARED_BASE} にする）")
    for b in bases:
        if b["id"] != SHARED_BASE:
            errors.append(f"{at}: ui-base の ID が {b['id']}（共有 ID {SHARED_BASE} にする）")
    for n in nodes:
        if n.get("type") == "ui-group" and not n.get("page"):
            errors.append(f"{at}: ui-group {n['id']} の page が空（ページに属さないグループは表示されない）")
        if "ui" not in n and n.get("type") != "ui-page":
            continue
        ui = n.get("ui", "")
        # ui-page は必ず共有 ui-base を指す。ほかのノードの ui は、空文字（ui-template の
        # グループ単位の表示など、ui-base を使わない設定）か共有 ID だけを許す（型は問わない）
        if n.get("type") == "ui-page" or ui != "":
            if ui != SHARED_BASE:
                errors.append(f"{at}: {n.get('type')} {n['id']} の ui が {ui!r}（共有 ID {SHARED_BASE} を指すこと）")
    ids = [n["id"] for n in nodes]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errors.append(f"{at}: 同じフローの中で ID が重なっている（{', '.join(dup)}）")
    # 参照先がそのフローの中に無いと、そのフローだけを読み込んだ利用者の画面が壊れる
    types = {n["id"]: n.get("type") for n in nodes}
    for n in nodes:
        for key, want in (("group", "ui-group"), ("page", "ui-page"), ("theme", "ui-theme")):
            ref = n.get(key)
            if not (isinstance(ref, str) and ref):
                continue
            if ref not in types:
                errors.append(f"{at}: {n.get('type')} {n['id']} の {key} が指す {ref} がこのフローの中に無い")
            elif types[ref] != want:
                errors.append(f"{at}: {n.get('type')} {n['id']} の {key} が {types[ref]} を指している（{want} を指すこと）")
    seq = [(CONFIG_RANK[n["type"]], n) for n in nodes if n.get("type") in CONFIG_RANK]
    for (r1, n1), (r2, n2) in zip(seq, seq[1:]):
        if r2 < r1:
            errors.append(
                f"{at}: 設定ノードの順序が逆（{n1['type']} {n1['id']} の後に {n2['type']} {n2['id']}）。"
                "ui-base → ui-theme → ui-page → ui-group の順に並べる"
            )
            break
    return errors


def comparable(node):
    """中身の比較用（座標は除く）"""
    return json.dumps({k: v for k, v in node.items() if k not in ("x", "y")}, sort_keys=True, ensure_ascii=False)


def check_site(blocks):
    """決まり4・5（ファイルをまたぐもの）"""
    errors = []
    where = defaultdict(list)  # id -> [(path, line, node, start)]
    for path, line, nodes, start in blocks:
        for n in nodes:
            where[n["id"]].append((path, line, n, start))

    for path, line, nodes, start in blocks:
        if not is_dashboard(nodes):
            continue
        for n in nodes:
            nid = n["id"]
            others = [w for w in where[nid] if (w[0], w[3]) != (path, start)]
            if not others:
                continue
            # 共有 ui-base の ID は、重なる相手もすべて ui-base のときだけ許す
            # （ほかのフローのタブなどが同じ ID を持つと、最初の Dashboard の読み込みで衝突する）
            if nid == SHARED_BASE and n.get("type") == "ui-base" and all(w[2].get("type") == "ui-base" for w in others):
                continue
            if nid in ALLOWED_SHARED and n.get("type") == "ui-theme":
                diff = [w for w in others if comparable(w[2]) != comparable(n)]
                if diff:
                    errors.append(f"{path}:{line}: 共有するテーマ {nid} の中身が {diff[0][0]}:{diff[0][1]} と違う")
                continue
            o = others[0]
            errors.append(
                f"{path}:{line}: ID {nid}（{n.get('type')}）が {o[0]}:{o[1]} のフローと重なる"
                "（ガイドごとの接頭辞を付けて一意にする）"
            )

    paths = defaultdict(list)  # page path -> [(path, line, page id)]
    for path, line, nodes, _start in blocks:
        if not is_dashboard(nodes):
            continue
        for n in nodes:
            if n.get("type") == "ui-page":
                paths[n.get("path")].append((path, line, n["id"]))
    for page_path, uses in paths.items():
        if len({u[2] for u in uses}) > 1:
            a, b = uses[0], next(u for u in uses if u[2] != uses[0][2])
            errors.append(f"{b[0]}:{b[1]}: ページのパス {page_path} が {a[0]}:{a[1]} のページと重なる")
    return errors


class TipText(HTMLParser):
    """<div class="tip"> の中の、表示されるテキストを集める（HTML コメントと script・style の中身は含めない）"""

    HIDDEN = {"script", "style"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0  # tip の div の中での div の入れ子の深さ（0 なら tip の外）
        self.texts = []
        self.hidden = 0  # script・style の中にいるか

    def handle_starttag(self, tag, attrs):
        if tag in self.HIDDEN:
            self.hidden += 1
            return
        if tag != "div":
            return
        if self.depth:
            self.depth += 1
        elif "tip" in (dict(attrs).get("class") or "").split():
            self.depth = 1
            self.texts.append("")

    def handle_endtag(self, tag):
        if tag in self.HIDDEN and self.hidden:
            self.hidden -= 1
            return
        if tag == "div" and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth and not self.hidden:
            self.texts[-1] += data


def check_notice(blocks):
    """決まり6"""
    errors = []
    root = os.path.dirname(_here)
    for path in sorted({b[0] for b in blocks if is_dashboard(b[2])}):
        if not fnmatch.fnmatch(os.path.basename(path), GUIDE_GLOB):
            continue
        # ソース全体を文字列で探すと、コメントに文言だけを残した場合も通ってしまう。
        # 表示される tip の中に案内があるかを見る
        parser = TipText()
        parser.feed(open(os.path.join(root, path), encoding="utf-8").read())
        if not any(NOTICE in text for text in parser.texts):
            errors.append(f"{path}: 「{NOTICE}」の案内が無い（サンプルフローと演習の節の冒頭に入れる）")
    return errors


def main():
    if sys.argv[1:]:
        print("引数は使わない（ファイルをまたぐ決まりを見るため、常にサイトの全 HTML を検査する）", file=sys.stderr)
    root = os.path.dirname(_here)
    paths = sorted(glob.glob(os.path.join(root, "*.html")))
    blocks = load_blocks(paths)
    dash = [b for b in blocks if is_dashboard(b[2])]

    errors = []
    for path, line, nodes, _start in dash:
        errors.extend(check_block(path, line, nodes))
    errors.extend(check_site(blocks))
    errors.extend(check_notice(blocks))

    # 対象が見つからないまま成功扱いにしない（静かに素通りする失敗を防ぐ）
    if not any(fnmatch.fnmatch(os.path.basename(p), GUIDE_GLOB) for p, *_ in dash):
        errors.append(f"{os.path.basename(root)}: Dashboard 2.0 のガイド（{GUIDE_GLOB}）のフローが1つも見つからない")

    for e in errors:
        print(e)
    print(f"\n{len(dash)} Dashboard flows in {len({b[0] for b in dash})} files checked "
          f"(against {len(blocks)} flows), {len(errors)} problems found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
