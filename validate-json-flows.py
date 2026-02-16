#!/usr/bin/env python3
"""
Node-REDガイドファイルのJSON構文検証スクリプト（改善版）

すべての nodered-*-guide.html ファイルから <div class="flow-json"> 内の
JSONを抽出し（ブラケットカウント方式）、構文エラーをチェックします。
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

def extract_json_from_position(content: str, start_pos: int) -> Optional[Tuple[str, int]]:
    """
    指定位置からJSONを抽出（ブラケットカウント方式）

    Args:
        content: HTML content
        start_pos: Start position to search from

    Returns:
        (json_text, end_pos) or None
    """
    # 開始ブラケット '[' を探す
    json_start = content.find('[', start_pos)
    if json_start == -1:
        return None

    # ブラケットをカウントして対応する ']' を見つける
    depth = 0
    i = json_start
    in_string = False
    escape_next = False

    while i < len(content):
        char = content[i]

        if escape_next:
            escape_next = False
            i += 1
            continue

        if char == '\\':
            escape_next = True
            i += 1
            continue

        if char == '"':
            in_string = not in_string
        elif not in_string:
            if char == '[':
                depth += 1
            elif char == ']':
                depth -= 1
                if depth == 0:
                    # JSONブロックの終了
                    json_text = content[json_start:i+1]
                    return (json_text, i+1)

        i += 1

    return None

def extract_all_json_blocks(html_content: str, filename: str) -> List[Tuple[int, str]]:
    """
    HTMLから <div class="flow-json"> タグ内のすべてのJSONブロックを抽出

    Returns:
        List of (line_number, json_content) tuples
    """
    json_blocks = []
    search_pos = 0

    while True:
        # 次の <div class="flow-json"> を検索
        marker = '<div class="flow-json">'
        start_pos = html_content.find(marker, search_pos)
        if start_pos == -1:
            break

        # JSONブロックを抽出
        result = extract_json_from_position(html_content, start_pos + len(marker))
        if result:
            json_text, end_pos = result

            # 開始行番号を計算
            line_number = html_content[:start_pos].count('\n') + 1

            json_blocks.append((line_number, json_text))
            search_pos = end_pos
        else:
            search_pos = start_pos + len(marker)

    return json_blocks

def validate_json(json_content: str) -> Tuple[bool, str]:
    """
    JSON構文を検証

    Returns:
        (is_valid, error_message)
    """
    try:
        json.loads(json_content)
        return (True, "")
    except json.JSONDecodeError as e:
        return (False, f"Line {e.lineno}, Column {e.colno}: {e.msg}")
    except Exception as e:
        return (False, str(e))

def main():
    """メイン処理"""
    # ガイドファイルを取得
    guide_files = sorted(Path('.').glob('nodered-*-guide.html'))

    if not guide_files:
        print("❌ ガイドファイルが見つかりません")
        sys.exit(1)

    print(f"📋 検証対象: {len(guide_files)} ファイル\n")
    print("=" * 80)

    total_files = 0
    total_json_blocks = 0
    valid_files = 0
    invalid_files = 0
    errors = []

    for filepath in guide_files:
        total_files += 1
        filename = filepath.name

        # HTMLファイルを読み込み
        try:
            html_content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ {filename}: ファイル読み込みエラー: {e}")
            invalid_files += 1
            errors.append((filename, "ファイル読み込みエラー", str(e)))
            continue

        # JSONブロックを抽出
        json_blocks = extract_all_json_blocks(html_content, filename)

        if not json_blocks:
            print(f"⚠️  {filename}: JSONブロックが見つかりません")
            continue

        total_json_blocks += len(json_blocks)
        file_valid = True

        # 各JSONブロックを検証
        for block_index, (line_number, json_content) in enumerate(json_blocks, 1):
            is_valid, error_msg = validate_json(json_content)

            if not is_valid:
                file_valid = False
                error_info = f"Block #{block_index} (HTML Line {line_number}): {error_msg}"
                print(f"❌ {filename}: {error_info}")
                errors.append((filename, f"Block #{block_index}", error_msg))

        if file_valid:
            valid_files += 1
            print(f"✅ {filename}: {len(json_blocks)} JSONブロック - すべて有効")
        else:
            invalid_files += 1

    # サマリー
    print("=" * 80)
    print("\n📊 検証結果サマリー")
    print(f"  総ファイル数: {total_files}")
    print(f"  総JSONブロック数: {total_json_blocks}")
    print(f"  ✅ 有効: {valid_files} ファイル")
    print(f"  ❌ 無効: {invalid_files} ファイル")

    if errors:
        print(f"\n⚠️  {len(errors)} 件のエラーが見つかりました:")
        print("=" * 80)
        for filename, location, error_msg in errors:
            print(f"\nファイル: {filename}")
            print(f"  場所: {location}")
            print(f"  エラー: {error_msg}")
    else:
        print("\n🎉 すべてのJSONブロックが有効です！")

    # 終了コード
    sys.exit(0 if invalid_files == 0 else 1)

if __name__ == '__main__':
    main()
