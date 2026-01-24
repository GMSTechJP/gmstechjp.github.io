# Node-RED ノードガイド プロパティ監査手順書

## 概要

Node-REDノードガイド（標準ノードおよびDashboard 2.0ウィジェット）のプロパティ表・フローJSONを、ソースコードの`defaults`オブジェクトおよびエディタHTMLテンプレートを基準に監査・修正するための手順書。

---

## 対象ファイル一覧

### 標準ノード（32ガイド）

#### Common（共通）— 6ノード

| ファイル | ノード |
|---------|--------|
| `nodered-inject-node-guide.html` | Inject |
| `nodered-debug-node-guide.html` | Debug |
| `nodered-comment-node-guide.html` | Comment |
| `nodered-complete-status-node-guide.html` | Complete / Status |
| `nodered-link-node-guide.html` | Link In / Out / Call |
| `nodered-catch-node-guide.html` | Catch |

#### Function（機能）— 9ノード

| ファイル | ノード |
|---------|--------|
| `nodered-change-node-guide.html` | Change |
| `nodered-switch-node-guide.html` | Switch |
| `nodered-delay-node-guide.html` | Delay |
| `nodered-function-node-guide.html` | Function |
| `nodered-template-node-guide.html` | Template |
| `nodered-trigger-node-guide.html` | Trigger |
| `nodered-range-node-guide.html` | Range |
| `nodered-exec-node-guide.html` | Exec |
| `nodered-filter-node-guide.html` | Filter (RBE) |

#### Sequence（シーケンス）— 4ノード

| ファイル | ノード |
|---------|--------|
| `nodered-split-node-guide.html` | Split |
| `nodered-join-node-guide.html` | Join |
| `nodered-sort-node-guide.html` | Sort |
| `nodered-batch-node-guide.html` | Batch |

#### Parser（パーサー）— 5ノード

| ファイル | ノード |
|---------|--------|
| `nodered-json-node-guide.html` | JSON |
| `nodered-csv-node-guide.html` | CSV |
| `nodered-html-node-guide.html` | HTML |
| `nodered-xml-node-guide.html` | XML |
| `nodered-yaml-node-guide.html` | YAML |

#### Storage（ストレージ）— 2ノード

| ファイル | ノード |
|---------|--------|
| `nodered-file-node-guide.html` | Write File / Read File |
| `nodered-watch-node-guide.html` | Watch |

#### Network（ネットワーク）— 6ノード

| ファイル | ノード |
|---------|--------|
| `nodered-http-request-node-guide.html` | HTTP Request |
| `nodered-http-in-response-node-guide.html` | HTTP In / Response |
| `nodered-websocket-node-guide.html` | WebSocket |
| `nodered-mqtt-node-guide.html` | MQTT |
| `nodered-tcp-node-guide.html` | TCP |
| `nodered-udp-node-guide.html` | UDP |

---

### Dashboard 2.0（7ガイド）

| ファイル | 内容 |
|---------|------|
| `nodered-dashboard2-overview.html` | Dashboard 2.0 概要 |
| `nodered-dashboard2-widgets-display.html` | 表示系ウィジェット（ui-text, ui-markdown, ui-notification, ui-audio） |
| `nodered-dashboard2-widgets-input.html` | 入力系ウィジェット（ui-button, ui-switch, ui-slider, ui-dropdown, ui-text-input, ui-form, ui-radio-group, ui-button-group） |
| `nodered-dashboard2-widgets-visualization.html` | 可視化ウィジェット（ui-chart, ui-gauge, ui-table, ui-progress） |
| `nodered-dashboard2-widgets-advanced-part1-template.html` | 上級編 Part1（ui-template） |
| `nodered-dashboard2-widgets-advanced-part2-control-spacer.html` | 上級編 Part2（ui-control, ui-spacer） |
| `nodered-dashboard2-layout.html` | レイアウト（Grid, Tabs, Notebook） |

