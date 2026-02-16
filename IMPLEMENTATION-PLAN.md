# Node-REDノードガイドサイト品質向上プロジェクト 実装計画

## Context（背景）

このプロジェクトは、Node-RED初心者向けの日本語ガイドを提供する静的HTMLサイト（https://gmstechjp.github.io/）です。50以上のノードガイドHTMLファイルがあり、各ファイルには以下が含まれています：

- ノードの説明セクション
- **設定項目一覧**のテーブル（プロパティ表）
- サンプルフローJSON
- 演習問題とその回答フローJSON

### 現状の問題

AUDIT-REPORT.mdによる詳細な監査の結果、**27件の問題**が特定されています：

- **CRITICAL（3件）**: JSON構文エラー（ユーザーがフローを読み込めない）
- **HIGH（8件）**: Dashboard 2.0のConfig Node不完全（動作に影響）
- **MEDIUM（10件）**: 非推奨プロパティ残存、プロパティ不足
- **LOW（6件）**: ドキュメント不正確

### ユーザー要求

1. 各ノードの説明セクション（プロパティ表）の設定項目を**実態と合わせる**
2. **Node-REDエディタ上で実際に表示される設定項目名に完全一致**させる
3. 動作しないサンプルフロー/演習問題回答フローを修正
4. 全27件の問題を完全に修正
5. 徹底的な検証を実施（JSON構文、インポートテスト、ソースコード照合）
6. CLAUDE.mdを作成して将来のメンテナンス性を確保

---

## Implementation Plan（実装計画）

### Phase 0: 環境準備（優先度: 最高）

**目標**: 実装と検証に必要な環境を整備

**所要時間**: 約30分

#### Node-RED検証環境のセットアップ

**前提条件確認**:

```bash
# Node.jsバージョン確認（18.x以上が必要）
node --version

# npmバージョン確認
npm --version
```

**Node-REDのインストール**:

```bash
# グローバルインストール
npm install -g node-red

# インストール確認
node-red --version
```

**Dashboard 2.0のインストール**:

```bash
# Node-REDのユーザーディレクトリに移動
cd ~/.node-red

# Dashboard 2.0をインストール
npm install @flowfuse/node-red-dashboard

# インストール確認
npm list @flowfuse/node-red-dashboard
```

**Node-REDの起動と動作確認**:

```bash
# Node-REDを起動
node-red

# ブラウザで http://localhost:1880 にアクセス
# エディターが表示されればOK
```

**検証環境の確認事項**:

- [ ] Node-REDエディターが正常に表示される
- [ ] パレットに標準ノード（inject, debug等）が表示される
- [ ] パレットにDashboard 2.0ノードが表示される
- [ ] フローのインポート機能が動作する

**トラブルシューティング**:

- Node-REDが起動しない → ポート1880が使用中でないか確認
- Dashboard 2.0が表示されない → `~/.node-red/package.json`を確認

---

### Phase 1: CRITICAL問題の修正（優先度: 最高）

**目標**: JSON構文エラーを解消し、ユーザーがフローを読み込めるようにする

**対象ファイル**: 3件

1. **nodered-http-node-guide.html** (HTTP In/Response/Requestを含む)
   - templateノードの`template`プロパティから不要なHTML（フローティングホームボタン）を除去
   - 改行を`\n`エスケープシーケンスに統一
   - JSON検証（JSON.parse()でエラーなし）

2. **nodered-websocket-node-guide.html**
   - 同様にtemplateノードの修正
   - リテラル改行文字の除去

3. **nodered-xml-node-guide.html**
   - Cloudflareメール保護タグ（`<a href="/cdn-cgi/l/email-protection"...>`）を除去
   - メールアドレスを別形式に変更（`user@example.com` → `user[at]example.com`）
   - JSON検証

**検証**:
- すべてのJSONブロックがJSON.parse()でエラーなし
- Node-REDエディターでインポート成功
- デプロイして動作確認

