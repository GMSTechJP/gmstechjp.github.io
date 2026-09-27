"""Dashboard 2.0（表示系 / 入力系 / 可視化 / template / control / ui-led）の図"""
from lib import *

C = '#a6bbcf'   # Dashboard 2.0 ノードの色（エディター上の既定色に近い水色）


def screen(x, y, w, h, title='ダッシュボード'):
    """ブラウザで開いたダッシュボードの画面"""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{INK}" stroke-width="1.8"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="6" fill="#1976d2"/>'
            f'<rect x="{x}" y="{y+14}" width="{w}" height="6" fill="#1976d2"/>'
            + text(x + 10, y + 14, title, 10, '#fff', 'start', 'bold'))


def text_widget():
    p = Panel('ui-text ノードは、受け取った msg.payload の値をダッシュボードの画面に表示する。25.3 が届くと、画面の「温度」の横に 25.3 と出る', 560, 150, 'dtx')
    node, inp, _ = nrnode(230, 70, 'ui-text', C, w=100, outputs=0)
    p.add(packet(80, 70, 'payload: 25.3'), wire(120, 70, inp[0] - 5, inp[1]), node, screen(360, 25, 190, 100))
    p.add(text(380, 80, '温度', 13, '#666', 'start'), text(530, 80, '25.3', 18, BLUE, 'end', 'bold'))
    p.arrow(282, 70, 355, 70, GREEN, 2)
    p.add(text(318, 58, '表示', 10, GREEN, weight='bold'))
    return p