---

## ソースコード参照先

### 標準ノード

**リポジトリ**: https://github.com/node-red/node-red

各ノードのエディタ定義HTMLファイルの場所：

```
packages/node_modules/@node-red/nodes/core/<カテゴリ>/<ノード名>.html
```

#### カテゴリ別パス

| カテゴリ | パス | 含まれるノード |
|---------|------|--------------|
| common | `core/common/` | inject, debug, complete, status, catch, link-*, comment |
| function | `core/function/` | function, switch, change, template, delay, trigger, range, filter(rbe), exec |
| sequence | `core/sequence/` | split, join, sort, batch |
| parsers | `core/parsers/` | json, xml, yaml, csv, html |
| storage | `core/storage/` | file, file-in, watch |
| network | `core/network/` | http-in, http-response, http-request, websocket-*, mqtt-*, tcp-*, udp-* |

#### ソースコード取得例

```bash
# Raw URLパターン（例：injectノード）
https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html

# GitHub Web UI
https://github.com/node-red/node-red/blob/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html
```

---

### Dashboard 2.0

**リポジトリ**: https://github.com/FlowFuse/node-red-dashboard.git

各ウィジェット/設定ノードのエディタHTMLの場所：

```
nodes/config/ui_<name>.html   （Config Nodes: ui-base, ui-theme, ui-group, ui-page）
nodes/widgets/ui_<name>.html  （Widgets: ui-text, ui-button, ui-chart 等）
```

#### ソースコード取得例

```bash
# Config Node（例：ui-base）
https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_base.html

# Widget（例：ui-button）
https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/widgets/ui_button.html
```

---

### サードパーティノード（パッケージ）

サードパーティノードの場合は、各パッケージのGitHubリポジトリを参照する。

**特定方法：**
1. npmjs.com で当該パッケージを検索
2. パッケージページのリポジトリリンクからGitHubリポジトリを確認
3. リポジトリ内のノード定義HTML（通常 `nodes/` や `src/` 配下）を参照

```bash
# 例: node-red-contrib-xxx パッケージ
https://github.com/<owner>/node-red-contrib-xxx
```

---

## プロパティ分類の原則

ソースコードのエディタHTML内で以下の3つを確認し、プロパティを分類する：

### 1. `defaults`オブジェクトの確認

```javascript
RED.nodes.registerType('ノード名', {
    defaults: {
        name: { value: "" },
        property: { value: "payload" },
        // ... これがノードの公式プロパティ定義
    },
    ...
});
```

### 2. エディタフォーム要素の確認

```html
<!-- アクティブ（有効） -->
<div class="form-row">
    <label for="node-input-property">Property</label>
    <input type="text" id="node-input-property">
</div>

<!-- コメントアウト済み（無効化） -->
<!--
<div class="form-row">
    <label for="node-input-someProperty">Some Property</label>
    <input type="text" id="node-input-someProperty">
</div>
-->
```

### 3. 分類結果と対応

| 分類 | 条件 | プロパティ表 | フローJSON |
|------|------|-------------|-----------|
| **アクティブ** | defaults内 かつ フォーム要素あり（有効） | ✅ 記載する | ✅ 含める |
| **コメントアウト済み** | defaults内 だがフォーム要素がコメントアウト | ❌ 削除 | ❌ 削除 |
| **エディタ非表示** | defaults内 だがフォーム要素が存在しない | ❌ 削除 | ✅ 含める |
| **存在しない** | defaultsに定義なし | ❌ 削除 | ❌ 削除 |

> **標準ノードの場合**: 「コメントアウト済み」のケースはほぼ存在しない。
> Dashboard 2.0と異なり、標準ノードは成熟しているため「存在しない」プロパティが
> ガイドに誤記されているケースが主な修正対象となる。

> **Dashboard 2.0の場合**: 「コメントアウト済み」のケースが多く存在する（例：tooltip）。
> 開発途中のプロパティがエディタHTMLに残されているため、これらの判定が重要。

