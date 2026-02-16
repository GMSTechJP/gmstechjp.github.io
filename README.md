# Node-RED ノードガイドサイト

**公開URL**: https://gmstechjp.github.io/

Node-RED初心者向けの日本語ガイドを提供する静的HTMLサイトです。各ノードの使い方を詳しく解説し、実用的なサンプルフローと演習問題で実践的なスキルを習得できます。

> ⚠️ **注意**: これは公開リポジトリです。機密情報やAPIキーを含めないでください。

---

## 📚 プロジェクト概要

### 目的

- Node-RED初心者が各ノードの使い方を学べる日本語ガイドを提供
- 実用的なサンプルフローで実践的なスキルを習得
- 演習問題で理解を深める

### 対象ユーザー

- Node-REDを初めて使う方
- 各ノードの詳細な使い方を学びたい方
- 実践的なサンプルフローを探している方
- 演習問題で理解を深めたい方

### コンテンツ

- **50+件のノードガイド**: 標準ノード、Dashboard 2.0ウィジェット、サードパーティノード
- **171個のサンプルフロー**: すべてNode-REDでインポート可能
- **演習問題**: 各ガイドに実践的な演習を用意

---

## 🎯 品質指標

| 指標 | 値 |
|------|-----|
| **JSON有効率** | 100% (171/171ブロック) |
| **プロパティ表精度** | 100% (ソースコード完全一致) |
| **無効ファイル** | 0件 |
| **エラー件数** | 0件 |

*最終更新: 2026-02-16*

---

## 📁 リポジトリ構造

```
gmstechjp.github.io/
├── README.md                           # プロジェクト概要（本ファイル）
├── CLAUDE.md                          # 開発ガイド
├── IMPLEMENTATION-PLAN.md              # 改善実装計画
├── AUDIT-REPORT.md                     # 監査結果レポート
├── PHASE4-VERIFICATION-REPORT.md       # Phase 4詳細レポート
├── PROCEDURE-standard-nodes-audit.md   # 監査手順書
├── index.html                          # トップページ
├── nodered-*-node-guide.html          # 各ノードのガイド（50+件）
├── validate-json-flows.py             # JSON検証スクリプト
├── test-node-red-import.py            # インポートテストスクリプト
├── img/                                # 画像ディレクトリ
└── reference/                          # 参考資料
```

---

## 🚀 ローカル開発環境のセットアップ

### 前提条件

- **Node.js** 18.x以上
- **Node-RED** 3.x以上（検証用）
- **Python** 3.8以上（検証スクリプト用）

### セットアップ手順

#### 1. リポジトリのクローン

```bash
git clone https://github.com/GMSTechJP/gmstechjp.github.io.git
cd gmstechjp.github.io
```

#### 2. Node-REDのインストール（検証用）

```bash
# グローバルインストール
npm install -g node-red

# インストール確認
node-red --version
```

#### 3. Dashboard 2.0のインストール（オプション）

```bash
# Node-REDのユーザーディレクトリに移動
cd ~/.node-red

# Dashboard 2.0をインストール
npm install @flowfuse/node-red-dashboard

# インストール確認
npm list @flowfuse/node-red-dashboard
```

#### 4. Node-REDの起動

```bash
node-red
```

ブラウザで http://localhost:1880 にアクセスしてエディターを確認します。

---

## 🔧 検証ツールの使用方法

### JSON構文検証

全ガイドファイルのJSONブロックを検証します。

```bash
python3 validate-json-flows.py
```

**期待される出力**:
```
📊 検証結果サマリー
  総ファイル数: 40
  総JSONブロック数: 171
  ✅ 有効: 36 ファイル
  ❌ 無効: 0 ファイル

🎉 すべてのJSONブロックが有効です！
```

### Node-REDインポートテスト

サンプリング対象ファイルのNode-RED形式を検証します。

```bash
python3 test-node-red-import.py
```

