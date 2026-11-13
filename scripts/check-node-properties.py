#!/usr/bin/env python3
"""フローの各ノードで、設定・選択が要る欄に正しい値が入っているかを検査する。

利用者がフローを読み込んで編集画面を開いたときに、選択が空になっている欄や、
必須なのに空の欄があると、利用者は何を選べばよいか分からない。しかも、そういうフローの
多くは動いてしまう。実行時のコードは、選択肢に無い値を「既定以外」として扱うことが多く、
JSON としても正しいので、書き方の検査（validate-flow-json.py）も、動かす検査
（test-flows.py）も通る。

実例: UDP Out の「送信」が "broadcast" になっていた。エディターの選択肢は
false / broad / multi の3つで、編集画面では選択が空になった。実行時は "false" 以外を
ブロードキャストとして扱うため、フローは動き、CI も通っていた。

検査すること（判定のもとは tests/node-schemas.json。scripts/gen-node-schemas.mjs が、
ノードのエディター HTML から作る）:

  選択肢    <select> の欄の値が、選択肢のどれかと一致する。エディターは値と選択肢を
            型も含めて比べる（jQuery の val）。数値は文字列に直してから比べるが、真偽値は
            直さないので、真偽値は選択肢と一致しない。値が無いときは空文字として扱う。
            ただし、編集画面を開くときのスクリプトが値を補う・読み替えるノードがある
            （Dashboard 2.0 の ui-group の visible など）。そのノードで選択が空になるか
            どうかは、一覧を作るときに実際のスクリプトを模擬の画面で動かして決めてある
  必須      defaults に required: true のある欄が、空でない（画面に出ない欄は除く）
  数値・形式 RED.validators.number() / regex() の付いた欄が、その形式に合う
  値と型    型が JSON・数値の欄と行（RED.validators.typedInput、change・switch・inject の行）の
            値が、JSON・数値として読める。プロパティ式と JSONata の式の書き方は見ない
  設定ノード 設定ノードを選ぶ欄が、同じブロックにある、正しい種類の設定ノードを指している。
            空でよいのは required: false の欄だけ（エディターの判定と同じ）
  型の欄    値の型を選ぶ欄（typedInput）が、エディターで選べる型になっている。
            行ごとに種類と型を選ぶ一覧（change の「値の代入」、switch の条件、inject の
            プロパティ）は、選択肢を自動で取り出せないので、ソースから書き写した表で見る
  チェック  既定がオンのチェックボックスのプロパティが無いと、編集画面ではオフになる。
            オンかオフかを書く
  未知の型  一覧に定義の無いノードは検査できないので、失敗にする
            （gen-node-schemas.mjs の PACKAGES に足して作り直す）

公式サンプルにある違反は、公式の内容のまま載せる決まりなので、KNOWN に理由を書いて残す。

  python3 scripts/check-node-properties.py                全ガイド
  python3 scripts/check-node-properties.py a.html b.html  ファイルを絞る

終了コードは 0 = 問題なし、1 = 問題あり、2 = 検査できなかった。
"""

import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMAS = os.path.join(ROOT, "tests", "node-schemas.json")

# 編集画面を持たない（または検査する欄が無い）組み込みの種類
BUILTIN = {"tab", "junction", "group", "subflow"}

# エディターの RED.validators.number() と同じ判定（red.js）
NUMBER = re.compile(
    r"^NaN$|^[+-]?[0-9]*\.?[0-9]*([eE][-+]?[0-9]+)?$|^[+-]?(0b|0B)[01]+$"
    r"|^[+-]?(0o|0O)[0-7]+$|^[+-]?(0x|0X)[0-9a-fA-F]+$")
