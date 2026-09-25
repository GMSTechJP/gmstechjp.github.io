#!/usr/bin/env python3
"""サンプルフロー JSON の検証。

利用者はコピーボタン経由でフローを受け取る。コピーボタンは DOM のテキストを読むため、
ブラウザが解釈してしまうマークアップ（<html>, <style>, <a> など）が flow-json ブロックに
生のまま置かれていると、タグが消えた文字列が配布される。破損しても JSON としては valid な
ままなので、json.loads だけでは検出できない。

そこで「ソースに書いた JSON」と「利用者が受け取る JSON」を突き合わせる。

加えて、現時点ではコピー結果を壊さない生の文字も拒否する。タグと解釈されない生の `<` と、
`&amp;` / `&lt;` / `&gt;` 以外の `&` である。後者はブラウザが実体参照として解釈した場合
（例: &copy; → ©）、コピー結果と html.unescape が同じように変換するため突き合わせでは
原理的に検出できない。

ブロックの切り出しは正規表現ではなく HTMLParser で行う。JSON 文字列の中に `<div` が現れる
ケースを正規表現で数えると、閉じタグを取り違えてブロックを1件も返さず、検査ごと素通りする。
それは検出したい不具合そのものと同じ「静かにすり抜ける」失敗である。

教材としての誤りも1つ検査する。自動で直列化する出力ノード（AUTO_SERIALIZE）の直前の
function で msg.payload を JSON.stringify しているものである。
"""

import glob
import html
import json
import re
import sys
from html.parser import HTMLParser

CLASS_ATTR = re.compile(r'class="[^"]*\bflow-json\b[^"]*"')
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}

# ブロック内で許すのは規約どおりのエスケープ（&amp; / &lt;）と、同様に一意に復元される
# &gt; のみ。それ以外の & は、ブラウザが実体参照として解釈するか否かが書き手の意図と
# 無関係に決まる「曖昧な &」であり、解釈された場合（例: &copy; → ©）はコピー結果と
# html.unescape の両方が同じように変換するため、不一致検査では原理的に捕まらない。
AMBIGUOUS_AMP = re.compile(r"&(?!amp;|lt;|gt;)")

# null でも Buffer でもないオブジェクトの msg.payload を、引数なしの JSON.stringify と同じ
# 文字列に自動で直列化する出力ノード（Node-RED 本体のソースで確認済み）。
#   websocket out: RED.util.ensureString()（22-websocket.js）。「ペイロードを送信」モードのみ。
#                  「メッセージ全体を送信」モードは msg 全体を直列化するため対象外とする
#   mqtt out:      JSON.stringify()（10-mqtt.js）
# http response もオブジェクトを JSON で返すが、JSONP の callback や明示したヘッダーで結果が
# 変わりうるため、誤検知を避けて自動検査の対象には含めない。
# 教材の function でこれらの直前に JSON.stringify すると、学習者に不要な処理を覚えさせる。
AUTO_SERIALIZE = {"websocket out", "mqtt out"}
# 文字列化が不要な接続先と一緒につながっていても、判定を変えない接続先
HARMLESS_PEERS = {"debug"}
STRINGIFY_PAYLOAD = re.compile(r"(?<![\w$.])msg\.payload\s*=\s*JSON\.stringify\(")
# 引数がこれらのリテラルなら、出力は自動変換と一致しない（"a" は "\"a\"" になる）
PRIMITIVE_ARG = re.compile(r'""|-?\d[\d.eE+-]*|true|false|null|undefined')
# Buffer は自動変換の対象外（そのまま送られる）ため、手で JSON 化するのには意味がある
BUFFER_ARG = re.compile(r"(?<![\w$])Buffer(?![\w$])")


class FlowJsonExtractor(HTMLParser):
    """class="flow-json" の要素を、その生ソースと textContent の両方で取り出す。"""

    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.src = src
        self.line_starts = [0]
        for line in src.splitlines(keepends=True):
            self.line_starts.append(self.line_starts[-1] + len(line))
        self.blocks = []
        self.unclosed = None
        self._reset_block()

    def _reset_block(self):
        self.open_tag = None
        self.depth = 0
        self.start = None
        self.line = None
        self.parts = []
        self.markup = []

    def _offset(self):
        lineno, col = self.getpos()
        return self.line_starts[lineno - 1] + col

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if self.open_tag is None:
            if "flow-json" in classes:
                self.open_tag = tag
                self.line = self.getpos()[0]
                self.start = self._offset() + len(self.get_starttag_text())
            return
        self.markup.append(f"<{tag}")
        if tag not in VOID:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        if self.open_tag is not None:
            self.markup.append(f"<{tag}/>")

    def handle_endtag(self, tag):
        if self.open_tag is None:
            return
        if self.depth == 0:
            raw = self.src[self.start:self._offset()]
            self.blocks.append({
                "line": self.line, "tag": self.open_tag, "raw": raw,
                "start": self.start, "end": self._offset(),
                "delivered": "".join(self.parts), "markup": self.markup,
            })
            self._reset_block()
        else:
            self.depth -= 1
            self.markup.append(f"</{tag}")

    def handle_data(self, data):
        if self.open_tag is not None:
            self.parts.append(data)

    def handle_comment(self, data):
        if self.open_tag is not None:
            self.markup.append("<!--")

    def handle_decl(self, decl):
        if self.open_tag is not None:
            self.markup.append(f"<!{decl.split()[0]}")

    def unknown_decl(self, data):
        if self.open_tag is not None:
            self.markup.append("<![")

    def handle_pi(self, data):
        if self.open_tag is not None:
            self.markup.append("<?")

    def close(self):
        super().close()
        if self.open_tag is not None:
            self.unclosed = self.line


