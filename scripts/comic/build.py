"""ガイド HTML に埋め込んだ漫画風の図を再生成する。

HTML 側には次の目印を置き、その間を図の定義から生成した SVG で置き換える。

    <!-- comic:begin switch-basic -->
    （ここが生成される）
    <!-- comic:end -->

使い方:
    python3 scripts/comic/build.py                 # 全ガイド
    python3 scripts/comic/build.py nodered-switch-node-guide.html
    python3 scripts/comic/build.py --check         # 生成結果と HTML が一致するか検査（変更しない）
"""
import glob
import importlib
import os
import re
import sys

# 図の定義を書き換えた直後でも古いキャッシュを読まないよう、.pyc を作らない
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

BLOCK = re.compile(r'(<!-- comic:begin ([a-z0-9-]+) -->)(.*?)(<!-- comic:end -->)', re.S)


def load_figures():
    """figures/*.py の FIGURES（キー → 描画関数）をまとめる"""
    figs = {}
    for path in sorted(glob.glob(os.path.join(HERE, 'figures', '[!_]*.py'))):
        name = os.path.splitext(os.path.basename(path))[0]
        mod = importlib.import_module(f'figures.{name}')
        for key, fn in mod.FIGURES.items():
            if key in figs:
                raise SystemExit(f'図のキーが重複しています: {key}')
            figs[key] = fn
    return figs


def build(path, figs, check):
    src = open(path, encoding='utf-8').read()
    missing = []

    def repl(m):
        key = m.group(2)
        if key not in figs:
            missing.append(key)
            return m.group(0)
        indent = re.search(r'([ \t]*)$', src[:m.start()]).group(1)
        return f'{m.group(1)}\n{indent}{figs[key]().render()}\n{indent}{m.group(4)}'

    out = BLOCK.sub(repl, src)
    if missing:
        raise SystemExit(f'{path}: 定義のない図があります: {", ".join(missing)}')
    if out == src:
        return False
    if not check:
        open(path, 'w', encoding='utf-8').write(out)
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    figs = load_figures()
    paths = args or sorted(glob.glob(os.path.join(ROOT, '*.html')))
    changed = [p for p in paths if build(p, figs, check)]
    for p in changed:
        print(('要再生成: ' if check else '更新: ') + os.path.basename(p))
    if check and changed:
        sys.exit(1)
    print(f'{len(paths)} ファイルを確認、{len(changed)} ファイル{"が古い" if check else "を更新"}')


if __name__ == '__main__':
    main()
