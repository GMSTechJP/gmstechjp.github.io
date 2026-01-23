# 作業引き継ぎファイル: Dashboard 2.0 プロパティ監査 Phase 2

## ブランチ
`claude/fix-display-issues-p3ZU5`

## 作業概要

FlowFuse/node-red-dashboard リポジトリのソースコード（`defaults`オブジェクトおよびエディタHTML テンプレート）を基準に、ガイドHTMLファイルの以下を修正する:

1. **プロパティ表の修正**: エディタUIで使えないプロパティの記載を削除
2. **フローJSONの修正**: 不足プロパティの追加、余分なプロパティの削除、値の修正

### 原則

**プロパティ表に含めるべきもの**: エディタHTML内で **アクティブな**（コメントアウトされていない）`<input>`/`<select>` 等のフォーム要素があるプロパティのみ

**プロパティの3分類**:
1. **コメントアウト済み**: エディタHTMLにフォーム要素はあるが `<!-- -->` で囲まれている → プロパティ表からもフローJSONからも**削除**
2. **エディタ非表示**: `defaults`にあるがエディタHTMLにフォーム要素がない → フローJSONに**含める**が、プロパティ表には**含めない**
3. **存在しない**: `defaults`にすら存在しない → プロパティ表からもフローJSONからも**削除**

---

## 完了済み作業

### Phase 1（前ブランチ `claude/audit-dashboard-properties-Bq28N` で実施・マージ済み）

プロパティ表への不足プロパティ追加（全カテゴリ完了）:

| コミット | ファイル | 内容 |
|---------|--------|------|
| `88d5d87` | display.html | 表示系ウィジェットの不足プロパティを追加 |
| `607e437` | input.html | 入力系ウィジェットの不足プロパティを追加 |
| `c86dc12` | visualization.html | 可視化系ウィジェットの不足プロパティを追加 |
| `552f280` | advanced-part1-template.html | templateウィジェットのノード設定プロパティ表を追加 |
| `da0588d` | advanced-part2-control-spacer.html | control/spacerウィジェットの不足プロパティを追加 |
| `c4583a7` | layout.html | レイアウトガイドにConfig Nodeの不足プロパティを追加 |

### Phase 2（現ブランチで実施）

#### Display（nodered-dashboard2-widgets-display.html）✅ 完了

| コミット | 内容 |
|---------|------|
| `1ff855b` | サンプルフロー: ui-text/markdown/audioの不足プロパティ追加 |
| `d284bbf` | 演習フロー: Config Nodes + 全ウィジェットの不足プロパティ追加 |

修正内容:
- **サンプルフロー**: ui-text (wrapText, className, value, valueType)、ui-markdown (className)、ui-audio (className, group, order等)
- **演習フロー Config Nodes**: ui-base (headerContent, navigationStyle, titleBarStyle, showPageTitle等)、ui-theme (density)、ui-group (groupType)、ui-page (className, visible, disabled)
- **演習フロー Widgets**: ui-text (wrapText, className, value, valueType)、ui-markdown (className)、ui-notification (outputs, className)、ui-audio (className)

プロパティ表の問題: **なし**（全プロパティにアクティブなエディタUIあり）

#### Input（nodered-dashboard2-widgets-input.html）✅ 完了

| コミット | 内容 |
|---------|------|
| `cb54e1a` | サンプルフロー: 不足プロパティ追加 |
| `2c0d4a9` | サンプルフロー: tooltipプロパティ削除 |
| `50de0e1` | 演習フロー: Config Nodes + 全ウィジェットの不足プロパティ追加 |
| `0352006` | プロパティ表: エディタUI非表示のプロパティ説明を削除 |

修正内容:
- **サンプルフロー**: ui-button (className, color, bgcolor, icon, iconPosition)、ui-switch (className)、ui-slider (className, iconPrepend, iconAppend)、ui-dropdown (className)、ui-text-input (className, tooltip)、ui-form (className, splitLayout)、ui-radio-group (className)、ui-button-group (className)
- **tooltip削除**: ui-button、ui-slider、ui-dropdownからtooltip削除（コメントアウト済みプロパティ）
- **演習フロー Config Nodes**: ui-base、ui-theme、ui-group、ui-page
- **演習フロー Widgets**: 上記全ウィジェット

プロパティ表から削除したもの（7件）:
| ウィジェット | 削除プロパティ | 理由 |
|-------------|--------------|------|
| ui-button | Tooltip | コメントアウト済み |
| ui-slider | Tooltip | コメントアウト済み |
| ui-dropdown | Tooltip | コメントアウト済み |
| ui-switch | Style | defaultsにあるがエディタUIなし |
| ui-form | Pass Through | defaultsにあるがエディタUIなし |
| ui-button-group | Appearance | defaultsに存在しない |
| ui-button-group | Selection | defaultsに存在しない |

#### Visualization（nodered-dashboard2-widgets-visualization.html）✅ 完了