**Critical Files**:
- `/Users/gomuto/projects/gmstechjp.github.io/nodered-http-node-guide.html`
- `/Users/gomuto/projects/gmstechjp.github.io/nodered-websocket-node-guide.html`
- `/Users/gomuto/projects/gmstechjp.github.io/nodered-xml-node-guide.html`

---

### Phase 2: プロパティ表の整合性確保（優先度: 高）

**目標**: すべてのガイドのプロパティ表をNode-REDソースコードと完全一致させる

**所要時間**: 約15-20時間（Phase 2a: 15時間、Phase 2b: 3-5時間）

**重要な方針変更**:
- **設定項目名はNode-REDエディターの表示に完全一致**させる
- 既存の日本語訳は使用せず、実際のエディターHTMLから項目名を抽出
- エディターで英語表示される場合は英語で記載

**Phase 2を2つのサブフェーズに分割して段階的に実施**:
- **Phase 2a**: 標準ノード（Common, Function, Sequence, Parser, Storage, Network） - 21件
- **Phase 2b**: Dashboard 2.0ノードとその他 - 6件

---

#### Phase 2a: 標準ノードのプロパティ表修正（21件）

**対象ファイル**:

| カテゴリ | ファイル数 | 主な修正内容 |
|---------|-----------|-------------|
| Common | 4 | complete-status（uncaught削除）、link（linkType追加）、catch（tab/z追加） |
| Function | 5 | change（非推奨削除）、function（noerr削除）、trigger（最小表記） |
| Sequence | 3 | join/batch（property追加、型統一） |
| Parser | 2 | csv（型統一）、xml（4プロパティ追加） |
| Storage | 2 | watch（tab/z追加） |
| Network | 5 | http, websocket（CRITICAL修正済み）、mqtt, tcp, udp |

**推奨作業順序**: カテゴリ別に処理（Common → Function → Sequence → Parser → Storage → Network）

---

#### Phase 2b: Dashboard 2.0ノードのプロパティ表修正（4件）

**対象ファイル**:

| カテゴリ | ファイル数 | 主な修正内容 |
|---------|-----------|-------------|
| Dashboard 2.0 | 4 | overview（8プロパティ）、advanced-part2（tooltip削除）、layout（tooltip削除）、advanced-part1（検証のみ） |

**注意**: Phase 2bの前に、参照ガイド（display, input, visualization）の検証を実施すること

---

#### 作業手順（各ノードごと）

**Step 1: Node-REDソースコードの取得**

標準ノード:
```
リポジトリ: https://github.com/node-red/node-red
パス: packages/node_modules/@node-red/nodes/core/<category>/<node>.html
```

Dashboard 2.0:
```
リポジトリ: https://github.com/FlowFuse/node-red-dashboard
パス: nodes/widgets/ui_<name>.html または nodes/config/ui_<name>.html
```

**Step 2: defaultsオブジェクトとフォーム要素の抽出**

```javascript
// defaultsオブジェクト
RED.nodes.registerType('inject', {
    defaults: {
        name: { value: "" },
        props: { value: [...] },
        repeat: { value: "" },
        // ...
    }
});
```

```html
<!-- フォーム要素のラベルを確認 -->
<div class="form-row">
    <label for="node-input-repeat">Repeat</label>
    <input type="text" id="node-input-repeat">
</div>
```

**Step 3: プロパティの分類**

| 分類 | 条件 | プロパティ表に記載 | JSONに含める |
|------|------|-------------------|-------------|
| **アクティブ** | defaults内 AND フォーム要素あり（有効） | ✅ YES | ✅ YES |
| **コメントアウト済み** | defaults内 BUT フォーム要素がコメントアウト | ❌ NO | ❌ NO |
| **エディタ非表示** | defaults内 BUT フォーム要素なし | ❌ NO | ✅ YES |
| **存在しない** | defaultsに定義なし | ❌ NO | ❌ NO |

**Step 4: プロパティ表の更新**

- アクティブなプロパティのみを記載
- 設定項目名はエディターHTMLの`<label>`テキストをそのまま使用
- 説明は日本語で記載（ユーザーフレンドリーに）

