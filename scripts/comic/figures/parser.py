"""Parser カテゴリ（json / csv / html / xml / yaml / base64 / buffer-parser）の図"""
from lib import *

C = NODE_COLORS['parser']


def _row(p, y, name, in_lines, out_lines, in_title='入ってくる msg', out_title='出ていく msg', nx=275, nw=100, out_x=None, hl=None, fs=12):
    """1 行分の「msg → ノード → msg」を描き、使った高さを返す"""
    c1, w1, h1 = msgcard(8, y, in_lines, in_title)
    node, inp, outs = nrnode(nx, y + h1 / 2, name, C, w=nw, fs=fs)
    ox = out_x or (nx + nw / 2 + 40)
    c2, w2, h2 = msgcard(ox, y, out_lines, out_title, stroke='#7cb342', hl=hl if hl is not None else tuple(range(len(out_lines))))
    p.add(c1, wire(8 + w1, y + h1 / 2, inp[0] - 5, inp[1]), node, wire(outs[0][0], outs[0][1], ox, y + h2 / 2), c2)
    return max(h1, h2)


def json_():
    p = Panel('json ノードは、JSON 形式の文字列が来たらオブジェクトに、オブジェクトが来たら JSON 形式の文字列に変換する（既定の「JSON文字列とオブジェクト間の相互変換」）', 560, 190, 'jsn')
    p.add(text(8, 18, '文字列 → オブジェクト', 11, BLUE, 'start', 'bold'))
    _row(p, 26, 'json', ['payload: \'{"temp":25}\'', '（文字列）'], ['payload: {temp: 25}', '（オブジェクト）'], hl=(0,))
    p.add(text(8, 110, 'オブジェクト → 文字列', 11, BLUE, 'start', 'bold'))
    _row(p, 118, 'json', ['payload: {temp: 25}', '（オブジェクト）'], ['payload: \'{"temp":25}\'', '（文字列）'], hl=(0,))
    return p


def csv():
    p = Panel('csv ノードで「1行目に列名を含む」をオンにすると、1 行目を列名として使い、2 行目以降を 1 行ずつオブジェクトにして、行ごとに別の msg で送り出す', 560, 190, 'csv')
    c1, w1, h1 = msgcard(8, 55, ['payload:', '"temp,hum', ' 25,60', ' 26,58"'], '入ってくる msg')
    node, inp, outs = nrnode(250, 95, 'csv', C, w=90)
    p.add(c1, wire(8 + w1, 55 + h1 / 2, inp[0] - 5, inp[1]), node)
    for i, (t, h) in enumerate([(25, 60), (26, 58)]):
        y = 30 + 78 * i
        c, w, hh = msgcard(360, y, [f'payload: {{', f'  temp: {t}, hum: {h}', '}'], f'msg {i+1}（{i+2} 行目）', stroke='#7cb342', hl=(1,))
        p.add(wire(outs[0][0], outs[0][1], 360, y + hh / 2), c)
    p.add(text(250, 135, '1 行目は列名', 10, '#666'), text(250, 150, '数値は数値に直す', 10, '#666'))
    return p


def html():
    p = Panel('html ノードで「セレクタ」に li を指定すると、HTML の中から li 要素の中身を取り出し、配列にして送り出す', 560, 130, 'htm')
    _row(p, 30, 'html', ['payload: "<ul>', ' <li>りんご</li>', ' <li>みかん</li>', '</ul>"'], ['payload: [', '  "りんご",', '  "みかん"', ']'], nx=265, hl=(1, 2))
    p.add(text(265, 105, 'セレクタ：li', 10, '#666'))
    return p


def xml():
    p = Panel('xml ノードは、XML 文字列をオブジェクトに変換する。要素の属性は $ に、要素の文字は _ に入る（既定）。オブジェクトを渡すと XML 文字列に戻す', 560, 180, 'xml')
    _row(p, 25, 'xml', ['payload:', '\'<temp unit="C">25</temp>\''], ['payload: {', '  temp: {', '    $: {unit: "C"},', '    _: "25"', '  }', '}'], nx=270, out_x=350, hl=(2, 3))
    p.add(text(270, 118, '属性は $、文字は _ に入る', 10, '#666'))
    return p


def yaml():
    p = Panel('yaml ノードは、YAML 形式の文字列が来たらオブジェクトに、オブジェクトが来たら YAML 形式の文字列に変換する', 560, 130, 'yml')
    _row(p, 25, 'yaml', ['payload:', '"temp: 25', ' unit: C"'], ['payload: {', '  temp: 25,', '  unit: "C"', '}'], nx=265, hl=(1, 2))
    p.add(text(265, 110, '逆向きの変換もできる', 10, '#666'))
    return p


def base64():
    p = Panel('base64 ノードは既定で、Buffer や通常の文字列が来たら Base64 文字列にエンコードし、有効な Base64 文字列が来たら Buffer にデコードする', 560, 180, 'b64')
    p.add(text(8, 18, 'エンコード', 11, BLUE, 'start', 'bold'))
    _row(p, 26, 'base64', ['payload: "Hello"'], ['payload: "SGVsbG8="'], nx=265)
    p.add(text(8, 100, 'デコード', 11, BLUE, 'start', 'bold'))
    _row(p, 108, 'base64', ['payload: "SGVsbG8="'], ['payload: <Buffer 48 65 6c …>'], nx=265, out_x=345)
    return p


def buffer_parser():
    p = Panel('buffer-parser ノードは、Buffer のどの位置を何の型で読むかを項目ごとに決めておくと、読み取った値を名前付きで取り出す。0 と 2 バイト目からの int16be を読むと temp 25、hum 60 になる', 560, 200, 'bfp')
    c1, w1, h1 = msgcard(8, 40, ['payload: <Buffer', '  00 19 00 3c>'], '入ってくる msg')
    node, inp, outs = nrnode(290, 65, 'buffer-parser', C, w=140, fs=11)
    p.add(c1, wire(8 + w1, 40 + h1 / 2, inp[0] - 5, inp[1]), node)
    c2, w2, h2 = msgcard(400, 40, ['payload: {', '  temp: 25,', '  hum: 60', '}'], '出ていく msg', stroke='#7cb342', hl=(1, 2))
    p.add(wire(outs[0][0], outs[0][1], 400, 40 + h2 / 2), c2)
    # 項目の表
    rows = [('名前', '型', '位置'), ('temp', 'int16be', '0'), ('hum', 'int16be', '2')]
    x0, y0 = 170, 110
    p.add(f'<rect x="{x0}" y="{y0}" width="220" height="{18 * len(rows) + 8}" rx="4" fill="#fffde7" stroke="#c9b458"/>')
    for i, r in enumerate(rows):
        for j, c in enumerate(r):
            p.add(text(x0 + 36 + 74 * j, y0 + 18 + 18 * i, c, 11, INK if i else '#666', 'middle', 'bold' if i == 0 else 'normal'))
    p.add(text(290, 190, '00 19 → 25、00 3c → 60（2 バイトずつ、上位バイトが先）', 10, '#666'))
    return p


FIGURES = {'json-basic': json_, 'csv-basic': csv, 'html-basic': html, 'xml-basic': xml, 'yaml-basic': yaml,
           'base64-basic': base64, 'buffer-parser-basic': buffer_parser}
