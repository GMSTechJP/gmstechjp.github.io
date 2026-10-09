#!/usr/bin/env python3
"""ガイドのフローを手元の Node-RED で動かし、ステータスと debug に届いた値を確かめる。

フローの書き方の検査（validate-flow-json.py）は、外部につながるかどうかを調べられない。
MQTT・HTTP request・WebSocket client など外部へ接続するノードは、書き方が正しくても
利用者の Node-RED でつながらないことがある（実例: broker.hivemq.com は mosquitto_sub では
つながるが、Node.js 20 以降の Node-RED では「接続中」のまま止まった）。そこで、利用者と
同じ経路、つまり Node-RED の上でフローを動かして確かめる。

利用者のフローを壊さないため、次のようにする。

- 管理 API の POST /flow で、新しいタブを1つ追加する。既存のタブには触れない
- ノードと設定ノードの ID には、ブロックごとの接頭辞を付ける。同じフローが既に
  読み込まれていても、ブロックどうしで ID が同じでも重ならない
- ID では避けられない重なり（待ち受けのパス・ポート、MQTT の固定のクライアント ID）が
  既存のフローとあるときは、追加しない
- 手元の環境に副作用のあるノード（OS コマンド、ファイルの書き込み、実機など）を含む
  ブロックは、--allow-unsafe を付けない限り動かさない
- 終わったら（失敗しても）DELETE /flow でタブごと消す

タブには、記録用のノードを足す。status ノードはタブ内のノードの最後のステータスを、
有効な debug ノードの手前に足す function は debug が表示する値（「対象」の設定に合わせる。
JSONata のときは msg.payload）を、それぞれフローコンテキストに記録する。記録は
GET /context/flow で読む。

使い方:
    python3 scripts/live-check-flow.py nodered-mqtt-node-guide.html --list
    python3 scripts/live-check-flow.py nodered-mqtt-node-guide.html --blocks 2,3 \\
        --inject "Hello送信" --expect "Hello MQTT!"

判定: 次のどれかに当たると不合格。
- 最後のステータスが赤・黄、または文字が「undefined」のノードがある
- 接続するノード（mqtt in / out、WebSocket client を使う websocket in / out）なのに、
  ステータスが1度も記録されていない
- --expect の文字列が、debug に届いた値のどれにも含まれない
ステータスでは確かめられないノード（http request、tcp、udp、待ち受け側の websocket）を
含むときは、--expect を指定しないと中止する（何も確かめずに合格にしない）。
最後のステータスだけを見るため、途中で失敗して復帰したものは分からない。

終了コード: 0 = 合格、1 = 不合格、2 = 実行できなかった（Node-RED に接続できない、
指定の誤り、既存のフローとの重なり、一時的なタブを消せなかったなど）。
"""

import argparse
import http.client
import importlib.util
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "validate_flow_json", os.path.join(HERE, "validate-flow-json.py"))
validate_flow_json = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_flow_json)

HTTP_TIMEOUT = 10  # 管理 API 1回あたりの待ち時間（秒）

# 手元の環境に副作用があるノード。--allow-unsafe を付けない限り動かさない
UNSAFE_TYPES = {"exec", "file", "daemon", "sqlite", "ftp", "e-mail", "e-mail in"}
UNSAFE_PREFIXES = ("rpi-", "serial ", "modbus-", "mc ", "mcprotocol")

# 接続先へつなぎ、ステータスを出すノード。ステータスが無ければ確かめられていない
def is_connecting(node, configs):
    if node.get("d"):
        return False  # 無効にしたノードは動かない
    t = node.get("type")
    if t in ("mqtt in", "mqtt out"):
        return True
    if t in ("websocket in", "websocket out"):
        return configs.get(node.get("client") or "", {}).get("type") == "websocket-client"
    return False

# 外部につなぐが、ステータスでは確かめられないノード。--expect が必要
UNVERIFIED_TYPES = {"http request", "tcp in", "tcp out", "tcp request", "udp in", "udp out"}

def needs_expect(node, configs):
    if node.get("d"):
        return False
    t = node.get("type")
    if t in UNVERIFIED_TYPES:
        return True
    return t in ("websocket in", "websocket out") and not is_connecting(node, configs)

