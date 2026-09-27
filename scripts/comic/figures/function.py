"""Function カテゴリ（function / template / trigger / range / exec / filter）の図"""
from lib import *

C = NODE_COLORS['function']
FN = '#fdd0a2'   # function / exec の色


def _code(p, x, y, lines, w=220):
    h = 12 + 17 * len(lines)
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#2d3133"/>')
    for i, l in enumerate(lines):
        p.add(f'<text x="{x+10}" y="{y+20+17*i}" font-size="11" fill="#f8f8f2" font-family="\'Courier New\', monospace">{esc(l)}</text>')


def function_basic():
    p = Panel('function ノードは、書いた JavaScript で msg を加工し、return した msg を送り出す。摂氏 20 の payload が華氏 68 になって出る', 560, 160, 'fnb')
    card, w, h = msgcard(8, 40, ['payload: 20'], '入ってくる msg')
    node, inp, outs = nrnode(270, 60, 'function', FN, w=110)
    p.add(card, wire(8 + w, 40 + h / 2, inp[0] - 5, inp[1]), node)
    _code(p, 125, 100, ['msg.payload = msg.payload * 1.8 + 32;', 'return msg;'], 290)
    p.add(line(270, 80, 270, 98, '#999', 1.5, '3 3'), text(280, 93, '中に書いたコード', 10, '#666', 'start'))
    card, w2, h2 = msgcard(420, 40, ['payload: 68'], '出ていく msg', hl=(0,), stroke='#7cb342')
    p.add(wire(outs[0][0], outs[0][1], 420, 40 + h2 / 2), card)
    return p


def function_outputs():
    p = Panel('出力を 2 つにした function ノードで、return [msg, null] とすると出力1だけから、return [null, msg] とすると出力2だけから出る。return null のときはどこからも出ない', 560, 200, 'fno')
    node, inp, outs = nrnode(230, 100, 'function', FN, w=110, outputs=2, h=60)
    p.add(packet(60, 100, 'payload: 35'), wire(100, 100, inp[0] - 5, inp[1]), node)
    p.add(wire(outs[0][0], outs[0][1], 330, 55), wire(outs[1][0], outs[1][1], 330, 145))
    p.add(packet(380, 55, '出力1：30 以上', '#fdecea', RED), packet(380, 145, '出力2：30 未満', '#e3f2fd', BLUE))
    _code(p, 20, 20, ['if (msg.payload >= 30) return [msg, null];', 'return [null, msg];'], 300)
    p.add(text(480, 102, '35 は出力1へ', 11, RED, 'middle', 'bold'), text(300, 190, 'return null なら、どの出力からも出ない', 11, '#666'))
    return p


def template():
    p = Panel('template ノードは、テンプレートの {{payload}} の部分を msg の値で置き換えた文字列を、msg.payload に入れて送り出す', 560, 190, 'tpl')
    card, w, h = msgcard(8, 40, ['payload: "田中"'], '入ってくる msg')
    node, inp, outs = nrnode(215, 60, 'template', C, w=110)
    p.add(card, wire(8 + w, 40 + h / 2, inp[0] - 5, inp[1]), node)
    p.add(f'<rect x="115" y="100" width="200" height="50" rx="5" fill="#fffde7" stroke="#c9b458" stroke-width="1.5"/>',
          text(215, 118, 'テンプレート', 10, '#666'),
          f'<text x="215" y="140" font-size="12" fill="{INK}" text-anchor="middle">こんにちは <tspan fill="{RED}" font-weight="bold">{{{{payload}}}}</tspan> さん</text>',
          line(215, 80, 215, 98, '#999', 1.5, '3 3'))
    card, w2, h2 = msgcard(318, 40, ['payload: "こんにちは 田中 さん"'], '出ていく msg', hl=(0,), stroke='#7cb342')
    p.add(wire(outs[0][0], outs[0][1], 380, 40 + h2 / 2), card)
    return p


def trigger():
    p = Panel('trigger ノードは、msg が届くとすぐに 1 を送り、250 ミリ秒後に 0 を送る（既定）。待っているあいだに届いた msg は無視される', 560, 200, 'trg')
    node, _, _ = nrnode(300, 22, 'trigger 250ms', C, w=150, h=32)
    p.add(node)
    X0, U = 150, 1.3   # 1 ミリ秒あたりの幅
    y_in, y_out, y_ax = 70, 130, 170
    p.add(line(X0, y_ax, X0 + 390, y_ax, '#999', 1.5))
    for t in [0, 100, 200, 300]:
        x = X0 + t * U
        p.add(line(x, y_ax - 4, x, y_ax + 4, '#999', 1.5), text(x, y_ax + 17, f'{t}ms', 10, '#666'))
    p.add(text(40, y_in + 5, '入ってくる', 11, '#666', 'start'), text(40, y_out + 5, '出ていく', 11, '#666', 'start'))
    p.add(packet(X0, y_in, 'A'), packet(X0 + 120 * U, y_in, 'B', '#eceff1', '#999'), text(X0 + 120 * U, y_in - 16, '無視', 10, '#999', weight='bold'))
    p.add(packet(X0, y_out, '1', '#e8f5e9', GREEN), packet(X0 + 250 * U, y_out, '0', '#e8f5e9', GREEN))
    p.arrow(X0, y_in + 10, X0, y_out - 12, '#bbb', 1.5, '4 3').arrow(X0 + 8, y_in + 8, X0 + 250 * U - 10, y_out - 12, '#bbb', 1.5, '4 3')
    p.add(f'<rect x="{X0+8}" y="{y_out+14}" width="{250*U-16}" height="8" rx="4" fill="#fff3e0"/>',
          text(X0 + 125 * U, y_out + 22, '待っているあいだ', 9, ORANGE, weight='bold'))
    return p


