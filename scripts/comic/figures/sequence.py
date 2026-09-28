"""Sequence カテゴリ（split / join / sort / batch）の図（17-split.js / 18-sort.js / 19-batch.js）"""
from lib import *

C = NODE_COLORS['sequence']


def split():
    p = Panel('split ノードは、配列の payload [10, 20, 30] を 3 つの msg に分け、それぞれに何番目か（parts.index）と全部で何個か（parts.count）を付けて送り出す', 560, 200, 'spl')
    card, w, h = msgcard(8, 70, ['payload: [10, 20, 30]'], '入ってくる msg')
    node, inp, outs = nrnode(250, 95, 'split', C, w=96)
    p.add(card, wire(8 + w, 70 + h / 2, inp[0] - 5, inp[1]), node)
    for i, v in enumerate([10, 20, 30]):
        y = 18 + 58 * i
        c, w2, h2 = msgcard(360, y, [f'payload: {v}', f'parts.index: {i}  count: 3'], f'msg {i+1}', stroke='#7cb342', hl=(0,))
        p.add(wire(outs[0][0], outs[0][1], 360, y + h2 / 2), c)
    return p


def join_auto():
    p = Panel('join ノードの「自動」モードは、split で分けられた msg を parts の情報を頼りに集め、全部そろったら元の配列 [10, 20, 30] に戻して 1 つの msg で送り出す', 560, 200, 'jna')
    for i, v in enumerate([10, 20, 30]):
        y = 18 + 58 * i
        c, w, h = msgcard(8, y, [f'payload: {v}', f'parts.index: {i}  count: 3'], f'msg {i+1}')
        p.add(c, wire(8 + w, y + h / 2, 270 - 53, 100))
    node, inp, outs = nrnode(270, 100, 'join（自動）', C, w=106, fs=11)
    p.add(node)
    c, w2, h2 = msgcard(380, 78, ['payload: [10, 20, 30]'], '出ていく msg', stroke='#7cb342', hl=(0,))
    p.add(wire(outs[0][0], outs[0][1], 380, 78 + h2 / 2), c, text(450, 140, '3 つそろったら 1 つにまとめる', 10, '#666'))
    return p


def join_manual():
    p = Panel('join ノードの「手動」モードで「キー／値の組」を選び、2 件でまとめると、topic をキー、payload を値にしたオブジェクトが 1 つの msg で出る', 560, 180, 'jnm')
    for i, (t, v) in enumerate([('temp', 25), ('hum', 60)]):
        y = 28 + 72 * i
        c, w, h = msgcard(8, y, [f'topic: "{t}"', f'payload: {v}'], f'msg {i+1}')
        p.add(c, wire(8 + w, y + h / 2, 270 - 53, 90))
    node, inp, outs = nrnode(270, 90, 'join（手動）', C, w=106, fs=11)
    p.add(node)
    c, w2, h2 = msgcard(370, 68, ['payload: {', '  temp: 25,', '  hum: 60', '}'], '出ていく msg', stroke='#7cb342', hl=(1, 2))
    p.add(wire(outs[0][0], outs[0][1], 370, 68 + h2 / 2), c)
    return p


def sort():
    p = Panel('sort ノードは、msg.payload の配列 [30, 10, 20] を並べ替え、[10, 20, 30] にして送り出す（既定は昇順）', 560, 130, 'srt')
    card, w, h = msgcard(8, 40, ['payload: [30, 10, 20]'], '入ってくる msg')
    node, inp, outs = nrnode(275, 65, 'sort', C, w=96)
    p.add(card, wire(8 + w, 40 + h / 2, inp[0] - 5, inp[1]), node, text(275, 105, '小さい順に並べる', 10, '#666'))
    c, w2, h2 = msgcard(380, 40, ['payload: [10, 20, 30]'], '出ていく msg', stroke='#7cb342', hl=(0,))
    p.add(wire(outs[0][0], outs[0][1], 380, 40 + h2 / 2), c)
    return p


def batch():
    p = Panel('batch ノードの「メッセージ数でグループ化」で 3 件にすると、次々に届く msg を 3 件ずつの列に区切り、3 件たまった時点で、各 msg に列の情報（parts）を付けて送り出す。中身はまとめない', 560, 190, 'bat')
    node, _, _ = nrnode(290, 22, 'batch（3件ずつ）', C, w=160, h=32, fs=11)
    p.add(text(290, 104, '3 件たまったら、その 3 件を送り出す（中身はまとめない）', 10, '#666'))
    p.add(node, text(20, 75, '入ってくる', 11, '#666', 'start'), text(20, 140, '出ていく', 11, '#666', 'start'))
    labs = 'ABCDEF'
    for i, l in enumerate(labs):
        x = 120 + 70 * i
        p.add(packet(x, 70, l))
        p.add(packet(x, 135, l, '#e8f5e9', GREEN))
        p.arrow(x, 80, x, 92, '#ddd', 1.2)
        p.arrow(x, 112, x, 123, '#ddd', 1.2)
    for g, (a, b) in enumerate([(0, 2), (3, 5)]):
        x1, x2 = 120 + 70 * a - 20, 120 + 70 * b + 20
        p.add(f'<path d="M{x1} 152 v8 h{x2-x1} v-8" fill="none" stroke="{ORANGE}" stroke-width="2"/>',
              text((x1 + x2) / 2, 177, f'列 {g+1}（parts.index 0〜2）', 10, ORANGE, weight='bold'))
    return p


FIGURES = {'split-basic': split, 'join-auto': join_auto, 'join-manual': join_manual, 'sort-basic': sort, 'batch-basic': batch}
