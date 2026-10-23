#!/usr/bin/env python3
"""ガイドのフローを Node-RED で実際に動かし、tests/flow-tests.json に書いた結果になるか確かめる。

フローの書き方の検査（validate-flow-json.py）は、動かしたときの結果を調べない。
送る側と受ける側の区切り文字が食い違うフロー（実例: TCP ガイドのサンプルフローは、
送る側が改行を付けず、受ける側が改行を待ち続けて止まっていた）も、書き方は正しいので
検査を通る。手で動かす live-check-flow.py は、使うかどうかが作業する人の判断任せで、
サンプルフローが一度も動かされないまま残った。そこで、何を確かめるかをファイルに書き、
CI で全部を動かす。

tests/flow-tests.json に載せたガイド（対象のガイド）では、次をすべて満たさないと失敗にする。
動かさないまま、または一部だけ確かめないまま、フローを公開できないようにするため。

- フローのブロックは、どれもタブを1つだけ持ち、そのタブの ID で記載されている
- 記載は次のどれか1つ
    "expect"     動かして確かめる（"inject" で押すボタン、"with" で一緒に動かすタブも書ける）
    "covered_by" ほかのタブの記載の "with" で一緒に動かしている
    "manual"     CI では動かせない。理由を書く（実機、外部サービスなど）
- 動かすブロックの inject（名前のあるもの）は、すべて "inject" で押すか、
  "skip_inject" に理由を書く。debug（有効なもの）は、すべて "expect" で確かめるか、
  "skip_debug" に理由を書く。確かめない部分を黙って残せないようにするため
- 記載のタブがガイドに無い（タブの ID を変えた・消した）ときも失敗にする

対象でないガイドは、ブロックの数を表示するだけで失敗にしない（順に対象を広げるため）。

使い方:
    python3 scripts/test-flows.py                      # 対象の全ガイドを動かす
    python3 scripts/test-flows.py --coverage           # 記載の漏れだけ調べる（Node-RED 不要）
    python3 scripts/test-flows.py --guide nodered-tcp-node-guide.html --tab tcp_sample_tab
    python3 scripts/test-flows.py --port-offset 10000  # 手元で、読み込み済みのフローと重ねない

手元の Node-RED で動かすときは、利用者のフローと待ち受けが重なると中止する
（live-check-flow.py と同じ）。CI では空の Node-RED を起動して動かす。

終了コード: 0 = 合格、1 = 不合格（記載の漏れを含む）、2 = 実行できなかった。
"""

import argparse
import copy
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC_PATH = os.path.join(ROOT, "tests", "flow-tests.json")

_spec = importlib.util.spec_from_file_location(
    "live_check_flow", os.path.join(HERE, "live-check-flow.py"))
live = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(live)

ENTRY_KEYS = {"expect", "inject", "with", "covered_by", "manual", "skip_inject", "skip_debug",
              "override", "wait", "after", "gap", "allow_unsafe", "note"}
DEFAULTS = {"wait": 3, "after": 3, "gap": 1}


def tab_of(block):
    tabs = [n for n in block["flow"] or [] if n.get("type") == "tab"]
    return tabs[0]["id"] if len(tabs) == 1 else None


def guide_blocks(guide):
    """ガイドのブロックを、タブの ID ごとにまとめる。問題は errors に足す。"""
    errors = []
    blocks = live.load_blocks(os.path.join(ROOT, guide))
    by_tab = {}
    for b in blocks:
        tab = tab_of(b)
        if tab is None:
            errors.append(f"{guide} {b['line']}行目: ブロックがタブをちょうど1つ持っていない")
        elif tab in by_tab:
            errors.append(f"{guide} {b['line']}行目: タブの ID「{tab}」が別のブロックと重なる")
        else:
            by_tab[tab] = b
    return blocks, by_tab, errors


def active_debugs(flow):
    return [n for n in flow if n.get("type") == "debug"
            and n.get("active", True) is not False and not n.get("d")]


