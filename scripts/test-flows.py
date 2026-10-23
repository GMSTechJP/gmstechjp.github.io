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
- 動かすブロックの inject は、すべて "inject" で押すか、"skip_inject" に理由を書く。
  debug（有効なもの）は、すべて "expect" で確かめるか、"skip_debug" に理由を書く。
  inject と debug には名前を付ける（名前で指定するため）。確かめない部分を黙って残せないようにするため
- http in の待ち受けは、"requests" で呼ぶか、同じフローの http request が localhost:1880 の
  URL で呼んでいるか、"skip_http" に理由を書く（"GET /api/users/:id" の形で書く）
- expect の "absent": true は、その debug に何も届かないことを確かめる（届いてはいけない経路の確認）
- "requests" は、テストの実行役が送る HTTP リクエスト。応答のステータス（status、既定 200）、
  本文（contains / not_contains / match）、Content-Type（content_type）を確かめる。
  "save": {"id": "note.id"} で応答の値を覚え、後の path に {id} と書いて使える
- エラーの経路をわざと通すとき、そのノードのステータスが赤・黄になるのを許すには、
  "allow_status" にノードの名前と理由を書く
- http request が手元以外のホスト（外部の API など）を呼ぶときは、そのホストを "external" に書く。
  --external-warn を付けると、その記載の不合格は警告にとどめる（デプロイの前に使う。
  外部のサービスが一時的に止まっただけで、ほかの修正の公開を止めないため）
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
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC_PATH = os.path.join(ROOT, "tests", "flow-tests.json")

_spec = importlib.util.spec_from_file_location(
    "live_check_flow", os.path.join(HERE, "live-check-flow.py"))
live = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(live)

ENTRY_KEYS = {"expect", "inject", "with", "covered_by", "manual", "skip_inject", "skip_debug",
              "requests", "skip_http", "allow_status", "external", "override", "wait", "after", "gap",
              "allow_unsafe", "note"}
REQUEST_KEYS = {"method", "path", "json", "body", "headers", "status", "contains", "not_contains",
                "match", "content_type", "save"}
# 同じフローの http request が待ち受けを呼んでいると見なす送り先（このサイトのフローは 1880 を使う）
SELF_HOSTS = ("localhost:1880", "127.0.0.1:1880")
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


def endpoint_key(method, url):
    """http in の待ち受けを "GET /api/users/:id" の形にそろえる。"""
    return f"{str(method or 'get').upper()} {live.route(url)}"


def endpoint_regex(url):
    """http in の URL（:id などの引数を含む）に合うパスの正規表現。大文字・小文字と末尾の / は区別しない。"""
    parts = [("[^/]+" if p.startswith(":") else re.escape(p)) for p in live.route(url).split("/")]
    return re.compile("^" + "/".join(parts).rstrip("/") + "/?$", re.IGNORECASE)


def http_endpoints(flow):
    """有効な http in の待ち受け（method, url）。"""
    return [(str(n.get("method") or "get"), n.get("url")) for n in flow
            if n.get("type") == "http in" and not n.get("d")]


def self_calls(flow):
    """同じフローの http request が、設定の URL で呼んでいる（method, パス）。"""
    calls = []
    for n in flow:
        u = str(n.get("url") or "")
        if n.get("type") == "http request" and not n.get("d") and any(h in u for h in SELF_HOSTS):
            calls.append((str(n.get("method") or "GET"), urllib.parse.urlsplit(u).path))
    return calls


def external_hosts(flow, override):
    """http request が設定の URL で呼ぶ、手元以外のホスト（override で書き換えた後の値で見る）。"""
    hosts = set()
    for n in flow:
        if n.get("type") != "http request" or n.get("d"):
            continue
        u = str({**n, **override.get(n["id"], {})}.get("url") or "")
        host = urllib.parse.urlsplit(u).hostname
        if host and host not in ("localhost", "127.0.0.1") and "{{" not in u:
            hosts.add(host)
    return hosts


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
        if not e.get("debug") or len({"contains", "match", "absent"} & set(e)) != 1 \
                or "absent" in e and e["absent"] is not True:
            errs.append(f"{where}: expect の各件は debug と、contains・match・absent（true）のどれか1つを書く: {e}")

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
    for r in entry.get("requests", []):
        bad = set(r) - REQUEST_KEYS
        if bad or not str(r.get("path", "")).startswith("/") or "json" in r and "body" in r:
            errs.append(f"{where}: requests の書き方が誤っている（path は / で始め、json と body は一方だけ）: {r}")
    # http in の待ち受けは、requests で呼ぶか、同じフローの http request が呼ぶか、理由を書いて外す
    calls = [(str(r.get("method", "GET")), urllib.parse.urlsplit(r.get("path", "")).path)
             for r in entry.get("requests", [])] + self_calls(flow)
    skipped = set(entry.get("skip_http", {}))
    endpoints = {endpoint_key(m, u) for m, u in http_endpoints(flow)}
    for m, u in http_endpoints(flow):
        key = endpoint_key(m, u)
        hit = any(cm.upper() == m.upper() and endpoint_regex(u).match(cp) for cm, cp in calls)
        if not hit and key not in skipped:
            errs.append(f"{where}: 待ち受け {key} を requests で呼ぶか、skip_http に理由を書く")
    for key in sorted(skipped - endpoints):
        errs.append(f"{where}: skip_http の {key} が、動かすブロックに無い")
    for key, reason in entry.get("skip_http", {}).items():
        if not str(reason).strip():
            errs.append(f"{where}: 「{key}」を確かめない理由を書く")
    # 外部のサービスに頼る部分は、どのホストに頼るかを external に書く（CI で扱いを分けるため）
    needed = external_hosts(flow, entry.get("override", {}))
    listed = set(entry.get("external", []))
    for host in sorted(needed - listed):
        errs.append(f"{where}: 外部のホスト {host} を呼んでいる。external に書く")
    for host in sorted(listed - needed):
        errs.append(f"{where}: external の {host} を、動かすブロックの http request が呼んでいない")
    for name, reason in entry.get("allow_status", {}).items():
        if not any(n.get("name") == name for n in flow):
            errs.append(f"{where}: allow_status のノード「{name}」が、動かすブロックに無い")
        if not str(reason).strip():
            errs.append(f"{where}: allow_status の「{name}」に、赤・黄を許す理由を書く")
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