**期待される出力**:
```
📊 テスト結果サマリー
  総ファイル数: 16
  テスト済みJSONブロック数: 16
  ✅ 合格: 16 ファイル (16 ブロック)
  ❌ 不合格: 0 ファイル

🎉 すべてのJSONブロックがNode-RED形式として有効です！
```

---

## 📝 ガイド作成・更新のワークフロー

### 新規ガイドの作成

詳細は [PROCEDURE-standard-nodes-audit.md](PROCEDURE-standard-nodes-audit.md) を参照してください。

**基本手順**:

1. **対象ノードの特定**: GitHubからソースコードを取得
2. **プロパティの分類**: アクティブ、コメントアウト済み、エディタ非表示
3. **HTMLガイドファイルの作成**: テンプレートに従って作成
4. **プロパティ表の作成**: エディターの表示に完全一致させる
5. **サンプルフローの作成**: defaultsの全プロパティを網羅
6. **検証**: JSON構文、インポートテスト、ソースコード照合

### 既存ガイドの修正

1. **問題の特定**: [AUDIT-REPORT.md](AUDIT-REPORT.md) で確認
2. **ソースコードとの照合**: GitHubから最新のソースコードを取得
3. **修正の実施**: プロパティ表、サンプルフローを更新
4. **検証**: 3層の検証（JSON構文、インポート、ソースコード照合）

---

## 🤝 コントリビューション

### コントリビューションガイドライン

1. **Issue作成**: バグ報告や機能要望はIssueで報告
2. **フォーク**: リポジトリをフォーク
3. **ブランチ作成**: `feature/<feature-name>` または `fix/<issue-number>`
4. **変更実施**: [CLAUDE.md](CLAUDE.md) の品質基準に従う
5. **検証**: `validate-json-flows.py` と `test-node-red-import.py` を実行
6. **プルリクエスト**: mainブランチへPRを作成

### Git運用

**ブランチ戦略**:
- `main`: 本番環境（GitHub Pages公開ブランチ）
- `feature/<feature-name>`: 新機能開発
- `fix/<issue-number>`: バグ修正

**コミットメッセージ規則**:

コンベンショナルコミット形式を使用:
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

### 品質基準

すべての変更は以下の基準を満たす必要があります:

- ✅ JSON構文が有効（`validate-json-flows.py`で検証）
- ✅ Node-RED形式として有効（`test-node-red-import.py`で検証）
- ✅ プロパティ表がソースコードと一致
- ✅ サンプルフローがdefaults全プロパティを網羅
- ✅ 設定項目名がエディターの表示と一致

---

## 📖 ドキュメント

| ドキュメント | 説明 |
|------------|------|
| [CLAUDE.md](CLAUDE.md) | 開発ガイド・品質基準 |
| [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md) | 改善実装計画（Phase 1-5） |
| [AUDIT-REPORT.md](AUDIT-REPORT.md) | 監査結果レポート |
| [PHASE4-VERIFICATION-REPORT.md](PHASE4-VERIFICATION-REPORT.md) | Phase 4詳細レポート |
| [PROCEDURE-standard-nodes-audit.md](PROCEDURE-standard-nodes-audit.md) | 監査手順書 |

---

## 🔗 リンク

- **公開サイト**: https://gmstechjp.github.io/
- **Node-RED公式**: https://nodered.org/
- **Dashboard 2.0**: https://dashboard.flowfuse.com/
- **GitHubリポジトリ**: https://github.com/GMSTechJP/gmstechjp.github.io

---

## 📄 ライセンス

このプロジェクトは公開リポジトリです。機密情報を含めないでください。

---

## 🙏 謝辞

- Node-REDコミュニティの皆様
- FlowFuse（Dashboard 2.0）開発チーム
- すべてのコントリビューター

---

**最終更新**: 2026-02-16
**メンテナー**: Claude Sonnet 4.5
