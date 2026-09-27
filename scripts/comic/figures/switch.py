"""switch ノードの図（10-switch.js の挙動に合わせる）"""
from lib import *

C = NODE_COLORS['function']


def basic():
    p = Panel('payload が -3、0、7 の 3 つの msg が switch に入り、条件「< 0」「== 0」「> 0」に合う出力へ 1 つずつ振り分けられる', 560, 200, 'swb')
    node, inp, outs = nrnode(280, 100, 'switch', C, w=120, outputs=3, h=96)
    ins = [('payload: -3', 55, '#fdecea', RED), ('payload: 0', 100, '#eceff1', '#607d8b'), ('payload: 7', 145, '#e3f2fd', BLUE)]
    for t, y, f, st in ins:
        p.add(packet(80, y, t, f, st), wire(80 + tw(t, 11) / 2 + 6, y, inp[0] - 5, inp[1]))
    p.add(node, text(80, 25, '入ってくる msg', 11, '#666'))
    rules = [('① < 0', '-3', '#fdecea', RED), ('② == 0', '0', '#eceff1', '#607d8b'), ('③ > 0', '7', '#e3f2fd', BLUE)]
    for (lab, v, f, st), (ox, oy) in zip(rules, outs):
        p.add(wire(ox, oy, 430, oy), text(ox + 10, oy - 6, lab, 11, INK, 'start', 'bold'), packet(470, oy, f'payload: {v}', f, st))
    p.add(text(470, 25, '条件に合う出力から出る', 11, '#666'))
    return p


def checkall():
    p = Panel('条件が「> 10」「> 0」「その他」のとき、payload 20 は「全ての条件を適用」では出力1と出力2の両方から、「最初に合致した条件で終了」では出力1だけから出る', 560, 210, 'swc')
    for i, (title, both) in enumerate([('全ての条件を適用（既定）', True), ('最初に合致した条件で終了', False)]):
        ox0 = i * 280
        if i:
            p.add(line(280, 20, 280, 200, '#ddd', 1.5, '4 4'))
        p.add(text(ox0 + 140, 22, title, 12, INK, weight='bold'))
        node, inp, outs = nrnode(ox0 + 160, 115, 'switch', C, w=90, outputs=3, h=90)
        p.add(packet(ox0 + 52, 115, 'payload: 20'))
        p.add(wire(ox0 + 96, 115, inp[0] - 5, inp[1], '#999'), node)
        labs = ['> 10', '> 0', 'その他']
        for k, ((x, y), lab) in enumerate(zip(outs, labs)):
            hit = k == 0 or (k == 1 and both)
            p.add(text(x + 6, y - 5, lab, 10, '#666', 'start'))
            if hit:
                p.add(wire(x, y, ox0 + 236, y, GREEN, 2.5), packet(ox0 + 256, y, '20', '#e8f5e9', GREEN))
            else:
                p.add(wire(x, y, ox0 + 244, y, '#ccc', 1.5, '3 3'), text(ox0 + 264, y + 4, '出ない', 10, '#999'))
    return p


FIGURES = {'switch-basic': basic, 'switch-checkall': checkall}
