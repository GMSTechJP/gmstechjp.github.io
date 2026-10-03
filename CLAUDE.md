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
- **条件付きで表示される欄は、表示条件を必ず書く**。エディターHTMLの `oneditprepare` 内の
  `.show()` / `.hide()` / `.toggle()` と、`class="hide"` の付いた `form-row` を確認する。
  条件を書かないと、利用者はガイドにある項目を画面で見つけられない
  （実例: websocket-client の「TLS設定」は URL が `wss://` のときだけ表示されるが、
  条件を書いていなかったため `ws://` の画面で探して見つからなかった）
- 設定ノードに存在しない欄を、存在するかのように書かない（例: websocket-listener には
  TLS設定欄が無く、`wss://` は Node-RED 本体の https 設定で決まる）

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

**公式サンプル第一の原則（必須）**:

最初のサンプルフローには、**公式同梱のサンプルフローを使う**。独自フローをゼロから
作るのは、公式サンプルが存在しない場合に限る。

- 標準ノード: Node-RED 本体同梱の examples
  （`packages/node_modules/@node-red/nodes/examples/<category>/<node>/`）。
  common / function / network / parser / sequence / storage の6カテゴリがある。
- Dashboard 2.0: FlowFuse リポジトリの `examples/`。
- 公式サンプルが複数あるノードは、inject ガイドの流儀に合わせて **1つのタブに統合**する。
  ノード ID・英語コメント・構成は公式のまま保持し、ノード名だけ日本語化してよい。
- 公式サンプルに含まれない独自の教材（ブラウザテストページ等）を追加する場合は、
  **「サイト独自の応用例」であることを本文で明示**し、公式サンプルと同じ節に混ぜない。

この原則の理由: 公式サンプルは本家がメンテナンスする実績ある構成であり、要求環境が
明確になる（例: websocket / http の公式サンプルは `localhost:1880` へのループバック構成
のため、ブラウザ経由の Mixed Content 問題は構造的に発生しない代わりに、ローカル環境 🖥️
が前提になる）。サイト独自の付加物が環境依存の不具合を持ち込んだ実例があるため、
独自教材は分離して管理する。

**必須要件**:
- [ ] JSON構文が有効（`JSON.parse()` でエラーなし）
- [ ] **`<` を含む値はすべて `&lt;` にエスケープ**（後述の「フローJSONに生のタグを書かない」を参照）
- [ ] `defaults` の全プロパティを網羅（アクティブ + エディタ非表示）
- [ ] Config Nodeのプロパティも完全
- [ ] tabノードを含む
- [ ] 各ノードに `z` プロパティを含む
- [ ] 複数出力ノードは `outputs` と `wires` のサイズが一致
- [ ] `python3 scripts/validate-flow-json.py` が通る

**フォーマット**:

`<div class="flow-json">` の直下に JSON テキストのみを置く。`<textarea>` や `<pre>` で
包まない。コピーボタンは JavaScript が実行時に追加するため、HTMLに直接書かない。

```html
<details>
    <summary>📋 サンプルフロー（クリックで展開）</summary>
    <div class="flow-json">[
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
        "type": "template",
        "z": "tab_id",
        "template": "&lt;h1&gt;Hello&lt;/h1&gt;"
    }
]</div>
</details>
```

##### フローJSONに生のタグを書かない（必須）

`template` や `function` の値にHTMLやXMLを含めるときは、`<` を必ず `&lt;` と書く。

`div` は `textarea` と違い、中身がHTMLとして解釈される。生のタグを書くと、ブラウザは
それをDOMの要素に変換してしまう。コピーボタンは `textContent` を読むため、**利用者の
手元にはタグが消えた文字列が届く**。しかも破損後もJSONとしては valid なので、
`JSON.parse()` による検証も、Node-REDへのインポートも成功してしまう。

```html
<!-- ❌ NG: コピーすると <!DOCTYPE html> 等が消える -->
"template": "<!DOCTYPE html>\n<html>\n<body>Hello</body>\n</html>"

<!-- ✅ OK: コピー時に textContent が元の文字列へ復元される -->
"template": "&lt;!DOCTYPE html&gt;\n&lt;html&gt;\n&lt;body&gt;Hello&lt;/body&gt;\n&lt;/html&gt;"
```

