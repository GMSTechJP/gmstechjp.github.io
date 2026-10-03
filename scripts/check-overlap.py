#!/usr/bin/env python3
"""ページを描画して、ほかの要素に隠れている文字を探す。

図の中で、図形（待機のバー、配線、回転させた矢印など）が文字に重なると、本来見せたい
文字（例: trigger のタイムラインの出力 "1"）が隠れる。HTML としては正しく、ソースを読む
レビューでも見つからないため、ヘッドレスの Chrome でページを描画して調べる。

調べ方: ページの文字（SVG の文字を含む）ごとに、文字の幅の 5 か所で
document.elementFromPoint() を呼び、一番手前の要素がその文字の要素（または祖先・子孫）で
なければ「隠れている」と報告する。画面に固定した要素（ホームボタンなど）は除く。
隠している要素が透明でも報告する（文字は見えても、その上ではクリックや選択ができない）。

重なりは画面の幅で変わるため、既定ではパソコンの幅（1200px）とスマートフォンの幅（390px）
の両方で調べる。閉じた <details> の中は調べない。

    python3 scripts/check-overlap.py                       # 全ページ、2 つの幅
    python3 scripts/check-overlap.py nodered-trigger-node-guide.html --width 390

Chrome が必要なため CI では実行しない。図やレイアウトを変えたら手元で実行する。
Chrome の場所は環境変数 CHROME で指定できる。
"""

import argparse
import glob
import html
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
]

JS = r"""
function check(doc, page) {
  const out = []; const win = doc.defaultView;
  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const t = n.textContent.trim(); if (!t) continue;
    const el = n.parentElement; if (!el) continue;
    if (el.closest('script,style,defs,.flow-json,pre,textarea,option')) continue;
    const det = el.closest('details');
    if (det && !det.open && !el.closest('summary')) continue;
    const cs = win.getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const r = doc.createRange(); r.selectNodeContents(n);
    for (const rect of r.getClientRects()) {
      if (rect.width < 2 || rect.height < 2) continue;
      let found = null;
      for (const f of [0.15, 0.3, 0.5, 0.7, 0.85]) {
        const x = rect.left + rect.width * f, y = rect.top + rect.height / 2;
        const hit = doc.elementFromPoint(x, y);
        if (!hit || hit === el || el.contains(hit) || hit.contains(el)) continue;
        if (win.getComputedStyle(hit).position === 'fixed') continue;
        found = {hit, y}; break;
      }
      if (found) {
        const cls = e => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className ? '.' + e.className.trim().split(/\s+/).join('.') : '');
        out.push({page, text: t.slice(0, 40), el: cls(el), hit: cls(found.hit), y: Math.round(found.y + doc.defaultView.scrollY)});
        break;
      }
    }
  }
  return out;
}
const pages = PAGES; const results = []; let i = 0;
function next() {
  if (i >= pages.length) { document.getElementById('out').textContent = JSON.stringify(results); return; }
  const f = document.createElement('iframe'); f.style.width = WIDTH + 'px'; f.style.height = '100px';
  f.src = pages[i]; document.body.appendChild(f);
  f.onload = () => { setTimeout(() => { try {
      const d = f.contentDocument; f.style.height = (d.documentElement.scrollHeight + 50) + 'px';
      setTimeout(() => { try { results.push(...check(d, pages[i])); results.push({page: pages[i], done: true}); }
        catch (e) { results.push({page: pages[i], error: String(e)}); }
        f.remove(); i++; next(); }, 300);
    } catch (e) { results.push({page: pages[i], error: String(e)}); f.remove(); i++; next(); } }, 300); };
}
next();
"""


def find_chrome():
    env = os.environ.get("CHROME")
    if env:
        return env
    for c in CANDIDATES:
        if os.path.exists(c) or shutil.which(c):
            return c
    return None


def run_until_result(cmd, timeout):
    """Chrome を起動し、結果の <pre id="out"> が出力しきった時点で止めて、出力を返す。

    --dump-dom は DOM を出力したあとも Chrome が終わらない環境がある（macOS で確認）。
    そのため終了を待たず、結果の閉じタグまで読んだら止める。時間内に結果が出ない、
    または結果が出る前に Chrome が異常終了したときは None を返す（検査できなかった扱い）。
    """
    # Chrome は子プロセスを起動するため、プロセスグループごと止められるように新しいセッションで起動する
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                            start_new_session=True)
    chunks = []
    done = threading.Event()

    def reader():
        for line in proc.stdout:
            chunks.append(line)
            if "</pre>" in line and '<pre id="out">' in "".join(chunks):
                break
        done.set()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    finished = done.wait(timeout)
    out = "".join(chunks)
    complete = re.search(r'<pre id="out">(?!PENDING</pre>).*?</pre>', out, re.S) is not None
    try:
        os.killpg(proc.pid, signal.SIGKILL)  # 子プロセスも含めて止める
    except ProcessLookupError:
        pass
    proc.wait()
    proc.stdout.close()
    thread.join(5)
    if not finished or not complete:
        return None
    return out


def scan(chrome, pages, width):
    urls = ["file://" + os.path.join(ROOT, p) for p in pages]
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "scan.html")
        js = JS.replace("PAGES", json.dumps(urls)).replace("WIDTH", str(width))
        with open(page, "w", encoding="utf-8") as f:
            f.write(f'<!DOCTYPE html><html><body><pre id="out">PENDING</pre><script>{js}</script></body></html>')
        cmd = [chrome, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
               f"--user-data-dir={os.path.join(tmp, 'profile')}", "--window-size=1300,900",
               f"--virtual-time-budget={len(pages) * 4000}", "--dump-dom", "file://" + page]
        out = run_until_result(cmd, timeout=60 + len(pages) * 8)
    if out is None:
        return None
    m = re.search(r'<pre id="out">(.*?)</pre>', out, re.S)
    if not m or m.group(1) == "PENDING":
        return None
    try:
        results = json.loads(html.unescape(m.group(1)))
    except json.JSONDecodeError:
        return None
    return results if isinstance(results, list) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pages", nargs="*", help="調べる HTML（既定: 全ページ）")
    ap.add_argument("--width", type=int, action="append", help="画面の幅（複数指定可。既定: 1200 と 390）")
    args = ap.parse_args()
    pages = args.pages or sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))
    widths = args.width or [1200, 390]
    chrome = find_chrome()
    if not chrome:
        print("Chrome が見つからない（環境変数 CHROME で場所を指定する）")
        return 2

    problems = 0
    for width in widths:
        results = scan(chrome, pages, width)
        if results is None:
            print(f"幅 {width}px: 描画の結果を取得できなかった（時間切れ、Chrome の異常終了など）")
            return 2
        done = {r["page"] for r in results if r.get("done")}
        if len(done) != len(pages):
            # 1 ページでも調べ損ねたら、成功扱いにしない
            print(f"幅 {width}px: {len(pages)} ページ中 {len(done)} ページしか調べられなかった")
            for r in results:
                if r.get("error"):
                    print("  ", r["page"], r["error"])
            return 2
        for r in results:
            if r.get("done"):
                continue
            problems += 1
            print(f"{os.path.basename(r['page'])}（幅 {width}px, y={r['y']}）: "
                  f"「{r['text']}」（{r['el']}）が {r['hit']} に隠れている")
    print(f"\n{len(pages)} pages × {len(widths)} widths checked, {problems} problems found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