def apply_override(block, override, port_offset=0, node_red_port=1880):
    """ノードの設定を書き換えた写しを返す（例: 相手の PC の IP を 127.0.0.1 にする）。

    port_offset を指定すると、TCP・UDP のポート番号をずらす。手元の Node-RED で、
    利用者が読み込み済みの同じフロー（同じポートで待ち受けている）と重ならないようにするため。
    node_red_port が 1880 でないときは、フローが自分自身を呼ぶ :1880 を、
    動かしている Node-RED のポートに書き換える（手元で別のポートに起動して動かすため）。
    """
    b = copy.deepcopy(block)
    for n in b["flow"]:
        n.update(override.get(n["id"], {}))
        for field in PORT_FIELDS.get(n.get("type"), ()):
            if port_offset and str(n.get(field, "")).isdigit():
                n[field] = str(int(n[field]) + port_offset)
        if node_red_port != 1880 and n.get("type") != "comment":
            for k, v in n.items():
                n[k] = to_port(v, node_red_port)
    return b


def to_port(value, port):
    """値（入れ子を含む）の中の :1880 を、指定のポートに書き換える。

    localhost:1880 だけでなく、テンプレートで組み立てる URL（http://{{targetIp}}:1880/...）も
    自分の Node-RED を呼ぶため、:1880 をすべて書き換える。
    """
    if isinstance(value, str):
        return re.sub(r":1880\b", f":{port}", value)
    if isinstance(value, list):
        return [to_port(v, port) for v in value]
    if isinstance(value, dict):
        return {k: to_port(v, port) for k, v in value.items()}
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--url", default="http://localhost:1880", help="Node-RED の URL")
    ap.add_argument("--coverage", action="store_true", help="記載の漏れだけ調べる（Node-RED 不要）")
    ap.add_argument("--guide", help="このガイドだけ動かす")
    ap.add_argument("--tab", help="このタブの記載だけ動かす（--guide と一緒に使う）")
    ap.add_argument("--external-warn", action="store_true",
                    help="外部のサービスに頼る記載（external）の不合格を、警告にとどめる（デプロイの前に使う）")
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
            port = urllib.parse.urlsplit(url).port or 80
            picked = [apply_override(by_tab[t], entry.get("override", {}), args.port_offset, port)
                      for t in [tab] + entry.get("with", [])]
            opts = {k: entry.get(k, v) for k, v in DEFAULTS.items()}
            try:
                code = live.check(url, picked, f"{guide} {tab}",
                                  inject=entry.get("inject", []), expect=entry["expect"],
                                  requests=entry.get("requests", []),
                                  allow_status=set(entry.get("allow_status", {})),
                                  allow_unsafe=entry.get("allow_unsafe", False), **opts)
            except live.LiveCheckError as e:
                print(f"実行できなかった: {e}")
                code = 2
            result = {0: "合格", 1: "不合格"}.get(code, "実行できなかった")
            note = ""
            if result == "不合格" and entry.get("external") and args.external_warn:
                # 外部のサービスが一時的に止まっただけで、ほかの修正の公開を止めないため。
                # 実行できなかった（一時的なタブを消せないなど）ときは、警告にしない
                result, note = "警告", f"外部のサービス（{', '.join(entry['external'])}）に頼る記載"
            results.append((guide, tab, result, note))

    print("\n===== まとめ =====")
    for guide, tab, result, note in results:
        if result == "manual":
            note = f"CI では動かさない: {note}"
        print(f"  {result:<8} {guide} / {tab}" + (f"（{note}）" if note else ""))
    if any(r == "実行できなかった" for _, _, r, _ in results):
        return 2
    return 1 if any(r == "不合格" for _, _, r, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
