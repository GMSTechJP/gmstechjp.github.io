#!/usr/bin/env python3
"""サイトの更新履歴ページ(updates.html)を git 履歴から生成し、
index.html の「サイト最終更新」日を最新コミット日に更新する。

- updates.html : 非マージコミットを日付ごとにまとめた更新履歴ページ
- index.html   : <!-- SITE_LAST_UPDATED:START -->...<!-- SITE_LAST_UPDATED:END -->
                 を最新コミット日(YYYY-MM-DD)に置換

ローカル実行でも GitHub Actions 実行でも同じ結果になるよう、git log のみに依存する。
Actions による自動コミット([skip ci])は履歴に出さないよう除外する。
"""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
UPDATES = ROOT / "updates.html"

US = "\x1f"  # フィールド区切り(Unit Separator)

# コミットtype -> (表示ラベル, バッジ色)
TYPE_LABELS = {
    "feat": ("新機能", "#42b883"),
    "fix": ("修正", "#e76f51"),
    "docs": ("ドキュメント", "#4a9eda"),
    "refactor": ("リファクタ", "#9c6ade"),
    "perf": ("性能", "#2a9d8f"),
    "test": ("テスト", "#f4a261"),
    "style": ("スタイル", "#6b7280"),
    "chore": ("その他", "#6b7280"),
}
OTHER = ("更新", "#6b7280")

PREFIX_RE = re.compile(r"^([a-z]+)(?:\([^)]*\))?(?:!)?:\s*(.*)$")
# 自動生成コミットや CI スキップ印は履歴から除外
SKIP_RE = re.compile(r"\[skip ci\]|更新履歴と最終更新日を自動生成")


def git_log():
    fmt = f"%cd{US}%s"
    out = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--no-merges", "--date=short",
         f"--pretty=format:{fmt}"],
        capture_output=True, text=True, check=True,
    ).stdout
    entries = []
    for line in out.splitlines():
        if US not in line:
            continue
        date, subject = line.split(US, 1)
        if SKIP_RE.search(subject):
            continue
        entries.append((date, subject))
    return entries


def classify(subject):
    m = PREFIX_RE.match(subject)
    if m:
        label, color = TYPE_LABELS.get(m.group(1), OTHER)
        return label, color, m.group(2) or subject
    return OTHER[0], OTHER[1], subject


def build_updates_html(entries):
    latest = entries[0][0] if entries else "----"
    groups = []
    for date, subject in entries:
        if not groups or groups[-1][0] != date:
            groups.append((date, []))
        groups[-1][1].append(subject)

    sections = []
    for date, subjects in groups:
        items = []
        for subject in subjects:
            label, color, desc = classify(subject)
            items.append(
                '                    <li class="u-item">'
                f'<span class="u-badge" style="background:{color}">{html.escape(label)}</span>'
                f'<span class="u-text">{html.escape(desc)}</span></li>'
            )
        sections.append(
            '            <section class="u-day">\n'
            f'                <h2 class="u-date">{html.escape(date)}</h2>\n'
            '                <ul class="u-list">\n'
            + "\n".join(items) + "\n"
            '                </ul>\n'
            '            </section>'
        )

    return (TEMPLATE
            .replace("__COUNT__", str(len(entries)))
            .replace("__LATEST__", html.escape(latest))
            .replace("__BODY__", "\n".join(sections)))


def update_index(latest):
    text = INDEX.read_text(encoding="utf-8")
    new = re.sub(
        r"(<!-- SITE_LAST_UPDATED:START -->).*?(<!-- SITE_LAST_UPDATED:END -->)",
        rf"\g<1>{latest}\g<2>",
        text, flags=re.DOTALL,
    )
    if new != text:
        INDEX.write_text(new, encoding="utf-8")
        return True
    return False


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>更新履歴 | Node-RED 学習ガイド</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #42b883;
            --primary-dark: #35495e;
            --bg-light: #f8fafc;
            --bg-card: #ffffff;
            --text-primary: #2c3e50;
            --text-secondary: #6b7280;
            --border: #e5e7eb;
            --shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            --radius: 12px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, var(--bg-light) 0%, #e2e8f0 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, var(--primary-dark) 0%, #1a252f 100%);
            color: white;
            padding: 48px 20px;
            text-align: center;
        }
        .header h1 { font-size: 2.2em; font-weight: 700; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .container { max-width: 860px; margin: 0 auto; padding: 40px 20px; }
        .u-intro {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 18px 24px;
            margin-bottom: 28px;
            color: var(--text-secondary);
        }
        .u-day {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 18px 24px;
            margin-bottom: 18px;
        }
        .u-date {
            font-size: 1.05em;
            color: var(--primary-dark);
            border-bottom: 2px solid var(--primary);
            display: inline-block;
            padding-bottom: 4px;
            margin-bottom: 12px;
        }
        .u-list { list-style: none; }
        .u-item { display: flex; align-items: flex-start; gap: 10px; padding: 5px 0; }
        .u-badge {
            flex: 0 0 auto;
            color: white;
            font-size: 0.78em;
            font-weight: 700;
            padding: 2px 9px;
            border-radius: 10px;
            margin-top: 3px;
            white-space: nowrap;
        }
        .u-text { color: var(--text-primary); }
        .footer {
            text-align: center;
            padding: 30px 20px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        .footer a { color: var(--primary-dark); }
        @media (max-width: 600px) { .header h1 { font-size: 1.6em; } }
    </style>
</head>
<body>
    <header class="header">
        <h1>📝 更新履歴</h1>
        <p>Node-RED 学習ガイドの変更履歴（全 __COUNT__ 件）</p>
    </header>
    <div class="container">
        <div class="u-intro">
            このページは git のコミット履歴から<strong>自動生成</strong>されています。最新の更新日: <strong>__LATEST__</strong>
        </div>
__BODY__
    </div>
    <footer class="footer">
        <p><a href="index.html">← トップページへ戻る</a></p>
        <p style="margin-top: 8px;">© 2024-2025 Node-RED 学習ガイド</p>
    </footer>
    <!-- フローティングホームボタン -->
    <a href="index.html" style="position: fixed; bottom: 20px; right: 20px; width: 56px; height: 56px; background: linear-gradient(135deg, #42b883 0%, #35495e 100%); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000;" title="トップページへ">🏠</a>
</body>
</html>
"""


def main():
    entries = git_log()
    if not entries:
        print("コミットが見つかりません", file=sys.stderr)
        return 1
    latest = entries[0][0]
    UPDATES.write_text(build_updates_html(entries), encoding="utf-8")
    changed = update_index(latest)
    print(f"updates.html 生成: {len(entries)} 件 / 最終更新 {latest} / "
          f"index.html {'更新' if changed else '変更なし'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
