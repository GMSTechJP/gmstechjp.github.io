# ガイドファイル監査レポート

**監査日**: 2026-01-24
**監査基準**: `PROCEDURE-standard-nodes-audit.md`

---

## 監査概要

`PROCEDURE-standard-nodes-audit.md`に定義された監査手順に基づき、リポジトリ内の全ガイドファイルを対象に以下の観点で監査を実施した。

### 監査基準
1. **プロパティ表**: ソースコードの`defaults`オブジェクトと一致しているか
2. **フローJSON構文**: JSONとして正常にパース可能か
3. **フローJSONプロパティ**: defaults内プロパティの網羅性・不要プロパティの有無
4. **設定ノード**: Config Nodeのプロパティ完全性
5. **構造的整合性**: tabノード・zプロパティの有無

---

## 対象ファイル一覧と監査状況

### 既監査済み（手順書の完了記録より）— 14ファイル

| ファイル | ノード | 状態 |
|---------|--------|------|
| nodered-inject-node-guide.html | Inject | 修正済み |
| nodered-debug-node-guide.html | Debug | 修正済み |
| nodered-sort-node-guide.html | Sort | 修正済み |
| nodered-range-node-guide.html | Range | 修正済み |
| nodered-delay-node-guide.html | Delay | 修正済み |
| nodered-filter-node-guide.html | Filter (RBE) | 修正済み |
| nodered-http-request-node-guide.html | HTTP Request | 修正済み |
| nodered-json-node-guide.html | JSON | 修正済み |
| nodered-yaml-node-guide.html | YAML | 修正済み |
| nodered-template-node-guide.html | Template | 修正済み |
| nodered-html-node-guide.html | HTML | 修正済み |
| nodered-dashboard2-widgets-display.html | Display widgets | 修正済み |
| nodered-dashboard2-widgets-input.html | Input widgets | 修正済み |
| nodered-dashboard2-widgets-visualization.html | Visualization widgets | 修正済み |

### 今回監査実施 — 25ファイル

**標準ノード（21ファイル）:**
- Common: comment, complete/status, link, catch
- Function: change, switch, function, trigger, exec
- Sequence: split, join, batch
- Parser: csv, xml
- Storage: file, watch
- Network: http-in/response, websocket, mqtt, tcp, udp

**Dashboard 2.0（4ファイル）:**
- Advanced Part1 (ui-template)
- Advanced Part2 (ui-control, ui-spacer)
- Layout
- Overview

---

## 問題一覧（重大度別）

### CRITICAL（致命的）— 3件

| # | ファイル | ブロック | 問題内容 |
|---|---------|---------|---------|
| 1 | `nodered-http-in-response-node-guide.html` | メインサンプル | **無効なJSON**: templateノードのtemplate値にリテラル改行文字が含まれる（フローティングホームボタンHTMLの混入） |
| 2 | `nodered-websocket-node-guide.html` | メインサンプル | **無効なJSON**: templateノードのtemplate値にリテラル改行文字が含まれる（フローティングホームボタンHTMLの混入） |
| 3 | `nodered-xml-node-guide.html` | 演習1 | **無効なJSON**: Cloudflareメール保護がtemplateノード内のメールアドレスを書き換え、JSONが壊れている |

### HIGH（重大）— 8件（すべてnodered-dashboard2-overview.html）

| # | ファイル | 問題内容 |
|---|---------|---------|
| 4 | `nodered-dashboard2-overview.html` | ui-button に `tooltip: ""` が存在（削除すべき） |
| 5 | `nodered-dashboard2-overview.html` | ui-group に `groupType` プロパティが不足 |
| 6 | `nodered-dashboard2-overview.html` | ui-page に `visible` プロパティが不足 |
| 7 | `nodered-dashboard2-overview.html` | ui-page に `disabled` プロパティが不足 |
| 8 | `nodered-dashboard2-overview.html` | ui-base に `headerContent` プロパティが不足 |
| 9 | `nodered-dashboard2-overview.html` | ui-base に `navigationStyle` プロパティが不足 |
| 10 | `nodered-dashboard2-overview.html` | ui-base に `titleBarStyle` プロパティが不足 |
| 11 | `nodered-dashboard2-overview.html` | ui-theme の `sizes` に `density` が不足 |

### MEDIUM（中程度）— 10件

