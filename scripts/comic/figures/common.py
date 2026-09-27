"""Common カテゴリ（inject / debug / complete / status / link / catch）の図"""
from lib import *

C = NODE_COLORS['common']


def inject():
    p = Panel('inject ノードは、左のボタンを押したとき、または設定した間隔や時刻になったときに、payload と topic を入れた msg を作って送り出す', 560, 190, 'inj')
    p.add(f'<rect x="150" y="84" width="16" height="22" rx="3" fill="{C}" stroke="#999" stroke-width="1.5"/>')
    node, _, outs = nrnode(230, 95, 'inject', C, w=110, inputs=0)
    p.add(node)
    # きっかけ
    p.add(box(62, 55, 110, 26, '手でクリック', '#fff', '#90a4ae', 11),
          box(62, 135, 110, 26, '5秒ごとに自動', '#fff', '#90a4ae', 11))
    p.arrow(118, 60, 148, 88, BLUE, 1.8).arrow(118, 130, 148, 102, BLUE, 1.8)
    card, w, h = msgcard(360, 50, ['payload: 1790520000000', 'topic: ""'], '出ていく msg', hl=(0,), stroke='#7cb342')
    p.add(wire(outs[0][0], outs[0][1], 360, 50 + h / 2), card)
    p.add(text(360 + w / 2, 132, 'payload の既定は現在時刻（ミリ秒）', 10, '#666'),
          text(62, 25, 'きっかけ', 11, '#666'))
    return p


def debug():
    p = Panel('debug ノードは受け取った msg の payload を右のデバッグサイドバーに表示する。出力の端子はなく、msg は先へ流れない', 560, 200, 'dbg')
    card, w, h = msgcard(8, 60, ['payload: 25.3', 'topic: "temp"'], '入ってくる msg')
    p.add(card)
    node, inp, _ = nrnode(230, 90, 'debug', '#87a980', w=100, outputs=0)
    p.add(wire(8 + w, 60 + h / 2, inp[0] - 5, inp[1]), node,
          f'<rect x="{230+50+2}" y="80" width="14" height="20" rx="3" fill="#87a980" stroke="#999" stroke-width="1.5"/>')
    # デバッグサイドバー
    p.add(f'<rect x="340" y="20" width="210" height="160" rx="6" fill="#fafafa" stroke="{INK}" stroke-width="1.5"/>',
          f'<rect x="340" y="20" width="210" height="24" rx="6" fill="#eceff1"/>',
          text(445, 37, 'デバッグ（サイドバー）', 11, INK, weight='bold'),
          f'<rect x="352" y="56" width="186" height="58" rx="3" fill="#fff" stroke="#ddd"/>',
          text(360, 72, '2026/9/27 13:05:12  debug', 9, '#999', 'start'),
          text(360, 88, 'temp : msg.payload : number', 10, '#8e24aa', 'start'),
          text(360, 106, '25.3', 12, BLUE, 'start', 'bold'))
    p.arrow(304, 90, 336, 90, GREEN, 2)
    p.add(text(445, 140, '既定は msg.payload を表示', 10, '#666'),
          text(445, 158, '「msg 全体」にも切り替えられる', 10, '#666'))
    return p


def complete():
    p = Panel('complete ノードは、見張っているノードが msg の処理を終えたときに、その msg を受け取って送り出す', 560, 170, 'cmp')
    n1, i1, o1 = nrnode(150, 60, 'http request', '#e7e7ae', w=130)
    p.add(packet(35, 60, 'msg'), wire(58, 60, i1[0] - 5, i1[1]), n1, wire(o1[0][0], o1[0][1], 290, 60), text(300, 64, '…', 14))
    p.add(text(95, 96, '✓ 処理が終わった', 11, GREEN, 'start', 'bold'))
    n2, i2, o2 = nrnode(150, 135, 'complete', C, w=120, inputs=0)
    p.add(n2)
    p.arrow(150, 100, 150, 112, '#bbb', 1.5, '3 3')
    p.add(text(160, 108, '見張る', 10, '#666', 'start'))
    card, w, h = msgcard(330, 105, ['payload: （処理した msg）'], '出ていく msg', stroke='#7cb342')
    p.add(wire(o2[0][0], o2[0][1], 330, 105 + h / 2), card)
    return p


def status():
    p = Panel('status ノードは、見張っているノードのステータス表示が変わったとき、その内容を msg.status に入れて送り出す', 560, 190, 'sts')
    n1, i1, o1 = nrnode(130, 50, 'mqtt in', '#d8bfd8', w=110, inputs=0)
    p.add(n1, status_dot(80, 84, '接続済み', GREEN))
    n2, i2, o2 = nrnode(130, 145, 'status', C, w=100, inputs=0)
    p.add(n2)
    p.arrow(130, 94, 130, 124, '#bbb', 1.5, '3 3')
    p.add(text(140, 112, '見張る', 10, '#666', 'start'))
    card, w, h = msgcard(270, 60, ['status.text: "接続済み"', 'status.fill: "green"', 'status.shape: "dot"', 'status.source.type: "mqtt in"'], '出ていく msg', hl=(0,), stroke='#7cb342')
    p.add(wire(o2[0][0], o2[0][1], 270, 60 + h / 2), card)
    return p


