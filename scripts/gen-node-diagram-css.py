#!/usr/bin/env python3
"""ノード図（node-example）の共有スタイル css/node-diagram.css を生成する。

ガイドの「実用的な使用パターン」などでは、処理の流れを
<div class="node-example"> の中にノードの箱（<span class="node node-inject">）と
配線（<span class="arrow">→</span>）を並べて示す。この箱を Node-RED エディター上の
ノードと同じ見た目（ノードの色、アイコン、入出力ポート、灰色の配線、方眼のワークスペース）
で描くための CSS を、下の対応表から生成する。

対応表の値は、各ノードのエディター HTML の RED.nodes.registerType() から取った
color / icon / inputs / outputs / align である（2026-10-03 確認）。
- 標準ノード: Node-RED 5.0.7（@node-red/nodes/core）
- Dashboard 2.0: @flowfuse/node-red-dashboard 1.32.0（色は ui-base の --nrdb-node-*）、
  @flowfuse/node-red-dashboard-2-ui-led 1.1.1
- その他: node-red-node-base64 1.0.0、node-red-node-email 5.2.5、node-red-contrib-ftp 0.0.8、
  node-red-contrib-ftp-server 1.0.4、node-red-node-sqlite 2.0.1、
  node-red-node-pi-sense-hat 0.2.0、node-red-contrib-modbus、
  node-red-contrib-buffer-parser

アイコンは img/node-icons/ に置く（出典は img/node-icons/README.md）。

ノードの種類を追加するときは NODES に1行足し、このスクリプトを実行して
css/node-diagram.css を更新する。CSS を直接編集しない。

    python3 scripts/gen-node-diagram-css.py          # 生成
    python3 scripts/gen-node-diagram-css.py --check  # 生成結果とファイルが一致するか（CI 用）
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "css", "node-diagram.css")

# Dashboard 2.0 のノード色（ui-base の --nrdb-node-light 等）
DB_LIGHT = "#a0e6ec"
DB_MEDIUM = "#5ad2dc"
DB_DARK = "#27b7c3"
DB_DARKEST = "#20a0aa"

# クラス名（node- を除く）: (色, アイコン, 入力ポート数, 出力ポート数, アイコンの位置)
# 出力ポート数は、エディターで数が決まっているノードだけ 2 以上にする。switch・function・trigger
# のように設定で数が変わるノードは 1 にしておき、図ごとに outputs-N のクラスで指定する。
NODES = {
    # common
    "inject": ("#a6bbcf", "inject.svg", 0, 1, "left"),
    "debug": ("#87a980", "debug.svg", 1, 0, "right"),
    "complete": ("#c0edc0", "alert.svg", 0, 1, "left"),
    "catch": ("#e49191", "alert.svg", 0, 1, "left"),
    "status": ("#94c1d0", "status.svg", 0, 1, "left"),
    "link-in": ("#dddddd", "link-out.svg", 0, 1, "left"),
    "link-call": ("#dddddd", "link-call.svg", 1, 1, "left"),
    "link-out": ("#dddddd", "link-out.svg", 1, 0, "right"),
    # link out の「呼び出し元へ返却」モード（エディターはアイコンを link-return.svg に替える）
    "link-return": ("#dddddd", "link-return.svg", 1, 0, "right"),
    "comment": ("#ffffff", "comment.svg", 0, 0, "left"),
    # function
    "function": ("#fdd0a2", "function.svg", 1, 1, "left"),
    "switch": ("#e2d96e", "switch.svg", 1, 1, "left"),
    "change": ("#e2d96e", "swap.svg", 1, 1, "left"),
    "range": ("#e2d96e", "range.svg", 1, 1, "left"),
    "template": ("#f3b567", "template.svg", 1, 1, "left"),
    "delay": ("#e6e0f8", "timer.svg", 1, 1, "left"),
    "trigger": ("#e6e0f8", "trigger.svg", 1, 1, "left"),
    "exec": ("#e9967a", "cog.svg", 1, 3, "left"),
    "filter": ("#e2d96e", "rbe.svg", 1, 1, "left"),
    # network
    "mqtt-in": ("#d8bfd8", "bridge.svg", 0, 1, "left"),
    "mqtt-out": ("#d8bfd8", "bridge.svg", 1, 0, "right"),
    "http-in": ("#e7e7ae", "white-globe.svg", 0, 1, "left"),
    "http-response": ("#e7e7ae", "white-globe.svg", 1, 0, "right"),
    "http-request": ("#e7e7ae", "white-globe.svg", 1, 1, "left"),
    "http": ("#e7e7ae", "white-globe.svg", 1, 1, "left"),
    "websocket-in": ("#d7d7a0", "white-globe.svg", 0, 1, "left"),
    "websocket-out": ("#d7d7a0", "white-globe.svg", 1, 0, "right"),
    "tcp-in": ("#c0c0c0", "bridge-dash.svg", 0, 1, "left"),
    "tcp-out": ("#c0c0c0", "bridge-dash.svg", 1, 0, "right"),
    "tcp-request": ("#c0c0c0", "bridge-dash.svg", 1, 1, "left"),
    "udp-in": ("#c0c0c0", "bridge-dash.svg", 0, 1, "left"),
    "udp-out": ("#c0c0c0", "bridge-dash.svg", 1, 0, "right"),
    # sequence
    "split": ("#e2d96e", "split.svg", 1, 1, "left"),
    "join": ("#e2d96e", "join.svg", 1, 1, "left"),
    "sort": ("#e2d96e", "sort.svg", 1, 1, "left"),
    "batch": ("#e2d96e", "batch.svg", 1, 1, "left"),
    # parser
    "csv": ("#debd5c", "parser-csv.svg", 1, 1, "left"),
    "html": ("#debd5c", "parser-html.svg", 1, 1, "left"),
    "json": ("#debd5c", "parser-json.svg", 1, 1, "left"),
    "xml": ("#debd5c", "parser-xml.svg", 1, 1, "left"),
    "yaml": ("#debd5c", "parser-yaml.svg", 1, 1, "left"),
    "base64": ("#debd5c", "parser-base64.png", 1, 1, "left"),
    "buffer-parser": ("#0090d4", "fa-expand.svg", 1, 1, "left"),
    "buffer-maker": ("#0090d4", "fa-compress.svg", 1, 1, "left"),
    # storage
    "file": ("#deb887", "file-out.svg", 1, 1, "left"),
    "file-in": ("#deb887", "file-in.svg", 1, 1, "left"),
    "watch": ("#deb887", "watch.svg", 0, 1, "left"),
    "sqlite": ("#e97b00", "sqlite.png", 1, 1, "left"),
    # サードパーティ
    "email-in": ("#c7e9c0", "envelope.svg", 0, 1, "left"),
    "email-out": ("#c7e9c0", "envelope.svg", 1, 0, "right"),
    "ftp": ("#deb887", "file.svg", 1, 1, "left"),
    "ftp-server": ("#f37a33", "ftp.png", 0, 2, "left"),
    "modbus-read": ("#e9967a", "modbus.png", 0, 2, "left"),
    "modbus-getter": ("#e9967a", "modbus.png", 1, 2, "left"),
    "modbus-flex-getter": ("#e9967a", "modbus.png", 1, 2, "left"),
    "modbus-write": ("#e9967a", "modbus.png", 1, 2, "right"),
    "modbus-server": ("#e9967a", "modbus.png", 1, 5, "right"),
    "sensehat-in": ("#c6dbef", "rpi.svg", 0, 1, "left"),
    "sensehat-out": ("#c6dbef", "rpi.svg", 1, 0, "right"),
    # Dashboard 2.0
    "ui-button": (DB_LIGHT, "fa-hand-pointer-o.svg", 1, 1, "left"),
    "ui-button-group": (DB_LIGHT, "fa-toggle-off.svg", 1, 1, "left"),
    "ui-dropdown": (DB_LIGHT, "fa-bars.svg", 1, 1, "left"),
    "ui-form": (DB_LIGHT, "fa-list-alt.svg", 1, 1, "left"),
    "ui-progress": (DB_LIGHT, "fa-percent.svg", 1, 0, "left"),
    "ui-radio": (DB_LIGHT, "fa-dot-circle-o.svg", 1, 1, "left"),
    "ui-slider": (DB_LIGHT, "fa-sliders.svg", 1, 1, "left"),
    "ui-spacer": (DB_LIGHT, "fa-arrows-h.svg", 0, 0, "left"),
    "ui-switch": (DB_LIGHT, "fa-toggle-on.svg", 1, 1, "left"),
    "ui-text-input": (DB_LIGHT, "fa-i-cursor.svg", 1, 1, "left"),
    "ui-audio": (DB_MEDIUM, "fa-volume-up.svg", 1, 1, "right"),
    "ui-chart": (DB_MEDIUM, "fa-line-chart.svg", 1, 1, "right"),
    "ui-gauge": (DB_MEDIUM, "ui-gauge.svg", 1, 1, "right"),
    "ui-led": (DB_MEDIUM, "fa-lightbulb-o.svg", 1, 0, "left"),
    "ui-notification": (DB_MEDIUM, "fa-envelope-o.svg", 1, 1, "right"),
    "ui-table": (DB_MEDIUM, "fa-table.svg", 1, 1, "left"),
    "ui-text": (DB_MEDIUM, "fa-font.svg", 1, 0, "right"),
    "ui-markdown": (DB_DARK, "ui-markdown.svg", 1, 1, "left"),
    "ui-template": (DB_DARK, "fa-code.svg", 1, 1, "left"),
    "ui-control": (DB_DARKEST, "fa-arrow-circle-right.svg", 1, 1, "right"),
}

# 図ごとに outputs-N で指定できる出力ポート数の上限
MAX_OUTPUTS = 5
# エディターと同じ寸法（@node-red/editor-client の view.js）。ノードの高さは
# max(30, 出力数 × 15)、出力ポートは中央を基準に 13px 間隔で並ぶ
PORT_GAP = 13

# 設定ノード（ワークスペースには置かれず、サイドバーの「設定ノード」に並ぶ）。
# ポートもアイコンも無い箱で描く。
CONFIG_NODES = ["ui-page", "ui-group"]

BASE = """\
/*
 * ノード図（node-example）の共有スタイル
 *
 * このファイルは scripts/gen-node-diagram-css.py が生成する。直接編集しない。
 * ノードの見た目は Node-RED エディターに合わせている（ノードの色・アイコン・
 * ポート・配線の色はエディターの既定のテーマ）。
 */

