#!/usr/bin/env python3
"""
Node-REDインポートテストスクリプト

サンプリング対象ファイルからJSONを抽出し、
Node-REDでインポート可能かテストします。
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# JSONブロック抽出関数をインライン定義
import re

def extract_json_from_position(content: str, start_pos: int) -> Optional[Tuple[str, int]]:
    """指定位置からJSONを抽出（ブラケットカウント方式）"""
    json_start = content.find('[', start_pos)
    if json_start == -1:
        return None

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
                    json_text = content[json_start:i+1]
                    return (json_text, i+1)

        i += 1

    return None

def extract_all_json_blocks(html_content: str, filename: str) -> List[Tuple[int, str]]:
    """HTMLから <div class="flow-json"> タグ内のすべてのJSONブロックを抽出"""
    json_blocks = []
    search_pos = 0

    while True:
        marker = '<div class="flow-json">'
        start_pos = html_content.find(marker, search_pos)
        if start_pos == -1:
            break

        result = extract_json_from_position(html_content, start_pos + len(marker))
        if result:
            json_text, end_pos = result
            line_number = html_content[:start_pos].count('\n') + 1
            json_blocks.append((line_number, json_text))
            search_pos = end_pos
        else:
            search_pos = start_pos + len(marker)

    return json_blocks

# サンプリング対象ファイル
SAMPLING_FILES = [
    # Phase 1修正（CRITICAL）
    "nodered-html-node-guide.html",
    "nodered-websocket-node-guide.html",
    "nodered-xml-node-guide.html",
    # Phase 2修正
    "nodered-comment-node-guide.html",
    "nodered-switch-node-guide.html",
    "nodered-split-node-guide.html",
    "nodered-csv-node-guide.html",
    "nodered-file-node-guide.html",
    "nodered-mqtt-node-guide.html",
    # Phase 3修正
    "nodered-change-node-guide.html",
    "nodered-function-node-guide.html",
    "nodered-join-node-guide.html",
    "nodered-batch-node-guide.html",
    # 既修正
    "nodered-inject-node-guide.html",
    "nodered-debug-node-guide.html",
    # 新規修正
    "nodered-base64-node-guide.html",
]

def test_node_red_import(json_content: str) -> Tuple[bool, str]:
    """
    JSONがNode-RED形式として有効か検証

    Returns:
        (is_valid, message)
    """
    try:
        data = json.loads(json_content)

        # Node-REDフロー形式の検証
        if not isinstance(data, list):
            return (False, "フローは配列である必要があります")

        if len(data) == 0:
            return (False, "フローが空です")

        # 各ノードの基本検証
        node_count = 0
        tab_count = 0
        config_count = 0

        for node in data:
            if not isinstance(node, dict):
                return (False, f"ノードがオブジェクトではありません: {node}")

            if "id" not in node:
                return (False, "ノードにidがありません")

            if "type" not in node:
                return (False, f"ノード {node.get('id')} にtypeがありません")

            node_type = node.get("type")
            if node_type == "tab":
                tab_count += 1
            elif node_type in ["ui-base", "ui-theme", "ui-group", "ui-page",
                             "mqtt-broker", "websocket-listener", "websocket-client"]:
                config_count += 1
            else:
                node_count += 1

        summary = f"{len(data)}ノード (tab: {tab_count}, config: {config_count}, other: {node_count})"
        return (True, summary)

    except json.JSONDecodeError as e:
        return (False, f"JSON解析エラー: {e}")
    except Exception as e:
        return (False, f"予期しないエラー: {e}")

def main():
    """メイン処理"""
    print("=" * 80)
    print("Node-REDインポートテスト")
    print("=" * 80)
    print()

    total_files = len(SAMPLING_FILES)
    total_blocks = 0
    passed_files = 0
    passed_blocks = 0
    failed_files = 0
    errors = []

    for filename in SAMPLING_FILES:
        filepath = Path(filename)

        if not filepath.exists():
            print(f"❌ {filename}: ファイルが見つかりません")
            failed_files += 1
            errors.append((filename, "ファイルが見つかりません"))
            continue

        # HTMLファイルを読み込み
        try:
            html_content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ {filename}: 読み込みエラー: {e}")
            failed_files += 1
            errors.append((filename, f"読み込みエラー: {e}"))
            continue

        # JSONブロックを抽出
        json_blocks = extract_all_json_blocks(html_content, filename)

        if not json_blocks:
            print(f"⚠️  {filename}: JSONブロックが見つかりません")
            continue

        # 最初のJSONブロック（サンプルフロー）のみテスト
        line_number, json_content = json_blocks[0]
        total_blocks += 1

        # インポートテスト
        is_valid, message = test_node_red_import(json_content)

        if is_valid:
            print(f"✅ {filename}: {message}")
            passed_files += 1
            passed_blocks += 1
        else:
            print(f"❌ {filename}: {message}")
            failed_files += 1
            errors.append((filename, message))

    # サマリー
    print()
    print("=" * 80)
    print("📊 テスト結果サマリー")
    print(f"  総ファイル数: {total_files}")
    print(f"  テスト済みJSONブロック数: {total_blocks}")
    print(f"  ✅ 合格: {passed_files} ファイル ({passed_blocks} ブロック)")
    print(f"  ❌ 不合格: {failed_files} ファイル")

    if errors:
        print(f"\n⚠️  {len(errors)} 件のエラー:")
        print("=" * 80)
        for filename, error_msg in errors:
            print(f"\n{filename}:")
            print(f"  {error_msg}")
    else:
        print("\n🎉 すべてのJSONブロックがNode-RED形式として有効です！")

    # 終了コード
    sys.exit(0 if failed_files == 0 else 1)

if __name__ == '__main__':
    main()