同じ理由で、`&` は `&amp;` と書く。

##### ノードの実行順に注意する（必須）

`template` ノードの mustache（`{{foo}}`）が展開されるのは、そのノードが実行された
時点である。値をセットする `change` ノードは、必ず `template` より**前**に置く。
順序を逆にすると、その項目は空欄のまま出力される。

```text
✅ http in → change（値をセット） → template（描画） → http response
❌ http in → template（描画） → change（値をセット） → http response
```

#### 7. 演習問題の作成

**構成**:
- 難易度表示（初級/中級/上級）
- 問題文
- ヒント
- 解答例フロー（サンプルフローと同じ品質基準）

**動作確認の経路を、実在するものだけで書く（必須）**:

演習の「作る範囲」の図や動作確認の手順に出てくるクライアント・ツール・ページは、
**その演習のパス・ポートに実際に接続できるもの**でなければならない。

- 「ブラウザ（既にあるもの）」のように、実在しないクライアントを図に書かない。
  応用フローのテストページ等は接続先が固定されていることが多く、演習のパスには使えない
- 学習者が作るもの（サーバー側・待ち受け）と、ガイドが用意するもの（動作確認用フロー等）の
  分担を明記する。「接続先は自分で作るまで存在しない」ことを書く
- 動作確認用フローの接続先 URL が設定ノードに隠れている場合は、どこで確認できるかを書く
- `ws://` などブラウザのアドレスバーで開けないアドレスは、開けないことを演習の近くに書く
- 自作フローと解答例フロー、動作確認用フローを同時にデプロイしたとき、debug サイドバーで
  どれの出力か区別できるよう、debug ノード名に役割（例:「サーバー側:」「クライアント側:」）を付ける
- 成功の条件には、利用者の画面に実際に出るものを書く。データ型もそれに合わせる
  （例: WebSocket・MQTT で届く payload は文字列。「JSONオブジェクトが返ってくる」とは書かない）

### 既存ガイドの修正手順

#### 1. 問題の特定

問題を重大度で分類：
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
# 全ファイル。CI（.github/workflows/deploy.yml）でも同じものが走る
python3 scripts/validate-flow-json.py

# ファイルを絞る場合
python3 scripts/validate-flow-json.py nodered-http-node-guide.html
```

**検証していること**:

このスクリプトは「ソースに書いたJSON」ではなく、**利用者がコピーボタンで受け取るJSON**を
検査する。具体的には、ブラウザの `textContent` を再現した文字列とソースを突き合わせ、
両者が一致するかを見る。

なぜパース成功だけでは足りないのか。生のタグを書いてしまうと、コピーされる文字列からは
タグだけが消える。残った文字列は**JSONとしては valid** なので、`JSON.parse()` も
Node-REDへのインポートも通ってしまう。壊れているのは `template` 等の値の中身だけであり、
それはJSON構文検査では原理的に検出できない。

具体的には次を検出する。

| 検出項目 | 内容 |
| --- | --- |
| 生タグ | ブロック内にHTMLとして解釈される要素・コメント・宣言がある |
| タグ以外の生 `<` | タグとして解釈されない位置（`i < 10` 等）でも、生の `<` がブロック内にある |
| 曖昧な `&` | `&amp;` / `&lt;` / `&gt;` 以外の `&` がある。`&copy;` のように実体参照へ変換されるケースは、コピー結果と `html.unescape` が同じように変換するため突き合わせでは原理的に検出できず、ソースの時点で拒否する |
| 容器の誤り | `flow-json` が `<div>` 以外（`<textarea>` 等）に置かれている |
| 二重エスケープ | パース後の値に `&lt;` / `&gt;` が残っている（`&amp;lt;` と書いた場合） |
| 取りこぼし | class に `flow-json` を持つ要素の個数と、抽出できたブロック数が食い違う（個数は HTMLParser で数えるので、class 属性の引用符の種類や文字参照によらない） |
| 不要な直列化 | function が `msg.payload = JSON.stringify(x)` して、websocket out（ペイロードを送信モード）/ mqtt out に直接渡している |
| 閉じ忘れ | ブロックが閉じられていない |
| 参照切れ | `wires` の接続先IDがフロー内に存在しない |

ブロックの切り出しは正規表現ではなくHTMLパーサで行う。JSON文字列の中に `<div` が現れると、
正規表現によるネスト計数は閉じタグを取り違え、**ブロックを1件も返さないまま成功扱い**になる。
それは検出したい不具合と同じ「静かにすり抜ける」失敗である。

**合格基準**:

- `python3 scripts/validate-flow-json.py` が終了コード 0 を返す
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

### 環境バッジ（☁️ クラウドOK）との整合性

index.html の ☁️ バッジは「https で公開された共有クラウド環境でも、ガイドの主要な
学習手順が成立する」ことの表明である。バッジを裏切ると、初心者は原因を切り分けられない
（実例: サイト独自のテストページが ws:// 固定だったため、https 環境で Mixed Content に
よりブロックされ、「接続中」にならなかった）。☁️ を付けるガイドは次を満たすこと。

- 最初のサンプルフローは公式サンプル（前述の「公式サンプル第一の原則」）を使い、公式の
  設定値はそのまま保持する。公式サンプルが `ws://localhost:1880/...` や
  `http://localhost:1880/...` のようにサーバー内部から自分自身へ接続する値を含む場合、
  内部ポートが 1880 でない共有クラウド環境では動作しない（websocket で実測確認済み）。
  設定値の読み替え案内でしのがず、ガイド自体を 🖥️ へ変更する（websocket / http が該当）。
