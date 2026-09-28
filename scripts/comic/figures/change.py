"""change ノードの図（15-change.js の挙動に合わせる）"""
from lib import *

C = NODE_COLORS['function']


def rules():
    p = Panel('change ノードは設定したルールを上から順に適用する。代入で unit が加わり、置換で NG が 異常 に変わり、削除で debug が消え、移動で topic が line に移る', 560, 250, 'chr')
    card, w1, h1 = msgcard(8, 55, ['payload: "NG"', 'topic: "line1"', 'debug: true'], '入ってくる msg')
    p.add(card)
    node, inp, outs = nrnode(280, 70, 'change', C, w=110)
    p.add(wire(8 + w1, 55 + h1 / 2, inp[0] - 5, inp[1]), node)
    # ルールの一覧
    rl = ['① 値の代入　msg.unit ← "℃"', '② 値の置換　payload の NG → 異常', '③ 値の削除　msg.debug', '④ 値の移動　msg.topic → msg.line']
    p.add(f'<rect x="170" y="108" width="220" height="{20 + 20 * len(rl)}" rx="5" fill="#fffde7" stroke="#c9b458" stroke-width="1.5"/>',
          text(280, 124, 'ルール（上から順に実行）', 11, INK, weight='bold'))
    for i, r in enumerate(rl):
        p.add(text(180, 145 + 20 * i, r, 11, INK, 'start'))
    card, w2, h2 = msgcard(412, 45, ['payload: "異常"', 'topic: "line1"', 'debug: true', 'unit: "℃"', 'line: "line1"'],
                           '出ていく msg', hl=(0, 3, 4), strike=(1, 2), stroke='#7cb342')
    p.add(wire(outs[0][0], outs[0][1], 412, 45 + h2 / 2), card)
    p.add(text(412 + w2 / 2, 30, '黄色が変わった値、線が消えた値', 10, '#666'))
    return p


FIGURES = {'change-rules': rules}
