# 作業引き継ぎファイル: Dashboard 2.0 プロパティ監査

## ブランチ
`claude/audit-dashboard-properties-Bq28N`

## 作業概要
FlowFuse/node-red-dashboard リポジトリのソースコード（`defaults`オブジェクト）を基準に、ガイドHTMLファイルのプロパティ表とサンプル/演習フローの不足プロパティを追加する。

## 完了済み作業

### Phase 1: プロパティ表の修正（全カテゴリ完了・コミット済み）

| コミット | ファイル | 内容 |
|---------|--------|------|
| `88d5d87` | nodered-dashboard2-widgets-display.html | 表示系ウィジェットの不足プロパティを追加 |
| `607e437` | nodered-dashboard2-widgets-input.html | 入力系ウィジェットの不足プロパティを追加 |
| `c86dc12` | nodered-dashboard2-widgets-visualization.html | 可視化系ウィジェットの不足プロパティを追加 |
| `552f280` | nodered-dashboard2-widgets-advanced-part1-template.html | templateウィジェットのノード設定プロパティ表を追加 |
| `da0588d` | nodered-dashboard2-widgets-advanced-part2-control-spacer.html | control/spacerウィジェットの不足プロパティを追加 |
| `c4583a7` | nodered-dashboard2-layout.html | レイアウトガイドにConfig Nodeの不足プロパティを追加 |

### Phase 2: サンプルフローの修正（Display一部完了・コミット済み）

| コミット | 内容 |
|---------|------|
| `1ff855b` | 表示系サンプルフローにui-text/markdown/audioの不足プロパティを追加 |

修正済みノード（サンプルフローのみ）:
- **ui-text** 3ノード: `wrapText`, `className`, `value`, `valueType` 追加
- **ui-markdown** 3ノード: `className` 追加
- **ui-audio** 3ノード: `className` 追加（TTSノードは`group`, `order`, `width`, `height`も追加）

---

## 未完了作業

### Display（nodered-dashboard2-widgets-display.html）残りのフロー修正

#### 1. サンプルフローのConfig Nodes

**ui-group 3ノード** (`sample_ui_group_text`, `sample_ui_group_markdown`, `sample_ui_group_audio`):
- 追加: `"groupType": "default"`
- 位置: `"disabled": false` の後に追加

**ui-theme 1ノード** (`sample_ui_theme`):
- 追加: sizesオブジェクト内に `"density": "default"`
- 位置: `"widgetGap": "12px"` の後に追加

**ui-base 1ノード** (`6692685697ac2af1`):
- 追加: `"showPageTitle": true`
- 位置: `"titleBarStyle": "default"` の後に追加（他のプロパティは既に存在）

#### 2. 演習フロー - ui-text ノード（4ノード）

| 行番号 | ノードID | 演習 |
|--------|---------|------|
| 2555 | t1_ui_text | T-1 |
| 2636 | t2_ui_text | T-3 |
| 2676 | t3_ui_text | T-4 |
| ※T-2は存在しない（Functionノードのみ） | | |

追加するプロパティ（各ノードの `"color":"#000000"` の後に追加）:
```json
"wrapText":false,"className":"","value":"payload","valueType":"msg"
```

#### 3. 演習フロー - ui-markdown ノード（2ノード）

| 行番号 | ノードID | 演習 |
|--------|---------|------|
| 2717 | m1_markdown | M-1 |
| 2757 | m2_markdown | M-2 |

追加するプロパティ（`"content":"..."` の後に追加）:
```json
"className":""
```

#### 4. 演習フロー - ui-notification ノード（3ノード）

| 行番号 | ノードID | 演習 | 既存outputs |
|--------|---------|------|------------|
| 2904 | n3_notification | N-2 | outputs:1 あり |
| 3052-3069 | ex3_notify | N-3 | なし |
| 3258-3274 | ex4_notify | A-3 | なし |

追加するプロパティ:
- `n3_notification`: `"className":""` のみ追加（`"raw":false` の後）
- `ex3_notify`: `"outputs": 1` と `"className": ""` 追加（`"name": "通知"` の前）
- `ex4_notify`: `"outputs": 1` と `"className": ""` 追加（`"name": "警告通知"` の前）

#### 5. 演習フロー - ui-audio ノード（3ノード）

