"""Storage カテゴリ（file / watch / sqlite / ftp-sftp）の図"""
from lib import *

C = NODE_COLORS['storage']


def doc(x, y, lines, title, w=150, hl=()):
    """ファイル（右上が折れた紙）"""
    h = 26 + 16 * len(lines)
    s = [f'<path d="M{x} {y} h{w-16} l16 16 v{h-16} h-{w} z" fill="#fff" stroke="{INK}" stroke-width="1.8"/>',
         f'<path d="M{x+w-16} {y} v16 h16" fill="none" stroke="{INK}" stroke-width="1.5"/>',
         text(x + 8, y + 16, title, 11, INK, 'start', 'bold')]
    for i, l in enumerate(lines):
        ly = y + 34 + 16 * i
        if i in hl:
            s.append(f'<rect x="{x+4}" y="{ly-12}" width="{w-10}" height="15" rx="2" fill="#fff59d"/>')
        s.append(f'<text x="{x+8}" y="{ly}" font-size="11" fill="{INK}" font-family="\'Courier New\', monospace" style="white-space:pre">{esc(l)}</text>')
    return ''.join(s)


def file_write():
    p = Panel('write file ノードは、msg.payload をファイルの末尾に書き足す（既定）。書き終わると、受け取った msg をそのまま次へ送り出す', 560, 170, 'fwr')
    node, inp, outs = nrnode(230, 50, 'write file', C, w=120)
    p.add(packet(70, 50, 'payload: "25.3"'), wire(115, 50, inp[0] - 5, inp[1]), node,
          wire(outs[0][0], outs[0][1], 420, 50), packet(470, 50, '同じ msg', '#e8f5e9', GREEN))
    p.add(doc(170, 90, ['24.8', '25.1', '25.3'], 'log.txt', 140, hl=(2,)))
    p.arrow(230, 72, 230, 88, BLUE, 2)
    p.add(text(320, 150, '末尾に 1 行追加（改行付き）', 10, BLUE, 'start'))
    return p


def file_read():
    p = Panel('read file ノードは、msg が届くとファイルを読み、中身を msg.payload に入れて送り出す（既定は UTF-8 の文字列で 1 つの msg）', 560, 170, 'frd')
    node, inp, outs = nrnode(230, 50, 'read file', C, w=120)
    p.add(packet(70, 50, 'きっかけの msg'), wire(115, 50, inp[0] - 5, inp[1]), node)
    p.add(doc(170, 90, ['24.8', '25.1', '25.3'], 'log.txt', 140))
    p.arrow(230, 88, 230, 72, BLUE, 2)
    c, w, h = msgcard(390, 20, ['payload: "24.8', '25.1', '25.3"'], '出ていく msg', stroke='#7cb342', hl=(0, 1, 2))
    p.add(wire(outs[0][0], outs[0][1], 390, 20 + h / 2), c, text(250, 82, '読む', 10, BLUE, 'start'))
    return p


def watch():
    p = Panel('watch ノードは、見張っているフォルダでファイルが作られたり変わったりすると、そのファイルのパスなどを入れた msg を送り出す', 560, 190, 'wat')
    p.add(f'<path d="M20 60 h50 l10 10 h90 v100 h-150 z" fill="#fff8e1" stroke="{INK}" stroke-width="1.8"/>',
          text(95, 90, '/data/inbox', 11, INK, weight='bold'),
          doc(55, 105, [], 'new.csv', 80), sparkle(145, 108), text(95, 185, 'ファイルが置かれた', 10, ORANGE, weight='bold'))
    node, _, outs = nrnode(250, 90, 'watch', C, w=100, inputs=0)
    p.add(node, eye(250, 50, 0.8))
    p.arrow(175, 100, 196, 92, '#bbb', 1.5, '4 3')
    c, w, h = msgcard(335, 40, ['payload: "/data/inbox/new.csv"', 'file: "new.csv"', 'event: "change"', 'type: "file"'], '出ていく msg', stroke='#7cb342', hl=(0,))
    p.add(wire(outs[0][0], outs[0][1], 335, 40 + h / 2), c)
    return p


def sqlite():
    p = Panel('sqlite ノードは、既定では msg.topic に入った SQL 文をデータベースで実行し、結果の行を配列にして msg.payload で送り出す', 560, 200, 'sql')
    c, w, h = msgcard(8, 40, ['topic: "SELECT * FROM temps"'], '入ってくる msg')
    node, inp, outs = nrnode(300, 62, 'sqlite', C, w=96)
    p.add(c, wire(8 + w, 40 + h / 2, inp[0] - 5, inp[1]), node)
    # データベース（円柱）
    p.add(f'<path d="M255 130 v40 a45 10 0 0 0 90 0 v-40" fill="#e3f2fd" stroke="{INK}" stroke-width="1.8"/>',
          f'<ellipse cx="300" cy="130" rx="45" ry="10" fill="#bbdefb" stroke="{INK}" stroke-width="1.8"/>',
          text(300, 160, 'temps 表', 11, INK, weight='bold'))
    p.add(f'<path d="M290 84 v32" stroke="{BLUE}" stroke-width="2" marker-end="url(#m{p.id}b)"/>',
          f'<path d="M312 116 v-30" stroke="{GREEN}" stroke-width="2" marker-end="url(#m{p.id}g)"/>',
          text(284, 104, 'SQL', 9, BLUE, 'end'), text(318, 104, '行', 9, GREEN, 'start'))
    c2, w2, h2 = msgcard(385, 40, ['payload: [', '  {id: 1, temp: 24.8},', '  {id: 2, temp: 25.3}', ']'], '出ていく msg', stroke='#7cb342', hl=(1, 2))
    p.add(wire(outs[0][0], outs[0][1], 385, 40 + h2 / 2), c2)
    return p


def ftp():
    p = Panel('ftp in ノードの get は、FTP サーバーのファイルを Node-RED 側のフォルダへ保存し、結果の文字列を msg.payload に入れて送り出す', 560, 180, 'ftp')
    node, inp, outs = nrnode(230, 45, 'ftp in（get）', C, w=130, fs=11)
    p.add(packet(70, 45, 'きっかけの msg'), wire(115, 45, inp[0] - 5, inp[1]), node,
          wire(outs[0][0], outs[0][1], 330, 45), packet(430, 45, 'payload: "Get operation successful. …"', '#e8f5e9', GREEN, 10))
    p.add(server(490, 125, 'happy', 'FTP サーバー'), doc(365, 105, [], 'report.csv', 90))
    p.add(f'<path d="M15 100 h40 l8 8 h90 v70 h-138 z" fill="#fff8e1" stroke="{INK}" stroke-width="1.8"/>',
          text(84, 125, 'ローカル', 11, INK, weight='bold'), doc(40, 138, [], 'report.csv', 90))
    p.add(f'<path d="M360 128 C300 150 200 150 135 150" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#m{p.id}b)"/>',
          text(250, 168, 'ダウンロードして保存', 10, BLUE, weight='bold'))
    return p


FIGURES = {'file-write': file_write, 'file-read': file_read, 'watch-basic': watch, 'sqlite-basic': sqlite, 'ftp-get': ftp}