def button_widget():
    p = Panel('ダッシュボードのボタンが押されると、ui-button ノードが設定した値を msg.payload に入れて送り出す。スライダーを動かすと、ui-slider ノードが新しい値を送り出す', 560, 190, 'dbt')
    p.add(screen(10, 20, 190, 150))
    p.add(f'<rect x="40" y="55" width="130" height="30" rx="4" fill="#1976d2"/>', text(105, 75, '運転開始', 12, '#fff', weight='bold'),
          f'<path d="M150 80 l10 16 l3 -6 l6 3z" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
    p.add(line(40, 130, 170, 130, '#90caf9', 4), line(40, 130, 92, 130, BLUE, 4), f'<circle cx="92" cy="130" r="8" fill="{BLUE}"/>',
          text(105, 155, '40', 11, BLUE, weight='bold'))
    n1, _, o1 = nrnode(300, 70, 'ui-button', C, w=110)
    n2, _, o2 = nrnode(300, 130, 'ui-slider', C, w=110)
    p.add(n1, n2, wire(o1[0][0], o1[0][1], 385, 70), packet(460, 70, 'payload: "start"', '#e8f5e9', GREEN),
          wire(o2[0][0], o2[0][1], 385, 130), packet(450, 130, 'payload: 40', '#e8f5e9', GREEN))
    p.add(f'<path d="M172 62 C230 30 280 30 290 48" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="4 3" marker-end="url(#m{p.id}b)"/>',
          f'<path d="M172 122 C220 100 280 95 290 108" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="4 3" marker-end="url(#m{p.id}b)"/>',
          text(230, 30, '押す', 10, BLUE, weight='bold'), text(230, 100, '動かす', 10, BLUE, weight='bold'))
    p.add(text(460, 95, '（ボタンに設定した値）', 10, '#666'))
    return p


def chart_widget():
    p = Panel('ui-chart ノードは、届いた msg.payload の値を 1 点ずつグラフに足していく。msg.topic が同じ値は同じ線になる', 560, 180, 'dch')
    for i, v in enumerate([24, 26, 25]):
        p.add(packet(60, 40 + 45 * i, f'温度 {v}'))
        p.add(wire(92, 40 + 45 * i, 185, 85))
    p.add(text(60, 180 - 10, 'topic: "温度"', 10, '#666'))
    node, inp, _ = nrnode(240, 85, 'ui-chart', C, w=100, outputs=0)
    p.add(node, screen(340, 20, 210, 150))
    # グラフ
    x0, y0 = 360, 150
    p.add(line(x0, y0, 535, y0, '#999', 1.5), line(x0, y0, x0, 50, '#999', 1.5))
    pts = [(x0 + 30, 105), (x0 + 80, 75), (x0 + 130, 90)]
    p.add(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
    for a, b in pts:
        p.add(f'<circle cx="{a}" cy="{b}" r="4" fill="{BLUE}"/>')
    p.add(sparkle(x0 + 150, 82), text(x0 + 130, 118, '新しい点', 10, BLUE, weight='bold'))
    p.arrow(292, 85, 336, 85, GREEN, 2)
    return p


def template_widget():
    p = Panel('ui-template ノードは、自分で書いた画面の部品に msg.payload を差し込んで表示する。部品の中から send() を呼ぶと、その値が msg として出力から出る', 560, 190, 'dtp')
    node, inp, outs = nrnode(200, 60, 'ui-template', C, w=120)
    p.add(packet(55, 60, 'payload: 25.3'), wire(95, 60, inp[0] - 5, inp[1]), node)
    p.add(f'<rect x="115" y="100" width="205" height="44" rx="5" fill="#2d3133"/>',
          f'<text x="125" y="118" font-size="10" fill="#f8f8f2" font-family="\'Courier New\', monospace">&lt;p&gt;{{{{ msg.payload }}}} ℃&lt;/p&gt;</text>',
          f'<text x="125" y="135" font-size="10" fill="#f8f8f2" font-family="\'Courier New\', monospace">&lt;button @click="send(…)"&gt;</text>',
          line(200, 82, 200, 98, '#999', 1.5, '3 3'))
    p.add(screen(340, 20, 210, 150))
    p.add(text(445, 75, '25.3 ℃', 20, BLUE, weight='bold'),
          f'<rect x="395" y="100" width="100" height="28" rx="4" fill="#1976d2"/>', text(445, 119, 'リセット', 11, '#fff', weight='bold'))
    p.arrow(262, 55, 336, 60, GREEN, 2)
    p.add(wire(outs[0][0], outs[0][1], 300, 170, '#999'), packet(300, 175, '押すと msg が出る', '#e8f5e9', GREEN, 10))
    p.add(f'<path d="M395 120 C360 150 360 170 352 175" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="4 3" marker-end="url(#m{p.id}b)"/>')
    return p


def control_widget():
    p = Panel('ui-control ノードに msg.payload として {page: "設定"} を渡すと、開いているダッシュボードの画面が「設定」ページに切り替わる', 560, 170, 'dct')
    node, inp, outs = nrnode(240, 85, 'ui-control', C, w=110)
    p.add(packet(82, 85, 'payload: {page: "設定"}', '#fff8e1', ORANGE, 10), wire(143, 85, inp[0] - 5, inp[1]), node)
    p.add(screen(330, 30, 100, 110, 'ホーム'), screen(450, 30, 100, 110, '設定'))
    p.add(text(380, 95, '…', 16, '#999'), text(500, 95, '設定画面', 11, INK, weight='bold'), sparkle(535, 60))
    p.arrow(432, 85, 446, 85, BLUE, 2.5)
    p.arrow(297, 85, 326, 85, GREEN, 2)
    p.add(text(380, 160, 'ページが切り替わる', 10, BLUE, weight='bold'))
    return p


def led_widget():
    p = Panel('ui-led ノードは既定で、msg.payload が true なら緑、false なら赤に LED を点ける。対応表にない値は消灯（グレー）', 560, 170, 'led')
    for i, (v, color, lab) in enumerate([('true', '#00c853', '緑'), ('false', '#ff1744', '赤'), ('"abc"', '#bdbdbd', '消灯')]):
        y = 35 + 50 * i
        p.add(packet(70, y, f'payload: {v}'))
        p.add(wire(112, y, 235, 85))
        p.add(f'<circle cx="440" cy="{y}" r="14" fill="{color}" stroke="{INK}" stroke-width="1.5"/>', text(465, y + 4, lab, 11, INK, 'start', 'bold'))
    node, inp, _ = nrnode(290, 85, 'ui-led', C, w=100, outputs=0)
    p.add(node)
    p.arrow(342, 85, 420, 40, '#bbb', 1.5, '4 3').arrow(342, 85, 420, 85, '#bbb', 1.5, '4 3').arrow(342, 85, 420, 130, '#bbb', 1.5, '4 3')
    return p


FIGURES = {'dash-text': text_widget, 'dash-button': button_widget, 'dash-chart': chart_widget,
           'dash-template': template_widget, 'dash-control': control_widget, 'dash-led': led_widget}