def check_entry(guide, tab, entry, spec, by_tab):
    """1つの記載を調べる。問題の一覧を返す。"""
    where = f"{guide} の {tab}"
    errs = []
    unknown = set(entry) - ENTRY_KEYS
    if unknown:
        errs.append(f"{where}: 知らないキー {', '.join(sorted(unknown))}")
    kinds = [k for k in ("expect", "covered_by", "manual") if k in entry]
    if len(kinds) != 1:
        return errs + [f"{where}: expect・covered_by・manual のどれか1つを書く（{kinds or 'どれも無い'}）"]
    kind = kinds[0]
    if kind != "expect" and "with" in entry:
        errs.append(f"{where}: with は expect の記載にだけ書ける（manual・covered_by では一緒に動かさない）")
    if kind == "manual":
        if not str(entry["manual"]).strip():
            errs.append(f"{where}: manual に CI で動かせない理由を書く")
        return errs
    if kind == "covered_by":
        owner = spec.get(entry["covered_by"], {})
        if "expect" not in owner:
            # manual や covered_by の記載を指すと、このタブはどこでも動かない
            errs.append(f"{where}: covered_by の {entry['covered_by']} が、動かして確かめる記載（expect）でない")
        elif tab not in owner.get("with", []):
            errs.append(f"{where}: covered_by の {entry['covered_by']} が with に {tab} を書いていない")
        return errs

    for t in entry.get("with", []):
        if t not in by_tab:
            errs.append(f"{where}: with のタブ {t} がガイドに無い")
        elif spec.get(t, {}).get("covered_by") != tab:
            errs.append(f"{where}: with の {t} の記載を {{\"covered_by\": \"{tab}\"}} にする")
    flow = [n for t in [tab] + entry.get("with", []) if t in by_tab for n in by_tab[t]["flow"]]
    for e in entry["expect"]:
        if not e.get("debug") or len({"contains", "match"} & set(e)) != 1:
            errs.append(f"{where}: expect の各件は debug と、contains か match のどちらかを書く: {e}")

    injects = {n.get("name") for n in flow if n.get("type") == "inject"}
    if None in injects or "" in injects:
        errs.append(f"{where}: 名前の無い inject がある（押すボタンを名前で指定するため、名前を付ける）")
    pressed = set(entry.get("inject", [])) | set(entry.get("skip_inject", {}))
    for name in sorted(n for n in injects if n):
        if name not in pressed:
            errs.append(f"{where}: inject「{name}」を inject で押すか、skip_inject に理由を書く")
    for name in sorted(pressed - injects):
        errs.append(f"{where}: inject「{name}」が、動かすブロックに無い（名前を変えたなら記載も直す）")
    if any(not n.get("name") for n in active_debugs(flow)):
        errs.append(f"{where}: 名前の無い debug がある（確かめる debug を名前で指定するため、名前を付ける）")
    debugs = {n["name"] for n in active_debugs(flow) if n.get("name")}
    checked = {e.get("debug") for e in entry["expect"]} | set(entry.get("skip_debug", {}))
    for name in sorted(debugs - checked):
        errs.append(f"{where}: debug「{name}」を expect で確かめるか、skip_debug に理由を書く")
    for name in sorted(checked - debugs):
        errs.append(f"{where}: debug「{name}」が、動かすブロックに無い（または無効）")
    for name, reason in {**entry.get("skip_inject", {}), **entry.get("skip_debug", {})}.items():
        if not str(reason).strip():
            errs.append(f"{where}: 「{name}」を確かめない理由を書く")
    for nid in entry.get("override", {}):
        if not any(n["id"] == nid for n in flow):
            errs.append(f"{where}: override のノード {nid} が、動かすブロックに無い")
    return errs


def coverage(spec_all):
    """記載の漏れを調べる。(問題の一覧, 対象のガイド→(ブロック, タブ→ブロック)) を返す。"""
    errors, loaded = [], {}
    for guide, spec in spec_all["guides"].items():
        if not os.path.exists(os.path.join(ROOT, guide)):
            errors.append(f"{guide}: ファイルが無い")
            continue
        blocks, by_tab, errs = guide_blocks(guide)
        errors += errs
        loaded[guide] = (blocks, by_tab)
        for tab in by_tab:
            if tab not in spec:
                errors.append(f"{guide} の {tab}: 記載が無い（動かして確かめるか、manual に理由を書く）")
        for tab, entry in spec.items():
            if tab not in by_tab:
                errors.append(f"{guide} の {tab}: ガイドにこのタブが無い（ID を変えたなら記載も直す）")
                continue
            errors += check_entry(guide, tab, entry, spec, by_tab)
    return errors, loaded


def untargeted(spec_all):
    """対象でないガイドと、そのブロックの数。"""
    out = []
    for name in sorted(os.listdir(ROOT)):
        if name.endswith(".html") and name not in spec_all["guides"]:
            src = open(os.path.join(ROOT, name), encoding="utf-8").read()
            if "flow-json" in src:
                out.append((name, len(live.load_blocks(os.path.join(ROOT, name)))))
    return out