| # | ファイル | 問題内容 |
|---|---------|---------|
| 12 | `nodered-dashboard2-widgets-advanced-part2-control-spacer.html` | ui-spacer に `tooltip: ""` が存在（削除すべき） |
| 13 | `nodered-dashboard2-layout.html` | 演習4の ui-text-input に `tooltip: ""` が存在（削除すべき） |
| 14 | `nodered-xml-node-guide.html` | プロパティ表とJSONに `multi, attrkey, charkey, indent` の4プロパティが不足 |
| 15 | `nodered-change-node-guide.html` | 全changeノードに非推奨プロパティ（`action`, `property`, `from`, `to`, `reg`）が残存 |
| 16 | `nodered-function-node-guide.html` | 全functionノードに非推奨プロパティ `noerr` が残存 |
| 17 | `nodered-join-node-guide.html` | 全splitノードに `property` プロパティが不足 |
| 18 | `nodered-batch-node-guide.html` | 演習5のsplitノードに `property` プロパティが不足 |
| 19 | `nodered-batch-node-guide.html` | `count`, `overlap`, `interval` の型が文字列/数値で不統一 |
| 20 | `nodered-catch-node-guide.html` | 演習フロー(4ブロック)にtabノードとzプロパティが不足 |
| 21 | `nodered-watch-node-guide.html` | 演習フロー(4ブロック)にtabノードとzプロパティが不足 |

### LOW（軽微）— 6件

| # | ファイル | 問題内容 |
|---|---------|---------|
| 22 | `nodered-change-node-guide.html` | `onlyset` プロパティがdefaultsに存在するがJSONに含まれていない |
| 23 | `nodered-complete-status-node-guide.html` | Completeノードに `uncaught` プロパティが含まれている（Catchノード用） |
| 24 | `nodered-link-node-guide.html` | Link Callの `linkType` プロパティがプロパティ表に未記載 |
| 25 | `nodered-trigger-node-guide.html` | 補助functionノードに `libs`, `timeout` 等が不足（最小表記） |
| 26 | `nodered-csv-node-guide.html` | `skip` が数値でなく文字列型で格納 |
| 27 | `nodered-dashboard2-overview.html` | プロパティ表にui-theme の Density、ui-page の visible/disabled が未記載 |

---

## カテゴリ別詳細結果

### 標準ノード — Common（4ファイル）

| ファイル | JSONブロック数 | JSON有効 | 問題数 |
|---------|:---:|:---:|:---:|
| comment-node-guide | 5 | 5/5 | 0 |
| complete-status-node-guide | 4 | 4/4 | 1 (LOW) |
| link-node-guide | 5 | 5/5 | 1 (LOW) |
| catch-node-guide | 5 | 5/5 | 1 (MEDIUM) |

### 標準ノード — Function（5ファイル）

| ファイル | JSONブロック数 | JSON有効 | 問題数 |
|---------|:---:|:---:|:---:|
| change-node-guide | 5 | 5/5 | 2 (MEDIUM+LOW) |
| switch-node-guide | 5 | 5/5 | 0 |
| function-node-guide | 5 | 5/5 | 1 (MEDIUM) |
| trigger-node-guide | 5 | 5/5 | 1 (LOW) |
| exec-node-guide | 5 | 5/5 | 0 |

### 標準ノード — Sequence（3ファイル）

| ファイル | JSONブロック数 | JSON有効 | 問題数 |
|---------|:---:|:---:|:---:|
| split-node-guide | 5 | 5/5 | 0 |
| join-node-guide | 5 | 5/5 | 1 (MEDIUM) |
| batch-node-guide | 5 | 5/5 | 2 (MEDIUM) |

### 標準ノード — Parser（2ファイル）

| ファイル | JSONブロック数 | JSON有効 | 問題数 |
|---------|:---:|:---:|:---:|
| csv-node-guide | 5 | 5/5 | 1 (LOW) |
| xml-node-guide | 5 | 4/5 | 2 (CRITICAL+MEDIUM) |

### 標準ノード — Storage（2ファイル）

| ファイル | JSONブロック数 | JSON有効 | 問題数 |
|---------|:---:|:---:|:---:|
| file-node-guide | 5 | 5/5 | 0 |
| watch-node-guide | 5 | 5/5 | 1 (MEDIUM) |

### 標準ノード — Network（5ファイル）

| ファイル | JSONブロック数 | JSON有効 | 問題数 |
|---------|:---:|:---:|:---:|
| http-in-response-node-guide | 5 | 4/5 | 1 (CRITICAL) |
| websocket-node-guide | 5 | 4/5 | 1 (CRITICAL) |
| mqtt-node-guide | 5 | 5/5 | 0 |
| tcp-node-guide | 5 | 5/5 | 0 |
| udp-node-guide | 5 | 5/5 | 0 |

### Dashboard 2.0（4ファイル）

| ファイル | JSONブロック数 | JSON有効 | 問題数 |
|---------|:---:|:---:|:---:|
| advanced-part1-template | 5 | 5/5 | 0 |
| advanced-part2-control-spacer | 1 | 1/1 | 1 (MEDIUM) |
| layout | 5 | 5/5 | 1 (MEDIUM) |
| overview | 1 | 1/1 | 9 (HIGH×8+LOW×1) |

---

## 問題パターンの分析

