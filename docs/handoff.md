# 作業引き継ぎノート

別セッションへ作業を引き継ぐためのノート。現在地と残タスクだけを置く。
作業が一段落したら本ファイルは更新するか削除してよい。

最終更新：2026-08-21

## 真実の情報源

- [style-guide.md](style-guide.md) … 文章と図解の基準、および「適用状況」テーブル
- [settings-audit.md](settings-audit.md) … 設定項目表 H 監査のチェックリスト
- [roadmap.md](roadmap.md) / [../requirements.md](../requirements.md) … ガイド追加テーマの設計と要件

本ノートと上記が食い違ったら、上記を正とする。

## 直前に完了した作業（2026-08-21）

設定項目表の H 監査は **全対象完了**（dashboard2 ウィジェット 6 本を含む）。
詳細は settings-audit.md と style-guide.md の適用状況を参照。

演習の「作る範囲」図を新設し、通信系ガイドへ横展開した。

| ガイド | 内容 |
| --- | --- |
| http | 演習を 4 件から 7 件へ（演習3 POST受信、演習5 外部APIラップ、演習7 社内LAN2人組を追加）。全演習に図 |
| mqtt / websocket / tcp / udp / ftp-sftp / email | 演習ごとに図を追加 |
| modbus | 4 件とも同一構造のため、節の冒頭に図を 1 つ |

---

## 残タスク

### 1. Node-RED への実インポート検証（未実施・優先度高）

本セッションで **新規作成したフロー JSON 4 本** が、実際に Node-RED で動くかを未検証。

| 対象 | ファイル |
| --- | --- |
| 演習3 解答例（POST受信） | nodered-http-node-guide.html |
| 演習5 解答例（外部APIラップ） | 同上 |
| 演習7 解答例（サーバー担当） | 同上 |
| 演習7 解答例（クライアント担当） | 同上 |

未実施の理由：ローカルの Node-RED へタブを作るとデプロイで稼働中フローが再起動するため、
利用者の許可を取っていない。許可を得てから行う。

- 手順：タブ作成 → `curl` で応答確認 → タブ削除
- 演習7 は本来 2 台必要。1 台で確認するならクライアント側の URL を
  `http://localhost:1880/api/hello` にして疎通だけ見る
- **他ガイド（mqtt 等 6 本）は図の追加のみでフロー JSON は無改変**。インポート検証は不要
- 静的検証は全て通過済み（`validate-flow-json.py` 56 ファイル 0 件、
  Function コードは `node --check` 通過、`wires` の参照切れなし）

### 2. 文章推敲（style-guide B〜G）の未適用ガイド 28 本

style-guide.md の適用状況テーブルに文章推敲として載っていないもの。

```
buffer-parser / ftp-sftp / git-basics / git-install-windows /
linux-basics / linux-commands / linux-directory / linux-glossary /
pi-sense-hat / plc-register / production-operation / split / sqlite /
switch / tcp / template / trigger / udp / watch / websocket / xml / yaml /
dashboard2-ui-led / dashboard2-widgets-advanced-part1 /
dashboard2-widgets-advanced-part2 / dashboard2-widgets-display /
dashboard2-widgets-input / dashboard2-widgets-visualization
```

dashboard2 の 6 本と上記の一部は **H（設定項目）は適用済み**だが、B〜G の文章推敲は未適用。
今回図を入れた websocket / tcp / udp / ftp-sftp もこの群に含まれる。図の日本語はガイドの
トーンに合わせたが、周囲の本文は未推敲のまま残っている。

**絵文字を機械的に消さないこと。** style-guide B は「図解の中のアイコンは残してよい。
内容に対応するアイコン（手紙＝📮、電話＝📞 など）は図の一部であり、装飾ではない」と
定めている。パイロット適用済みの network-basics に残る `📮 手紙を送る` `📞 電話で話す` は
この例外として意図的に残されたもの。1 本ずつ判断する。

参考までに機械検出した件数（上記の例外を含むため上限値であり、そのままの作業量ではない）。

| 検出対象 | 件数 |
| --- | --- |
| 見出し（h1〜h4）先頭の絵文字 | 362 件 / 34 ファイル |
| callout（tip / important / warning）先頭の絵文字 | 126 件 / 20 ファイル |

