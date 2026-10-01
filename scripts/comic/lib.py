"""漫画風の図（インライン SVG）を描くための共通部品。

ガイド本文の図はこの部品で生成し、scripts/comic/build.py で HTML に埋め込む。
手で SVG を直接書き換えず、図の定義（scripts/comic/figures/*.py）を直して再生成すること。
"""
import itertools
_uid = itertools.count(1)
INK = '#37474f'
RED = '#c62828'
GREEN = '#2e7d32'
BLUE = '#1976d2'
ORANGE = '#ef6c00'

def tw(t, fs=12):
    """文字列のおおよその描画幅。

    Python 3.12 から sum() が浮動小数の誤差を補正して足すようになり、3.11 以前と
    末尾の桁が変わる（191.5999999999999 と 191.6）。生成結果を Python の版に
    よらず同じにするため、小数第 2 位で丸める。
    """
    return round(sum(fs if ord(c) > 255 else fs * 0.6 for c in t), 2)

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, t, fs=12, fill=INK, anchor='middle', weight='normal'):
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(t)}</text>'

def pc(x, y, mood='neutral', label=None, screen='#e3f2fd'):
    """顔つきのパソコン。(x, y) は画面の中心"""
    s = [f'<rect x="{x-22}" y="{y-17}" width="44" height="32" rx="4" fill="#fff" stroke="{INK}" stroke-width="2"/>',
         f'<rect x="{x-18}" y="{y-13}" width="36" height="24" rx="2" fill="{screen}"/>',
         f'<rect x="{x-4}" y="{y+15}" width="8" height="5" fill="{INK}"/>',
         f'<rect x="{x-12}" y="{y+20}" width="24" height="3" rx="1" fill="{INK}"/>']
    if mood == 'happy':
        s.append(f'<path d="M{x-8} {y-5} q3 -4 6 0 M{x+2} {y-5} q3 -4 6 0" fill="none" stroke="{INK}" stroke-width="1.8"/>')
        s.append(f'<path d="M{x-7} {y+1} Q{x} {y+9} {x+7} {y+1}" fill="none" stroke="{INK}" stroke-width="2"/>')
    else:
        s.append(f'<circle cx="{x-6}" cy="{y-5}" r="2.2" fill="{INK}"/><circle cx="{x+6}" cy="{y-5}" r="2.2" fill="{INK}"/>')
        if mood == 'sad':
            s.append(f'<path d="M{x-7} {y+6} Q{x} {y} {x+7} {y+6}" fill="none" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<path d="M{x+24} {y-20} q-4 7 0 9 q4 -2 0 -9z" fill="#64b5f6"/>')
        elif mood == 'confused':
            s.append(f'<path d="M{x-6} {y+4} q3 -3 6 0 q3 3 6 0" fill="none" stroke="{INK}" stroke-width="2"/>')
            s.append(text(x + 27, y - 12, '?', 16, RED, weight='bold'))
        elif mood == 'surprised':
            s.append(f'<circle cx="{x}" cy="{y+4}" r="3" fill="none" stroke="{INK}" stroke-width="2"/>')
            s.append(text(x + 27, y - 12, '!', 16, RED, weight='bold'))
        else:
            s.append(f'<line x1="{x-5}" y1="{y+4}" x2="{x+5}" y2="{y+4}" stroke="{INK}" stroke-width="2"/>')
    if label:
        s.append(text(x, y + 37, label, 12))
    return ''.join(s)