/* ワークスペース（方眼の白い背景） */
.node-example {
    background-color: #ffffff;
    background-image:
        linear-gradient(#eeeeee 1px, transparent 1px),
        linear-gradient(90deg, #eeeeee 1px, transparent 1px);
    background-size: 20px 20px;
    border: 1px solid #cccccc;
    border-radius: 5px;
    padding: 20px 16px;
    margin: 20px 0;
    color: #333333;
    font-family: "Helvetica Neue", Arial, Helvetica, sans-serif;
    font-size: 14px;
    line-height: 2.6;
    white-space: nowrap;
    overflow-x: auto;
}

/* ノード */
.node-example .node {
    position: relative;
    display: inline-block;
    box-sizing: border-box;
    min-width: 100px;
    min-height: 30px;
    margin: 4px 5px;
    padding: 6px 12px 6px 38px;
    border: 1px solid #999999;
    border-radius: 5px;
    background-color: #ffffff;
    background-image:
        var(--node-icon, none),
        linear-gradient(to right,
            rgba(0, 0, 0, 0.05) 0 30px,
            rgba(0, 0, 0, 0.1) 30px 31px,
            transparent 31px);
    background-repeat: no-repeat, no-repeat;
    background-position: 5px center, 0 0;
    background-size: 20px 30px, 100% 100%;
    color: #212121;
    font-family: "Helvetica Neue", Arial, Helvetica, sans-serif;
    font-size: 14px;
    font-weight: normal;
    line-height: 16px;
    text-align: left;
    vertical-align: middle;
    white-space: nowrap;
    z-index: 1;
}

/* 補足の行（ノード名の下の小さい文字） */
.node-example .node small {
    font-size: 12px;
    color: inherit;
}

/* 入力ポート（左）と出力ポート（右） */
.node-example .node::before,
.node-example .node::after {
    content: "";
    position: absolute;
    top: 50%;
    width: 10px;
    height: 10px;
    margin-top: -5px;
    box-sizing: border-box;
    border: 1px solid #999999;
    border-radius: 3px;
    background: #d9d9d9;
}

.node-example .node::before {
    left: -6px;
}

.node-example .node::after {
    right: -6px;
}

/* ノードの下のステータス表示 */
.node-example .status-label {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 3px;
    font-size: 11px;
    line-height: 12px;
    color: #424242;
    white-space: nowrap;
}

.node-example .status-label::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    margin-right: 4px;
    border-radius: 50%;
    background: #5a8;
    vertical-align: -1px;
}

/* 届かないノード（点線の枠で表す） */
.node-example .node.unreached {
    border: 2px dashed #c62828;
}

/* 配線 */
.node-example .arrow,
.node-example .arrow-dashed {
    display: inline-block;
    position: relative;
    width: 32px;
    height: 3px;
    margin: 0 -5px;
    background: #999999;
    vertical-align: middle;
    z-index: 0;
    font-size: 0;
    line-height: 0;
    color: transparent;
}

/* link ノードの仮想配線（エディターでも点線で描かれる） */
.node-example .arrow-dashed {
    width: 48px;
    background: repeating-linear-gradient(to right, #999999 0 6px, transparent 6px 10px);
}

/* 時間をおいて届く配線 */
.node-example .arrow.delayed {
    width: 48px;
    background: repeating-linear-gradient(to right, #999999 0 3px, transparent 3px 7px);
}

/* 複数の msg が流れる配線（線の上に msg を 3 つ描く） */
.node-example .arrow.multi {
    width: 56px;
}

.node-example .arrow.multi::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    width: 8px;
    height: 8px;
    margin: -4px 0 0 -4px;
    border-radius: 50%;
    background: #ff9800;
    box-shadow: -14px 0 0 #ff9800, 14px 0 0 #ff9800;
}

/* 途中で止まる配線（✗ 印） */
.node-example .arrow.broken::before {
    content: "\\2715";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    padding: 0 2px;
    background: #ffffff;
    color: #c62828;
    font-size: 16px;
    font-weight: bold;
    line-height: 16px;
}

/* 配線の途中に置く説明 */
.node-example .wire-label {
    display: inline-block;
    position: relative;
    z-index: 1;
    margin: 0 8px;
    font-size: 12px;
    line-height: 16px;
    color: #424242;
    vertical-align: middle;
}

/* 分岐（1つの出力から複数のノードへ配線する） */
.node-example .branch {
    display: inline-flex;
    flex-direction: column;
    position: relative;
    margin-left: -5px;
    padding-left: 18px;
    vertical-align: middle;
    line-height: 16px;
}

.node-example .branch::before {
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    width: 18px;
    height: 3px;
    margin-top: -1px;
    background: #999999;
}

.node-example .branch-row {
    display: flex;
    align-items: center;
    position: relative;
    padding: 2px 0;
}

.node-example .branch-row::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: #999999;
}

.node-example .branch-row:first-child::before {
    top: 50%;
}

.node-example .branch-row:last-child::before {
    bottom: 50%;
}

.node-example .branch-row .arrow {
    width: 24px;
    margin-left: 0;
}

/* 合流（複数のノードから1つのノードへ配線する）。分岐を左右反転したもの */
.node-example .merge {
    display: inline-flex;
    flex-direction: column;
    align-items: flex-end;
    position: relative;
    margin-right: -5px;
    padding-right: 18px;
    vertical-align: middle;
    line-height: 16px;
}

.node-example .merge::after {
    content: "";
    position: absolute;
    right: 0;
    top: 50%;
    width: 18px;
    height: 3px;
    margin-top: -1px;
    background: #999999;
}

.node-example .merge-row {
    display: flex;
    align-items: center;
    position: relative;
    padding: 2px 0;
}

.node-example .merge-row::after {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: #999999;
}

.node-example .merge-row:first-child::after {
    top: 50%;
}

.node-example .merge-row:last-child::after {
    bottom: 50%;
}

.node-example .merge-row .arrow {
    width: 24px;
    margin-right: 0;
}

/* 配線でつながらない隣どうしのノード（ポートが重ならないよう離す） */
.node-example .node + .node {
    margin-left: 16px;
}

/* 図の中の注記 */
.node-example .diagram-note {
    display: inline-block;
    margin: 0 8px;
    font-size: 12px;
    line-height: 16px;
    color: #424242;
    vertical-align: middle;
}

.node-example .diagram-note.error {
    color: #c62828;
}

/* 分岐の点線版（link の仮想配線や、配線せずに監視する関係） */
.node-example .branch.dashed::before,
.node-example .branch.dashed .branch-row::before {
    background: none;
}

.node-example .branch.dashed::before {
    border-top: 3px dashed #999999;
    height: 0;
}

.node-example .branch.dashed .branch-row::before {
    width: 0;
    border-left: 3px dashed #999999;
}

.node-example .branch-row .arrow-dashed {
    width: 32px;
    margin-left: 0;
}

/* 設定ノードどうし・設定ノードとウィジェットの関係（配線ではないので細い点線で描く） */
.node-example .node.config + .arrow,
.node-example .node-ui-page + .arrow,
.node-example .node-ui-group + .arrow {
    height: 0;
    margin: 0 4px;
    background: none;
    border-top: 2px dotted #999999;
}

/* 設定ノード（ワークスペースには置かれない） */
.node-example .node.config {
    min-width: 0;
    padding: 6px 12px;
    background-image: none;
    border-color: #bbbbbb;
}

.node-example .node.config::before,
.node-example .node.config::after {
    content: none;
}

/*
 * 配線のスクリプト（js/node-diagram.js）が動いたときの表示。
 * スクリプトは分岐・合流・複数の出力ポートからの配線を、エディターと同じ曲線で描き、
 * .node-example に .wired を付ける。スクリプトが動かない環境では、上の直線の表示のまま。
 */
.node-example.wired {
    position: relative;
}

.node-example .node-wires {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
    overflow: visible;
    z-index: 0;
}

.node-example.wired .branch::before,
.node-example.wired .branch-row::before,
.node-example.wired .merge::after,
.node-example.wired .merge-row::after {
    content: none;
}

.node-example.wired .branch {
    padding-left: 36px;
}

.node-example.wired .merge {
    padding-right: 36px;
}

/* 曲線で描き直した配線（線だけを消し、msg の印などは残す） */
.node-example.wired .arrow.redrawn {
    width: 48px;
    background: transparent;
}

/* ノードの色・アイコン・ポート */
"""


def build():
    out = [BASE]
    for name, (color, icon, inputs, outputs, align) in NODES.items():
        out.append(
            f".node-example .node-{name} {{\n"
            f"    background-color: {color};\n"
            f"    --node-icon: url(\"../img/node-icons/{icon}\");\n"
            f"}}\n"
        )
    no_in = [n for n, v in NODES.items() if v[2] == 0]
    no_out = [n for n, v in NODES.items() if v[3] == 0]
    right = [n for n, v in NODES.items() if v[4] == "right"]
    sel = lambda names, pseudo="": ",\n".join(f".node-example .node-{n}{pseudo}" for n in names)
    out.append("\n/* 入力ポートの無いノード */\n" + sel(no_in, "::before") + " {\n    content: none;\n}\n")
    out.append("\n/* 出力ポートの無いノード */\n" + sel(no_out, "::after") + " {\n    content: none;\n}\n")
    out.append(
        "\n/* アイコンが右側にあるノード */\n" + sel(right) + " {\n"
        "    padding: 6px 38px 6px 12px;\n"
        "    background-position: right 5px center, 0 0;\n"
        "    background-image:\n"
        "        var(--node-icon, none),\n"
        "        linear-gradient(to left,\n"
        "            rgba(0, 0, 0, 0.05) 0 30px,\n"
        "            rgba(0, 0, 0, 0.1) 30px 31px,\n"
        "            transparent 31px);\n"
        "}\n"
    )
    # 複数の出力ポート。::after を一番上のポートにし、残りを box-shadow で下へ並べる
    # （2 つ重ねた影で、ポートの塗りと枠を描く）。ポートの数は --node-outputs で配線のスクリプトに伝える
    for n in range(2, MAX_OUTPUTS + 1):
        names = [k for k, v in NODES.items() if v[3] == n]
        node_sel = ",\n".join([f".node-example .node.outputs-{n}"] + [f".node-example .node-{k}" for k in names])
        after_sel = ",\n".join([f".node-example .node.outputs-{n}::after"] + [f".node-example .node-{k}::after" for k in names])
        shadows = ",\n        ".join(
            f"0 {PORT_GAP * j}px 0 -1px #d9d9d9, 0 {PORT_GAP * j}px 0 0 #999999" for j in range(1, n))
        out.append(
            f"\n/* 出力ポートが {n} 個のノード */\n{node_sel} {{\n"
            f"    min-height: {max(30, n * 15)}px;\n"
            f"    --node-outputs: {n};\n"
            f"}}\n\n{after_sel} {{\n"
            f"    margin-top: {-5 - (n - 1) * PORT_GAP / 2:g}px;\n"
            f"    box-shadow:\n        {shadows};\n"
            f"}}\n"
        )
    out.append(
        "\n/* 設定ノード */\n" + sel(CONFIG_NODES) + " {\n"
        "    min-width: 0;\n"
        "    padding: 6px 12px;\n"
        "    background-color: #f3f3f3;\n"
        "    background-image: none;\n"
        "    border-color: #bbbbbb;\n"
        "}\n\n"
        + sel(CONFIG_NODES, "::before") + ",\n" + sel(CONFIG_NODES, "::after") + " {\n"
        "    content: none;\n"
        "}\n"
    )
    return "".join(out)


def main():
    css = build()
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != css:
            print("css/node-diagram.css が生成結果と一致しません。"
                  "python3 scripts/gen-node-diagram-css.py を実行してください。")
            return 1
        missing = [v[1] for v in NODES.values()
                   if not os.path.exists(os.path.join(ROOT, "img", "node-icons", v[1]))]
        if missing:
            print("アイコンがありません:", ", ".join(sorted(set(missing))))
            return 1
        print("OK: css/node-diagram.css は最新です")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"生成しました: {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