- サイト独自の応用例で**ブラウザから実行されるコード**（テストページ内の JavaScript 等）は、
  接続先を固定で書かず、ページのプロトコルから自動判定する
  （例: `(location.protocol === "https:" ? "wss://" : "ws://") + location.host`）。
- 本文の説明・URL 例は `localhost:1880` を基準に書き、環境分岐の説明を本文に散在させない
  （共有クラウド利用者向けの読み替え案内は学習環境ガイドへの参照に集約する）。
- これを満たせない内容（OSコマンド実行・専用ポート・実機ハード・公式サンプルの
  localhost ループバック接続など）を扱う場合は、☁️ ではなく ⚠️／🖥️／🍓 の該当バッジへ
  変更する。

### サンプルフローと演習の解答例での function ノード

初心者が標準ノードの使い方を復習できるよう、サンプルフローと演習の解答例では、
標準ノードで書ける処理を function ノードで書かない。function 1つにまとめた解答例は、
コードを読まないと処理の流れが分からず、初心者には分かりにくい。

function ノードを使うかどうかは、次の基準で判断する。

| 基準 | 条件 | 扱い |
| --- | --- | --- |
| A 置き換える | 標準ノードで素直に書ける | 値の生成・加工は change（JSONata 式を含む）、分岐は switch、形式の変換は json / csv 等の専用ノードで書く |
| B function が主題 | function・JavaScript を学ぶガイド（function / function-node2 / javascript-operators / variable-types-2）、または function を使うこと自体が学習内容の演習（catch のエラー発生、complete-status のステータス更新、base64 のバイナリ操作など） | function を残し、処理ごとに日本語のコメントを付ける |
| C 冗長になる | 標準ノードに置き換えると、ノードが5〜6個を超える | function を残し、処理ごとに日本語のコメントを付ける |

- 課題文や要求仕様が「Functionノードで〜」と指定していても、function の役割が付随的なもの
  （入力値の生成、平均の計算など）なら B に当たらない。要件とヒントを標準ノードに書き換えて A で扱う
- 置き換えたら、課題文・要求仕様・ヒントの文言も解答例に合わせて書き換える。
  ヒントに function のコードが残っていると、解答例と食い違う
- 置き換えの前後で、同じ入力に対する出力が変わらないことを、Node-RED で旧フローと新フローを
  動かして確かめる