---

## 作業手順

### Step 1: ソースコードの取得

対象ノードのGitHubリポジトリから、エディタHTMLファイルを取得する。

- **標準ノード**: `https://github.com/node-red/node-red` → `packages/node_modules/@node-red/nodes/core/<category>/<node>.html`
- **Dashboard 2.0**: `https://github.com/FlowFuse/node-red-dashboard.git` → `nodes/widgets/ui_<name>.html` または `nodes/config/ui_<name>.html`
- **サードパーティ**: 各パッケージのGitHubリポジトリを参照

### Step 2: `defaults`オブジェクトの抽出

ソースHTMLから `RED.nodes.registerType` を探し、`defaults`オブジェクトのプロパティ一覧を取得する。

```javascript
// 例：inject ノードの defaults
defaults: {
    name: { value: "" },
    props: { value: [...] },
    repeat: { value: "" },
    crontab: { value: "" },
    once: { value: false },
    onceDelay: { value: 0.1 },
    topic: { value: "" },
    payload: { value: "" },
    payloadType: { value: "date" }
}
```

### Step 3: フォーム要素の確認

`<script type="text/html" data-template-name="ノード名">` セクション内で、各プロパティに対応するフォーム要素を確認する。

### Step 4: ガイドファイルのプロパティ表を監査

ガイドHTMLの `<table>` 内のプロパティ一覧を確認し、Step 2-3の結果と比較する。

**確認ポイント：**
- プロパティ表にdefaultsに存在しないプロパティがないか
- エディタ非表示のプロパティがテーブルに含まれていないか
- コメントアウト済みのプロパティがテーブルに含まれていないか（Dashboard 2.0）

### Step 5: サンプルフローの監査

`<div class="flow-json">` 内の `<textarea>` に格納されたJSONフローを確認する。

**確認ポイント：**
- ノードJSONにdefaultsに存在しないプロパティがないか
- defaults内のプロパティで不足しているものがないか
- 値のデフォルト値が正しいか

### Step 6: 演習フローの監査

演習セクション内のフローJSONも同様に確認する。

### Step 7: 修正の実施

問題を発見したら、分類原則に従って修正する。

---

## ノードタイプ別の注意事項

### 標準ノード特有の注意事項

#### 1. ノードバージョンによるプロパティ差異

Node-RED のバージョンによってプロパティが追加・変更されることがある。
最新の `master` ブランチのソースを参照すること。

#### 2. 設定ノード（config node）のパターン

標準ノードにも設定ノードがある（例：`mqtt-broker`, `websocket-listener`）。
設定ノードはフロー上にx/y座標を持たない：

```json
{
    "id": "broker1",
    "type": "mqtt-broker",
    "name": "Local MQTT",
    "broker": "localhost",
    "port": "1883"
    // x, y, wires は持たない
}
```

#### 3. 複数出力ノード

switch、split等は `outputs` プロパティで出力ポート数を制御する。
`wires` 配列のサイズが `outputs` と一致していることを確認する：

```json
{
    "type": "switch",
    "outputs": 3,
    "wires": [["node1"], ["node2"], ["node3"]]
}
```

#### 4. `propertyType` 系プロパティ

標準ノードでは TypedInput ウィジェットを多用する。
`property` と `propertyType` がペアで存在することが多い：

```json
{
    "type": "switch",
    "property": "payload",
    "propertyType": "msg"
}
```

#### 5. 動的に生成されるプロパティ

一部のノードはエディタで動的にプロパティを生成する（例：switchの `rules`、changeの `rules`）。
これらは `defaults` に配列として定義されるが、フォーム要素は動的に生成される。

---

### Dashboard 2.0 特有の注意事項

#### 1. Config Nodes の不足プロパティ

Dashboard 2.0のフローJSONには以下のConfig Nodesが頻出する。これらの不足プロパティに注意：

