# Node-RED 標準ノード プロパティ監査手順書

## 概要

Dashboard 2.0ウィジェットガイドで実施したプロパティ監査と同じ原則を、Node-RED標準ノードガイドに適用するための手順書。

## 対象ファイル一覧

### コアノード
| ファイル | ノード |
|---------|--------|
| `nodered-inject-node-guide.html` | inject |
| `nodered-debug-node-guide.html` | debug |
| `nodered-function-node-guide.html` | function |
| `nodered-switch-node-guide.html` | switch |
| `nodered-change-node-guide.html` | change |
| `nodered-template-node-guide.html` | template |

### HTTP・ネットワーク
| ファイル | ノード |
|---------|--------|
| `nodered-http-request-node-guide.html` | http request |
| `nodered-http-in-response-node-guide.html` | http in / http response |
| `nodered-mqtt-node-guide.html` | mqtt in / mqtt out / mqtt-broker |
| `nodered-tcp-node-guide.html` | tcp in / tcp out / tcp request |
| `nodered-udp-node-guide.html` | udp in / udp out |
| `nodered-websocket-node-guide.html` | websocket in / websocket out / websocket-listener / websocket-client |

### データ変換
| ファイル | ノード |
|---------|--------|
| `nodered-json-node-guide.html` | json |
| `nodered-xml-node-guide.html` | xml |
| `nodered-yaml-node-guide.html` | yaml |
| `nodered-csv-node-guide.html` | csv |
| `nodered-html-node-guide.html` | html |

### フロー制御
| ファイル | ノード |
|---------|--------|
| `nodered-split-node-guide.html` | split |
| `nodered-join-node-guide.html` | join |
| `nodered-filter-node-guide.html` | rbe (filter) |
| `nodered-batch-node-guide.html` | batch |
| `nodered-sort-node-guide.html` | sort |
| `nodered-range-node-guide.html` | range |
| `nodered-trigger-node-guide.html` | trigger |
| `nodered-delay-node-guide.html` | delay |
| `nodered-catch-node-guide.html` | catch |
| `nodered-complete-status-node-guide.html` | complete / status |
| `nodered-link-node-guide.html` | link in / link out / link call |

### ファイル・システム
| ファイル | ノード |
|---------|--------|
| `nodered-file-node-guide.html` | file / file in |
| `nodered-exec-node-guide.html` | exec |
| `nodered-watch-node-guide.html` | watch |

### その他
| ファイル | ノード |
|---------|--------|
| `nodered-comment-node-guide.html` | comment |

---

## ソースコード参照先

Node-RED標準ノードのソースコードは以下のGitHubリポジトリにある：

```
https://github.com/node-red/node-red
```

各ノードのエディタ定義HTMLファイルの場所：

```
packages/node_modules/@node-red/nodes/core/<カテゴリ>/<ノード名>.html
```

### カテゴリ別パス

| カテゴリ | パス | 含まれるノード |
|---------|------|--------------|
| common | `core/common/` | inject, debug, complete, status, catch, link-*, comment |
| function | `core/function/` | function, switch, change, template, delay, trigger, range, filter(rbe) |
| network | `core/network/` | http-in, http-response, http-request, websocket-*, mqtt-*, tcp-*, udp-* |
| parsers | `core/parsers/` | json, xml, yaml, csv, html |
| sequence | `core/sequence/` | split, join, sort, batch |
| storage | `core/storage/` | file, file-in, watch |

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

> **注意**: 標準ノードでは「コメントアウト済み」のケースはほぼ存在しない。
> Dashboard 2.0と異なり、標準ノードは成熟しているため「存在しない」プロパティが
> ガイドに誤記されているケースが主な修正対象となる。

---

## 作業手順

### Step 1: ソースコードの取得

```bash
# ノードのエディタHTMLを取得（例：injectノード）
# ブラウザまたはWebFetchで以下URLを確認：
https://raw.githubusercontent.com/node-red/node-red/master/packages/node_modules/@node-red/nodes/core/common/20-inject.html
```

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

## 標準ノード特有の注意事項

### 1. ノードバージョンによるプロパティ差異

Node-RED のバージョンによってプロパティが追加・変更されることがある。
最新の `master` ブランチのソースを参照すること。

### 2. 設定ノード（config node）のパターン

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

### 3. 複数出力ノード

switch、split等は `outputs` プロパティで出力ポート数を制御する。
`wires` 配列のサイズが `outputs` と一致していることを確認する：

```json
{
    "type": "switch",
    "outputs": 3,
    "wires": [["node1"], ["node2"], ["node3"]]
}
```

### 4. `propertyType` 系プロパティ

標準ノードでは TypedInput ウィジェットを多用する。
`property` と `propertyType` がペアで存在することが多い：

```json
{
    "type": "switch",
    "property": "payload",
    "propertyType": "msg"
}
```

### 5. 動的に生成されるプロパティ

一部のノードはエディタで動的にプロパティを生成する（例：switchの `rules`、changeの `rules`）。
これらは `defaults` に配列として定義されるが、フォーム要素は動的に生成される。

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

---

## 効率的な作業順序（推奨）

同じカテゴリのノードはソースコードの確認をまとめて行うと効率が良い。

### Phase 1: コアノード（6ファイル）
最も使用頻度が高く、影響範囲が大きい。
1. inject
2. debug
3. function
4. switch
5. change
6. template

### Phase 2: データ変換（5ファイル）
構造が類似しており、まとめて作業しやすい。
1. json
2. xml
3. yaml
4. csv
5. html

### Phase 3: フロー制御（11ファイル）
ノード数が最も多いカテゴリ。
1. split / join（ペアで確認）
2. filter / batch / sort
3. range / trigger / delay
4. catch / complete-status / link

### Phase 4: ネットワーク（6ファイル）
設定ノードが多く、確認項目が多い。
1. http-request
2. http-in-response
3. mqtt
4. tcp
5. udp
6. websocket

### Phase 5: ファイル・その他（4ファイル）
1. file
2. exec
3. watch
4. comment

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
- [ ] 設定ノードのプロパティを確認した
- [ ] JSONの構文が正しいことを確認した（カンマ、括弧）
- [ ] コミットしてプッシュした