- 公式サンプルは「公式サンプル第一の原則」に従い、function を含んでいてもそのまま保持する
- 分岐の書き方は、全プロジェクト共通の「Node-RED フロー可読性ルール」（分岐は switch で
  表現する）にも従う

### Dashboard 2.0 のフロー

Dashboard 2.0 では、`/dashboard` にダッシュボード設定ノード（ui-base）が2つ以上あると、
先に作られた1つのページしか配信されない（Dashboard 1.32.0 で実測）。利用者が複数のガイドの
フローを読み込んでもページが消えないよう、サイトの Dashboard 2.0 のフローはすべて
1つの ui-base を共有する。新しいフローを作るとき・既存のフローを直すときは、次をすべて守る。

- **ui-base の ID は `c2e1aa56f50f03bd` にする**。公式ドキュメントのサンプル（FlowFuse の
  `docs/examples`）と同じ ID で、サイトの全フローがこれを使う。新しい ID の ui-base を作らない
- **ui-base 以外の ID は、サイト内の他のどのフローとも重ねない**。タブ・通常ノード・ui-page・
  ui-group・ui-theme が対象で、ガイドごとの接頭辞（例: `d2viz_`）を付ける。
  例外は、中身が同一の公式テーマ（`129e99574def90a3`、`afa24cae12543ca5`、`c2ff5ba1f92a0f0e`）だけ
- **ページのパスはサイト全体で一意にする**。ui-page・ui-group を複数のガイドで共有しない
- **設定ノードは ui-base → ui-theme → ui-page → ui-group の順に並べる**
- 各ガイドの「📌 複数のフローを読み込むとき」の案内（`<div class="tip">`）を残す。
  Dashboard 2.0 のフローを含む新しいガイドにも、サンプルフローと演習の節の冒頭に同じ案内を入れる

ID を重ねてはいけない理由: 読み込むフローの ID が1つでも既存のものと重なると、エディタは
「読み込もうとしているノードのいくつかは、既にワークスペース内に存在しています。」と通知し、
利用者は「コピーを読み込み」を選ぶ。このとき、まだ存在しない設定ノードには新しい ID が振られる。
最初に読み込んだ Dashboard 2.0 のフローでこれが起きると、ui-base が共有の ID で作られず、
以後のフローの ui-base と2つに分かれる。ui-base 以外のすべての ID が重ならなければ、
最初の読み込みでは通知が出ず、ui-base は共有の ID のまま作られる。2つ目以降は ui-base などが
重なって通知が出るが、「コピーを読み込み」は同じ ID の既存の設定ノードを再利用するので、
ページは1つのダッシュボードにまとまる。

ページ・グループを共有してはいけない理由: 2つ目以降の読み込みは「コピー」になるため、
まだ存在しないページには新しい ID が振られる。2つのガイドが同じページを共有していると、
同じパスのページが別の ID で2つできる。

設定ノードの並び順の理由: 「コピーを読み込み」では、エディタの依存順の並べ替えが働かない
（Node-RED 5.0.7 の `importNodes`）。参照先より先に追加された設定ノードは参照先の利用者として
登録されず、使用中のページやテーマがエディタの設定ノード画面で「未使用」と表示される。
案内では「未使用の設定ノードを削除する」手順を書いているため、利用者が使用中のページを
消してしまう。

ui-base の設定値（ヘッダーやメニューの表示）は、最初に読み込んだフローのものが使われる。
演習で ui-base の設定値そのものを教材にしない。

**検査**: 上の決まり（ui-base の ID と参照先、設定ノードの並び順、ID とページのパスの一意性、
案内の有無）は `python3 scripts/check-dashboard-flows.py` で検査する（CI でも実行する）。
ID の一意性はファイルをまたぐため、常にサイトの全 HTML が対象になる。フローを編集したら、
編集を終えた時点で必ず実行する（途中で実行しただけでは、あとから足した ID の重なりを見落とす）。

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

### ノード図（node-example）