| Config Node | よく不足するプロパティ |
|-------------|---------------------|
| ui-base | `headerContent`, `navigationStyle`, `titleBarStyle`, `showPageTitle` |
| ui-theme | `density`（sizes内） |
| ui-group | `groupType` |
| ui-page | `className`, `visible`, `disabled` |

#### 2. コメントアウト済みプロパティの典型例

| ウィジェット | コメントアウト済みプロパティ |
|-------------|--------------------------|
| ui-button | tooltip |
| ui-slider | tooltip |
| ui-dropdown | tooltip |

#### 3. topicType に関する注意

`topicType` がソースdefaultsでは `"msg"` だがフロー内で `"str"` になっているケースがある。これは実際の使い方次第で正しい可能性があるため、修正は保留とする。

---

## JSON修正パターン集

### パターン1: 不要プロパティの削除

```
修正前:
    "tooltip": "",
    "order": 1,

修正後:
    "order": 1,
```

### パターン2: 不足プロパティの追加

```
修正前:
    "name": "テスト",
    "width": 0,
    "height": 0

修正後:
    "name": "テスト",
    "width": 0,
    "height": 0,
    "className": ""
```

### パターン3: 設定ノードのプロパティ補完

```
修正前:
  {
    "id": "broker1",
    "type": "mqtt-broker",
    "name": "Local MQTT",
    "broker": "localhost",
    "port": "1883"
  }

修正後:
  {
    "id": "broker1",
    "type": "mqtt-broker",
    "name": "Local MQTT",
    "broker": "localhost",
    "port": "1883",
    "clientid": "",
    "autoConnect": true,
    "usetls": false,
    "protocolVersion": "4",
    "keepalive": "60",
    "cleansession": true
  }
```

### パターン4: Dashboard Config Nodeのプロパティ補完

```
修正前:
  {
    "id": "group1",
    "type": "ui-group",
    "name": "グループ1"
  }

修正後:
  {
    "id": "group1",
    "type": "ui-group",
    "name": "グループ1",
    "groupType": "default"
  }
```

---

## 効率的な作業順序（推奨）

### Phase 1: 標準ノード — Common（6ファイル）

最も使用頻度が高く、影響範囲が大きい。

1. Inject
2. Debug
3. Comment
4. Complete / Status
5. Link In / Out / Call
6. Catch

### Phase 2: 標準ノード — Function（9ファイル）

最もノード数が多いカテゴリ。

1. Change
2. Switch
3. Delay
4. Function
5. Template
6. Trigger
7. Range
8. Exec
9. Filter (RBE)

### Phase 3: 標準ノード — Sequence（4ファイル）

構造が類似しており、まとめて作業しやすい。

1. Split
2. Join
3. Sort
4. Batch

### Phase 4: 標準ノード — Parser（5ファイル）

構造が類似しており、まとめて作業しやすい。

1. JSON
2. CSV
3. HTML
4. XML
5. YAML

### Phase 5: 標準ノード — Storage（2ファイル）

1. Write File / Read File
2. Watch

### Phase 6: 標準ノード — Network（6ファイル）

設定ノードが多く、確認項目が多い。

1. HTTP Request
2. HTTP In / Response
3. WebSocket
4. MQTT
5. TCP
6. UDP

### Phase 7: Dashboard 2.0（7ファイル）

1. Display（表示系ウィジェット）
2. Input（入力系ウィジェット）
3. Visualization（可視化ウィジェット）
4. Advanced Part1（ui-template）
5. Advanced Part2（ui-control, ui-spacer）
6. Layout（レイアウト）
7. Overview（概要）

---

## 完了済み作業記録

### 標準ノード — 完了済み

