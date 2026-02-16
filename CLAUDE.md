# Node-RED ノードガイドサイト 開発ガイド

## プロジェクト概要

### サイトの目的

このプロジェクトは、Node-RED初心者向けの日本語ガイドを提供する静的HTMLサイトです。各ノードの使い方を詳しく解説し、実用的なサンプルフローと演習問題で実践的なスキルを習得できるようにします。

**公開URL**: https://gmstechjp.github.io/

### 対象ユーザー

- Node-REDを初めて使う方
- 各ノードの詳細な使い方を学びたい方
- 実践的なサンプルフローを探している方
- 演習問題で理解を深めたい方

### リポジトリ構造

```
gmstechjp.github.io/
├── README.md                           # プロジェクト概要
├── CLAUDE.md                          # 開発ガイド（本ファイル）
├── PROCEDURE-standard-nodes-audit.md   # 監査手順書
├── AUDIT-REPORT.md                     # 監査結果レポート
├── IMPLEMENTATION-PLAN.md              # 改善実装計画
├── index.html                          # トップページ
├── nodered-*-node-guide.html          # 各ノードのガイド（50+件）
├── img/                                # 画像ディレクトリ
└── reference/                          # 参考資料
```

### プロジェクトの基本方針

- **公開リポジトリ**: 機密情報・APIキーは含めない
- **初心者フレンドリー**: 専門用語には丁寧な説明を付ける
- **品質重視**: 正確性と動作検証を最優先
- **メンテナンス性**: 将来の更新を容易にする構造

---

## 開発ワークフロー

### 新規ガイドの作成手順

詳細は `PROCEDURE-standard-nodes-audit.md` のセクション1を参照してください。

#### 1. 対象ノードの特定

| カテゴリ | ソースリポジトリ | パス |
|---------|-----------------|------|
| 標準ノード | https://github.com/node-red/node-red | `packages/node_modules/@node-red/nodes/core/<category>/<node>.html` |
| Dashboard 2.0 | https://github.com/FlowFuse/node-red-dashboard | `nodes/widgets/ui_<name>.html` または `nodes/config/ui_<name>.html` |
| サードパーティ | 各パッケージのGitHubリポジトリ | パッケージにより異なる |

#### 2. ソースコードの取得と分析

```bash
# 例：Injectノードのソース取得
curl https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html
```

**確認項目**:
- `defaults` オブジェクト：ノードの全プロパティ定義
- フォーム要素：エディターで表示される設定項目
- `data-i18n` 属性：国際化されたラベル名

#### 3. プロパティの分類

| 分類 | 条件 | プロパティ表に記載 | フローJSONに含める |
|------|------|-------------------|-------------------|
| **アクティブ** | defaults内 AND フォーム要素あり（有効） | ✅ YES | ✅ YES |
| **コメントアウト済み** | defaults内 BUT フォーム要素がコメントアウト | ❌ NO | ❌ NO |
| **エディタ非表示** | defaults内 BUT フォーム要素なし | ❌ NO | ✅ YES |
| **存在しない** | defaultsに定義なし | ❌ NO | ❌ NO |

#### 4. HTMLガイドファイルの作成

**テンプレート構造**:
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Node-RED [ノード名]ノード ガイド</title>
    <style>
        /* 統一されたCSSスタイル */
    </style>
</head>
<body>
    <div class="container">
        <h1>Node-RED [ノード名]ノード ガイド</h1>

        <!-- 1. 概要 -->
        <!-- 2. 設定項目一覧（プロパティ表） -->
        <!-- 3. 実用的な使用パターン -->
        <!-- 4. サンプルフロー -->
        <!-- 5. 演習問題 -->
        <!-- 6. まとめ -->
        <!-- 7. トラブルシューティング -->
    </div>
</body>
</html>
```

#### 5. プロパティ表の作成

**重要な原則**:
- **設定項目名はNode-REDエディターの表示に完全一致させる**
- エディターHTMLの `<label>` テキストをそのまま使用
- 説明は日本語で記載（ユーザーフレンドリーに）

**例（Injectノード）**:
```html
<h3>📋 設定項目一覧</h3>
<table>
    <tr>
        <th>設定項目</th>
        <th>説明</th>
        <th>備考</th>
    </tr>
    <tr>
        <td><strong>Payload</strong></td>
        <td>送信するデータの内容</td>
        <td>様々な型を選択可能</td>
    </tr>
    <tr>
        <td><strong>Topic</strong></td>
        <td>メッセージのトピック</td>
        <td>任意の文字列</td>
    </tr>
    <tr>
        <td><strong>Repeat</strong></td>
        <td>定期実行の間隔</td>
        <td>秒/分/時間で指定</td>
    </tr>
    <!-- ... -->