### パターン1: フローティングホームボタンHTMLの混入（CRITICAL）

**該当**: http-in/response, websocket

templateノードの`template`プロパティ値にページのフローティングホームボタンHTML（`<a href="index.html" ...>`）が混入し、JSON文字列内にリテラル改行が含まれている。これによりJSONとしてパース不可能となり、ユーザーはフローをインポートできない。

**修正方針**: templateノードのtemplate値から不要なHTMLを除去し、改行を`\n`エスケープに統一する。

### パターン2: Cloudflareメール保護による破損（CRITICAL）

**該当**: xml

Cloudflareのメール保護機能がフローJSON内のメールアドレス（`yamada@example.com`）を検出し、`<a href="/cdn-cgi/l/email-protection" ...>`に置換している。これによりJSONが破壊されている。

**修正方針**: メールアドレスを含まない形式にサンプルを変更するか、Cloudflareの保護対象外にする。

### パターン3: Dashboard 2.0 Config Nodeプロパティ不足（HIGH）

**該当**: overview

`nodered-dashboard2-overview.html`のHello DashboardサンプルフローのConfig Nodeが大幅にプロパティ不足。他のDashboard 2.0ガイド（display, input, visualization, advanced-part1）では修正済み。

### パターン4: tooltip残存（MEDIUM）

**該当**: overview, advanced-part2, layout

Dashboard 2.0のソースでコメントアウトされている`tooltip`プロパティがフローJSONに残存。

### パターン5: 非推奨プロパティの残存（MEDIUM）

**該当**: change, function

- changeノード: 旧形式のトップレベルフィールド（`action`, `property`, `from`, `to`, `reg`）
- functionノード: 旧バージョン用の `noerr` プロパティ

### パターン6: tabノード・zプロパティ不足（MEDIUM）

**該当**: catch, watch

演習フローにtabノードが含まれず、各ノードに`z`プロパティがない。インポート時に現在のタブに配置されてしまう。

---

## 手順書に未記載のファイル

以下のファイルは手順書の対象一覧に含まれていないが、リポジトリに存在する。

| ファイル | 内容 | 監査対象候補 |
|---------|------|:---:|
| `nodered-function-node2-javascript-guide.html` | Function Node JavaScript解説 | - |
| `nodered-base64-node-guide.html` | Base64ノード（サードパーティ） | ○ |
| `nodered-email-node-guide.html` | Emailノード（サードパーティ） | ○ |
| `nodered-dashboard2-ui-led-guide.html` | LEDウィジェット（サードパーティ） | ○ |
| `nodered-variable-types-guide.html` | 変数型解説 | - |
| `nodered-javascript-operators-guide.html` | JavaScript演算子解説 | - |
| `nodered-settings-guide.html` | settings.js設定解説 | - |
| `nodered-windows-install-guide.html` | Windowsインストール | - |
| `nodered-raspberry-pi-install-guide.html` | Raspberry Piインストール | - |
| `nodered-overview.html` | Node-RED概要 | - |

---

## 統計サマリー

| 項目 | 数値 |
|------|:---:|
| 監査対象ファイル数 | 25 |
| JSONブロック総数 | 116 |
| JSON有効数 | 113/116 (97.4%) |
| JSON無効数（CRITICAL） | 3 |
| 問題総数 | 27 |
| CRITICAL | 3 |
| HIGH | 8 |
| MEDIUM | 10 |
| LOW | 6 |
| 問題なしファイル数 | 10/25 (40%) |

---

## 推奨対応優先度

### 優先度1（即時対応推奨）
- [ ] `nodered-http-in-response-node-guide.html` — メインサンプルJSON修正
- [ ] `nodered-websocket-node-guide.html` — メインサンプルJSON修正
- [ ] `nodered-xml-node-guide.html` — 演習1 JSON修正（Cloudflare対策）

### 優先度2（早期対応推奨）
- [ ] `nodered-dashboard2-overview.html` — Config Nodeプロパティ追加・tooltip削除（8件）
- [ ] `nodered-dashboard2-widgets-advanced-part2-control-spacer.html` — tooltip削除
- [ ] `nodered-dashboard2-layout.html` — tooltip削除

### 優先度3（定期メンテナンス時）
- [ ] `nodered-xml-node-guide.html` — 不足プロパティ追加（multi, attrkey, charkey, indent）
- [ ] `nodered-catch-node-guide.html` — 演習フローにtab/z追加
- [ ] `nodered-watch-node-guide.html` — 演習フローにtab/z追加
- [ ] `nodered-change-node-guide.html` — 非推奨プロパティ削除
- [ ] `nodered-function-node-guide.html` — `noerr`プロパティ削除
- [ ] `nodered-join-node-guide.html` — splitノードにproperty追加
- [ ] `nodered-batch-node-guide.html` — 型統一・property追加