処理の流れを示すノード図（`<div class="node-example">`）は、Node-RED エディターの
ノードと同じ見た目（ノードの色、アイコン、入出力ポート、灰色の配線、方眼のワークスペース）で
描く。見た目はサイト共通の `css/node-diagram.css` で決め、ページの `<style>` には
ノード図の規則を書かない。各ページは `<head>` で
`<link rel="stylesheet" href="css/node-diagram.css">` と
`<script src="js/node-diagram.js" defer></script>` を読み込む。分岐・合流・複数の出力ポートからの
配線は、このスクリプトがエディターと同じ曲線で描く（スクリプトが動かない環境では直線のまま）。

**書き方**:

```html
<div class="node-example">
    <span class="node node-inject">Inject</span>
    <span class="arrow">→</span>
    <span class="node node-function">Function<br><small>(加工)</small></span>
    <span class="arrow">→</span>
    <span class="node node-debug">Debug</span>
</div>
```

| 部品 | 書き方 | 表すもの |
| --- | --- | --- |
| ノード | `<span class="node node-種類">名前</span>` | 種類ごとの色・アイコン・ポートで描く。補足は `<br><small>` |
| 配線 | `<span class="arrow">→</span>` | 灰色の線。矢印の文字は描かない |
| 複数の msg | `<span class="arrow multi">→→→</span>` | 線の上に msg を 3 つ描く（split の出力など） |
| 時間をおいて届く | `<span class="arrow delayed">⋯→</span>` | 点線 |
| 途中で止まる | `<span class="arrow broken">✗</span>` | 線の上に ✗ |
| link の仮想配線 | `<span class="arrow-dashed">- - -</span>` | 破線（エディターと同じ） |
| 配線の途中の説明 | `<span class="wire-label">正常完了</span>` | 線と線の間に置く小さい文字 |
| 分岐 | `<span class="branch">` の中に `<span class="branch-row">` を並べる | 直前のノードの出力ポートから複数のノードへ。点線にするときは `branch dashed` |
| 複数の出力ポート | `class="node node-switch outputs-3"` | switch・function・trigger など、設定で出力の数が変わるノードに付ける。exec（3）・modbus（2）など数が決まっているノードは CSS が自動で描く |
| ポートの指定 | `<span class="branch-row" data-port="2">`、`<span class="arrow" data-port="3">` | その配線を何番目の出力ポートから出すか。省略すると、分岐は行の順、直線は 1 番目 |
| 合流 | `<span class="merge">` の中に `<span class="merge-row">` を並べる | 複数のノードから1つのノードへ |
| 届かないノード | `class="node node-debug unreached"` | 赤い点線の枠 |
| ステータス | ノードの中に `<span class="status-label">接続中</span>` | ノードの下の緑の点と文字 |
| 注記 | `<span class="diagram-note">…</span>`（赤字は `diagram-note error`） | 図の中の説明 |

- 分岐・合流・複数行の図を、`margin-left` の px や `visibility: hidden` の箱で
  位置合わせしない。ノードの幅が変わると崩れる。`branch` / `merge` を使う
- **出力が複数あるノードは、ポートを出力の数だけ描き、ポートごとに配線する**。
  1つの配線を途中で分けて、別々の出力に見せない（エディターでは出力ごとにポートがある）。
  1つのポートから複数のノードへ配線するのは、同じ msg を複数のノードへ送るときだけ
- 図の配線は、そのガイドのサンプルフローの実際の配線（`wires`）と合わせる。
  サンプルで出力が3つに分かれているのに、図で1つの Debug にまとめない
- ノードのクラスは、ラベルではなく**実際のノードの種類**に合わせる
  （例: 「mqtt in」を node-inject で描かない。「file read」は node-file-in）。
  図はアイコンでも種類を示すため、食い違いが目に付く
- ノードの色・アイコン・ポートの有無は、ノードのエディター HTML の
  `RED.nodes.registerType()`（color / icon / inputs / outputs / align）に合わせる。
  ノードの種類を追加するときは `scripts/gen-node-diagram-css.py` の対応表に1行足して
  実行し、`css/node-diagram.css` を生成し直す。CSS を直接編集しない。
  アイコンは `img/node-icons/` に置き、出典を同じフォルダの README.md に書く
- 箱をインライン style で塗り替えない（エディターではノードの色は変わらない）。
  状態は `unreached` などの部品で表す