def link():
    p = Panel('link out ノードに入った msg は、線でつながっていない別のフローの link in ノードから出てくる', 560, 170, 'lnk')
    for x0, title in [(10, 'フロー 1'), (290, 'フロー 2')]:
        p.add(f'<rect x="{x0}" y="30" width="260" height="120" rx="8" fill="#fafafa" stroke="#bbb" stroke-dasharray="5 4"/>',
              text(x0 + 14, 50, title, 11, '#666', 'start', 'bold'))
    n1, i1, _ = nrnode(185, 95, 'link out', '#ddd', w=100, outputs=0)
    p.add(packet(60, 95, 'msg'), wire(83, 95, i1[0] - 5, i1[1]), n1)
    n2, _, o2 = nrnode(375, 95, 'link in', '#ddd', w=100, inputs=0)
    p.add(n2, wire(o2[0][0], o2[0][1], 480, 95), packet(505, 95, 'msg', '#e8f5e9', GREEN))
    p.add(f'<path d="M235 80 C260 20 300 20 325 80" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#m{p.id}b)"/>',
          text(280, 24, '見えない線でワープ', 11, BLUE, weight='bold'))
    return p


def link_call():
    p = Panel('link call ノードは、呼び出し先の link in から始まる処理に msg を渡し、最後の link out（呼び出し元へ戻る）で戻ってきた msg を自分の出力から送り出す', 560, 190, 'lkc')
    n1, i1, o1 = nrnode(130, 50, 'link call', '#ddd', w=110)
    p.add(packet(30, 50, 'msg'), wire(52, 50, i1[0] - 5, i1[1]), n1, wire(o1[0][0], o1[0][1], 230, 50), packet(265, 50, '結果の msg', '#e8f5e9', GREEN))
    p.add(f'<rect x="200" y="100" width="350" height="80" rx="8" fill="#fafafa" stroke="#bbb" stroke-dasharray="5 4"/>',
          text(214, 118, '呼び出される処理（サブルーチン）', 11, '#666', 'start', 'bold'))
    a, _, ao = nrnode(270, 150, 'link in', '#ddd', w=90, inputs=0)
    b, bi, bo = nrnode(385, 150, 'change', NODE_COLORS['function'], w=90)
    c, ci, _ = nrnode(495, 150, 'link out', '#ddd', w=90, outputs=0)
    p.add(a, b, c, wire(ao[0][0], ao[0][1], bi[0] - 5, bi[1]), wire(bo[0][0], bo[0][1], ci[0] - 5, ci[1]),
          text(495, 180, '呼び出し元へ戻る', 9, '#666'))
    p.add(f'<path d="M150 72 C170 120 200 150 222 150" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#m{p.id}b)"/>',
          f'<path d="M520 128 C530 70 420 50 345 50" fill="none" stroke="{GREEN}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#m{p.id}g)"/>',
          text(175, 108, '行き', 10, BLUE, weight='bold'), text(470, 70, '戻り', 10, GREEN, weight='bold'))
    return p


def catch():
    p = Panel('function ノードでエラーが起きると、同じフローの catch ノードが、元の msg にエラーの内容（msg.error）を加えて送り出す', 560, 190, 'cth')
    n1, i1, o1 = nrnode(160, 55, 'function', '#fdd0a2', w=110, mood='sad')
    p.add(packet(40, 55, 'msg'), wire(63, 55, i1[0] - 5, i1[1]), n1,
          f'<path d="M218 32 l9 -16 l9 16z" fill="#ffeb3b" stroke="{RED}" stroke-width="1.5"/>', text(227, 29, '!', 11, RED, weight='bold'),
          text(250, 30, 'エラー発生', 11, RED, 'start', 'bold'), xmark(250, 55, 6))
    p.add(wire(o1[0][0], o1[0][1], 240, 55, '#ccc', 1.5, '3 3'), text(264, 60, '先へ進まない', 10, '#999', 'start'))
    n2, _, o2 = nrnode(160, 140, 'catch', '#e49191', w=100, inputs=0)
    p.add(n2)
    p.arrow(160, 78, 160, 118, RED, 1.8, '4 3')
    p.add(text(170, 102, '受け止める', 10, RED, 'start'))
    card, w, h = msgcard(300, 90, ['payload: （元の値）', 'error.message: "…is not defined"', 'error.source.type: "function"'], '出ていく msg', hl=(1, 2), stroke='#7cb342')
    p.add(wire(o2[0][0], o2[0][1], 300, 90 + h / 2), card)
    return p


FIGURES = {'inject-basic': inject, 'debug-basic': debug, 'complete-basic': complete, 'status-basic': status,
           'link-basic': link, 'link-call': link_call, 'catch-basic': catch}