def raw_char_errors(path, block, src):
    """タグとして解釈されない生の `<` と、曖昧な `&` を検出する。

    どちらも現在のブラウザではコピー結果を壊さない（壊すものは既存の検査で捕まる）が、
    規約（`<` は `&lt;`、`&` は `&amp;`）に反し、周囲の編集しだいでタグや実体参照として
    解釈される側に転ぶ。転んだ後では検出できないものもあるため、ソースの時点で拒否する。
    """
    errors = []
    for label, matches in (
        ("タグ以外の生の `<`。`&lt;` と書くこと", re.finditer(r"<", block["raw"])),
        ("曖昧な `&`。`&amp;` と書くこと", AMBIGUOUS_AMP.finditer(block["raw"])),
    ):
        for m in matches:
            # block["line"] は開始タグの行なので、タグが複数行に渡ると起点がずれる。
            # ブロック内容の絶対オフセットから数え直す。
            line = src.count("\n", 0, block["start"] + m.start()) + 1
            context = block["raw"][max(0, m.start() - 20):m.start() + 20]
            errors.append(f"{path}:{line}: {label}: {context!r}")
    return errors


def escaped_entities(value):
    """パース後の値に残ったエスケープ痕跡（二重エスケープの疑い）を返す。"""
    return [e for e in ("&lt;", "&gt;") if e in value]


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_strings(v)


def strip_comments_and_strings(code):
    """コメントを空白に、文字列リテラルを "" に置き換えたコードを返す。

    文字列やコメントの中に書かれた `msg.payload = JSON.stringify(` を、実際の処理と
    取り違えないためのもの。テンプレートリテラルの `${...}` は入れ子も含めて文字列の
    一部として扱う。正規表現リテラルは区別しない。
    """
    out = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        if code.startswith("//", i):
            j = code.find("\n", i)
            i = n if j < 0 else j
            out.append(" ")
        elif code.startswith("/*", i):
            j = code.find("*/", i + 2)
            i = n if j < 0 else j + 2
            out.append(" ")
        elif c in "\"'":
            i += 1
            while i < n and code[i] != c:
                i += 2 if code[i] == "\\" else 1
            i += 1
            out.append('""')
        elif c == "`":
            i = skip_template(code, i)
            out.append('""')
        else:
            out.append(c)
            i += 1
    return "".join(out)


def skip_template(code, i):
    """code[i] の ` で始まるテンプレートリテラルの直後の位置を返す（入れ子に対応）。"""
    n = len(code)
    i += 1
    while i < n:
        c = code[i]
        if c == "\\":
            i += 2
        elif c == "`":
            return i + 1
        elif code.startswith("${", i):
            i += 2
            depth = 0
            while i < n:
                c = code[i]
                if c == "`":
                    i = skip_template(code, i)
                    continue
                if c in "\"'":
                    i += 1
                    while i < n and code[i] != c:
                        i += 2 if code[i] == "\\" else 1
                elif c == "{":
                    depth += 1
                elif c == "}":
                    if depth == 0:
                        break
                    depth -= 1
                i += 1
            i += 1
        else:
            i += 1
    return n