**プロパティ表の記載例**:

```html
<h3>📋 設定項目一覧</h3>
<table>
    <tr>
        <th>設定項目</th>
        <th>説明</th>
        <th>備考</th>
    </tr>
    <tr>
        <td><strong>Repeat</strong></td>
        <td>定期実行の間隔を設定します</td>
        <td>秒/分/時間/cron式で指定可能</td>
    </tr>
    <tr>
        <td><strong>Inject once after</strong></td>
        <td>Node-RED起動後に自動実行する遅延時間</td>
        <td>デフォルト: 0.1秒</td>
    </tr>
    <tr>
        <td><strong>Name</strong></td>
        <td>ノードの表示名</td>
        <td>用途がわかる名前を推奨</td>
    </tr>
</table>
```

**重要な原則**:
- ❌ 誤: `<td><strong>繰り返し</strong></td>` （日本語訳）
- ✅ 正: `<td><strong>Repeat</strong></td>` （エディターの実際の表示）
- 説明列で日本語の詳細を提供

**対象ファイル（カテゴリ別）**:

| カテゴリ | ファイル数 | 主な修正内容 |
|---------|-----------|-------------|
| Common | 4 | complete-status（uncaught削除）、link（linkType追加）、catch（tab/z追加） |
| Function | 5 | change（非推奨削除）、function（noerr削除）、trigger（最小表記） |
| Sequence | 3 | join/batch（property追加、型統一） |
| Parser | 2 | csv（型統一）、xml（4プロパティ追加） |
| Storage | 2 | watch（tab/z追加） |
| Network | 5 | http, websocket（CRITICAL修正済み）、mqtt, tcp, udp |
| Dashboard 2.0 | 4 | overview（8プロパティ）、advanced-part2, layout（tooltip削除） |

**Critical Files**:
- `/Users/gomuto/projects/gmstechjp.github.io/PROCEDURE-standard-nodes-audit.md`（手順書）
- GitHub: `https://github.com/node-red/node-red` （標準ノードのソース）
- GitHub: `https://github.com/FlowFuse/node-red-dashboard` （Dashboard 2.0のソース）

---

### Phase 3: サンプルフロー/演習フローの完全性確保（優先度: 中）

**目標**: すべてのフローJSONがdefaultsオブジェクトを完全に網羅

**所要時間**: 約15-20時間

---

#### Phase 3の事前作業: 参照ガイドの検証（重要）

Phase 3で「既存の修正済みガイド（display, input, visualization）を参考に統一」する前に、これらの参照ガイド自体が正確であることを確認する必要があります。

**検証対象**:
- `nodered-dashboard2-widgets-display.html`
- `nodered-dashboard2-widgets-input.html`
- `nodered-dashboard2-widgets-visualization.html`

**検証手順**:

1. Dashboard 2.0のGitHubソースから最新のConfig Node定義を取得

```bash
# ui-base, ui-theme, ui-group, ui-pageのソースを確認
curl https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_base.html
curl https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_theme.html
curl https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_group.html
curl https://raw.githubusercontent.com/FlowFuse/node-red-dashboard/main/nodes/config/ui_page.html
```

2. 各参照ガイドのConfig Nodeセクションを確認

```bash
# display, input, visualizationガイドからui-baseのプロパティを抽出
grep -A 20 '"type": "ui-base"' nodered-dashboard2-widgets-display.html
grep -A 20 '"type": "ui-base"' nodered-dashboard2-widgets-input.html
grep -A 20 '"type": "ui-base"' nodered-dashboard2-widgets-visualization.html
```

3. 不一致があれば先に修正

**確認項目**:
- [ ] ui-baseに `headerContent`, `navigationStyle`, `titleBarStyle` が含まれているか
- [ ] ui-themeに `sizes.density` が含まれているか
- [ ] ui-groupに `groupType` が含まれているか
- [ ] ui-pageに `visible`, `disabled` が含まれているか
- [ ] `tooltip: ""` が削除されているか

**この事前作業が完了してから、overviewガイドの修正に進むこと**

---