</table>
```

#### 6. サンプルフローの作成

**必須要件**:
- [ ] JSON構文が有効（`JSON.parse()` でエラーなし）
- [ ] `defaults` の全プロパティを網羅（アクティブ + エディタ非表示）
- [ ] Config Nodeのプロパティも完全
- [ ] tabノードを含む
- [ ] 各ノードに `z` プロパティを含む
- [ ] 複数出力ノードは `outputs` と `wires` のサイズが一致

**フォーマット**:
```html
<details>
    <summary>📋 サンプルフロー（クリックで展開）</summary>
    <div class="flow-json">
        <textarea readonly>
[
    {
        "id": "tab_id",
        "type": "tab",
        "label": "Example Flow",
        "disabled": false,
        "info": "",
        "env": []
    },
    {
        "id": "node_id",
        "type": "inject",
        "z": "tab_id",
        "name": "example",
        // ... 全プロパティ
    }
]
        </textarea>
    </div>
</details>
```

#### 7. 演習問題の作成

**構成**:
- 難易度表示（初級/中級/上級）
- 問題文
- ヒント
- 解答例フロー（サンプルフローと同じ品質基準）

### 既存ガイドの修正手順

詳細は `PROCEDURE-standard-nodes-audit.md` のセクション2を参照してください。

#### 1. 問題の特定

`AUDIT-REPORT.md` で問題を確認：
- CRITICAL：JSON構文エラー → 最優先
- HIGH：Config Node不完全 → 高優先
- MEDIUM：プロパティ不足・非推奨 → 中優先
- LOW：ドキュメント不正確 → 低優先

#### 2. ソースコードとの照合

1. GitHubから最新のソースコードを取得
2. `defaults` オブジェクトを抽出
3. フォーム要素を確認
4. ガイドのプロパティ表と比較

#### 3. 修正の実施

**プロパティ表の修正**:
- アクティブなプロパティのみ記載
- 設定項目名をエディターの表示に一致
- 不要行の削除、不足行の追加

**サンプルフローの修正**:
- 非推奨プロパティの削除
- 不足プロパティの追加
- Config Nodeの完全性確保
- JSON検証

#### 4. 検証

**3層の検証**:
1. **JSON構文検証**: `JSON.parse()` でエラーなし
2. **ソースコード照合**: defaults と完全一致
3. **インポートテスト**: Node-REDエディターで動作確認

---

## 品質基準

### プロパティ表の完全性

**必須チェック項目**:
- [ ] `defaults` オブジェクトの全アクティブプロパティを記載
- [ ] コメントアウト済みプロパティは記載しない
- [ ] エディタ非表示プロパティは記載しない
- [ ] 設定項目名がエディターの `<label>` テキストと一致
- [ ] 各プロパティに日本語の説明を付与
- [ ] 備考欄に使用例やデフォルト値を記載

**NG例**:
```html
<!-- ❌ エディターに存在しないプロパティ -->
<td><strong>tooltip</strong></td>

<!-- ❌ 日本語訳のみで英語表記と不一致 -->
<td><strong>繰り返し</strong></td>  <!-- エディターでは "Repeat" -->
```

**OK例**:
```html
<!-- ✅ エディターの表示と一致 -->
<td><strong>Repeat</strong></td>
<td>定期実行の間隔</td>
<td>秒/分/時間で指定</td>
```

### JSON検証要件

**必須検証**:
```bash
# すべてのHTMLファイルのJSONブロックを検証
for file in nodered-*-guide.html; do
    python3 -c "import json, sys; json.loads(sys.stdin.read())" < \
        <(grep -Pzo '(?<=<textarea[^>]*>).*?(?=</textarea>)' "$file")
    if [ $? -eq 0 ]; then
        echo "✅ $file: Valid JSON"
    else
        echo "❌ $file: Invalid JSON"
    fi
