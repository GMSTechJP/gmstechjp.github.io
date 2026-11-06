"""Network ほか（http / websocket / mqtt / tcp / udp / email / modbus / pi-sense-hat）の図"""
from lib import *

C = NODE_COLORS['network']


def browser(x, y, label='ブラウザ', mood='happy'):
    return pc(x, y, mood, label)


def http_in():
    p = Panel('ブラウザが /hello に GET でアクセスすると、http in ノードが msg を作り、途中のノードで作った payload を http response ノードがブラウザへ返す', 560, 200, 'hin')
    p.add(browser(50, 60))
    n1, i1, o1 = nrnode(190, 60, 'http in', C, w=100, inputs=0)
    n2, i2, o2 = nrnode(330, 60, 'template', NODE_COLORS['function'], w=100)
    n3, i3, _ = nrnode(470, 60, 'http response', C, w=130, outputs=0, fs=11)
    p.add(n1, n2, n3, wire(o1[0][0], o1[0][1], i2[0] - 5, i2[1]), wire(o2[0][0], o2[0][1], i3[0] - 5, i3[1]))
    p.arrow(76, 50, 136, 50, BLUE, 2)
    p.add(text(105, 38, 'GET /hello', 10, BLUE, weight='bold'))
    p.add(f'<path d="M470 84 C470 160 60 160 55 102" fill="none" stroke="{GREEN}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#m{p.id}g)"/>',
          packet(270, 142, '「こんにちは」の HTML', '#e8f5e9', GREEN, 10), text(270, 180, 'msg.res を使って、同じ相手に返す', 10, '#666'))
    return p


def http_request():
    p = Panel('http request ノードは、msg を受け取ると設定した URL へ要求を送り、返ってきた本文を msg.payload に、ステータスコードを msg.statusCode に入れて送り出す', 560, 190, 'hrq')
    node, inp, outs = nrnode(220, 55, 'http request', C, w=130, fs=11)
    p.add(packet(70, 55, 'きっかけの msg'), wire(115, 55, inp[0] - 5, inp[1]), node, server(480, 120, 'happy', '天気 API'))
    p.arrow(250, 78, 455, 110, BLUE, 1.8, '5 4')
    p.arrow(455, 130, 250, 130, GREEN, 1.8, '5 4')
    p.add(text(330, 108, 'GET https://api…/weather', 10, BLUE, weight='bold'), text(350, 146, '200 {"weather":"晴れ"}', 10, GREEN, weight='bold'))
    c, w, h = msgcard(300, 8, ['payload: {weather: "晴れ"}', 'statusCode: 200'], '出ていく msg', stroke='#7cb342', hl=(0, 1))
    p.add(wire(outs[0][0], outs[0][1], 300, 8 + h / 2), c, text(110, 160, '（出力形式を「JSON」にしたとき）', 10, '#666'))
    return p


def websocket():
    p = Panel('websocket in ノードはブラウザから届いた文字列を msg.payload にして送り出し、websocket out ノードは msg.payload を接続中のブラウザ全員に送る', 560, 200, 'wsk')
    p.add(browser(50, 50, 'ブラウザ A'), browser(50, 145, 'ブラウザ B'))
    n1, _, o1 = nrnode(220, 50, 'websocket in', C, w=130, inputs=0, fs=11)
    p.add(n1, wire(o1[0][0], o1[0][1], 330, 50), packet(390, 50, 'payload: "hello"', '#e8f5e9', GREEN))
    p.arrow(78, 42, 150, 44, BLUE, 2)
    p.add(text(115, 32, '"hello"', 10, BLUE, weight='bold'))
    n2, i2, _ = nrnode(300, 140, 'websocket out', C, w=130, outputs=0, fs=11)
    p.add(packet(470, 140, 'payload: "全員へ"'), wire(425, 140, i2[0] - 5, i2[1]), n2)
    p.add(f'<path d="M235 140 C170 140 120 80 80 62" fill="none" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#m{p.id}o)"/>',
          f'<path d="M235 146 C170 150 120 150 80 150" fill="none" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#m{p.id}o)"/>',
          text(160, 185, '接続中の全員に届く', 10, ORANGE, weight='bold'))
    return p