#### HIGH問題の修正（8件）

**nodered-dashboard2-overview.html**:

| Config Node | 不足プロパティ | デフォルト値 |
|-------------|---------------|-------------|
| ui-button | `tooltip: ""` を**削除** | - |
| ui-group | `groupType` を**追加** | `"default"` |
| ui-page | `visible` を**追加** | `true` |
| ui-page | `disabled` を**追加** | `false` |
| ui-base | `headerContent` を**追加** | `""` |
| ui-base | `navigationStyle` を**追加** | `"default"` |
| ui-base | `titleBarStyle` を**追加** | `"default"` |
| ui-theme | `sizes.density` を**追加** | `"default"` |

**修正方法**: Dashboard 2.0のGitHubリポジトリから最新のdefaultsを確認し、既存の修正済みガイド（display, input, visualization）を参考に統一

#### MEDIUM問題の修正（10件）

| ファイル | 問題 | 修正方法 |
|---------|------|---------|
| change | 非推奨プロパティ残存 | `action`, `property`, `from`, `to`, `reg` を全changeノードから削除 |
| function | 非推奨プロパティ残存 | `noerr` を全functionノードから削除 |
| join, batch | splitノードに`property`不足 | `"property": "payload"` を追加 |
| batch | 型不統一 | `count`, `overlap`, `interval` を数値型に統一 |
| catch, watch | 構造的欠落 | 演習フローにtabノードと各ノードの`z`プロパティを追加 |
| xml | プロパティ不足 | `multi`, `attrkey`, `charkey`, `indent` の4プロパティを追加 |

#### LOW問題の修正（6件）

| ファイル | 問題 | 修正方法 |
|---------|------|---------|
| change | `onlyset`プロパティの扱い | defaultsに存在するか確認し、JSONに追加 |
| complete-status | 誤ったプロパティ混在 | Completeノードから`uncaught`を削除（Catch専用） |
| link | プロパティ表の未記載 | Link Callの`linkType`をプロパティ表に追加 |
| trigger | 補助functionの最小表記 | `libs`, `timeout`等を追加（完全な形式） |
| csv | 型の問題 | `skip`を文字列から数値型に変更 |
| dashboard2-overview | プロパティ表の未記載 | ui-themeの`density`、ui-pageの`visible/disabled`を追加 |

**Critical Files**:
- `/Users/gomuto/projects/gmstechjp.github.io/AUDIT-REPORT.md`（問題リスト）
- 全対象HTMLファイル（27件）

---

### Phase 4: 検証とテスト（優先度: 高）

**目標**: すべての修正が正しく、品質基準を満たすことを確認

#### 検証レベル1: JSON構文検証（必須）

**方法**: すべてのHTMLファイルからJSONブロックを抽出し、自動検証

```bash
#!/bin/bash
# validate-all-flows.sh

for file in nodered-*-node-guide.html; do
    echo "Validating $file..."
    # textareaタグ内のJSONを抽出
    # JSON.parse()で検証
    # 結果を記録
done
```

**合格基準**: すべてのJSONブロックがエラーなくパース可能

#### 検証レベル2: Node-REDインポートテスト

**方法**: 実際のNode-REDエディターでサンプリングテスト

**サンプリング率**:
- CRITICAL/HIGH問題のファイル: 100%（11件）
- MEDIUM問題のファイル: 50%（5件）
- LOW問題のファイル: 30%（2件）
- 問題なしファイル: 10%（2件）

**合格基準**: インポート成功、デプロイ可能、基本動作確認

#### 検証レベル3: プロパティ表とソースコードの照合

**方法**: 各ノードのGitHubソースコードのdefaultsオブジェクトとプロパティ表を比較

**チェック項目**:
- アクティブなプロパティがすべて記載されているか
- コメントアウト済みプロパティが記載されていないか
- 設定項目名がエディターのラベルと一致しているか

**合格基準**: 全ノードで完全一致

#### テストマトリックス