def server(x, y, mood='neutral', label=None):
    """顔つきのサーバー（縦長の箱）。(x, y) は中心"""
    s = [f'<rect x="{x-18}" y="{y-24}" width="36" height="48" rx="4" fill="#fff" stroke="{INK}" stroke-width="2"/>',
         f'<line x1="{x-12}" y1="{y+12}" x2="{x+12}" y2="{y+12}" stroke="{INK}" stroke-width="1.5"/>',
         f'<line x1="{x-12}" y1="{y+18}" x2="{x+12}" y2="{y+18}" stroke="{INK}" stroke-width="1.5"/>']
    fy = y - 8
    if mood == 'happy':
        s.append(f'<path d="M{x-8} {fy-3} q3 -4 6 0 M{x+2} {fy-3} q3 -4 6 0" fill="none" stroke="{INK}" stroke-width="1.8"/>')
        s.append(f'<path d="M{x-6} {fy+3} Q{x} {fy+10} {x+6} {fy+3}" fill="none" stroke="{INK}" stroke-width="2"/>')
    else:
        s.append(f'<circle cx="{x-5}" cy="{fy-3}" r="2.2" fill="{INK}"/><circle cx="{x+5}" cy="{fy-3}" r="2.2" fill="{INK}"/>')
        if mood == 'sad':
            s.append(f'<path d="M{x-6} {fy+8} Q{x} {fy+2} {x+6} {fy+8}" fill="none" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<path d="M{x+21} {y-28} q-4 7 0 9 q4 -2 0 -9z" fill="#64b5f6"/>')
        elif mood == 'evil':
            s.append(f'<path d="M{x-9} {fy-8} l7 3 M{x+9} {fy-8} l-7 3" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<path d="M{x-6} {fy+4} Q{x} {fy+9} {x+6} {fy+4}" fill="none" stroke="{INK}" stroke-width="2"/>')
        else:
            s.append(f'<line x1="{x-5}" y1="{fy+5}" x2="{x+5}" y2="{fy+5}" stroke="{INK}" stroke-width="2"/>')
    if label:
        s.append(text(x, y + 40, label, 12))
    return ''.join(s)