**検査**: 次の誤りは HTML としては正しく、ソースを読むレビューでも
フローの検証でも見つからないため、スクリプトで検査する（CI でも実行する）。

```bash
python3 scripts/check-node-colors.py          # 未定義のクラス、コントラスト、opacity
python3 scripts/gen-node-diagram-css.py --check  # 共有 CSS が対応表と一致するか、アイコンがあるか
```

- **未定義のクラスを使わない**: 使ったクラスが `css/node-diagram.css`（またはページの CSS）に
  無いと、箱に色もアイコンも付かない
- **文字と背景のコントラスト比を 4.5 以上にする**（WCAG 2.x AA）。箱の文字は 14px で
  「大きい文字」に当たらない。文字色は共通で `#212121`
- **箱を opacity で薄くしない**: 下の背景と混ざって読めなくなる
- 検査が判定できない書き方がある。rgb() や CSS 変数の色、CSS 規則側の opacity は
  検査されないため、そう書いたときは描画して確かめる

**レビューでの扱い**: 見た目に関わる変更（CSS、色、図、レイアウト）は、レビュー依頼で
「描画したときに読めるか」も確認対象に含め、可能ならヘッドレスブラウザで描画して確かめる。

**重なりの検査**: 図形が文字に重なって、見せたい文字が隠れていないかは
`python3 scripts/check-overlap.py` で調べる（Chrome が必要なため CI では実行しない）。
パソコンの幅（1200px）とスマートフォンの幅（390px）で全ページを描画し、文字の上に
別の要素が重なっている箇所を報告する。図やレイアウトを変えたら実行する。
重なりやすい書き方:

- 位置を `left: 10%` で指定した丸やバー。左端の位置なのか中心の位置なのかをそろえ
  （中心にするなら `transform: translateX(-50%)`）、文字を持つ要素を `z-index` で手前に置く
- `bottom: -20px` のように上へ伸びる位置指定。2行の文字が上の図形に重なる。下へ伸ばす（`top: 100%`）
- `position: absolute` で横に並べたラベル。狭い画面でぶつかる。flex などで並べる
- 回転（`transform: rotate`）させた箱。箱の幅のまま回るので、まわりに重なる

### 動作の図（顔つきノードの図）

各ノードガイドには、セクション1の末尾に「動作を図で見る」を置き、msg がどう入って
どう出ていくかを図で示す。ノードに顔を付けて擬人化し、入ってくる msg と出ていく msg を
カードや封筒で描く。困り顔はエラー、笑顔はふつうの動作を表す。

**作り方**:

- 図はインライン SVG だが、HTML に手で書かない。`scripts/comic/figures/*.py` に定義し、
  `python3 scripts/comic/build.py` で生成する
- HTML 側は `<!-- comic:begin キー -->` と `<!-- comic:end -->` の間が生成箇所。
  ここを直接編集しても、次の生成で上書きされる
- 共通部品は `scripts/comic/lib.py` にある（`nrnode` 顔つきノード、`msgcard` msg のカード、
  `packet` 小さな msg、`pc` と `server` 顔つきの機器、`wire` 配線など）
- `Panel` の第 1 引数（aria-label）には、図が示すことを 1 文で書く。
  `<figcaption>` には短い要約を書く

**正確さ**:

- 図に描く挙動は、ノードのソース（`.js`）で確かめてから描く。既定値を描くときは
  エディター HTML の `defaults` で確かめる。図は文章より印象に残るため、誤りの影響が大きい
- 設定で挙動が変わるノードは、既定の動作を描き、既定以外を描くときは図の中か説明文に
  その設定を書く（例: csv の「1行目に列名を含む」をオンにした場合）

**検査**:

```bash
# 図の定義と HTML が食い違っていないか（CI でも実行する）
python3 scripts/comic/build.py --check
```

---

## ドキュメント体系

### ドキュメント間の関係

```
CLAUDE.md（本ファイル）
├── プロジェクト全体の開発ガイド
├── ガイド作成・修正の手順
├── 品質基準の定義
└── トラブルシューティング

README.md
├── プロジェクト概要
├── セットアップ方法
└── コントリビューション
```