| コミット | ファイル | 内容 |
|---------|--------|------|
| `9c58033` | inject, sort, range | プロパティ表・サンプルフロー修正 |
| `28fc236` | delay, filter, debug, http-request | プロパティ表修正 |
| `a6955f7` | json, yaml, template | プロパティ表にname行追加 |
| `86e852c` | html | プロパティ表修正 |

### Dashboard 2.0 — 完了済み

#### Display（nodered-dashboard2-widgets-display.html）✅

- サンプルフロー: ui-text/markdown/audioの不足プロパティ追加
- 演習フロー: Config Nodes + 全ウィジェットの不足プロパティ追加
- プロパティ表: 問題なし

#### Input（nodered-dashboard2-widgets-input.html）✅

- サンプルフロー: 不足プロパティ追加 + tooltip削除
- 演習フロー: Config Nodes + 全ウィジェットの不足プロパティ追加
- プロパティ表から削除: ui-button/slider/dropdown のTooltip、ui-switch のStyle、ui-form のPass Through、ui-button-group のAppearance/Selection

#### Visualization（nodered-dashboard2-widgets-visualization.html）✅

- サンプルフロー: 不足プロパティ追加
- 演習フロー: Config Nodes + 全ウィジェットの不足プロパティ追加
- プロパティ表から削除: ui-gauge のStyle Rounded/Glow、ui-table のPass Through、ui-progress のStyle/Show Value/Min/Max

### Dashboard 2.0 — 未完了

#### Advanced Part1（nodered-dashboard2-widgets-advanced-part1-template.html）

- [ ] プロパティ表の調査
- [ ] フロー修正（ui-group groupType追加、ui-base/theme/page/template 不足プロパティ追加）

#### Advanced Part2（nodered-dashboard2-widgets-advanced-part2-control-spacer.html）

- [ ] プロパティ表の調査
- [ ] フロー修正（ui-group groupType追加、ui-base/theme/page/control/spacer 不足プロパティ追加）

#### Layout（nodered-dashboard2-layout.html）

- [ ] プロパティ表の調査
- [ ] フロー修正（ui-group groupType追加、ui-theme/base/page 不足プロパティ追加）

---

## コミットメッセージ規則

```
<ノード名>ガイドのプロパティ表・サンプルフローを修正

- <変更内容の箇条書き>
```

例：
```
injectガイドのプロパティ表・サンプルフローを修正

- プロパティ表からtopic行を削除（エディタ非表示のため）
- サンプルフロー×1に不足プロパティ追加（onceDelay等）
- 演習フロー×4のpropsプロパティを修正
```

---

## チェックリスト（各ファイル作業時）

- [ ] ソースコードの `defaults` オブジェクトを確認した
- [ ] エディタHTMLのフォーム要素を確認した
- [ ] プロパティ表の不要行を削除した
- [ ] サンプルフローの不要プロパティを削除した
- [ ] サンプルフローの不足プロパティを追加した
- [ ] 演習フローの不要プロパティを削除した
- [ ] 演習フローの不足プロパティを追加した
- [ ] 設定ノードのプロパティを確認した（該当する場合）
- [ ] JSONの構文が正しいことを確認した（カンマ、括弧）
- [ ] コミットしてプッシュした

---

## 技術的な注意事項

### JSON修正時のパターン

1. **ウィジェットノード（x, y, wiresあり）**: プロパティは `"x":` の直前に追加
2. **Config Nodes（x, y, wiresなし）**: プロパティは閉じ括弧 `}` の前に追加
3. **コンパクト形式（1行JSON）**: 既存プロパティの後に `,` で区切って挿入
4. **replace_all活用**: 同一パターンのConfig Nodes（ui-base, ui-theme等）は `replace_all` で一括修正可能

### フロー内の値の修正事項

| プロパティ | 誤った値 | 正しい値 | 対象 |
|-----------|---------|---------|------|
| removeOlderUnit | `"60"` | `"3600"` | ui-chart |
| tooltip | `""` (存在) | (削除) | ui-button, ui-slider, ui-dropdown |
