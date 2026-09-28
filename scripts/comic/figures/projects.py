"""プロジェクト機能ガイドの図"""
from lib import *
from figures.storage import doc


def folder(x, y, w, h, label, fill='#fff8e1'):
    return (f'<path d="M{x} {y} h{w*0.35} l8 10 h{w*0.65-8} v{h-10} h-{w} z" fill="{fill}" stroke="{INK}" stroke-width="1.8"/>'
            + text(x + w / 2, y + 30, label, 11, INK, weight='bold'))


def overview():
    p = Panel('Node-RED のエディターでデプロイすると、フローはプロジェクトのフォルダ（Git リポジトリ）に書き込まれる。コミットで履歴に記録し、必要ならリモート（GitHub など）とプッシュ、プルでやり取りする', 560, 210, 'pjo')
    p.add(pc(70, 95, 'happy', 'エディター'))
    p.add(folder(185, 45, 170, 120, 'プロジェクト（リポジトリ）'),
          doc(200, 90, [], 'flows.json', 90), doc(245, 118, [], 'package.json', 100))
    p.add(server(480, 95, 'happy', 'GitHub など'))
    p.arrow(92, 88, 180, 88, BLUE, 2).arrow(360, 80, 452, 80, ORANGE, 2).arrow(452, 112, 360, 112, GREEN, 2)
    p.add(text(135, 76, 'デプロイ', 10, BLUE, weight='bold'), text(406, 68, 'プッシュ', 10, ORANGE, weight='bold'), text(406, 130, 'プル', 10, GREEN, weight='bold'))
    # コミットの積み重ね
    for i in range(4):
        p.add(f'<circle cx="{215 + 36 * i}" cy="188" r="8" fill="#c00000"/>')
        if i:
            p.add(line(215 + 36 * (i - 1) + 8, 188, 215 + 36 * i - 8, 188, '#c00000', 2))
    p.add(text(270, 207, 'コミット（記録）が積み重なる', 10, '#c00000', weight='bold'))
    return p


def commit_flow():
    p = Panel('フローを直してデプロイすると、履歴タブの「ローカルの変更」に flows.json が出る。「変更をステージング」でコミット対象に移し、メッセージを入れてコミットすると「コミット履歴」に 1 件増える', 560, 200, 'pjc')
    steps = [('① 編集してデプロイ', 'デプロイ', '#8f0000'),
             ('② ローカルの変更', 'flows.json', ORANGE),
             ('③ ステージング', '＋ で移す', BLUE),
             ('④ コミット', 'メッセージ', GREEN)]
    for i, (title, sub, col) in enumerate(steps):
        x = 12 + 137 * i
        p.add(f'<rect x="{x}" y="30" width="125" height="150" rx="8" fill="#fafafa" stroke="{col}" stroke-width="2"/>',
              text(x + 62, 50, title, 11, col, weight='bold'))
        if i < 3:
            p.arrow(x + 127, 105, x + 135, 105, '#999', 2)
    # ① デプロイボタン
    p.add(pc(74, 105, 'happy'), f'<rect x="40" y="140" width="68" height="22" rx="4" fill="#8f0000"/>', text(74, 155, 'デプロイ', 11, '#fff', weight='bold'))
    # ② 変更の一覧
    p.add(doc(160, 70, [], 'flows.json', 100), text(211, 118, '変更あり', 10, ORANGE, weight='bold'),
          text(211, 150, 'クリックで差分', 10, '#666'))
    # ③ ステージング
    p.add(f'<circle cx="348" cy="100" r="16" fill="{BLUE}"/>', text(348, 106, '＋', 16, '#fff', weight='bold'),
          text(348, 140, '変更をステージング', 10, BLUE, weight='bold'))
    # ④ コミット
    p.add(f'<rect x="436" y="72" width="100" height="40" rx="4" fill="#fff" stroke="#bbb"/>', text(486, 90, '温度の閾値を', 10, INK), text(486, 104, '30℃に変更', 10, INK),
          f'<rect x="452" y="122" width="68" height="22" rx="4" fill="{GREEN}"/>', text(486, 137, 'コミット', 11, '#fff', weight='bold'),
          text(486, 166, '履歴に 1 件増える', 10, GREEN, weight='bold'))
    return p


def clone():
    p = Panel('パソコンで作ったプロジェクトを GitHub にプッシュし、ラズパイの Node-RED で「プロジェクトをクローン」すると同じフローが動く。暗号化キーは元と同じものを入力し、足りないノードは依存関係からインストールする', 560, 200, 'pjk')
    p.add(pc(70, 90, 'happy', 'パソコン'), server(280, 85, 'happy', 'GitHub'), pc(490, 90, 'happy', 'ラズパイ'))
    p.arrow(92, 80, 252, 80, ORANGE, 2).arrow(308, 80, 458, 80, GREEN, 2)
    p.add(text(170, 68, 'プッシュ', 10, ORANGE, weight='bold'), text(385, 68, 'クローン', 10, GREEN, weight='bold'))
    p.add(lock(380, 150), text(398, 148, '暗号化キー（元と同じ）', 10, INK, 'start'),
          text(398, 166, '＋ 依存関係のインストール', 10, INK, 'start'))
    p.add(text(170, 150, 'キーは GitHub に送られない', 10, RED, weight='bold'))
    return p


FIGURES = {'projects-overview': overview, 'projects-commit': commit_flow, 'projects-clone': clone}