done
```

**合格基準**:
- すべてのJSONブロックがエラーなくパース可能
- インデントが適切（読みやすさ）
- 文字列内の改行は `\n` でエスケープ

### Node-REDインポートテスト要件

**テスト手順**:
1. Node-REDエディターを起動（ローカル環境）
2. サンプルフローJSONをコピー
3. メニュー → 読み込み → JSONをペースト
4. インポート成功を確認
5. デプロイして基本動作確認

**サンプリング率**:
- CRITICAL/HIGH問題のファイル：100%
- MEDIUM問題のファイル：50%
- LOW問題のファイル：30%
- 問題なしファイル：10%

**合格基準**:
- インポートエラーなし
- デプロイ成功
- 基本的な動作確認（メッセージ送信/受信）

### ドキュメント品質

**HTMLファイル構造**:
- [ ] 一貫したCSSスタイル
- [ ] フローティングホームボタン（`<a href="index.html">`）
- [ ] コピーボタン付きコードブロック
- [ ] レスポンシブデザイン
- [ ] 目次セクション（長いガイドの場合）

**コンテンツ品質**:
- [ ] 初心者にも分かりやすい説明
- [ ] 実用的な使用例
- [ ] 図解やコード例の適切な配置
- [ ] トラブルシューティングセクション

---

## ドキュメント体系

### ドキュメント間の関係

```
CLAUDE.md（本ファイル）
├── プロジェクト全体の開発ガイド
├── 品質基準の定義
└── トラブルシューティング

PROCEDURE-standard-nodes-audit.md
├── ガイド作成の詳細手順
├── 監査作業の手順
└── プロパティ分類の基準

AUDIT-REPORT.md
├── 監査結果の記録
├── 問題一覧（27件）
└── 修正状況のトラッキング

IMPLEMENTATION-PLAN.md
├── 改善計画（Phase 1〜5）
├── 検証方法
└── 成功基準

README.md
├── プロジェクト概要
├── セットアップ方法
└── コントリビューション
```

### 各ドキュメントの使い分け

| 状況 | 参照するドキュメント |
|------|---------------------|
| 新規ガイドを作成したい | PROCEDURE → CLAUDE.md（品質基準） |
| 既存ガイドに問題を発見 | AUDIT-REPORT で確認 → PROCEDURE で修正 |
| プロジェクト全体の改善計画 | IMPLEMENTATION-PLAN |
| 開発の基本方針を知りたい | CLAUDE.md |
| プロジェクトの概要を知りたい | README.md |

---

## コーディング規約

### Git運用

**ブランチ戦略**:
- `main`: 本番環境（GitHub Pages公開ブランチ）
- `feature/<feature-name>`: 新機能開発
- `fix/<issue-number>`: バグ修正

**コミットメッセージ規則**:

コンベンショナルコミット形式を使用：
```
<type>: <subject>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Type一覧**:
- `feat`: 新機能（新規ガイド追加）
- `fix`: バグ修正（JSON構文エラー、プロパティ不一致）
- `docs`: ドキュメント（README、PROCEDURE更新）
- `refactor`: リファクタリング（プロパティ表の整理）
- `test`: テスト追加・修正
- `chore`: その他の作業

**例**:
```
fix: injectノードガイドのプロパティ表を修正

- プロパティ表から非推奨のtopic行を削除
- サンプルフローにonceDelayプロパティを追加
- 演習フロー4件のpropsプロパティを修正

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### ファイル命名規則

**ガイドファイル**:
```
nodered-<node-name>-node-guide.html
```

**例**:
- `nodered-inject-node-guide.html`
- `nodered-debug-node-guide.html`
- `nodered-dashboard2-widgets-display.html`

### コードスタイル

**HTML**:
- インデント：スペース4個
- 属性値：ダブルクォート使用
- セマンティックHTML推奨

**JSON**:
- インデント：スペース4個
- プロパティの順序：`id`, `type`, `z`, その他、`x`, `y`, `wires`
- 文字列内の改行：`\n` でエスケープ

---

## トラブルシューティング

### よくある問題と解決方法

#### 問題1: JSON構文エラー

**症状**: Node-REDでフローをインポートできない

**原因**:
- リテラル改行文字の混入
- カンマの過不足
- 括弧の不一致

**解決方法**:
```bash
# JSON検証
python3 -m json.tool < flow.json

# または
node -e "JSON.parse(require('fs').readFileSync('flow.json'))"
```

**修正例**:
```json
// ❌ NG: リテラル改行
"template": "<html>
<body>Hello</body>
</html>"

