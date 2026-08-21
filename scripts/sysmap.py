# -*- coding: utf-8 -*-
"""演習の「作る範囲」図（sys-map）を各ガイドへ適用するための共通処理。

サイトは 1 ファイル完結構造で各 HTML が自前の <style> を持つため、図を入れる
ガイドごとに CSS を複製する必要がある。その CSS 定義と、図の組み立て・挿入・
検証をここにまとめている。図の見た目を変えるときはこのファイルを直してから
各ガイドへ反映する。

図の作法と適用済みガイドの一覧は docs/handoff.md を参照。

使い方の例:

    import sysmap
    t = sysmap.add_css(open(path).read())
    head, blocks, sep = sysmap.split_exercises(t)
    diagram = sysmap.sysmap([
        sysmap.actor("利用者", "ブラウザ や curl<br>（既にあるもの）"),
        sysmap.link("GET /api/status", "200 JSON"),
        sysmap.actor("Node-RED", "サーバー側<br>状態を返す", badge="これを作る"),
    ])
    blocks[0] = sysmap.insert_before(blocks[0], ANCHOR, diagram)
    open(path, "w").write(sysmap.join_exercises(head, blocks, sep))
    print(sysmap.verify(path))

注意: link() のラベルに矢印文字を含めないこと。末尾の矢印は link() が付ける。
"""
import io, re

CSS = "".join([
 "        .sys-map { background-color: #2d3133; padding: 20px 15px; border-radius: 5px; margin: 12px 0; display: flex; align-items: center; justify-content: safe center; flex-wrap: nowrap; gap: 6px; overflow-x: auto; }\n",
 "        .sys-actor { flex: 0 0 auto; border: 2px solid #78909c; border-radius: 6px; padding: 12px 14px; text-align: center; background-color: #37474f; max-width: 215px; }\n",
 "        .sys-name { font-weight: bold; font-size: 14px; color: #eceff1; }\n",
 "        .sys-role { font-size: 11px; line-height: 1.7; margin-top: 5px; color: #b0bec5; }\n",
 "        .sys-build { border-color: #ffca28; border-width: 3px; background-color: #3f3722; }\n",
 "        .sys-badge { display: inline-block; background-color: #ffca28; color: #3e2723; font-size: 11px; font-weight: bold; padding: 2px 10px; border-radius: 10px; margin-bottom: 6px; }\n",
 "        .sys-link { flex: 0 0 auto; display: flex; flex-direction: column; gap: 5px; padding: 0 4px; font-family: 'Courier New', Consolas, monospace; font-size: 11px; white-space: nowrap; text-align: center; }\n",
 "        .sys-req { color: #4fc3f7; }\n",
 "        .sys-res { color: #a6e22e; }\n",
])

def actor(name, role, badge=None, ind=16):
    p = " " * ind
    b = ('%s    <div><span class="sys-badge">%s</span></div>\n' % (p, badge)) if badge else ""
    return ('%s<div class="sys-actor%s">\n' % (p, " sys-build" if badge else "")
            + b
            + '%s    <div class="sys-name">%s</div>\n' % (p, name)
            + '%s    <div class="sys-role">%s</div>\n' % (p, role)
            + '%s</div>\n' % p)

def link(req, res=None, ind=16):
    """res=None なら一方向（矢印1本）。"""
    p = " " * ind
    s = '%s<div class="sys-link">\n%s    <div class="sys-req">%s &rarr;</div>\n' % (p, p, req)
    if res is not None:
        s += '%s    <div class="sys-res">&larr; %s</div>\n' % (p, res)
    return s + '%s</div>\n' % p

def sysmap(items, ind=12):
    p = " " * ind
    return ('%s<p><strong>作る範囲:</strong></p>\n' % p
            + '%s<div class="sys-map">\n' % p + "".join(items) + '%s</div>\n\n' % p)

def add_css(text):
    """.difficulty-hard 行の直後に sys-map の CSS を差し込む。"""
    m = re.search(r'^ *\.difficulty-hard \{[^\n]*\n', text, re.M)
    assert m, "difficulty-hard CSS not found"
    assert ".sys-map {" not in text, "CSS already present"
    return text[:m.end()] + CSS + text[m.end():]

def split_exercises(text):
    """(前, [演習ブロック...], 区切り文字列) を返す。"""
    sep = '        <div class="exercise">\n'
    parts = text.split(sep)
    return parts[0], parts[1:], sep

def join_exercises(head, blocks, sep):
    return head + "".join(sep + b for b in blocks)

def insert_before(block, anchor, diagram):
    """anchor の直前に図を置く（anchor は「要求仕様」等の見出し行）。"""
    assert block.count(anchor) >= 1, "anchor not found: %r" % anchor[:60]
    return block.replace(anchor, diagram + anchor, 1)

def verify(path):
    """タグ整合・内部リンク・sys-map数を返す。"""
    from html.parser import HTMLParser
    t = io.open(path, encoding="utf-8").read()
    VOID = {'br','img','hr','meta','link','input','area','base','col','embed','source','track','wbr'}
    class P(HTMLParser):
        def __init__(s): super().__init__(convert_charrefs=True); s.st=[]; s.e=[]
        def handle_starttag(s, tag, a):
            if tag not in VOID: s.st.append(tag)
        def handle_endtag(s, tag):
            if tag in VOID: return
            if not s.st or s.st[-1] != tag: s.e.append(tag)
            else: s.st.pop()
    p = P(); p.feed(t)
    ids = set(re.findall(r'\sid="([^"]+)"', t)); refs = set(re.findall(r'href="#([^"]+)"', t))
    return {"未閉鎖": p.st or "なし", "不一致": p.e or "なし",
            "リンク切れ": sorted(refs - ids) or "なし",
            "sys-map": t.count('class="sys-map"'), "演習": t.count('class="exercise"')}