### 各ドキュメントの使い分け

| 状況 | 参照するドキュメント |
|------|---------------------|
| 新規ガイドを作成したい | CLAUDE.md（開発ワークフロー・品質基準） |
| 既存ガイドに問題を発見 | CLAUDE.md（既存ガイドの修正手順） |
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
- `docs`: ドキュメント（README、CLAUDE.md更新）
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

**JavaScript（教材コード）**:

学習者が読み書きするコードは、現在のJavaScriptの書き方に合わせる。

- 変数宣言は `const` を第一候補とし、再代入するものだけ `let` にする。`var` は使わない
- 再代入の判定に注意する。`array.push()` / `obj.prop = x` / `date.setDate()` は
  参照先の変更であって変数への再代入ではないため、`const` のままでよい
- ループ変数（`for (let i = 0; ...)`）とインクリメント（`count += 1`）は `let`
- **ノードが自動でやる処理を function で書かない**。websocket out / mqtt out /
  http response はオブジェクトの `msg.payload` を自動で直列化するため、直前の function で
  `JSON.stringify` しない（http response では Content-Type も JSON でなくなる）。
  `python3 scripts/validate-flow-json.py` は websocket out / mqtt out の場合を検出する
  （http response は JSONP やヘッダー指定で結果が変わりうるため、目視で確認する）。他のノードの挙動を説明・利用する
  ときも、ノードのソース（`.js`）で実際の処理を確認してから書く

次の3つは例外として `var` を残す。

| 例外 | 理由 |
|------|------|
| 公式サンプル | 公式のコードをそのまま保持する（「公式サンプル第一の原則」） |
| 悪い例の教材 | `var` の問題を説明するために提示しているコードそのもの |
| 開発者ツールのConsole用コード | Consoleではトップレベルの `const` / `let` を再宣言できないブラウザがあり（Firefox、現行安定版のSafari）、同じコードを貼り直すとエラーになる |

Console用コードで `var` を使うときは、**なぜそこだけ `var` なのかを本文に書く**。
書かないと、サイトの他の箇所と矛盾しているように見える。

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

#### 問題5: コピーしたフローからHTMLタグが消える

**症状**: サイトのコピーボタンで取得したフローをNode-REDに読み込むと、`template` ノードの
HTMLからタグだけが消え、CSSや文字列がそのまま画面に表示される。

**原因**: `<div class="flow-json">` に生のタグを書いている。`div` の中身はHTMLとして
解釈されるため、ブラウザがタグをDOM要素に変換してしまう。コピーボタンは `textContent` を
読むので、利用者にはタグの抜けた文字列が渡る。

**紛らわしい点**: 破損してもJSONとしては valid なままなので、`JSON.parse()` による検証も
Node-REDへのインポートも成功する。ソースを目視しても正しく見える。**チャットやツール経由の
コピペでサニタイズされたわけではない**。

**解決方法**: フローJSON内の `<` を `&lt;` に、`&` を `&amp;` にエスケープする。
`python3 scripts/validate-flow-json.py` で検出できる。

**切り分け**: `curl -i http://<host>:1880/page` でレスポンス本文とヘッダーを直接見る。
`<h1>` などのタグが返ってくればテンプレートは正常で、原因は `Content-Type` 側にある。
ブラウザのレンダリング結果だけでは、タグが無いのかContent-Typeが違うのか区別できない。

#### 問題6: 教材コードの一括置換で、変えてはいけない箇所まで書き換わる

**症状**: `var` を `const` に変換するような一括置換を行ったところ、公式サンプルや
日本語の説明文まで書き換わった。

**原因と対策**:

**(1) 公式サンプルの判定はタブ単位で行う**

公式サンプルかどうかを、Node-RED本体の `examples` ディレクトリのコードと照合して
判定する場合、**ノード単位で照合すると取りこぼす**。公式サンプルは複数のJSONファイルに
分かれており、ガイド側はそれを1つのタブに統合しているため、統合後のタブには公式ファイルの
どれにも載っていないノードが含まれることがある。