// ✅ OK: エスケープ
"template": "<html>\n<body>Hello</body>\n</html>"
```

#### 問題2: プロパティ表とソースコードの不一致

**症状**: ガイドに記載されているプロパティが実際のエディターにない

**原因**:
- Node-REDのバージョンアップで変更
- コメントアウト済みプロパティを記載
- エディタ非表示プロパティを記載

**解決方法**:
1. 最新のソースコードを確認
2. `defaults` オブジェクトとフォーム要素を照合
3. プロパティ表を更新

```bash
# 最新のInjectノードソースを確認
curl https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html | grep -A 20 "defaults:"
```

#### 問題3: Dashboard 2.0のConfig Nodeプロパティ不足

**症状**: Dashboard 2.0のサンプルフローが正常に動作しない

**原因**: ui-base, ui-theme, ui-group, ui-page のプロパティが不完全

**解決方法**:

既存の修正済みガイド（display, input, visualization）を参照：
```bash
# ui-baseの正しいプロパティを確認
grep -A 20 '"type": "ui-base"' nodered-dashboard2-widgets-display.html
```

必須プロパティを追加：
- ui-base: `headerContent`, `navigationStyle`, `titleBarStyle`
- ui-theme: `sizes.density`
- ui-group: `groupType`
- ui-page: `visible`, `disabled`

#### 問題4: Cloudflareメール保護による破損

**症状**: XMLノードのサンプルフローにメール保護タグが混入

**原因**: Cloudflareがメールアドレスを自動検出して置換

**解決方法**:
```html
<!-- ❌ NG: メールアドレスを直接記載 -->
<email>user@example.com</email>

<!-- ✅ OK: 別形式に変更 -->
<email>user[at]example.com</email>
```

---

## メンテナンス

### 定期監査スケジュール

**四半期ごと（3ヶ月に1回）**:
- [ ] 全ガイドファイルのJSON検証
- [ ] プロパティ表とソースコードの照合（サンプリング20%）
- [ ] Node-REDエディターでインポートテスト（サンプリング10%）
- [ ] 新規発見問題をAUDIT-REPORTに追記

**年次（1年に1回）**:
- [ ] 全ガイドファイルの完全監査
- [ ] Node-REDバージョンアップ対応
- [ ] Dashboard 2.0更新対応
- [ ] ドキュメント（README、PROCEDURE、CLAUDE.md）の見直し

### Node-REDバージョンアップ時の対応

**手順**:
1. Node-RED公式リリースノートを確認
2. 変更されたノードをリストアップ
3. 該当ガイドのソースコード照合
4. プロパティ表とサンプルフローを更新
5. 検証（JSON構文、インポートテスト）
6. コミット・デプロイ

**影響を受けやすいノード**:
- Inject, Debug（頻繁に機能追加）
- Function（ランタイム変更）
- HTTP関連（セキュリティ強化）

### Dashboard 2.0更新時の対応

**手順**:
1. FlowFuseリポジトリのリリースノートを確認
2. 新規ウィジェット・機能をチェック
3. 既存ガイドの更新が必要か判断
4. 新規ガイド作成が必要か判断
5. Config Nodeのプロパティ変更を確認

**確認方法**:
```bash
# Dashboard 2.0の最新リリースを確認
curl https://api.github.com/repos/FlowFuse/node-red-dashboard/releases/latest
```

### 問題発見時の対応フロー

```
問題発見
  ↓
AUDIT-REPORTに記録（重大度を付与）
  ↓
優先度に応じて対応
  ├── CRITICAL: 即座に修正
  ├── HIGH: 1週間以内に修正
  ├── MEDIUM: 1ヶ月以内に修正
  └── LOW: 次回監査時に修正
  ↓
修正実施（PROCEDUREに従う）
  ↓
検証（JSON、ソースコード照合、インポートテスト）
  ↓
AUDIT-REPORTの問題ステータスを更新
  ↓
コミット・デプロイ
```

---

## 付録

### 便利なコマンド集

**JSON検証（一括）**:
```bash
#!/bin/bash
for file in nodered-*-guide.html; do
    echo "Validating $file..."
    python3 -c "import json, sys; json.loads(sys.stdin.read())" < \
        <(grep -Pzo '(?<=<textarea[^>]*>).*?(?=</textarea>)' "$file") 2>&1
done
```

**プロパティ表の抽出**:
```bash
# 特定のガイドからプロパティ表を抽出
grep -A 100 '<h3>📋 設定項目一覧</h3>' nodered-inject-node-guide.html | \
    grep -B 100 '</table>' | head -n -1
```

**Node-REDソースコードの取得**:
```bash
# Injectノードのソース
curl -o inject-source.html \
    https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html
```

### 外部リソース

**Node-RED公式**:
- ドキュメント: https://nodered.org/docs/
- GitHub: https://github.com/node-red/node-red
- フォーラム: https://discourse.nodered.org/

**Dashboard 2.0**:
- ドキュメント: https://dashboard.flowfuse.com/
- GitHub: https://github.com/FlowFuse/node-red-dashboard

**検証ツール**:
- JSONLint: https://jsonlint.com/
- JSON Formatter: https://jsonformatter.org/

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-02-16 | 1.0.0 | 初版作成 |

---

**作成者**: Claude Sonnet 4.5
**最終更新**: 2026-02-16