| コミット | 内容 |
|---------|------|
| `71b2ad4` | プロパティ表: エディタUI非表示・非存在プロパティ削除 + フロー修正 |
| `10ff872` | サンプルフロー: 不足プロパティ追加 |
| `85d5cc2` | 演習フロー: Config Nodes + 全ウィジェットの不足プロパティ追加 |

修正内容:
- **プロパティ表削除 + フローJSON削除**: styleRounded/styleGlow (gauge)、passthru (table)、style/showValue/min/max (progress)
- **演習ヒント修正**: P-1/P-2/P-3の演習説明から非存在プロパティ参照を削除
- **サンプルフロー**: ui-base (showPageTitle)、ui-theme (density)、ui-chart (removeOlderUnit修正)、ui-table (className)、ui-progress (className)、ui-slider (tooltip削除)
- **演習フロー Config Nodes**: ui-base (headerContent, navigationStyle, titleBarStyle, showPageTitle)、ui-theme (density)、ui-page (className)
- **演習フロー Widgets**: ui-button (tooltip削除)、ui-slider (tooltip削除)、ui-chart (removeOlderUnit修正, className)、ui-table (className)、ui-gauge (className)、ui-progress (className)

プロパティ表から削除したもの（6件）:
| ウィジェット | 削除プロパティ | 理由 |
|-------------|--------------|------|
| ui-gauge | Style Rounded | defaultsにあるがエディタUIなし |
| ui-gauge | Style Glow | defaultsにあるがエディタUIなし |
| ui-table | Pass Through | defaultsにあるがエディタUIなし |
| ui-progress | Style | defaultsに存在しない |
| ui-progress | Show Value | defaultsに存在しない |
| ui-progress | Min / Max | defaultsに存在しない |

---

## 未完了作業

### Advanced Part1（nodered-dashboard2-widgets-advanced-part1-template.html）

#### 1. プロパティ表の調査
エディタUIで使えないプロパティがプロパティ表に含まれていないか確認が必要。

#### 2. フロー修正
- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-base**: 不足プロパティ追加（headerContent, navigationStyle, titleBarStyle, showPageTitle等）
- **ui-theme**: sizesに `"density": "default"` 追加
- **ui-page**: `"className": ""`, `"visible": true`, `"disabled": false` 追加
- **ui-template**: `"className": ""` 追加
- **tooltipの確認**: ui-templateにtooltipプロパティがある場合、コメントアウト状態を確認して削除判断

---

### Advanced Part2（nodered-dashboard2-widgets-advanced-part2-control-spacer.html）

#### 1. プロパティ表の調査
エディタUIで使えないプロパティがプロパティ表に含まれていないか確認が必要。

#### 2. フロー修正
- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-base**: 不足プロパティ追加
- **ui-theme**: sizesに `"density": "default"` 追加
- **ui-page**: `"className": ""`, `"visible": true`, `"disabled": false` 追加
- **ui-control**: `"className": ""` 追加（要ソース確認）
- **ui-spacer**: `"className": ""` 追加（要ソース確認）

---

### Layout（nodered-dashboard2-layout.html）

#### 1. プロパティ表の調査
エディタUIで使えないプロパティがプロパティ表に含まれていないか確認が必要。

#### 2. フロー修正
- **全ui-groupノード**: `"groupType": "default"` 追加
- **ui-theme**: sizesに `"density": "default"` 追加
- **ui-base**: `"showPageTitle": true` 等の不足プロパティ追加
- **ui-page**: `"className": ""`, `"visible": true`, `"disabled": false` 追加

---

## 技術的な注意事項

### 作業手順（確立されたワークフロー）

1. **プロパティ表の調査**: ソースHTMLのエディタテンプレートを確認し、コメントアウトやエディタUIなしのプロパティを特定
2. **プロパティ表の修正**: 該当プロパティの行を削除
3. **サンプルフローの修正**: ソースの`defaults`に基づき不足プロパティを追加、余分なプロパティを削除
4. **演習フローの修正**: 同上

### JSON修正パターン

1. **ウィジェットノード（x, y, wiresあり）**: プロパティは `"x":` の直前に追加
2. **Config Nodes（x, y, wiresなし）**: プロパティは閉じ括弧 `}` の前に追加
3. **コンパクト形式（1行JSON）**: 既存プロパティの後に `,` で区切って挿入
4. **replace_all活用**: 同一パターンのConfig Nodes（ui-base, ui-theme等）は `replace_all` で一括修正可能

### フロー内の値の修正事項

| プロパティ | 誤った値 | 正しい値 | 対象 |
|-----------|---------|---------|------|
| removeOlderUnit | `"60"` | `"3600"` | ui-chart |
| tooltip | `""` (存在) | (削除) | ui-button, ui-slider, ui-dropdown |

### ソースコード参照先

defaultsおよびエディタHTML確認は以下のパターン:
- Config: `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_<name>.html`
- Widgets: `https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/widgets/ui_<name>.html`

### topicType に関する注意

監査で `topicType` がソースdefaultsでは `"msg"` だがフロー内で `"str"` になっているケースがある。これは「要確認」としており、実際の使い方次第で正しい可能性あり。修正は保留。