def call_argument(code, start):
    """code[start] から対応する ')' までの引数を返す。引数が1つでなければ None。"""
    depth = 0
    for i in range(start, len(code)):
        c = code[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                return code[start:i].strip() if c == ")" else None
            depth -= 1
        elif c == "," and depth == 0:
            return None
    return None


def listener_is_wholemsg(node, by_id):
    """websocket out の設定ノードが「メッセージ全体を送信」モードなら True。"""
    for key in ("server", "client"):
        ref = node.get(key)
        conf = by_id.get(ref) if isinstance(ref, str) else None
        if isinstance(conf, dict) and str(conf.get("wholemsg")) == "true":
            return True
    return False


def redundant_stringify(path, line, flow):
    """自動で直列化する出力ノードの直前で、引数なしの JSON.stringify をしている function を返す。

    CI を落とす検査なので、誤検知を避けて次をすべて満たすものに限る。
    - 出力が1つ（複数出力では、文字列化した msg がどこへ行くかをコードから判断できない）
    - コメントと文字列を除いたコードに `msg.payload = JSON.stringify(x)` があり、
      引数が1つで、リテラルでも Buffer でもない（これらは自動変換と出力が変わる）
    - 接続先がすべて AUTO_SERIALIZE か HARMLESS_PEERS で、AUTO_SERIALIZE を1つ以上含む
    - websocket out が「メッセージ全体を送信」モードではない
    """
    by_id = {n["id"]: n for n in flow
             if isinstance(n, dict) and isinstance(n.get("id"), str)}

    errors = []
    for node in flow:
        if not isinstance(node, dict) or node.get("type") != "function":
            continue
        func, wires = node.get("func"), node.get("wires")
        if not isinstance(func, str) or not isinstance(wires, list) or len(wires) != 1:
            continue
        if node.get("outputs", 1) not in (1, "1"):
            continue
        port = wires[0]
        if not isinstance(port, list) or not port:
            continue
        code = strip_comments_and_strings(func)
        args = [call_argument(code, m.end()) for m in STRINGIFY_PAYLOAD.finditer(code)]
        if not any(a and not PRIMITIVE_ARG.fullmatch(a) and not BUFFER_ARG.search(a)
                   for a in args):
            continue
        targets = [by_id.get(t) if isinstance(t, str) else None for t in port]
        if not all(isinstance(t, dict) for t in targets):
            continue
        types = [t.get("type") for t in targets]
        if not all(isinstance(t, str) and t in AUTO_SERIALIZE | HARMLESS_PEERS for t in types):
            continue
        auto = sorted({t for t in types if t in AUTO_SERIALIZE})
        if not auto:
            continue
        if any(t.get("type") == "websocket out" and listener_is_wholemsg(t, by_id)
               for t in targets):
            continue
        names = " / ".join(auto)
        errors.append(
            f"{path}:{line}: function {node.get('id', '?')} が msg.payload を "
            f"JSON.stringify して {names} に渡している。{names} はオブジェクトを"
            f"同じJSON文字列に自動で変換するため、教材では書かない"
        )
    return errors


def check_flow(path, line, delivered):
    errors = []
    try:
        flow = json.loads(delivered)
    except json.JSONDecodeError as e:
        return [f"{path}:{line}: JSON がパースできない: {e}"]

    if not isinstance(flow, list):
        return [f"{path}:{line}: フローは配列でなければならない"]

    ids = {n.get("id") for n in flow
           if isinstance(n, dict) and isinstance(n.get("id"), str)}
    for node in flow:
        if (not isinstance(node, dict) or not isinstance(node.get("id"), str)
                or not isinstance(node.get("type"), str)):
            errors.append(f"{path}:{line}: id / type を文字列で持たないノードがある")
            break
        wires = node.get("wires") or []
        if not isinstance(wires, list) or not all(isinstance(p, list) for p in wires):
            errors.append(f"{path}:{line}: ノード {node['id']} の wires が配列の配列でない")
            continue
        for port in wires:
            for target in port:
                if not isinstance(target, str) or target not in ids:
                    errors.append(
                        f"{path}:{line}: ノード {node['id']} の接続先 {target} が"
                        f"フロー内に存在しない"
                    )

    errors.extend(redundant_stringify(path, line, flow))

    for value in walk_strings(flow):
        found = escaped_entities(value)
        if found:
            errors.append(
                f"{path}:{line}: 二重エスケープの疑い。パース後の値に "
                f"{', '.join(found)} が残っている: {value[:40]!r}"
            )
            break
    return errors


def check(path):
    src = open(path, encoding="utf-8").read()
    parser = FlowJsonExtractor(src)
    parser.feed(src)
    parser.close()

    errors = []
    expected = len(CLASS_ATTR.findall(src))

    if parser.unclosed is not None:
        errors.append(f"{path}:{parser.unclosed}: flow-json ブロックが閉じられていない")
    # ブロックを取りこぼしたまま成功扱いにしない（今回のバグと同じ静かな見逃しを防ぐ）
    if len(parser.blocks) != expected:
        errors.append(
            f"{path}: flow-json 要素は {expected} 個だが {len(parser.blocks)} 個しか"
            f"抽出できなかった。ブロックの構造を確認すること"
        )

    for block in parser.blocks:
        path_line = f"{path}:{block['line']}"
        if block["tag"] != "div":
            errors.append(
                f"{path_line}: flow-json は <div> に置くこと（実際は <{block['tag']}>）"
            )
            continue
        if block["markup"]:
            sample = ", ".join(block["markup"][:3])
            errors.append(
                f"{path_line}: コピー時にマークアップが失われる。"
                f"生タグを HTML エスケープすること（例: {sample}）"
            )
            continue
        if block["delivered"] != html.unescape(block["raw"]):
            errors.append(f"{path_line}: ソースとコピー結果が一致しない")
            continue
        errors.extend(raw_char_errors(path, block, src))
        errors.extend(check_flow(path, block["line"], block["delivered"]))

    return errors


def main():
    targets = sys.argv[1:] or sorted(glob.glob("*.html"))
    errors = []
    checked = 0

    for path in targets:
        if not CLASS_ATTR.search(open(path, encoding="utf-8").read()):
            continue
        checked += 1
        errors.extend(check(path))

    for e in errors:
        print(e)
    print(f"\n{checked} files checked, {len(errors)} problems found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
