# Node-RED ノードガイド 手順書

## 概要

Node-REDノードガイド（標準ノード、Dashboard 2.0ウィジェット、サードパーティノード）の作成および監査に関する手順書。

---

## 1. ガイドを新たに追加する手順

### 1.1 対象ノードの特定

新規ガイドを作成する場合、まず対象ノードのカテゴリを特定する。

#### 標準ノード

| カテゴリ | ソースパス | 含まれるノード |
|---------|------|--------------|
| common | `core/common/` | inject, debug, complete, status, catch, link-*, comment |
| function | `core/function/` | function, switch, change, template, delay, trigger, range, filter(rbe), exec |
| sequence | `core/sequence/` | split, join, sort, batch |
| parsers | `core/parsers/` | json, xml, yaml, csv, html |
| storage | `core/storage/` | file, file-in, watch |
| network | `core/network/` | http-in, http-response, http-request, websocket-*, mqtt-*, tcp-*, udp-* |

#### Dashboard 2.0

| カテゴリ | ソースパス |
|---------|------|
| Config Nodes | `nodes/config/ui_<name>.html` |
| Widgets | `nodes/widgets/ui_<name>.html` |

#### サードパーティノード

1. npmjs.com で当該パッケージを検索
2. パッケージページのリポジトリリンクからGitHubリポジトリを確認
3. リポジトリ内のノード定義HTML（通常 `nodes/` や `src/` 配下）を参照

---

### 1.2 ソースコードの取得

#### 標準ノード

**リポジトリ**: https://github.com/node-red/node-red

各ノードのエディタ定義HTMLファイルの場所：

```
packages/node_modules/@node-red/nodes/core/<カテゴリ>/<ノード名>.html
```

取得例：

```bash
# Raw URLパターン（例：injectノード）
https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html

# GitHub Web UI
https://github.com/node-red/node-red/blob/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html
```

#### Dashboard 2.0

**リポジトリ**: https://github.com/FlowFuse/node-red-dashboard.git

取得例：

```bash
# Config Node（例：ui-base）
https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_base.html

# Widget（例：ui-button）
https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/widgets/ui_button.html
```

---

### 1.3 プロパティの抽出と分類

ソースコードのエディタHTML内で以下の3つを確認し、プロパティを分類する。

#### `defaults`オブジェクトの確認

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

#### エディタフォーム要素の確認

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

#### 分類結果と対応

| 分類 | 条件 | プロパティ表 | フローJSON |
|------|------|-------------|-----------|
| **アクティブ** | defaults内 かつ フォーム要素あり（有効） | ✅ 記載する | ✅ 含める |
| **コメントアウト済み** | defaults内 だがフォーム要素がコメントアウト | ❌ 記載しない | ❌ 含めない |
| **エディタ非表示** | defaults内 だがフォーム要素が存在しない | ❌ 記載しない | ✅ 含める |
| **存在しない** | defaultsに定義なし | ❌ 記載しない | ❌ 含めない |

> **標準ノードの場合**: 「コメントアウト済み」のケースはほぼ存在しない。
> 標準ノードは成熟しているため「存在しない」プロパティの誤記が主な問題となる。

> **Dashboard 2.0の場合**: 「コメントアウト済み」のケースが多く存在する（例：tooltip）。
> 開発途中のプロパティがエディタHTMLに残されているため、これらの判定が重要。

---

### 1.4 ガイドファイルの作成

#### プロパティ表の作成

「アクティブ」に分類されたプロパティのみをHTMLテーブルに記載する。

#### サンプルフローの作成

1. 「アクティブ」と「エディタ非表示」のプロパティをすべてフローJSONに含める
2. 設定ノード（Config Node）がある場合、そのプロパティも網羅する
3. tabノードを含め、各ノードに`z`プロパティを設定する
4. 複数出力ノードの場合、`wires`配列のサイズが`outputs`と一致することを確認する

#### 演習フローの作成

サンプルフローと同様のルールで、演習用のフローJSONを作成する。

---

### 1.5 ノードタイプ別の注意事項（作成時）

#### 標準ノード

1. **ノードバージョン**: 最新の`master`ブランチのソースを参照すること
2. **設定ノード**: `mqtt-broker`, `websocket-listener`等はx/y座標を持たない
3. **複数出力ノード**: switch等は`outputs`と`wires`のサイズを一致させる
4. **`propertyType`系**: TypedInputでは`property`と`propertyType`がペアで存在する
5. **動的プロパティ**: switchの`rules`等は`defaults`に配列として定義される