# 環境変数の指定は、エディターがどの検証でも正しい値として扱う
ENV_VALUE = re.compile(r"^\$\([a-zA-Z_][a-zA-Z0-9_]*\)$|^\$\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

# 直さずに残す違反。公式サンプルは、公式の内容のまま載せる決まり（CLAUDE.md の
# 「公式サンプル第一の原則」）なので、公式のフローにある違反はここに理由を書いて残す。
# (ガイド, ノードの ID, 報告の文に含まれる文字列) → 理由。文字列は、行やプロパティまで含めて書く
# （広く書くと、同じノードに後から足した別の違反まで隠してしまう）。
# 当てはまる違反が無くなった記載は、失敗にする（直したのに残っている記載を見逃さないため）。
KNOWN = {
    ("nodered-debug-node-guide.html", "a325a0b5fbc66ec5", 'props の 2 行目 の vt の "string"'):
        "公式サンプル（common/debug）のまま。inject の topic の型が、エディターに無い \"string\" になっている",
    ("nodered-debug-node-guide.html", "dac87e40.90376", 'props の 2 行目 の vt の "string"'):
        "公式サンプル（common/debug/02）のまま",
    ("nodered-debug-node-guide.html", "6f477e7d.3a8da", 'props の 2 行目 の vt の "string"'):
        "公式サンプル（common/debug/05）のまま",
}


def load_extractor():
    spec = importlib.util.spec_from_file_location(
        "validate_flow_json", os.path.join(HERE, "validate-flow-json.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def js_string(value):
    """jQuery の val() が select の選択肢と比べるときの文字列。比べられない値は None。"""
    if value is None:
        return ""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, str):
        return value
    return None


def show(value):
    return json.dumps(value, ensure_ascii=False)


MISSING = object()


def js_text(value):
    """JavaScript が値を文字列として扱うときの文字列。配列・オブジェクトは判定しない（None）。"""
    if value is MISSING:
        return "undefined"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return js_string(value)
    return None


def reject_constant(name):
    raise ValueError(name)  # NaN / Infinity は、JavaScript の JSON.parse では読めない


def typed_value(value, kind):
    """エディターの RED.utils.validateTypedProperty のうち、JSON と数値の判定。

    プロパティ式（msg / flow / global）と JSONata の式の書き方は、ここでは判定しない。
    """
    text = js_text(value)
    if text is None:
        return None
    if isinstance(value, str) and re.match(r"^\$\{[^}]+\}$", value):
        return None
    if kind == "json":
        try:
            json.loads(text, parse_constant=reject_constant)
        except ValueError:
            return f"型が JSON だが、値の {show(None if value is MISSING else value)} を JSON として読めない"
    elif kind == "num" and not NUMBER.match(text):
        return f"型が数値だが、値の {show(None if value is MISSING else value)} は数値でない"
    return None


def compile_js(source, flags):
    """JavaScript の正規表現を Python で使う。末尾の $ は、Python では最後の改行の前にも
    一致してしまうので、文字列の終わりだけに一致する \\Z に読み替える。"""
    if source.endswith("$") and not source.endswith("\\$"):
        source = source[:-1] + "\\Z"
    return re.compile(source, re.IGNORECASE if "i" in flags else 0)


UNKNOWN_NOTE = "。編集画面のスクリプトを模擬できず、空になるかを決められないので、選択肢の値を書く"


def check_select(node, prop, select, default):
    value = node.get(prop)
    options = select["values"]
    if select.get("multiple") and isinstance(value, list):
        bad = [v for v in value if js_string(v) not in options]
        if not bad:
            return None
        return f"{prop} の {show(bad)} は、エディターの選択肢 {show(options)} に無い"
    if js_string(value) in options:
        return None
    if prop not in node or value is None:
        # 編集画面のスクリプトが値を補うノードでは、無くても選択は空にならない
        outcome = select["missing"]
        if outcome == "ok":
            return None
        hint = f"（既定値は {show(default)}）" if default in options else ""
        return (f"{prop} が無い。エディターの選択肢 {show(options)} のどれかを書く{hint}"
                + ("。無いと、編集画面で選択が空になる" if outcome == "blank" else UNKNOWN_NOTE))
    if isinstance(value, bool):
        # 編集画面のスクリプトが真偽値を選択肢の文字列に読み替えるノードがある
        outcome = select["bool"]["true" if value else "false"]
        if outcome == "ok":
            return None
        return (f"{prop} が真偽値の {show(value)}。エディターの選択肢は文字列の {show(options)}"
                + ("（真偽値は一致せず、編集画面で選択が空になる）" if outcome == "blank" else UNKNOWN_NOTE))
    return (f"{prop} の {show(value)} は、エディターの選択肢 {show(options)} に無い"
            f"（編集画面で選択が空になる）")


def check_typed(node, prop, typed):
    """値の型を選ぶ欄。無ければ typedInput が既定の型を選ぶので、書いてある値だけを見る。"""
    value = node.get(prop)
    if value is None or value == "" or value in typed["types"]:
        return None
    return (f"{prop} の {show(value)} は、エディターで選べる型 {show(typed['types'])} に無い"
            f"（編集画面では別の型が選ばれる）")


def check_validator(node, prop, spec, mark):
    """エディターの validateNodeProperty と同じ順で、required と number / regex を見る。"""
    value = node.get(prop)
    present = prop in node
    if isinstance(value, str) and ENV_VALUE.match(value):
        return None
    if spec.get("required") is True:
        if value == "":
            return f"{prop} は必須だが、空になっている"
        # プロパティが無いときは、編集画面のスクリプトが値を補うか（ok）、欄が無いか（nofield）で決まる
        if value is None and spec.get("missing") in ("blank", "unknown"):
            return f"{prop} は必須だが、書かれていない（編集画面で欄が空になる）"
    if value is None and spec.get("missing") == "unchecked":
        return (f"{prop} が無い。既定はオン（true）だが、書かれていないと編集画面でチェックが外れる。"
                f"true か false を書く")
    if mark is None:
        return None
    if spec.get("required") is False and value == "":
        return None
    kind = mark.get("kind")
    if kind == "number":
        # エディターの判定: 空を許す指定なら "" と undefined は通る。そうでなければ、
        # "" は isNaN("") が false なので通り、undefined は数値でないので通らない
        if not present:
            if mark.get("blank"):
                return None
            return f"{prop} は数値が要るが、書かれていない（ノードに設定の誤りの印が付く）"
        # null・真偽値・数値・配列は、isNaN が false を返すので通る
        if value is None or value == "" or not isinstance(value, str):
            return None
        if NUMBER.match(value) or re.match(r"^\$\{[^}]+\}$", value):
            return None
        # 上の形に合わない文字列は、エディターが isNaN で判定する（前後の空白は無視される）
        if NUMBER.match(value.strip()) or value.strip() in ("Infinity", "+Infinity", "-Infinity"):
            return None
        return f"{prop} の {show(value)} は数値でない"
    if kind == "regex":
        # エディターは値をそのまま RegExp.test に渡す。無い値は "undefined"、数値は文字列として
        # 試される。Python で使えない書き方の正規表現は、起動時に検査を止める（main）
        text = js_text(value if present else MISSING)
        if text is not None and not compile_js(mark["source"], mark.get("flags", "")).search(text):
            return f"{prop} の {show(value)} は、エディターが求める形式（/{mark['source']}/）に合わない"
    if kind == "typedInput":
        # 値の型は、指定された型か、型の欄（typeField）のプロパティで決まる
        if (mark.get("allowBlank") and value == "") or (mark.get("allowUndefined") and not present):
            return None
        kind_of_value = mark.get("type") or (node.get(mark["typeField"]) if mark.get("typeField") else None)
        found = typed_value(value if present else MISSING, kind_of_value)
        if found:
            return f"{prop}: {found}（ノードに設定の誤りの印が付く）"
    return None


def check_config_ref(node, prop, spec, by_id, schemas):
    target = spec["type"]
    if target not in schemas or not schemas[target].get("config"):
        return None
    value = node.get(prop)
    if not value or value == "_ADD_":
        if spec.get("required") is False:
            return None
        return f"{prop} に設定ノード（{target}）が選ばれていない"
    ref = by_id.get(value) if isinstance(value, str) else None
    if ref is None:
        return f"{prop} が指す設定ノード（{target}）の {show(value)} が、同じフローに無い"
    if ref.get("type") != target:
        return (f"{prop} が指す {show(value)} は {ref.get('type')} で、"
                f"この欄で選べる {target} でない")
    return None


# ---- 行ごとに種類と型を選ぶ一覧（標準ノード） ----
#
# change の「値の代入」、switch の条件、inject のプロパティは、行ごとに種類と値の型を選ぶ。
# 行は編集画面のスクリプトが組み立てるので、選択肢を自動では取り出せない。Node-RED 5.0.7 の
# 15-change.html / 10-switch.html / 20-inject.html から書き写す。型が書かれていない行は、
# エディターが既定の型を選ぶので、書かれている値だけを見る。

STORES = ["msg", "flow", "global"]
CHANGE_KINDS = ["set", "change", "delete", "move"]
CHANGE_SET_TO = ["msg", "flow", "global", "str", "num", "bool", "json", "bin", "date", "jsonata", "env"]
CHANGE_FROM = ["msg", "flow", "global", "str", "re", "num", "bool", "env"]
CHANGE_TO = ["msg", "flow", "global", "str", "num", "bool", "json", "bin", "env"]
SWITCH_PROPERTY = ["msg", "flow", "global", "jsonata", "env"]
SWITCH_VALUE = ["msg", "flow", "global", "str", "num", "jsonata", "env", "prev"]
SWITCH_NUM = ["flow", "global", "num", "jsonata", "env"]
SWITCH_ISTYPE = ["string", "number", "boolean", "array", "buffer", "object", "json", "undefined", "null"]
SWITCH_VALUE_OPS = ["eq", "neq", "lt", "lte", "gt", "gte", "hask", "cont", "regex"]
SWITCH_BETWEEN_OPS = ["btwn", "index"]  # 値を2つ持つ（v / vt と v2 / v2t）。同じ入力部品を使う
SWITCH_NO_VALUE_OPS = ["true", "false", "null", "nnull", "empty", "nempty", "else"]
SWITCH_NUM_OPS = ["head", "tail"]
SWITCH_OPS = (SWITCH_VALUE_OPS + SWITCH_BETWEEN_OPS + SWITCH_NO_VALUE_OPS + SWITCH_NUM_OPS
              + ["istype", "jsonata_exp"])
INJECT_VALUE = ["flow", "global", "str", "num", "bool", "json", "bin", "date", "jsonata", "env", "msg"]


def one_of(where, key, item, allowed, required=False):
    value = item.get(key)
    if value is None or value == "":
        return [f"{where} の {key} が無い。{show(allowed)} のどれかを書く"] if required else []
    if value in allowed:
        return []
    return [f"{where} の {key} の {show(value)} は、エディターで選べる {show(allowed)} に無い"]


def typed_row(where, item, value_key, type_key, only_present=False):
    """行の値と型の組が合っているか（JSON と数値）。"""
    if only_present and value_key not in item:
        return []
    found = typed_value(item.get(value_key, MISSING), item.get(type_key))
    return [f"{where} の {value_key}: {found}（ノードに設定の誤りの印が付く）"] if found else []


def rows(node, key):
    value = node.get(key)
    return [(i + 1, r) for i, r in enumerate(value) if isinstance(r, dict)] if isinstance(value, list) else []


def check_change(node):
    problems = []
    for i, rule in rows(node, "rules"):
        where = f"rules の {i} 行目"
        problems += one_of(where, "t", rule, CHANGE_KINDS, required=True)
        problems += one_of(where, "pt", rule, STORES)
        kind = rule.get("t")
        if kind == "set":
            problems += one_of(where, "tot", rule, CHANGE_SET_TO)
        elif kind == "change":
            problems += one_of(where, "fromt", rule, CHANGE_FROM)
            problems += one_of(where, "tot", rule, CHANGE_TO)
        elif kind == "move":
            problems += one_of(where, "tot", rule, STORES)
        if kind in ("set", "change", "move"):
            problems += typed_row(where, rule, "to", "tot")
        if kind == "change":
            problems += typed_row(where, rule, "from", "fromt")
    return problems


def check_switch(node):
    problems = one_of("条件を調べるプロパティ", "propertyType", node, SWITCH_PROPERTY)
    for i, rule in rows(node, "rules"):
        where = f"rules の {i} 行目"
        problems += one_of(where, "t", rule, SWITCH_OPS, required=True)
        kind = rule.get("t")
        if kind in SWITCH_VALUE_OPS:
            problems += one_of(where, "vt", rule, SWITCH_VALUE)
        elif kind in SWITCH_BETWEEN_OPS:
            problems += one_of(where, "vt", rule, SWITCH_VALUE)
            problems += one_of(where, "v2t", rule, SWITCH_VALUE)
        elif kind in SWITCH_NUM_OPS:
            problems += one_of(where, "vt", rule, SWITCH_NUM)
        elif kind == "istype":
            problems += one_of(where, "vt", rule, SWITCH_ISTYPE)
        elif kind == "jsonata_exp":
            problems += one_of(where, "vt", rule, ["jsonata"])
        # 値と型の組は、エディターの rules の検証と同じく、istype 以外の行で見る
        if kind != "istype":
            problems += typed_row(where, rule, "v", "vt", only_present=True)
            problems += typed_row(where, rule, "v2", "v2t", only_present=True)
    return problems


def check_inject(node):
    problems = one_of("ペイロード", "payloadType", node, INJECT_VALUE)
    for i, prop in rows(node, "props"):
        where = f"props の {i} 行目"
        if not prop.get("p"):
            problems.append(f"{where} の p（代入先のプロパティ名）が空")
        problems += one_of(where, "vt", prop, INJECT_VALUE)
        problems += typed_row(where, prop, "v", "vt")
    return problems


ROW_CHECKS = {"change": check_change, "switch": check_switch, "inject": check_inject}


def check_node(node, by_id, schemas):
    kind = node.get("type")
    if kind in BUILTIN or (isinstance(kind, str) and kind.startswith("subflow:")):
        return []
    schema = schemas.get(kind)
    if schema is None:
        return [f"種類 {show(kind)} の定義が tests/node-schemas.json に無く、検査できない。"
                f"scripts/gen-node-schemas.mjs の PACKAGES にパッケージを足して作り直す"]
    problems = []
    for prop, spec in schema["defaults"].items():
        found = None
        if prop in schema["selects"]:
            found = check_select(node, prop, schema["selects"][prop], spec.get("value"))
        if found is None and prop in schema["typed"]:
            found = check_typed(node, prop, schema["typed"][prop])
        if found is None and "type" in spec and "validate" not in spec:
            found = check_config_ref(node, prop, spec, by_id, schemas)
        if found is None:
            found = check_validator(node, prop, spec, spec.get("validate"))
        if found:
            problems.append(found)
    if kind in ROW_CHECKS:
        problems.extend(ROW_CHECKS[kind](node))
    return problems


def check_file(path, extractor, schemas, used):
    src = open(path, encoding="utf-8").read()
    parser = extractor.FlowJsonExtractor(src)
    parser.feed(src)
    parser.close()
    errors = []
    for block in parser.blocks:
        try:
            flow = json.loads(block["delivered"])
        except json.JSONDecodeError:
            continue  # JSON として読めないブロックは validate-flow-json.py が報告する
        if not isinstance(flow, list):
            continue
        nodes = [n for n in flow if isinstance(n, dict)]
        by_id = {n.get("id"): n for n in nodes}
        for node in nodes:
            for problem in check_node(node, by_id, schemas):
                known = [key for key in KNOWN
                         if key[0] == os.path.basename(path) and key[1] == node.get("id") and key[2] in problem]
                if known:
                    used.update(known)
                    continue
                label = node.get("name") or node.get("label") or ""
                errors.append(f"{path}:{block['line']}: [{node.get('type')}] "
                              f"「{label}」（{node.get('id')}）: {problem}")
    return errors


def main():
    try:
        schemas = json.load(open(SCHEMAS, encoding="utf-8"))["nodes"]
    except (OSError, ValueError, KeyError) as e:
        print(f"tests/node-schemas.json を読めない: {e}")
        return 2
    for kind, schema in schemas.items():
        for prop, spec in schema["defaults"].items():
            mark = spec.get("validate") or {}
            if mark.get("kind") == "regex":
                try:
                    compile_js(mark["source"], mark.get("flags", ""))
                except re.error as e:
                    print(f"{kind} の {prop} の正規表現 /{mark['source']}/ を Python で使えない（{e}）。"
                          f"検査できないので、check-node-properties.py に読み替えを足す")
                    return 2
    extractor = load_extractor()
    # 引数のパスは、呼び出した場所から見たもの。リポジトリのルートへ移る前に読み替える
    given = [os.path.relpath(os.path.abspath(p), ROOT) for p in sys.argv[1:]]
    os.chdir(ROOT)
    targets = given or sorted(glob.glob("*.html"))
    errors = []
    checked = 0
    used = set()
    seen = set()
    for path in targets:
        try:
            src = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"{path} を読めない: {e}")
            return 2
        seen.add(os.path.basename(path))
        if not extractor.count_flow_json(src):
            continue
        checked += 1
        errors.extend(check_file(path, extractor, schemas, used))
    for key, reason in KNOWN.items():
        if key[0] in seen and key not in used:
            errors.append(f"{key[0]}: KNOWN の記載（ノード {key[1]}、{key[2]}）に当たる違反が無い。"
                          f"記載を消す（理由: {reason}）")
    for e in errors:
        print(e)
    print(f"\n{checked} files checked, {len(errors)} problems found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