def range_():
    p = Panel('range ノードは、入力の範囲 0〜1000 を出力の範囲 0〜100 に比例して変換する。payload 250 は 25 になって出る', 560, 180, 'rng')
    node, inp, outs = nrnode(280, 40, 'range', C, w=100)
    p.add(packet(90, 40, 'payload: 250'), wire(130, 40, inp[0] - 5, inp[1]), node,
          wire(outs[0][0], outs[0][1], 430, 40), packet(475, 40, 'payload: 25', '#e8f5e9', GREEN))
    for y, lo, hi, v, lab in [(95, '0', '1000', 250 / 1000, '入力の範囲'), (145, '0', '100', 25 / 100, '出力の範囲')]:
        x0, x1 = 150, 450
        p.add(line(x0, y, x1, y, INK, 3), line(x0, y - 6, x0, y + 6, INK, 2), line(x1, y - 6, x1, y + 6, INK, 2),
              text(x0, y + 20, lo, 11), text(x1, y + 20, hi, 11), text(x0 - 12, y + 4, lab, 11, '#666', 'end'),
              f'<circle cx="{x0 + (x1 - x0) * v}" cy="{y}" r="7" fill="{ORANGE}"/>')
    p.add(line(150 + 300 * 0.25, 103, 150 + 300 * 0.25, 137, ORANGE, 2, '4 3'), text(150 + 300 * 0.25 + 8, 124, '同じ割合（25%）の位置', 10, ORANGE, 'start'))
    return p


def exec_():
    p = Panel('exec ノードは、設定したコマンドに payload を付け足して OS で実行し、標準出力、標準エラー出力、終了コードを 3 つの出力から送り出す', 560, 200, 'exe')
    node, inp, outs = nrnode(230, 100, 'exec', FN, w=110, outputs=3, h=84)
    p.add(packet(70, 100, 'payload: "-l"'), wire(108, 100, inp[0] - 5, inp[1]), node)
    p.add(f'<rect x="150" y="12" width="160" height="26" rx="4" fill="#2d3133"/>',
          f'<text x="230" y="30" font-size="12" fill="#f8f8f2" text-anchor="middle" font-family="\'Courier New\', monospace">$ ls -l</text>',
          text(230, 52, 'コマンド＋payload を実行', 10, '#666'))
    labs = [('①標準出力', 'payload: "total 12 …"', '#e8f5e9', GREEN), ('②標準エラー出力', '（エラー文があるときだけ）', '#fdecea', RED), ('③終了コード', 'payload: {code: 0}', '#e3f2fd', BLUE)]
    for (ox, oy), (lab, v, f, st) in zip(outs, labs):
        p.add(wire(ox, oy, 380, oy), text(ox + 10, oy - 5, lab, 10, '#666', 'start'), packet(470, oy, v, f, st, 10))
    return p


def filter_():
    p = Panel('filter ノードは既定で、payload が前回と同じなら捨て、変わったときだけ送り出す。20、20、21、21、20 と届くと、20、21、20 が出る', 560, 170, 'flt')
    node, _, _ = nrnode(290, 22, 'filter', C, w=100, h=32)
    p.add(node, text(40, 75, '入ってくる', 11, '#666', 'start'), text(40, 135, '出ていく', 11, '#666', 'start'))
    vals = [20, 20, 21, 21, 20]
    prev = None
    for i, v in enumerate(vals):
        x = 160 + 80 * i
        p.add(packet(x, 70, str(v)))
        if v != prev:
            p.add(packet(x, 130, str(v), '#e8f5e9', GREEN))
            p.arrow(x, 80, x, 118, '#bbb', 1.5, '4 3')
        else:
            p.add(xmark(x, 100, 6), text(x, 160, '前回と同じ', 9, '#999'))
        prev = v
    return p


FIGURES = {'function-basic': function_basic, 'function-outputs': function_outputs, 'template-basic': template,
           'trigger-basic': trigger, 'range-basic': range_, 'exec-basic': exec_, 'filter-basic': filter_}
