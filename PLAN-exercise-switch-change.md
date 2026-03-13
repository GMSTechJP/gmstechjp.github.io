# 演習問題のFunctionノード → Switch/Changeノード置き換え計画

## 他端末での作業引き継ぎ方法

1. このプランファイルをプロジェクトの `.claude/plans/` にコピーしてコミット・push
2. 他端末で `git pull` 後、Claude Codeに「`.claude/plans/scalable-enchanting-shore.md` のプランに基づいて作業して」と指示
3. 作業完了後、`.claude/plans/` 内のプランファイルを削除してコミット

## Context
Pi Sense HATガイドの演習2で、Functionノード（JavaScript）をSwitch+Changeノードに置き換えたところ、よりNode-REDらしいビジュアルフローになった。同様の改善を他のガイドにも適用したい。

Functionノードガイド（function-node-guide, function-node2-javascript-guide）および、ループ・コンテキスト変数・エラー生成・バイナリ操作など複雑なロジックが必要な演習は対象外とする。

## 置き換え対象（明確にSwitch/Changeで実現可能なもの）

### 優先度A: 単純な値設定・プロパティ操作（Change単体で可能）

| # | ファイル | 演習 | 現在のFunction内容 | 置き換え方法 |
|---|---------|------|-------------------|-------------|
| 1 | `nodered-udp-node-guide.html` | 演習2: 送信元への返信（初級） | 文字列の先頭追加 | Change: payload設定 |
| 2 | `nodered-websocket-node-guide.html` | 演習3: ブロードキャスト配信（中級） | `delete msg._session` | Change: deleteルール |
| 3 | `nodered-exec-node-guide.html` | 演習2: システム日時の取得（初級） | `msg.payload.trim()` | Change: JSONata `$trim()` |
| 4 | `nodered-split-node-guide.html` | 演習4: Split+Joinで配列を加工（中級） | `msg.payload.toUpperCase()` | Change: JSONata `$uppercase()` |
| 5 | `nodered-xml-node-guide.html` | 演習2: オブジェクトからXML生成（初級） | オブジェクト構築 | Change: JSONで値設定 |
| 6 | `nodered-yaml-node-guide.html` | 演習2: オブジェクトからYAML生成（初級） | オブジェクト構築 | Change: JSONで値設定 |

### 優先度B: 条件分岐+値設定（Switch+Changeの組み合わせ）

| # | ファイル | 演習 | 現在のFunction内容 | 置き換え方法 |
|---|---------|------|-------------------|-------------|
| 7 | `nodered-dashboard2-ui-led-guide.html` | 演習2: 温度センサーの3段階表示（中級） | 温度範囲→"低"/"中"/"高"マッピング | Switch(範囲判定)+Change×3 |
| 8 | `nodered-split-node-guide.html` | 演習3: オブジェクトの分割と集計（中級） | キー名と値の文字列結合 | Change: JSONata template |
| 9 | `nodered-watch-node-guide.html` | 演習3: 画像ファイルの自動検出（中級） | 拡張子フィルタリング+ログ整形 | Switch(拡張子判定)+Change |
| 10 | `nodered-xml-node-guide.html` | 演習3: 属性付きXMLの処理（中級） | ネストプロパティアクセス | Change: JSONata式 |
| 11 | `nodered-yaml-node-guide.html` | 演習3: ネストした設定の取得（中級） | ネストプロパティアクセス | Change: JSONata式 |
| 12 | `nodered-yaml-node-guide.html` | 演習4: 配列を含むYAML（上級） | 配列長取得 | Change: JSONata `$count()` |

## 対象外（Functionノードが適切なもの）

以下は複雑なロジックが必要でSwitch/Changeでは不適切：
- ループ処理（batch, split演習のメッセージ生成）
- コンテキスト変数管理（email, trigger, watch演習）
- エラー生成（catch演習）
- バイナリ操作（base64演習）
- 日時フォーマット・乱数生成（inject, mqtt, tcp演習）
- CRUD API実装（http演習）
- JavaScript学習目的の演習（javascript-operators-guide, function-node2-javascript-guide）

## 修正方針

各演習について：
1. **ヒント文**: Functionノードの記述 → Switch/Changeノードの記述に変更
2. **解答フローJSON**: Functionノード → Switch/Changeノード（+必要に応じてJunction）に置き換え
3. **演習の難易度・成功条件**: 変更なし（機能的に同等のため）

## 修正対象ファイル一覧（9ファイル・12演習）

1. `nodered-udp-node-guide.html`
2. `nodered-websocket-node-guide.html`
3. `nodered-exec-node-guide.html`
4. `nodered-split-node-guide.html`（2演習）
5. `nodered-xml-node-guide.html`（2演習）
6. `nodered-yaml-node-guide.html`（3演習）
7. `nodered-dashboard2-ui-led-guide.html`
8. `nodered-watch-node-guide.html`

## 検証方法

- 各フローJSONが `JSON.parse()` でエラーなくパースできること
- ノード間のwires接続が正しいこと
- tabノード・zプロパティが含まれていること