# 待ち受けと接続先のポート番号を持つノードと、その欄
PORT_FIELDS = {"tcp in": ("port",), "tcp out": ("port",), "tcp request": ("port",),
               "udp in": ("port",), "udp out": ("port", "outport")}


def apply_override(block, override, port_offset=0):
    """ノードの設定を書き換えた写しを返す（例: 相手の PC の IP を 127.0.0.1 にする）。

    port_offset を指定すると、TCP・UDP のポート番号をずらす。手元の Node-RED で、
    利用者が読み込み済みの同じフロー（同じポートで待ち受けている）と重ならないようにするため。
    """
    b = copy.deepcopy(block)
    for n in b["flow"]:
        n.update(override.get(n["id"], {}))
        for field in PORT_FIELDS.get(n.get("type"), ()):
            if port_offset and str(n.get(field, "")).isdigit():
                n[field] = str(int(n[field]) + port_offset)
    return b


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--url", default="http://localhost:1880", help="Node-RED の URL")
    ap.add_argument("--coverage", action="store_true", help="記載の漏れだけ調べる（Node-RED 不要）")
    ap.add_argument("--guide", help="このガイドだけ動かす")
    ap.add_argument("--tab", help="このタブの記載だけ動かす（--guide と一緒に使う）")
    ap.add_argument("--port-offset", type=int, default=0,
                    help="TCP・UDP のポート番号をずらして動かす（手元で、読み込み済みのフローと重ならないように）")
    args = ap.parse_args()
    url = args.url.rstrip("/")

    try:
        spec_all = json.load(open(SPEC_PATH, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"実行できなかった: {SPEC_PATH} を読めない: {e}")
        return 2

    errors, loaded = coverage(spec_all)
    rest = untargeted(spec_all)
    print(f"対象のガイド: {len(loaded)} 件。対象でないガイド: {len(rest)} 件"
          f"（ブロック {sum(n for _, n in rest)} 個。動かしていない）")
    if errors:
        print("\n[記載の漏れ・誤り]")
        for e in errors:
            print(f"  NG  {e}")
        return 1
    print("記載の漏れはない")
    if args.coverage:
        return 0

    if args.guide and args.guide not in loaded:
        print(f"実行できなかった: {args.guide} は tests/flow-tests.json の対象のガイドでない")
        return 2
    if args.tab:
        if not args.guide:
            print("実行できなかった: --tab は --guide と一緒に指定する")
            return 2
        entry = spec_all["guides"][args.guide].get(args.tab)
        if entry is None:
            print(f"実行できなかった: {args.guide} に {args.tab} の記載が無い")
            return 2
        if "covered_by" in entry:
            # 演習のタブなどは、一緒に動かす記載（動作確認用フローなど）として動かす
            print(f"{args.tab} は {entry['covered_by']} と一緒に動かす")
            args.tab = entry["covered_by"]

    results = []
    for guide, spec in spec_all["guides"].items():
        if args.guide and guide != args.guide:
            continue
        _, by_tab = loaded[guide]
        for tab, entry in spec.items():
            if args.tab and tab != args.tab:
                continue
            if "manual" in entry:
                results.append((guide, tab, "manual", entry["manual"]))
                continue
            if "covered_by" in entry:
                continue
            print(f"\n===== {guide} / {tab} =====")
            picked = [apply_override(by_tab[t], entry.get("override", {}), args.port_offset)
                      for t in [tab] + entry.get("with", [])]
            opts = {k: entry.get(k, v) for k, v in DEFAULTS.items()}
            try:
                code = live.check(url, picked, f"{guide} {tab}",
                                  inject=entry.get("inject", []), expect=entry["expect"],
                                  allow_unsafe=entry.get("allow_unsafe", False), **opts)
            except live.LiveCheckError as e:
                print(f"実行できなかった: {e}")
                code = 2
            results.append((guide, tab, {0: "合格", 1: "不合格"}.get(code, "実行できなかった"), ""))

    print("\n===== まとめ =====")
    for guide, tab, result, note in results:
        print(f"  {result:<8} {guide} / {tab}" + (f"（CI では動かさない: {note}）" if note else ""))
    if any(r == "実行できなかった" for _, _, r, _ in results):
        return 2
    return 1 if any(r == "不合格" for _, _, r, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