タブ内のいずれか1つでも公式コードと一致したら、**そのタブ全体を対象外**にする。

```python
# 公式exampleのコードを集める
official = set()
for root, _, files in os.walk(EXAMPLES_DIR):
    ...  # func / initialize / finalize を空白正規化して収集

# タブ単位で判定する
is_official_tab = any(normalize(n.get(f) or "") in official
                      for n in tab_nodes for f in ("func", "initialize", "finalize"))
```

**(2) 日本語を含むファイルで `\w` を使わない**

Python の `\w` は Unicode 対応のため、日本語にもマッチする。次の正規表現は
「`var` は予期しない動作を…」というコメントの「は」を変数名と解釈し、
`// const は予期しない動作を…` という**意味が反転した書き換え**を起こす。

```python
re.sub(r'\bvar (\w+)', ...)        # ❌ 「var は」にマッチする
re.sub(r'\bvar ([A-Za-z_$][A-Za-z0-9_$]*)', ...)   # ✅ 識別子だけにマッチする
```

**検出方法**: 置換後に、追加行で `const` / `let` の直後に非ASCII文字が来ていないか確認する。

```bash
git diff -U0 | grep -E '^\+' | grep -E '(const|let) [^A-Za-z_$]'
```

**(3) 置換後は必ず差分を1対1で突き合わせる**

削除行と追加行を並べ、**キーワード以外に差分がないこと**を確認する。
そのうえで、フローJSON内の `func` / `initialize` / `finalize` をすべて
`node --check` にかけ、実機にデプロイして動作を確認する。構文チェックだけでは
スコープの誤り（`try` 内で宣言した変数を外から参照するなど）を検出できない。

---

## メンテナンス

### 定期監査スケジュール

**四半期ごと（3ヶ月に1回）**:
- [ ] 全ガイドファイルのJSON検証
- [ ] プロパティ表とソースコードの照合（サンプリング20%）
- [ ] Node-REDエディターでインポートテスト（サンプリング10%）
- [ ] 新規発見問題を記録し対応

**年次（1年に1回）**:
- [ ] 全ガイドファイルの完全監査
- [ ] Node-REDバージョンアップ対応
- [ ] Dashboard 2.0更新対応
- [ ] ドキュメント（README、CLAUDE.md）の見直し

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
重大度を判定
  ↓
優先度に応じて対応
  ├── CRITICAL: 即座に修正
  ├── HIGH: 1週間以内に修正
  ├── MEDIUM: 1ヶ月以内に修正
  └── LOW: 次回監査時に修正
  ↓
修正実施（本ガイドの手順に従う）
  ↓
検証（JSON、ソースコード照合、インポートテスト）
  ↓
コミット・デプロイ
```

---

## 付録

### 便利なコマンド集

**JSON検証（一括）**:
```bash
python3 scripts/validate-flow-json.py
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
| 2026-09-25 | 1.1.0 | 条件付き表示欄の表示条件、演習の動作確認経路、自動直列化ノード前の JSON.stringify 禁止を追加 |
| 2026-09-28 | 1.2.0 | 各ノードガイドの「動作を図で見る」と、図の生成スクリプト（scripts/comic）の決まりを追加 |
| 2026-10-02 | 1.3.0 | ノード図の色（未定義クラスとコントラスト）の決まりと検査を追加 |
| 2026-10-02 | 1.4.0 | サンプルフローと演習の解答例での function ノードの使い方の基準と、Dashboard 2.0 のフローで ui-base を共有する決まりを追加 |
| 2026-10-02 | 1.5.0 | Dashboard 2.0 のフローの決まりを検査する scripts/check-dashboard-flows.py を追加 |
| 2026-10-03 | 1.6.0 | ノード図を Node-RED エディターの見た目に統一し、共有 CSS（css/node-diagram.css）と部品の書き方を追加 |
| 2026-10-03 | 1.7.0 | 複数の出力ポートと配線のスクリプト（js/node-diagram.js）、重なりの検査（scripts/check-overlap.py）を追加 |

---

**作成者**: Claude Sonnet 4.5
**最終更新**: 2026-10-03