| ファイル | JSON構文 | defaults一致 | インポート | 動作確認 | ステータス |
|---------|---------|-------------|-----------|---------|----------|
| inject | ✅ | ✅ | ✅ | ✅ | 既修正 |
| debug | ✅ | ✅ | ✅ | ✅ | 既修正 |
| http | ⚠️ | 🔍 | 🔍 | 🔍 | Phase 1対象 |
| websocket | ⚠️ | 🔍 | 🔍 | 🔍 | Phase 1対象 |
| xml | ⚠️ | ⚠️ | 🔍 | 🔍 | Phase 1対象 |
| ... | ... | ... | ... | ... | ... |

凡例: ✅ 合格 | ⚠️ 問題あり | 🔍 未検証

**Critical Files**:
- 全HTMLファイル（50+件）
- Node-RED実行環境（ローカルまたはテスト環境）

---

### Phase 5: ドキュメント整備（優先度: 中）

**目標**: 将来のメンテナンス性を確保

**注意**: CLAUDE.mdは既に作成済み（2026-02-16完了 ✅）

#### AUDIT-REPORT.mdの更新

- 修正完了した問題にチェックマーク追加
- 最終統計の更新
- 新規発見問題の追記

#### README.mdの拡充

- プロジェクト概要の詳細化
- ローカル開発環境のセットアップ
- コントリビューションガイド

**Critical Files**:
- `/Users/gomuto/projects/gmstechjp.github.io/CLAUDE.md`（作成済み ✅）
- `/Users/gomuto/projects/gmstechjp.github.io/AUDIT-REPORT.md`（更新対象）
- `/Users/gomuto/projects/gmstechjp.github.io/README.md`（更新対象）

---

## Required Tools and Permissions（必要なツールと権限）

### ファイル編集権限
- ✅ `/Users/gomuto/projects/gmstechjp.github.io/` への読み書き権限
- ✅ GitHubリポジトリへのプッシュ権限

### 外部リソースへのアクセス
- ✅ Node-RED公式リポジトリ: https://github.com/node-red/node-red
- ✅ Dashboard 2.0リポジトリ: https://github.com/FlowFuse/node-red-dashboard
- ✅ WebFetchツールまたはブラウザアクセス（公開リポジトリ、認証不要）

### 検証ツール
- ✅ JSON検証: Python `json.tool`、Node.js `JSON.parse()`、またはオンラインツール（jsonlint.com）
- ✅ テキストエディタ: VS Code（JSON/HTML編集）
- ✅ Node-RED実行環境: Node.js 18.x+、Node-RED 3.x+、Dashboard 2.0インストール済み
- ✅ Bashスクリプト実行環境（JSON一括検証用）

### Git運用
- ✅ ブランチ作成・マージ権限
- ✅ コンベンショナルコミット形式の使用
- ✅ プルリクエスト作成権限（レビュープロセス用）

---

## Success Criteria（成功基準）

### 定量的基準
- [ ] AUDIT-REPORTの全27件の問題が修正済み
- [ ] JSON無効数が0件（現状: 3件 → 目標: 0件）
- [ ] JSON有効率が100%（現状: 97.4% → 目標: 100%）
- [ ] 全ガイドのプロパティ表がNode-REDソースコードと完全一致
- [ ] 50+ガイドファイルすべてがJSON検証合格

### 定性的基準
- [ ] ユーザーが全サンプルフローをエラーなくインポート可能
- [ ] プロパティ表の設定項目名がNode-REDエディターの実際の表示と完全一致
- [ ] CLAUDE.mdが整備され、将来のメンテナンスが容易
- [ ] コミット履歴が明確で、変更理由が追跡可能

### 検証完了基準
- [ ] JSON構文検証: 全ファイル合格
- [ ] Node-REDインポートテスト: サンプリングで100%成功
- [ ] ソースコード照合: 全プロパティ表で完全一致

---

## Risk Mitigation（リスクと対応）