def mqtt():
    p = Panel('mqtt out ノードは msg.payload をトピック sensor/temp でブローカーへ発行し、そのトピックを購読している mqtt in ノードから msg として出てくる', 560, 180, 'mqt')
    n1, i1, _ = nrnode(160, 60, 'mqtt out', '#d8bfd8', w=100, outputs=0)
    p.add(packet(50, 60, 'payload: 25.3'), wire(88, 60, i1[0] - 5, i1[1]), n1, server(290, 70, 'happy', 'ブローカー'))
    p.arrow(207, 60, 268, 62, ORANGE, 2)
    p.add(text(235, 42, 'sensor/temp', 10, ORANGE, weight='bold'))
    n2, _, o2 = nrnode(420, 60, 'mqtt in', '#d8bfd8', w=100, inputs=0)
    p.add(n2)
    p.arrow(312, 62, 366, 60, ORANGE, 2)
    p.add(text(420, 30, '購読：sensor/temp', 10, '#666'))
    c, w, h = msgcard(330, 110, ['topic: "sensor/temp"', 'payload: 25.3'], '出ていく msg', stroke='#7cb342', hl=(0, 1))
    p.add(wire(o2[0][0], o2[0][1], 480, 110, '#999'), c)
    return p


def tcp():
    p = Panel('tcp in ノード（待ち受け）は、接続してきた機器が送ったデータを、既定では Buffer のまま msg.payload にして送り出す', 560, 150, 'tcp')
    p.add(pc(50, 70, 'happy', '装置'))
    node, _, outs = nrnode(230, 70, 'tcp in :7000', C, w=130, inputs=0, fs=11)
    p.add(node)
    p.arrow(78, 62, 162, 64, BLUE, 2)
    p.add(text(120, 50, '"25.3\\n"', 10, BLUE, weight='bold'))
    c, w, h = msgcard(340, 45, ['payload: <Buffer', '  32 35 2e 33 0a>'], '出ていく msg', stroke='#7cb342', hl=(0, 1))
    p.add(wire(outs[0][0], outs[0][1], 340, 45 + h / 2), c, text(230, 120, '出力の設定で文字列にも変えられる', 10, '#666'))
    return p


def udp():
    p = Panel('udp out ノードは msg.payload を指定した IP アドレスとポートへ送りっぱなしで送り、相手の udp in ノードは受け取ったデータを Buffer の msg.payload にして送り出す', 560, 170, 'udp')
    n1, i1, _ = nrnode(160, 60, 'udp out', C, w=90, outputs=0)
    p.add(packet(50, 60, 'payload: "ON"'), wire(90, 60, i1[0] - 5, i1[1]), n1)
    n2, _, o2 = nrnode(400, 60, 'udp in :5000', C, w=120, inputs=0, fs=11)
    p.add(n2)
    p.arrow(205, 60, 334, 60, '#c2185b', 2, '6 4')
    p.add(text(270, 48, '192.168.1.20:5000 へ', 10, '#c2185b', weight='bold'), text(270, 80, '届いたかは確かめない', 10, '#666'))
    c, w, h = msgcard(330, 100, ['payload: <Buffer 4f 4e>'], '出ていく msg', stroke='#7cb342', hl=(0,))
    p.add(wire(o2[0][0], o2[0][1], 480, 100, '#999'), c)
    return p


# udp の 2 つのポートの図で使う色。宛先（相手の番号）は橙、差出人（自分の番号）は青
DEST_TEXT, DEST_BG = '#bf360c', '#fff3e0'
SRC_BG = '#e3f2fd'