なお `<summary>` 先頭の絵文字（`💡 ヒント` `✅ 解答例フロー` など）は 54 ファイル 478 件あり、
文章推敲を適用済みの http にも残っている。**サイト共通の作法として定着しているため
是正対象に含めない。**

### 3. mqtt ガイドの「あなたの名前」（style-guide E）

style-guide E は「読者を『あなた』と呼ばない」と定めるが、MQTT トピックの例に
`あなたの名前/test/hello` という表記が残っている。

| ファイル | 件数 |
| --- | --- |
| nodered-mqtt-node-guide.html | 4 件 |
| nodered-learning-environment-guide.html | 1 件 |

同じトピック表記を 2 ファイルで使っているため、**片方だけ直すと不整合になる**。
両方まとめて「自分の名前」等へ置き換える。演習の解答例フロー内の topic 文字列も対象。

### 4. 「作る範囲」図の CSS が 8 ファイルへ重複

サイトは 1 ファイル完結構造（各 HTML が自前の `<style>` を持つ）のため、`.sys-map` 系の
CSS を 8 ファイルへ個別に複製している。図の見た目を変えるときは 8 ファイルすべてを直す。

対象：http / mqtt / websocket / tcp / udp / modbus / ftp-sftp / email

生成用のヘルパを [../scripts/sysmap.py](../scripts/sysmap.py) に置いた。CSS の定義もこの
ファイルにあるので、変更するときはここを直してから各ガイドへ反映する。

---

## 「作る範囲」図の作法

横展開や新規ガイドで図を足すときの判断基準。

- **ノードの並びを描かない。** 登場人物とその役割だけを描く。ノード構成を図にすると、
  演習に取りかかる前に答えを見せてしまう（この理由で一度作り直している）
- 通信を**始める側を左**、受ける側を右に置く
- 作る対象に `sys-build` と「これを作る」バッジを付ける。外部サービスや相手側は
  「既にあるもの」「先に用意しておくもの」と役割欄に明記する
- 矢印のラベルは**プロトコル上を流れるもの**にする（msg のプロパティ名は書かない）。
  ラベル文字列に `→` を含めない（ヘルパが末尾に矢印を付けるため二重になる）
- 役割が演習ごとに変わるガイドは**演習ごと**に置く。全演習が同一構造なら**節の冒頭に 1 つ**
  （modbus がこの例）
- 演習の**課題文にもノード名を書かない**。構成はヒント側へ寄せる

### 役割の確定方法

課題文の印象で判断せず、**解答例フローのノード型で確定する**。実例として、tcp ガイドの
演習4 は「2台のNode-RED間通信」という題だが、実体は 1 フロー内で完結していた
（`tcp in` と `tcp request` が同じタブにある）。図では 2 つの箱の役割欄に
「同じNode-RED内」と明記して食い違いを補っている。

### 検証

```bash
python3 scripts/validate-flow-json.py          # フローJSON（56ファイル）
```

図を足したらブラウザで開き、各図の `scrollWidth` と `clientWidth` を比較して
**横スクロールが出ていないこと**を確認する（コンテンツ幅は 896px）。HTML のタグ整合と
内部リンク切れの検査は `scripts/sysmap.py` の `verify()` を使う。

---

## 運用ルール

- 公開リポジトリ。機密情報・API キーを含めない。
- 設定項目の節はエージェントへ丸投げしない。1 ノードずつソースと挙動を確認して書く。
- 1 ファイル＝ 1 コミット。コミットしたら push する。
- 設定項目名はエディターの実表示に完全一致させる。
- 仕様の裏取りは Node-RED のソースで行う（例：`uiHost` の既定値が `0.0.0.0` であることは
  `packages/node_modules/node-red/red.js` の該当行で確認した）。

## ローカル作業環境メモ（端末依存。git では同期されない）

- リポジトリ直下の未追跡ファイル `AGENTS.md`（開発ガイドのミラー）と
  `NodeREDガイド作成/` ディレクトリ。git 管理外なので別端末へは転送されない。
- グローバル `~/.claude/` 設定（プロジェクト外の CLAUDE.md・memory・フック）。
  初回操作時の事実提示ゲートや push 時のサンドボックス無効化はここに依存する。