# ノードの ID を参照するキー。値がどのノードの ID でも置き換える
REF_KEYS = {"wires", "links", "scope", "nodes", "g"}
# ID ではなく中身を表すキー。値がたまたまどれかの ID と同じでも置き換えない
CONTENT_KEYS = {"name", "topic", "payload", "func", "initialize", "finalize", "template",
                "info", "label", "statusVal", "url", "path", "v", "to", "from", "property",
                "env", "value", "clientid", "port", "host", "complete"}

STATUS_RECORDER = """\
// タブ内のノードの最後のステータスを、ノード ID ごとに記録する
const s = flow.get("status") || {};
const src = msg.status.source;
s[src.id] = {name: src.name || "", type: src.type, fill: msg.status.fill || "", text: String(msg.status.text ?? "")};
flow.set("status", s);
return null;"""

# debug ノードが表示する値を、900 文字までの文字列で、最後の 50 件まで記録する
# （管理 API は 1000 文字を超える文字列を切り詰めて返すため、その手前に収める）
RECEIVE_RECORDER = """\
// debug ノード「%(label)s」に届く値を記録する
const v = %(value)s;
let t;
try { t = typeof v === "string" ? v : JSON.stringify(v); } catch (e) { t = String(v); }
if (t === undefined) { t = "undefined"; }
const r = flow.get("received") || [];
r.push({debug: %(name)s, topic: String(msg.topic ?? ""), value: t.slice(0, 900)});
flow.set("received", r.slice(-50));
return null;"""


class LiveCheckError(Exception):
    pass