def _field(x, y, w, t, fill='#fff', stroke='#bbb'):
    """エディターの入力欄。(x, y) は左端の中央"""
    return (f'<rect x="{x}" y="{y-11}" width="{w}" height="22" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            + text(x + 6, y + 4, t, 11, INK, 'start'))


def _door(x, y, w, h, t, fill, stroke):
    """PC の出入り口（ポート）。(x, y) は左上"""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            + text(x + w / 2, y + h / 2 + 4, t, 11, INK, weight='bold'))


def udp_ports_fields():
    p = Panel('udp out の編集画面のうち、アドレスとポートは封筒の宛先にあたり、アドレスの下のドロップダウンで決めるローカルポートは差出人にあたる', 560, 196, 'udpf')
    p.add(text(10, 20, 'udp out の編集画面', 12, INK, 'start', 'bold'))
    p.add(text(10, 50, '送信', 11, INK, 'start'), _field(60, 46, 112, 'UDPメッセージ ▾'),
          text(178, 50, 'ポート', 11, INK, 'start'), _field(214, 46, 50, '1881', DEST_BG, ORANGE))
    p.add(text(10, 84, 'アドレス', 11, INK, 'start'), _field(60, 80, 130, 'localhost', DEST_BG, ORANGE), _field(196, 80, 68, 'ipv4 ▾'))
    p.add(_field(60, 114, 204, 'ローカルポートをランダムに使用 ▾', SRC_BG, BLUE))
    p.add(text(162, 140, 'または', 10, '#666'))
    p.add(_field(60, 158, 150, 'ローカルポートを使用 ▾', SRC_BG, BLUE), _field(214, 158, 50, '9005', SRC_BG, BLUE))
    # 欄のまとまりから封筒の行へ
    p.add(f'<path d="M270 35 H276 V91 H270" fill="none" stroke="{ORANGE}" stroke-width="2"/>')
    p.add(f'<path d="M270 103 H276 V169 H270" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    p.arrow(276, 63, 338, 63, ORANGE, 2)
    p.arrow(276, 136, 338, 136, BLUE, 2)
    # 封筒
    p.add(text(332, 20, '送り出すデータ（封筒にたとえる）', 12, INK, 'start', 'bold'))
    p.add(f'<rect x="332" y="30" width="220" height="158" rx="4" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    p.add(f'<rect x="340" y="38" width="204" height="50" rx="3" fill="{DEST_BG}" stroke="{ORANGE}" stroke-width="1.5"/>',
          text(348, 57, '宛先（送り先）', 11, DEST_TEXT, 'start', 'bold'), text(348, 77, 'localhost の 1881 番', 12, INK, 'start'))
    p.add(f'<rect x="340" y="111" width="204" height="50" rx="3" fill="{SRC_BG}" stroke="{BLUE}" stroke-width="1.5"/>',
          text(348, 130, '差出人（送り元）', 11, BLUE, 'start', 'bold'), text(348, 150, '自動の番号、または 9005 番', 12, INK, 'start'))
    p.add(text(348, 178, '中身：msg.payload', 11, INK, 'start'))
    return p


def udp_ports_where():
    p = Panel('ローカルポートは自分の PC の番号で、ポートは相手の PC の番号である。データは相手のポートに届き、自分のローカルポートの番号が相手の udp in の msg.port に入る', 560, 200, 'udpw')
    p.add(text(105, 22, '自分の PC', 12, INK, weight='bold'), text(455, 22, '相手の PC', 12, INK, weight='bold'))
    p.add('<rect x="10" y="30" width="190" height="100" rx="8" fill="#f5f5f5" stroke="#90a4ae" stroke-width="1.5"/>',
          '<rect x="360" y="30" width="190" height="100" rx="8" fill="#f5f5f5" stroke="#90a4ae" stroke-width="1.5"/>')
    n1, _, _ = nrnode(95, 80, 'udp out', C, w=110, outputs=0)
    n2, _, _ = nrnode(468, 80, 'udp in :1881', C, w=122, inputs=0, fs=11)
    p.add(n1, n2, wire(150, 80, 183, 80), wire(370, 80, 407, 80))
    p.add(_door(183, 62, 40, 36, '9005', SRC_BG, BLUE), _door(337, 62, 40, 36, '1881', DEST_BG, ORANGE))
    p.arrow(223, 80, 335, 80, INK, 2)
    p.add(packet(280, 58, '9005 → 1881'))
    p.add(text(203, 150, 'ローカルポート', 12, BLUE, weight='bold'), text(203, 167, '自分の出入り口の番号', 11, INK))
    p.add(text(357, 150, 'ポート', 12, DEST_TEXT, weight='bold'), text(357, 167, '相手の入口の番号', 11, INK))
    c, _, _ = msgcard(420, 138, ['port: 9005'], '届いた msg', w=120, stroke='#7cb342', hl=(0,))
    p.add(c)
    return p


def _reply_row(p, y, title, ok):
    p.add(text(10, y + 14, title, 12, GREEN if ok else RED, 'start', 'bold'))
    p.add(f'<rect x="10" y="{y+24}" width="180" height="104" rx="8" fill="#f5f5f5" stroke="#90a4ae" stroke-width="1.5"/>',
          text(90, y + 40, '自分の Node-RED', 11, INK))
    p.add(box(88, y + 62, 120, 28, 'udp out', fill=C, stroke='#999', fs=11),
          box(88, y + 104, 120, 28, 'udp in :9005', fill=C, stroke='#999', fs=11))
    p.add(wire(148, y + 62, 168, y + 62), wire(148, y + 104, 168, y + 104))
    src = '9005' if ok else '59196'
    if ok:
        # 同じ番号の udp out と udp in は 1 つの出入り口（ソケット）を使う
        p.add(_door(168, y + 46, 44, 74, '9005', SRC_BG, BLUE))
    else:
        p.add(_door(168, y + 48, 44, 28, '59196', SRC_BG, BLUE), _door(168, y + 90, 44, 28, '9005', '#fff', '#90a4ae'))
    p.add(pc(490, y + 76, 'neutral', '相手'), text(490, y + 130, f'msg.port: {src}', 11, INK, weight='bold'))
    p.arrow(212, y + 56, 460, y + 56, INK, 2)
    p.add(text(336, y + 48, f'差出人 {src}、宛先 1881', 11, INK))
    if ok:
        p.arrow(460, y + 104, 214, y + 104, GREEN, 2)
        p.add(text(336, y + 96, '9005 番へ返信', 11, INK), text(336, y + 121, 'udp in :9005 が受け取る', 11, GREEN, weight='bold'))
    else:
        p.arrow(460, y + 70, 214, y + 70, RED, 2)
        p.add(xmark(246, y + 70, 6), text(336, y + 86, '59196 番へ返信', 11, INK),
              text(222, y + 110, '受け取るノードがなく、udp in には届かない', 11, RED, 'start', 'bold'))


def udp_ports_reply():
    p = Panel('ローカルポートがランダムのときは、相手が自動の番号へ返信するので udp in :9005 に届かない。ローカルポートを 9005 にすると、相手が 9005 番へ返信するので udp in :9005 に届く', 560, 290, 'udpr')
    _reply_row(p, 2, '「ローカルポートをランダムに使用」のとき：返信は udp in に届かない', False)
    p.add(line(10, 144, 550, 144, '#ddd', 1))
    _reply_row(p, 150, '「ローカルポートを使用」に 9005 を入れたとき：返信が udp in に届く', True)
    return p


def email():
    p = Panel('email ノード（送信）は、msg.topic を件名、msg.payload を本文にしてメールを送る', 560, 150, 'eml')
    c, w, h = msgcard(8, 35, ['topic: "温度アラート"', 'payload: "35℃ を超えました"'], '入ってくる msg')
    node, inp, _ = nrnode(290, 60, 'email', '#c7e9c0', w=96, outputs=0)
    p.add(c, wire(8 + w, 35 + h / 2, inp[0] - 5, inp[1]), node)
    p.add(envelope(420, 60, 50, 32), text(420, 104, '件名：温度アラート', 10, INK), text(420, 120, '本文：35℃ を超えました', 10, INK))
    p.arrow(342, 60, 390, 60, GREEN, 2)
    p.add(text(366, 48, 'SMTP', 9, GREEN, weight='bold'))
    return p


def modbus():
    p = Panel('Modbus-Read ノードは、設定した間隔で装置のレジスタを読み、読み取った値を配列にして msg.payload で送り出す', 560, 170, 'mdb')
    p.add(box(70, 75, 110, 60, '', '#eceff1', '#455a64'), text(70, 65, '温調計', 12, INK, weight='bold'), text(70, 88, 'レジスタ 0: 250', 10, '#455a64'), text(70, 102, 'レジスタ 1: 600', 10, '#455a64'))
    node, _, outs = nrnode(270, 75, 'Modbus-Read', '#e9967a', w=130, inputs=0, fs=11)
    p.add(node, text(270, 115, '1 秒ごとに読む', 10, '#666'))
    p.arrow(205, 70, 128, 70, BLUE, 1.8, '4 3').arrow(128, 82, 205, 82, GREEN, 1.8, '4 3')
    c, w, h = msgcard(390, 50, ['payload: [250, 600]'], '出ていく msg', stroke='#7cb342', hl=(0,))
    p.add(wire(outs[0][0], outs[0][1], 390, 50 + h / 2), c, text(390 + w / 2, 110, '生の値。実値への換算は後で行う', 10, '#666'))
    return p


def sensehat():
    p = Panel('rpi-sensehat in ノードは、環境センサーの値を約 1 秒ごとに topic "environment" の msg で送り出す。rpi-sensehat out ノードは msg.payload の文字を LED に流す', 560, 190, 'shat')
    n1, _, o1 = nrnode(110, 50, 'sensehat in', '#c0c0c0', w=120, inputs=0, fs=11)
    c, w, h = msgcard(250, 12, ['topic: "environment"', 'payload: {temperature: 32.5,', '  humidity: 45.2, pressure: 1013.25}'], '出ていく msg', stroke='#7cb342', hl=(1, 2))
    p.add(n1, wire(o1[0][0], o1[0][1], 250, 12 + h / 2), c)
    n2, i2, _ = nrnode(200, 150, 'sensehat out', '#c0c0c0', w=120, outputs=0, fs=11)
    p.add(packet(55, 150, 'payload: "Hi"'), wire(96, 150, i2[0] - 5, i2[1]), n2)
    p.add(f'<rect x="330" y="112" width="76" height="76" rx="4" fill="#263238"/>')
    for r in range(8):
        for q in range(8):
            on = (q in (1, 3) and 1 <= r <= 6) or (r == 3 and q == 2) or (q == 5 and r in (1, 3, 4, 5, 6))
            p.add(f'<circle cx="{336 + 9 * q}" cy="{118 + 9 * r}" r="3.2" fill="{"#ffeb3b" if on else "#37474f"}"/>')
    p.arrow(262, 150, 326, 150, ORANGE, 2)
    p.add(text(420, 154, '文字が流れる', 10, '#666', 'start'))
    return p


FIGURES = {'http-in': http_in, 'http-request': http_request, 'websocket-basic': websocket, 'mqtt-basic': mqtt,
           'tcp-basic': tcp, 'udp-basic': udp, 'udp-ports-fields': udp_ports_fields, 'udp-ports-where': udp_ports_where, 'udp-ports-reply': udp_ports_reply,
           'email-basic': email, 'modbus-basic': modbus, 'sensehat-basic': sensehat}