| リスク | 影響 | 発生確率 | 緩和策 |
|-------|-----|---------|-------|
| GitHubソースコードのバージョン不一致 | 中 | 中 | masterブランチの最新を基準にする |
| Cloudflareメール保護の再発 | 低 | 低 | メールアドレスを含まないサンプルに統一 |
| Dashboard 2.0のプロパティ変更 | 中 | 低 | 定期的な監査を実施 |
| JSON検証漏れ | 高 | 低 | 自動化スクリプトで全ファイルチェック |
| エディター表示名の調査漏れ | 中 | 中 | 実際のNode-REDで表示確認を実施 |
| 作業量の過小評価 | 中 | 中 | Phase 2を2つのサブフェーズに分割、段階的に実施 |
| 参照ガイドの不正確性 | 中 | 低 | Phase 3の事前作業で参照ガイドを検証 |

---

## Verification Plan（検証計画）

### Phase 1-3完了時の検証

**JSON構文検証**:
```bash
# すべてのHTMLファイルのJSONブロックを検証
for file in nodered-*-guide.html; do
    python3 -c "import json, sys; json.loads(sys.stdin.read())" < <(grep -Pzo '(?<=<textarea[^>]*>).*?(?=</textarea>)' "$file")
done
```

**インポートテスト**:
1. Node-REDエディターを起動
2. サンプリング対象ファイルを開く
3. JSONをコピー → メニュー → 読み込み → ペースト
4. インポート成功を確認
5. デプロイして基本動作確認

**プロパティ表照合**:
1. 各ノードのGitHubソースを開く
2. defaultsオブジェクトとフォーム要素を確認
3. ガイドのプロパティ表と比較
4. 不一致があれば記録・修正

### 最終検証（全Phase完了後）

- [ ] すべてのファイルでJSON構文エラーなし
- [ ] サンプリングテストで100%インポート成功
- [ ] プロパティ表の完全一致を確認
- [ ] CLAUDE.mdのレビュー完了
- [ ] AUDIT-REPORT.mdの更新完了
- [ ] README.mdの拡充完了

---

## Next Steps（次のステップ）

### 推奨実施順序

1. **Phase 0: 環境準備**（所要時間: 30分）
   - Node-RED検証環境のセットアップ
   - Dashboard 2.0のインストール
   - 動作確認

2. **Phase 5（一部完了）: CLAUDE.md作成**（所要時間: 完了済み ✅）
   - プロジェクト開発ガイドの整備
   - ※CLAUDE.mdは既に作成済み。Phase 5の残作業（AUDIT-REPORT、README更新）は最後に実施

3. **Phase 1: CRITICAL問題の修正**（所要時間: 2-3時間）
   - JSON構文エラーの解消（3件）
   - 即座に検証とNode-REDインポートテスト

4. **Phase 2a: 標準ノードのプロパティ表修正**（所要時間: 15時間）
   - Common, Function, Sequence, Parser, Storage, Networkの21件
   - カテゴリ別に段階的に実施

5. **Phase 2b: Dashboard 2.0ノードのプロパティ表修正**（所要時間: 3-5時間）
   - 事前に参照ガイド（display, input, visualization）を検証
   - Dashboard 2.0の4件を修正・検証

6. **Phase 3: サンプルフロー/演習フローの完全性確保**（所要時間: 15-20時間）
   - 事前作業: 参照ガイドの検証
   - HIGH/MEDIUM/LOW問題の修正（24件）

7. **Phase 4: 検証とテスト**（所要時間: 5-8時間）
   - JSON構文検証（全ファイル）
   - Node-REDインポートテスト（サンプリング）
   - ソースコード照合（全プロパティ表）

8. **Phase 5: ドキュメント整備**（所要時間: 3-5時間）
   - AUDIT-REPORT.mdの更新
   - README.mdの拡充
   - 最終レビュー

### 総所要時間見積もり

- **最小**: 約40時間
- **最大**: 約50時間
- **推奨**: 段階的に実施し、各Phase完了後に検証を実施

### 各Phase完了後の必須作業

- [ ] 成功基準との照合
- [ ] 検証の実施
- [ ] 進捗のドキュメント化（AUDIT-REPORT.mdの更新）
- [ ] Git commit（コンベンショナルコミット形式）