def api(base, method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as res:
            text = res.read().decode()
            is_json = "json" in (res.headers.get("Content-Type") or "")
    except urllib.error.HTTPError as e:
        raise LiveCheckError(f"{method} {path} が失敗した: HTTP {e.code} {e.read().decode()[:300]}")
    except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
        raise LiveCheckError(f"{base} の Node-RED との通信に失敗した（{method} {path}）: {e}")
    if not is_json or not text.strip():
        return None  # POST /inject などは JSON でなく "OK" を返す
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise LiveCheckError(f"{method} {path} の応答が JSON として読めない: {text[:200]}")


def load_blocks(path):
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        raise LiveCheckError(f"{path} を読めない: {e}")
    parser = validate_flow_json.FlowJsonExtractor(src)
    parser.feed(src)
    parser.close()
    blocks = []
    for b in parser.blocks:
        try:
            flow = json.loads(b["delivered"])
        except json.JSONDecodeError:
            flow = None
        if not (isinstance(flow, list) and all(isinstance(n, dict) and "id" in n for n in flow)):
            flow = None
        blocks.append({"line": b["line"], "flow": flow})
    return blocks


def describe(block):
    if block["flow"] is None:
        return "（フローとして読めない）"
    tabs = [n.get("label", "") for n in block["flow"] if n.get("type") == "tab"]
    types = sorted({n.get("type") for n in block["flow"] if n.get("z")})
    return f"タブ: {', '.join(tabs) or '（なし）'} / ノード: {', '.join(types)}"


def unsafe_types(flow):
    return sorted({n.get("type") for n in flow
                   if n.get("type") in UNSAFE_TYPES
                   or str(n.get("type")).startswith(UNSAFE_PREFIXES)})


def remap(value, ids, config_ids, key=None):
    """ID を参照する値を、接頭辞付きの ID に置き換える。

    配線などの REF_KEYS はすべての ID を、それ以外のキー（broker 欄の設定ノードなど）は
    設定ノードの ID だけを置き換える。CONTENT_KEYS は中身なので置き換えない。
    """
    if key in CONTENT_KEYS:
        return value
    if isinstance(value, str):
        return (ids if key in REF_KEYS else config_ids).get(value, value)
    if isinstance(value, list):
        return [remap(v, ids, config_ids, key) for v in value]
    if isinstance(value, dict):
        return {k: remap(v, ids, config_ids, k) for k, v in value.items()}
    return value


def recorded_value(debug):
    """debug ノードが表示する値を取り出す JavaScript の式。"""
    complete = debug.get("complete")
    if debug.get("targetType") == "jsonata":
        return "msg.payload"  # JSONata の式はここでは評価しない
    if complete in (None, "", "false", "payload"):
        return "msg.payload"
    if complete in (True, "true"):
        # http in の req / res は大きく循環もするので除く（debug の表示でも中身は出ない）
        return "(({req, res, ...rest}) => rest)(msg)"
    return f"RED.util.getMessageProperty(msg, {json.dumps(complete)})"


def build_flow(blocks, prefix, label):
    nodes, configs, env = [], [], {}
    for i, block in enumerate(blocks):
        flow = block["flow"]
        if any(n.get("type", "").startswith("subflow") for n in flow):
            raise LiveCheckError(f"{block['line']}行目のブロックはサブフローを含むため扱えない")
        ids = {n["id"]: f"{prefix}b{i}_{n['id']}" for n in flow}
        # 無効なタブのノードは、一時的なタブでも無効のまま動かさない
        disabled_tabs = {n["id"] for n in flow if n.get("type") == "tab" and n.get("disabled")}
        config_ids = {k: v for k, v in ids.items()
                      if not any(n["id"] == k and (n.get("z") or n.get("type") == "tab")
                                 for n in flow)}
        for n in flow:
            if n.get("type") == "tab":
                # タブの環境変数は、一時的なタブに引き継ぐ
                for e in n.get("env") or []:
                    if env.setdefault(e.get("name"), e) != e:
                        raise LiveCheckError(f"タブの環境変数「{e.get('name')}」がブロックどうしで食い違う")
                continue
            m = remap({k: v for k, v in n.items() if k != "id"}, ids, config_ids)
            m["id"] = ids[n["id"]]
            if n.get("z"):
                if n["z"] in disabled_tabs:
                    m["d"] = True
                m.pop("z")
                nodes.append(m)
            else:
                configs.append(m)

    # 有効な debug ノードへ配線しているノードは、記録用の function にも配線する
    debugs = [n for n in nodes if n.get("type") == "debug"
              and n.get("active", True) is not False and not n.get("d")]
    recorders = {}
    for i, d in enumerate(debugs):
        name = d.get("name") or d["id"]
        rid = f"{prefix}rec{i}"
        recorders[d["id"]] = rid
        func = RECEIVE_RECORDER % {"label": name.replace("\n", " "),
                                   "value": recorded_value(d),
                                   "name": json.dumps(name, ensure_ascii=False)}
        nodes.append({"id": rid, "type": "function", "name": f"記録: {name}", "func": func,
                      "outputs": 0, "x": 900, "y": 40 + 40 * i, "wires": []})
    for n in nodes:
        for port in n.get("wires", []):
            port.extend(recorders[t] for t in list(port) if t in recorders)

    nodes.append({"id": f"{prefix}status", "type": "status", "name": "記録: ステータス",
                  "scope": None, "x": 700, "y": 20, "wires": [[f"{prefix}status_rec"]]})
    nodes.append({"id": f"{prefix}status_rec", "type": "function", "name": "記録: ステータス",
                  "func": STATUS_RECORDER, "outputs": 0, "x": 900, "y": 20, "wires": []})
    return {"label": label, "nodes": nodes, "configs": configs, "env": list(env.values())}


def route(path, loose=False):
    """先頭に / を付けたパスにそろえる（Node-RED は "api" を "/api" として待ち受ける）。

    loose のときは、Express の既定のルーティングと同じく大文字・小文字と末尾の / を区別しない。
    """
    p = "/" + str(path or "").lstrip("/")
    return (p.rstrip("/") or "/").lower() if loose else p


def broker_address(n):
    """mqtt-broker の接続先を "ホスト:ポート" にそろえる（"mqtt://h:1883" と "h" + 1883 は同じ）。"""
    b = str(n.get("broker") or "").lower()
    b = b.split("://", 1)[-1].split("/", 1)[0]
    if b.startswith("["):  # [::1]:1883
        host, _, rest = b[1:].partition("]")
        port = rest.lstrip(":")
    elif b.count(":") > 1:  # ::1（IPv6 のアドレスだけ）
        host, port = b, ""
    else:
        host, _, port = b.partition(":")
    return f"{host}:{port or n.get('port') or 1883}"


def endpoints(nodes):
    """ID を変えても重なるもの。既存のフローと同じものを追加すると、利用者のフローと衝突する。

    無効にしたタブと、無効にしたノードの中のものは数えない。
    """
    disabled = {n["id"] for n in nodes if n.get("type") == "tab" and n.get("disabled")}
    # MQTT ブローカーは、有効なノードが使っているときだけ接続する
    used_brokers = {n.get("broker") for n in nodes
                    if n.get("type") in ("mqtt in", "mqtt out")
                    and not n.get("d") and n.get("z") not in disabled}
    found = set()
    for n in nodes:
        if n.get("d") or n.get("z") in disabled:
            continue
        t = n.get("type")
        if t == "websocket-listener":
            found.add(("websocket", route(n.get("path"))))
        elif t == "http in":
            found.add(("http", str(n.get("method") or "get").lower(), route(n.get("url"), loose=True)))
        elif (t == "tcp in" and n.get("server") == "server") or \
                (t == "tcp out" and n.get("beserver") == "server"):
            found.add(("tcp", str(n.get("port"))))
        elif t == "udp in":
            found.add(("udp", str(n.get("port"))))
        elif t == "mqtt-broker" and n.get("clientid") and n["id"] in used_brokers:
            # 同じクライアント ID で接続すると、ブローカーが先の接続を切る
            found.add(("mqtt-clientid", broker_address(n), str(n.get("clientid"))))
    return found


def read_context(base, flow_id, key):
    data = api(base, "GET", f"/context/flow/{flow_id}/{key}")
    # 記録が無いキーは {"msg": "(undefined)", "format": "undefined"} が返る
    if not isinstance(data, dict) or "msg" not in data or data.get("format") == "undefined":
        return None
    try:
        return json.loads(data["msg"])
    except json.JSONDecodeError:
        # 管理 API は 1000 文字を超える文字列を切り詰めるため、JSON として読めないことがある
        raise LiveCheckError(f"フローコンテキスト「{key}」を読めない: {data['msg'][:200]}")


def find_tab(base, label, tries=1):
    """ラベルでタブを探す。追加の途中で中断したときは、追加が終わるのを待って何度か探す。"""
    for i in range(tries):
        if i:
            time.sleep(2)
        flows = api(base, "GET", "/flows") or []
        found = next((n["id"] for n in flows
                      if n.get("type") == "tab" and n.get("label") == label), None)
        if found:
            return found
    return None


def cleanup(args, label, flow_id):
    """一時的なタブを消す。消せた（または作られていない）なら True。"""
    try:
        # POST が時間切れや中断でも、タブは作られていることがある。ラベルで探して消す
        flow_id = flow_id or find_tab(args.url, label, tries=5)
        if flow_id:
            api(args.url, "DELETE", f"/flow/{flow_id}")
            print("タブを削除した")
        return True
    except LiveCheckError as e:
        print(f"タブを削除できなかった。エディターで「{label}」を消すこと: {e}")
        return False


def run(args):
    blocks = load_blocks(args.guide)
    if args.list or not args.blocks:
        for i, b in enumerate(blocks, 1):
            print(f"{i:2d}. {b['line']}行目  {describe(b)}")
        return 0

    try:
        picked = [blocks[int(i) - 1] for i in args.blocks.split(",") if int(i) > 0]
    except (ValueError, IndexError):
        picked = []
    if len(picked) != len(args.blocks.split(",")):
        raise LiveCheckError(f"--blocks の指定が誤っている（ブロックは 1〜{len(blocks)}）")
    if any(b["flow"] is None for b in picked):
        raise LiveCheckError("フローとして読めないブロックがある。先に validate-flow-json.py を通すこと")
    unsafe = sorted({t for b in picked for t in unsafe_types(b["flow"])})
    if unsafe and not args.allow_unsafe:
        raise LiveCheckError(f"手元の環境に副作用のあるノードを含む: {', '.join(unsafe)}。"
                             "エディターで確かめるか、内容を確かめたうえで --allow-unsafe を付ける")

    prefix = f"lc{secrets.token_hex(3)}_"
    label = f"live-check {prefix} {os.path.basename(args.guide)} {args.blocks}"
    flow = build_flow(picked, prefix, label)
    configs = {c["id"]: c for c in flow["configs"]}
    injects = {}
    for n in flow["nodes"]:
        if n.get("type") == "inject" and n.get("name"):
            injects.setdefault(n["name"], []).append(n["id"])
    missing = [name for name in args.inject if name not in injects]
    if missing:
        raise LiveCheckError(f"inject ノードが見つからない: {', '.join(missing)}"
                             f"（あるもの: {', '.join(injects) or 'なし'}）")

    # 選んだブロックどうしでも、同じ待ち受けを2つ置くと2つ目が動かない
    seen = set()
    for i, b in enumerate(picked):
        inner = seen & endpoints(b["flow"])
        if inner:
            raise LiveCheckError(
                "選んだブロックどうしが重なるため、一緒には動かせない: "
                + ", ".join(":".join(c) for c in sorted(inner)))
        seen |= endpoints(b["flow"])
    unverified = sorted({n["type"] for n in flow["nodes"] if needs_expect(n, configs)})
    if not args.expect and (unverified or not any(is_connecting(n, configs) for n in flow["nodes"])):
        raise LiveCheckError(
            f"ステータスでは確かめられないノード（{', '.join(unverified) or 'mqtt、WebSocket client 以外'}）"
            "があるので、--expect で debug に届くべき文字列を指定すること（何も確かめずに合格にしない）")

    clash = seen & endpoints(api(args.url, "GET", "/flows") or [])
    if clash:
        raise LiveCheckError(
            "既存のフローと重なるため追加しない（利用者のフローが動かなくなる）: "
            + ", ".join(":".join(c) for c in sorted(clash)))

    flow_id = None
    posted = False
    cleaned = True
    try:
        posted = True
        res = api(args.url, "POST", "/flow", flow)
        if not isinstance(res, dict) or "id" not in res:
            raise LiveCheckError(f"POST /flow の応答に id が無い: {res!r}")
        flow_id = res["id"]
        print(f"タブ「{label}」を追加した（{flow_id}）。{args.wait:g} 秒待つ")
        time.sleep(args.wait)
        for name in args.inject:
            for nid in injects[name]:
                api(args.url, "POST", f"/inject/{nid}")
            print(f"inject「{name}」を押した")
        if args.inject:
            time.sleep(args.after)

        status = read_context(args.url, flow_id, "status") or {}
        received = read_context(args.url, flow_id, "received") or []
    finally:
        if posted and not args.keep:
            cleaned = cleanup(args, label, flow_id)

    failed = False
    print("\n[ステータス]")
    for n in flow["nodes"]:
        if is_connecting(n, configs) and n["id"] not in status:
            failed = True
            print(f"  NG  {n.get('name') or n['type']}（{n['type']}）: ステータスが記録されていない")
    for s in status.values():
        # 赤はエラー、黄は「接続中」など未完了。文字が "undefined" なのは、ステータスに
        # 出す値を読み取れていない（例: debug ノードの statusType がエディターに無い値）
        bad = s["fill"] in ("red", "yellow") or s["text"] == "undefined"
        failed |= bad
        print(f"  {'NG' if bad else 'OK'}  {s['name'] or s['type']}（{s['type']}）: "
              f"{s['fill'] or '-'} {s['text']}")
    if not status:
        print("  （ステータスを出したノードはない）")

    print("\n[debug に届いた値]")
    if not received:
        print("  （なし）")
    for r in received:
        print(f"  {r['debug']}: topic={r['topic']!r} 値={r['value'][:200]}")

    for text in args.expect:
        hit = any(text in r["value"] for r in received)
        failed |= not hit
        print(f"\n期待: {text!r} → {'届いた' if hit else '届かなかった'}")

    print("\n結果: " + ("不合格" if failed else "合格"))
    if not cleaned:
        print("一時的なタブを消せなかったため、終了コードは 2 にする")
        return 2
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("guide", help="ガイドの HTML ファイル")
    ap.add_argument("--list", action="store_true", help="フローのブロックを番号つきで一覧する")
    ap.add_argument("--blocks", help="読み込むブロックの番号（1始まり、カンマ区切り）")
    ap.add_argument("--url", default="http://localhost:1880", help="Node-RED の URL")
    ap.add_argument("--wait", type=float, default=10, help="デプロイ後に待つ秒数（接続を待つ）")
    ap.add_argument("--inject", action="append", default=[],
                    help="待った後にボタンを押す inject ノードの名前（複数指定可）")
    ap.add_argument("--after", type=float, default=5, help="ボタンを押した後に待つ秒数")
    ap.add_argument("--expect", action="append", default=[],
                    help="debug に届くべき文字列（届いた値に含まれるか。複数指定可）")
    ap.add_argument("--allow-unsafe", action="store_true",
                    help="副作用のあるノード（exec、file など）を含むブロックも動かす")
    ap.add_argument("--keep", action="store_true", help="終わってもタブを消さない（調査用）")
    args = ap.parse_args()
    args.url = args.url.rstrip("/")

    try:
        return run(args)
    except LiveCheckError as e:
        print(f"実行できなかった: {e}")
        return 2
    except KeyboardInterrupt:
        print("中断した（一時的なタブは片付けを試みた）")
        return 2
    except Exception as e:  # 想定外の例外を「不合格」（1）と取り違えないよう 2 で終える
        print(f"実行できなかった（想定外のエラー）: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