| 行番号 | ノードID | 演習 | モード |
|--------|---------|------|--------|
| 3126 | a1_audio | A-1 | src（Audio Player） |
| 3168 | a2_tts | A-2 | tts |
| 3277-3289 | ex4_audio | A-3 | tts |

追加するプロパティ（`"muted":false` の後）:
```json
"className":""
```

#### 6. 演習フロー - ui-base ノード（2ノード）

| 行番号 | ノードID | 演習 |
|--------|---------|------|
| 2946-2954 | ex3_ui_base | N-3 |
| 3217-3224 | ex4_ui_base | A-3 |

追加するプロパティ（`"navigationStyle": "default"` の後）:
```json
"titleBarStyle": "default",
"showPageTitle": true,
"showReconnectNotification": true,
"notificationDisplayTime": 1,
"showDisconnectNotification": true,
"allowInstall": false
```

また `"path": "/dashboard"` の後に:
```json
"appIcon": "",
```

`"acceptsClientConfig"` の後に:
```json
"showPathInSidebar": false,
"headerContent": "page",
```
注: 一部既存プロパティあり。サンプルフローのui-base (`6692685697ac2af1`) を参照してフルセットにする。

---

### Input（nodered-dashboard2-widgets-input.html）フロー修正

全体的に以下が不足:
- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-button**: `"className": ""`, `"color": ""`, `"bgcolor": ""`, `"icon": ""`, `"iconPosition": "left"` 追加
- **ui-switch**: `"className": ""` 追加
- **ui-slider**: `"className": ""`, `"iconPrepend": ""`, `"iconAppend": ""` 追加
- **ui-dropdown**: `"className": ""` 追加
- **ui-text-input**: `"className": ""`, `"tooltip": ""` 追加
- **ui-form**: `"className": ""`, `"splitLayout": false` 追加
- **ui-radio-group**: `"className": ""` 追加
- **ui-button-group**: `"className": ""` 追加

---

### Visualization（nodered-dashboard2-widgets-visualization.html）フロー修正

- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-chart**: `"className": ""`, `"chartType": "line"` の確認
  - 値の修正: `"removeOlderUnit": "3600"` （現状 `"60"` は誤り）
  - 値の修正: `"categoryType": "msg"` （現状 `"none"` は誤り - ソースのdefault値は `"msg"`）
- **ui-gauge**: `"className": ""` 追加
- **ui-table**: `"className": ""` 追加
- **ui-progress**: `"className": ""` 追加
  - 注: ソースにない余分なプロパティ（`style`, `showValue`, `min`, `max`）がある可能性 → 要確認

---

### Advanced Part1（nodered-dashboard2-widgets-advanced-part1-template.html）フロー修正

- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-template**: `"className": ""` 追加

---

### Advanced Part2（nodered-dashboard2-widgets-advanced-part2-control-spacer.html）フロー修正

- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-control**: `"className": ""` 追加
- **ui-spacer**: `"className": ""` 追加

---

### Layout（nodered-dashboard2-layout.html）フロー修正

- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-theme**: sizesに `"density": "default"` 追加
- **ui-base**: `"showPageTitle": true` 等の不足プロパティ追加
- **ui-page**: `"className": ""`, `"visible": true`, `"disabled": false` 追加

---

## 技術的な注意事項

### JSON修正パターン

1. **ウィジェットノード（x, y, wiresあり）**: プロパティは `"x":` の直前に追加
2. **Config Nodes（x, y, wiresなし）**: プロパティは閉じ括弧 `}` の前に追加
3. **コンパクト形式（1行JSON）**: 既存プロパティの後に `,` で区切って挿入

### ソースコード参照先

defaults の確認は以下のファイルから:
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_base.html`
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_page.html`
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_group.html`
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_theme.html`
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/widgets/ui_text.html`
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/widgets/ui_markdown.html`
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/widgets/ui_notification.html`
- `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/widgets/ui_audio.html`
- 他のウィジェットも同パターン: `nodes/widgets/ui_<name>.html`

### topicType に関する注意

監査で `topicType` がソースdefaultsでは `"msg"` だがフロー内で `"str"` になっているケースがある。これは「要確認」としており、実際の使い方次第で正しい可能性あり。修正は保留。

### className について

`className` は CSS クラス名を指定するプロパティ。未使用時は空文字 `""` を設定する。JSONキー自体が欠落している状態（"未定義"）を修正し、空文字のキーとして明示的に含める。