def bubble(x, y, t, tail=None, fs=12, fill='#fff', stroke='#555', color=INK, shout=False):
    """吹き出し。(x, y) は中心、tail は尾の先端"""
    w = tw(t, fs) + 16
    h = fs + 12
    s = []
    if shout:
        # ギザギザの吹き出し
        pts = []
        n = 14
        import math
        for i in range(n * 2):
            a = math.pi * 2 * i / (n * 2)
            rx, ry = (w / 2 + (6 if i % 2 == 0 else 0)), (h / 2 + (6 if i % 2 == 0 else 0))
            pts.append(f'{x + rx*math.cos(a):.1f},{y + ry*math.sin(a):.1f}')
        s.append(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    else:
        if tail:
            tx, ty = tail
            bx = max(x - w / 2 + 10, min(x + w / 2 - 10, tx))
            by = y + h / 2 if ty > y else y - h / 2
            s.append(f'<polygon points="{bx-6},{by} {bx+6},{by} {tx},{ty}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" stroke-linejoin="round"/>')
        s.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        if tail:
            s.append(f'<line x1="{bx-5}" y1="{by}" x2="{bx+5}" y2="{by}" stroke="{fill}" stroke-width="3"/>')
    s.append(text(x, y + fs * 0.36, t, fs, color))
    return ''.join(s)

def packet(x, y, t, fill='#fff8e1', stroke=ORANGE, fs=11):
    w = tw(t, fs) + 12
    return (f'<rect x="{x-w/2}" y="{y-10}" width="{w}" height="20" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            + text(x, y + 4, t, fs, INK))

def box(x, y, w, h, t, fill='#eceff1', stroke=INK, fs=12, color=INK, rx=5):
    return (f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            + text(x, y + fs * 0.36, t, fs, color, weight='bold'))

def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>'

class Panel:
    def __init__(self, label, w=360, h=190, key=None):
        # key はページ内で一意にする（矢印の marker id に使う）
        self.id = key if key else next(_uid)
        self.w, self.h, self.label = w, h, label
        self.parts = []
    def add(self, *p):
        self.parts.extend(p); return self
    def arrow(self, x1, y1, x2, y2, color=INK, w=2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        mid = {INK: 'k', RED: 'r', GREEN: 'g', BLUE: 'b', ORANGE: 'o'}.get(color, 'k')
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d} marker-end="url(#m{self.id}{mid})"/>')
        return self
    def render(self):
        defs = ''.join(
            f'<marker id="m{self.id}{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>'
            for k, c in [('k', INK), ('r', RED), ('g', GREEN), ('b', BLUE), ('o', ORANGE)])
        return (f'<svg class="comic" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.label)}" '
                f'xmlns="http://www.w3.org/2000/svg" font-family="\'Segoe UI\', \'Hiragino Sans\', \'Meiryo\', sans-serif">'
                f'<defs>{defs}</defs>' + ''.join(self.parts) + '</svg>')

def xmark(x, y, s=8, color=RED):
    return line(x - s, y - s, x + s, y + s, color, 3) + line(x - s, y + s, x + s, y - s, color, 3)

def boom(x, y, r=18, t='ドカン'):
    import math
    pts = []
    for i in range(20):
        a = math.pi * 2 * i / 20
        rr = r if i % 2 == 0 else r * 0.55
        pts.append(f'{x + rr*math.cos(a)*1.4:.1f},{y + rr*math.sin(a):.1f}')
    return (f'<polygon points="{" ".join(pts)}" fill="#ffeb3b" stroke="{RED}" stroke-width="2"/>'
            + text(x, y + 4, t, 11, RED, weight='bold'))

def cloud(x, y, w, h, fill='#eceff1', stroke='#90a4ae'):
    rx, ry = w / 2, h / 2
    return (f'<g fill="{fill}" stroke="{stroke}" stroke-width="1.5">'
            f'<ellipse cx="{x-rx*0.45}" cy="{y+ry*0.15}" rx="{rx*0.55}" ry="{ry*0.75}"/>'
            f'<ellipse cx="{x+rx*0.45}" cy="{y+ry*0.15}" rx="{rx*0.55}" ry="{ry*0.75}"/>'
            f'<ellipse cx="{x}" cy="{y-ry*0.2}" rx="{rx*0.6}" ry="{ry*0.85}"/></g>'
            f'<ellipse cx="{x}" cy="{y+ry*0.1}" rx="{rx*0.85}" ry="{ry*0.6}" fill="{fill}"/>')

def lock(x, y, color=GREEN):
    return (f'<path d="M{x-6} {y-2} v-6 a6 6 0 0 1 12 0 v6" fill="none" stroke="{color}" stroke-width="2.5"/>'
            f'<rect x="{x-9}" y="{y-2}" width="18" height="14" rx="2" fill="{color}"/>'
            f'<circle cx="{x}" cy="{y+5}" r="2" fill="#fff"/>')

def eye(x, y, s=1.0):
    return (f'<path d="M{x-14*s} {y} Q{x} {y-11*s} {x+14*s} {y} Q{x} {y+11*s} {x-14*s} {y}z" fill="#fff" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="{4.5*s}" fill="{INK}"/>')

def envelope(x, y, w=40, h=26, fill='#fff', sealed=False):
    s = (f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
         f'<path d="M{x-w/2} {y-h/2} L{x} {y+2} L{x+w/2} {y-h/2}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    if sealed:
        s += f'<circle cx="{x}" cy="{y+1}" r="5" fill="{RED}"/>'
    return s

def hourglass(x, y):
    return (f'<path d="M{x-7} {y-10} h14 l-7 10 l7 10 h-14 l7 -10z" fill="#fff3e0" stroke="{INK}" stroke-width="1.8"/>'
            f'<path d="M{x-3} {y+7} h6 l-3 -4z" fill="{ORANGE}"/>')

def sparkle(x, y, color='#fbc02d'):
    return f'<path d="M{x} {y-8} L{x+2} {y-2} L{x+8} {y} L{x+2} {y+2} L{x} {y+8} L{x-2} {y+2} L{x-8} {y} L{x-2} {y-2}z" fill="{color}"/>'


# ---- ノードガイド用の部品 ------------------------------------------------

# Node-RED エディターのノードの色（パレットの分類ごと）
NODE_COLORS = {
    'function': '#E2D96E',   # switch / change / range / template など
    'delay': '#E6E0F8',      # delay / trigger
    'common': '#a6bbcf',     # inject / debug
    'parser': '#DEBD5C',
    'sequence': '#E2D96E',
    'network': '#C0DEED',
    'storage': '#E6E0F8',
}


def nrnode(x, y, label, color, w=None, outputs=1, mood='happy', h=None, inputs=1, fs=12):
    """Node-RED のノード（顔つき）。(x, y) は中心。

    戻り値は (svg, 入力ポート座標, 出力ポート座標のリスト)。
    """
    w = w or max(96, tw(label, 12) + 56)
    h = h or max(40, 22 * outputs + 8)
    left, top = x - w / 2, y - h / 2
    s = [f'<rect x="{left}" y="{top}" width="{w}" height="{h}" rx="6" fill="{color}" stroke="#999" stroke-width="1.5"/>',
         f'<rect x="{left}" y="{top}" width="30" height="{h}" rx="6" fill="rgba(0,0,0,0.08)"/>']
    # 顔（アイコン領域）
    fx, fy = left + 15, y
    if mood == 'happy':
        s.append(f'<path d="M{fx-7} {fy-4} q2.5 -3.5 5 0 M{fx+2} {fy-4} q2.5 -3.5 5 0" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        s.append(f'<path d="M{fx-5} {fy+2} Q{fx} {fy+8} {fx+5} {fy+2}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    else:
        s.append(f'<circle cx="{fx-4}" cy="{fy-4}" r="1.8" fill="{INK}"/><circle cx="{fx+4}" cy="{fy-4}" r="1.8" fill="{INK}"/>')
        if mood == 'sad':
            s.append(f'<path d="M{fx-5} {fy+7} Q{fx} {fy+2} {fx+5} {fy+7}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
            s.append(f'<path d="M{fx+10} {fy-12} q-3 5 0 7 q3 -2 0 -7z" fill="#64b5f6"/>')
        elif mood == 'surprised':
            s.append(f'<circle cx="{fx}" cy="{fy+4}" r="2.6" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        else:
            s.append(f'<line x1="{fx-4}" y1="{fy+4}" x2="{fx+4}" y2="{fy+4}" stroke="{INK}" stroke-width="1.8"/>')
    s.append(text(left + 30 + (w - 30) / 2, y + fs * 0.35, label, fs, INK, weight='bold'))
    inp = (left, y)
    if inputs:
        s.append(f'<rect x="{left-5}" y="{y-5}" width="10" height="10" rx="2" fill="#d9d9d9" stroke="#999"/>')
    outs = []
    for i in range(outputs):
        oy = y if outputs == 1 else top + (h / outputs) * (i + 0.5)
        s.append(f'<rect x="{left+w-5}" y="{oy-5}" width="10" height="10" rx="2" fill="#d9d9d9" stroke="#999"/>')
        outs.append((left + w + 5, oy))
    return ''.join(s), inp, outs


def status_dot(x, y, t, fill=GREEN, shape='dot'):
    """ノードの下に出るステータス表示（色つきの点と文字）"""
    mark = (f'<circle cx="{x+5}" cy="{y}" r="5" fill="{fill}"/>' if shape == 'dot'
            else f'<circle cx="{x+5}" cy="{y}" r="4" fill="#fff" stroke="{fill}" stroke-width="2"/>')
    return mark + text(x + 14, y + 4, t, 11, INK, 'start')


def msgcard(x, y, lines, title='msg', w=None, hl=(), strike=(), fill='#fff', stroke='#90a4ae'):
    """msg の中身を書いたカード。(x, y) は左上。

    hl は強調する行の番号（変わった値）、strike は取り消し線を引く行の番号（消えた値）。
    """
    w = w or max(tw(l, 11) for l in lines + [title]) + 20
    h = 22 + 17 * len(lines)
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="5" fill="{stroke}"/>',
         f'<rect x="{x}" y="{y+12}" width="{w}" height="6" fill="{stroke}"/>',
         text(x + 8, y + 13, title, 11, '#fff', 'start', 'bold')]
    for i, l in enumerate(lines):
        ly = y + 33 + 17 * i
        if i in hl:
            s.append(f'<rect x="{x+4}" y="{ly-12}" width="{w-8}" height="16" rx="3" fill="#fff59d"/>')
        color = '#999' if i in strike else INK
        s.append(f'<text x="{x+8}" y="{ly}" font-size="11" fill="{color}" font-family="\'Courier New\', monospace" style="white-space:pre">{esc(l)}</text>')
        if i in strike:
            s.append(line(x + 8, ly - 4, x + 8 + tw(l, 11), ly - 4, RED, 1.5))
    return ''.join(s), w, h


def wire(x1, y1, x2, y2, color='#999', w=2, dash=None):
    """ノード間の配線（ベジェ曲線）"""
    d = f' stroke-dasharray="{dash}"' if dash else ''
    cx = (x1 + x2) / 2
    return f'<path d="M{x1} {y1} C{cx} {y1} {cx} {y2} {x2} {y2}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>'


def trash(x, y):
    """ごみ箱（捨てられたメッセージ）"""
    return (f'<path d="M{x-9} {y-6} h18 l-2 18 h-14z" fill="#eceff1" stroke="{INK}" stroke-width="1.6"/>'
            f'<line x1="{x-11}" y1="{y-8}" x2="{x+11}" y2="{y-8}" stroke="{INK}" stroke-width="2"/>'
            f'<rect x="{x-3}" y="{y-12}" width="6" height="4" fill="none" stroke="{INK}" stroke-width="1.5"/>')