#### Dashboard 2.0

1. **Config Nodes**: ui-base, ui-theme, ui-group, ui-pageのプロパティを網羅する
2. **コメントアウト済みプロパティ**: tooltip等のコメントアウト状態を必ず確認する
3. **`topicType`**: ソースでは`"msg"`だがフロー内で`"str"`の場合は使い方次第で正しい可能性がある

---

### 1.6 コミットメッセージ規則

```
<ノード名>ガイドを追加

- <変更内容の箇条書き>
```

例：
```
injectノードガイドを追加

- プロパティ表にアクティブなプロパティを記載
- サンプルフロー×1を作成
- 演習フロー×4を作成
```

---

## 2. ガイドファイルの監査手順

### 2.1 対象ファイル一覧

#### 標準ノード（32ガイド）

##### Common（共通）— 6ノード

| ファイル | ノード |
|---------|--------|
| `nodered-inject-node-guide.html` | Inject |
| `nodered-debug-node-guide.html` | Debug |
| `nodered-comment-node-guide.html` | Comment |
| `nodered-complete-status-node-guide.html` | Complete / Status |
| `nodered-link-node-guide.html` | Link In / Out / Call |
| `nodered-catch-node-guide.html` | Catch |

##### Function（機能）— 9ノード

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

##### Sequence（シーケンス）— 4ノード

| ファイル | ノード |
|---------|--------|
| `nodered-split-node-guide.html` | Split |
| `nodered-join-node-guide.html` | Join |
| `nodered-sort-node-guide.html` | Sort |
| `nodered-batch-node-guide.html` | Batch |

##### Parser（パーサー）— 5ノード

| ファイル | ノード |
|---------|--------|
| `nodered-json-node-guide.html` | JSON |
| `nodered-csv-node-guide.html` | CSV |
| `nodered-html-node-guide.html` | HTML |
| `nodered-xml-node-guide.html` | XML |
| `nodered-yaml-node-guide.html` | YAML |

##### Storage（ストレージ）— 2ノード

| ファイル | ノード |
|---------|--------|
| `nodered-file-node-guide.html` | Write File / Read File |
| `nodered-watch-node-guide.html` | Watch |

##### Network（ネットワーク）— 6ノード

| ファイル | ノード |
|---------|--------|
| `nodered-http-request-node-guide.html` | HTTP Request |
| `nodered-http-in-response-node-guide.html` | HTTP In / Response |
| `nodered-websocket-node-guide.html` | WebSocket |
| `nodered-mqtt-node-guide.html` | MQTT |
| `nodered-tcp-node-guide.html` | TCP |
| `nodered-udp-node-guide.html` | UDP |

#### Dashboard 2.0（7ガイド）

| ファイル | 内容 |
|---------|------|
| `nodered-dashboard2-overview.html` | Dashboard 2.0 概要 |
| `nodered-dashboard2-widgets-display.html` | 表示系ウィジェット |
| `nodered-dashboard2-widgets-input.html` | 入力系ウィジェット |
| `nodered-dashboard2-widgets-visualization.html` | 可視化ウィジェット |
| `nodered-dashboard2-widgets-advanced-part1-template.html` | 上級編 Part1（ui-template） |
| `nodered-dashboard2-widgets-advanced-part2-control-spacer.html` | 上級編 Part2（ui-control, ui-spacer） |
| `nodered-dashboard2-layout.html` | レイアウト |

---

### 2.2 監査作業手順

#### Step 1: ソースコードの取得

対象ノードのGitHubリポジトリから、エディタHTMLファイルを取得する。

- **標準ノード**: `https://github.com/node-red/node-red` → `packages/node_modules/@node-red/nodes/core/<category>/<node>.html`
- **Dashboard 2.0**: `https://github.com/FlowFuse/node-red-dashboard.git` → `nodes/widgets/ui_<name>.html` または `nodes/config/ui_<name>.html`
- **サードパーティ**: 各パッケージのGitHubリポジトリを参照

#### Step 2: `defaults`オブジェクトの抽出

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

#### Step 3: フォーム要素の確認

`<script type="text/html" data-template-name="ノード名">` セクション内で、各プロパティに対応するフォーム要素を確認する。

#### Step 4: ガイドファイルのプロパティ表を監査

ガイドHTMLの `<table>` 内のプロパティ一覧を確認し、Step 2-3の結果と比較する。

