"""delay ノードの図（89-delay.js の挙動に合わせる）"""
from lib import *

C = NODE_COLORS['delay']
X0, SEC = 150, 110   # 時間軸の 0 秒の位置と 1 秒あたりの幅


def _axis(p, secs, y=160):
    p.add(line(X0, y, X0 + SEC * secs + 20, y, '#999', 1.5))
    for s in range(secs + 1):
        x = X0 + SEC * s
        p.add(line(x, y - 4, x, y + 4, '#999', 1.5), text(x, y + 17, f'{s}秒', 10, '#666'))
    p.add(text(40, 67, '入ってくる', 11, '#666', 'start'), text(40, 127, '出ていく', 11, '#666', 'start'))
    p.add(line(X0 - 10, 62, X0 + SEC * secs + 20, 62, '#eee', 1), line(X0 - 10, 122, X0 + SEC * secs + 20, 122, '#eee', 1))


def fixed():
    p = Panel('「指定した時間遅延」で 2 秒に設定すると、0 秒、0.5 秒、1 秒に入った msg が、それぞれ 2 秒後の 2 秒、2.5 秒、3 秒に出る', 560, 190, 'dlf')
    node, _, _ = nrnode(290, 22, 'delay 2秒', C, w=120, h=32)
    p.add(node)
    _axis(p, 3)
    for t, lab in [(0, 'A'), (0.5, 'B'), (1, 'C')]:
        xi, xo = X0 + SEC * t, X0 + SEC * (t + 2)
        p.add(packet(xi, 62, lab), packet(xo, 122, lab, '#e8f5e9', GREEN))
        p.arrow(xi + 8, 72, xo - 8, 110, '#bbb', 1.5, '4 3')
    return p


def rate_queue():
    p = Panel('「メッセージの流量制限」で 1 秒に 1 件、「中間メッセージをキューに追加」（既定）のとき、続けて入った A、B、C は、A がすぐに出て、B と C は 1 秒ずつ間を空けて出る', 560, 190, 'dlq')
    node, _, _ = nrnode(290, 22, 'delay 1件/秒', C, w=140, h=32)
    p.add(node)
    _axis(p, 3)
    for i, lab in enumerate('ABC'):
        xi, xo = X0 + 18 * i, X0 + SEC * i
        p.add(packet(xi, 62, lab), packet(xo, 122, lab, '#e8f5e9', GREEN))
        p.arrow(xi + 4, 72, xo - 2, 110, '#bbb', 1.5, '4 3')
    p.add(text(X0 + 250, 90, 'B と C は順番待ち（キュー）', 11, INK, 'start'))
    return p


def rate_drop():
    p = Panel('「メッセージの流量制限」で 1 秒に 1 件、「中間メッセージを削除」のとき、続けて入った A、B、C のうち A だけが出て、B と C は捨てられる', 560, 190, 'dld')
    node, _, _ = nrnode(290, 22, 'delay 1件/秒', C, w=140, h=32)
    p.add(node)
    _axis(p, 3)
    for i, lab in enumerate('ABC'):
        xi = X0 + 18 * i
        p.add(packet(xi, 62, lab))
    p.add(packet(X0, 122, 'A', '#e8f5e9', GREEN))
    p.arrow(X0, 72, X0, 110, '#bbb', 1.5, '4 3')
    p.add(trash(X0 + 150, 100))
    p.arrow(X0 + 46, 64, X0 + 136, 92, RED, 1.5, '4 3')
    p.add(text(X0 + 172, 100, 'B と C は捨てられる', 11, RED, 'start', 'bold'))
    return p


FIGURES = {'delay-fixed': fixed, 'delay-rate-queue': rate_queue, 'delay-rate-drop': rate_drop}