**確認ポイント：**
- プロパティ表にdefaultsに存在しないプロパティがないか
- エディタ非表示のプロパティがテーブルに含まれていないか
- コメントアウト済みのプロパティがテーブルに含まれていないか（Dashboard 2.0）

#### Step 5: サンプルフローの監査

`<div class="flow-json">` 内の `<textarea>` に格納されたJSONフローを確認する。

**確認ポイント：**
- ノードJSONにdefaultsに存在しないプロパティがないか
- defaults内のプロパティで不足しているものがないか
- 値のデフォルト値が正しいか

#### Step 6: 演習フローの監査

演習セクション内のフローJSONも同様に確認する。

#### Step 7: 修正の実施

問題を発見したら、セクション1.3の分類原則に従って修正する。

---

### 2.3 ノードタイプ別の注意事項（監査時）

#### 標準ノード特有の注意事項

1. **ノードバージョンによるプロパティ差異**: Node-REDのバージョンによってプロパティが追加・変更されることがある。最新の`master`ブランチのソースを参照すること。

2. **設定ノード（config node）のパターン**: フロー上にx/y座標を持たない：
```json
{
    "id": "broker1",
    "type": "mqtt-broker",
    "name": "Local MQTT",
    "broker": "localhost",
    "port": "1883"
}
```

3. **複数出力ノード**: `wires`配列のサイズが`outputs`と一致していることを確認する：
```json
{
    "type": "switch",
    "outputs": 3,
    "wires": [["node1"], ["node2"], ["node3"]]
}
```

4. **`propertyType`系プロパティ**: `property`と`propertyType`がペアで存在することが多い：
```json
{
    "type": "switch",
    "property": "payload",
    "propertyType": "msg"
}
```

5. **動的に生成されるプロパティ**: switchの`rules`、changeの`rules`等は`defaults`に配列として定義されるが、フォーム要素は動的に生成される。

#### Dashboard 2.0 特有の注意事項

1. **Config Nodesの不足プロパティ**: よく見落とされるプロパティ：

| Config Node | よく不足するプロパティ |
|-------------|---------------------|
| ui-base | `headerContent`, `navigationStyle`, `titleBarStyle`, `showPageTitle` |
| ui-theme | `density`（sizes内） |
| ui-group | `groupType` |
| ui-page | `className`, `visible`, `disabled` |

2. **コメントアウト済みプロパティの典型例**:

| ウィジェット | コメントアウト済みプロパティ |
|-------------|--------------------------|
| ui-button | tooltip |
| ui-slider | tooltip |
| ui-dropdown | tooltip |

3. **topicType**: ソースdefaultsでは`"msg"`だがフロー内で`"str"`の場合、実際の使い方次第で正しい可能性がある。修正は保留とする。

---

### 2.4 JSON修正パターン集

#### パターン1: 不要プロパティの削除

```
修正前:
    "tooltip": "",
    "order": 1,

修正後:
    "order": 1,
```

#### パターン2: 不足プロパティの追加

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

#### パターン3: 設定ノードのプロパティ補完

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

#### パターン4: Dashboard Config Nodeのプロパティ補完

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

### 2.5 チェックリスト（各ファイル監査時）

- [ ] ソースコードの `defaults` オブジェクトを確認した
- [ ] エディタHTMLのフォーム要素を確認した
- [ ] プロパティ表の不要行を削除した
- [ ] サンプルフローの不要プロパティを削除した
- [ ] サンプルフローの不足プロパティを追加した
- [ ] 演習フローの不要プロパティを削除した
- [ ] 演習フローの不足プロパティを追加した
- [ ] 設定ノードのプロパティを確認した（該当する場合）
- [ ] JSONの構文が正しいことを確認した（カンマ、括弧）
- [ ] tabノードとzプロパティが含まれていることを確認した
- [ ] コミットしてプッシュした

---

### 2.6 技術的な注意事項

#### JSON修正時の挿入位置

1. **ウィジェットノード（x, y, wiresあり）**: プロパティは `"x":` の直前に追加
2. **Config Nodes（x, y, wiresなし）**: プロパティは閉じ括弧 `}` の前に追加
3. **コンパクト形式（1行JSON）**: 既存プロパティの後に `,` で区切って挿入
4. **replace_all活用**: 同一パターンのConfig Nodes（ui-base, ui-theme等）は `replace_all` で一括修正可能

#### コミットメッセージ規則（監査修正時）

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
