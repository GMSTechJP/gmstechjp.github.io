# 作業引き継ぎノート（設定項目表 H 監査）

別端末・別セッションへ作業を引き継ぐためのノート。設定項目表をスタイルガイド
カテゴリ H へ準拠させる作業の現状と進め方をまとめる。作業が一段落したら本ファイルは
更新するか削除してよい。

最終更新：2026-06-29

## 真実の情報源

進捗と基準の正本は次の 2 ファイル（いずれも `main` に push 済みで、`git pull` で取得できる）。

- [settings-audit.md](settings-audit.md) … H 監査の是正チェックリスト（ノードごとの状態 `[ ]`/`[x]`）
- [style-guide.md](style-guide.md) … カテゴリ H の基準と「適用状況」テーブル

本ノートの進捗欄と上記が食い違ったら、上記 2 ファイルを正とする。

## 進捗（D1〜D3 標準ノード 24 本 ＋ contrib）

| グループ | 状態 |
| --- | --- |
| ① 確実に要修正 12 本 | 完了 |
| ② 軽微な不一致 3 本（batch / json / link） | 完了 |
| ③ 概ね準拠 4 本（catch / http / csv / function） | 完了 |
| ④ contrib | base64・email・modbus 完了。残り **mqtt** |
| 次フェーズ | dashboard2 ウィジェット 6 本（未着手） |

base64・email はいずれもエディターが日本語化済みだったため、英語併記ではなく実日本語
ラベルへ是正した（email は locale 未翻訳の Auth type / Token / Format to SASL のみ
「英語ラベル（日本語訳）」形式）。

## 残タスク

| 区分 | ノード | 補足 |
| --- | --- | --- |
| ④ contrib | mqtt | 標準ノードだが大きい。本体の設定表を個別に精査する（自動抽出では Will 表しか拾えない） |
| 次フェーズ | dashboard2 ウィジェット 6 本 | ui-led / widgets-display / widgets-input / widgets-visualization / widgets-advanced-part1 / widgets-advanced-part2 |

## 作業手順（ソース照合パイプライン）

1 ノードずつ、ソースを照合してから書く。エージェントへ一括で任せない。

1. ノードの `<node>.html` を取得し、`data-i18n` キーを抽出する。
2. ja と en-US の locale を取得して差分を取り、各ラベルが日本語化済みか英語へ
   フォールバックするかを判定する。
3. 日本語化済みの項目は、その日本語表示をそのまま見出しに使う。英語のままの項目だけ
   「**English Label**（日本語訳）」形式にする。
4. `defaults` のアクティブなプロパティを抜け・重複なく網羅し、エディターのタブや
   セクションの区切りに合わせてグループに分ける。
5. サンプルフロー（`<textarea>` 内の JSON）は編集後にパースが通ることを確認する。

ソース取得元の例（node-red-nodes モノレポ）：

```
https://raw.githubusercontent.com/node-red/node-red-nodes/master/<category>/<node>/<file>.html
https://raw.githubusercontent.com/node-red/node-red-nodes/master/<category>/<node>/locales/ja/<file>.json
https://raw.githubusercontent.com/node-red/node-red-nodes/master/<category>/<node>/locales/en-US/<file>.json
```

ファイル名やパスが不明なときは GitHub の git trees API で探す。

```
https://api.github.com/repos/node-red/node-red-nodes/git/trees/master?recursive=1
```

## 運用ルール

- 公開リポジトリ。機密情報・API キーを含めない。
- 設定項目の節はエージェントへ丸投げしない。1 ノードずつソースと挙動を確認して書く。
- 1 ファイル＝ 1 コミット（`refactor:` または `docs:`）。コミットしたら push する。
- 設定項目名はエディターの実表示に完全一致させる。助詞始まりの機械翻訳調ラベルを使わない。
- 設定項目表だけでなく、本文・コード例・演習・トラブルシュートに残る旧ラベルも同時に直す。
- 完了したら settings-audit.md の該当行を `[x]` にし、style-guide.md の適用状況へ反映する。

## ローカル作業環境メモ（端末依存。git では同期されない）

別端末では次が引き継がれない。必要に応じて再取得・再設定する。

- `/tmp/claude/` 配下の検証スクリプト（flow-json バリデータ）、ソース HTML キャッシュ、
  `ja-messages.json`（node-red 標準ノードの ja locale）。標準ノードのラベル解決に使う
  ため、必要なら再取得する。
- リポジトリ直下の未追跡ファイル `AGENTS.md`（プロジェクト開発ガイドのミラー）と
  `NodeREDガイド作成/` ディレクトリ。git 管理外なので別端末へは転送されない。
- グローバル `~/.claude/` 設定（プロジェクト外の CLAUDE.md・memory・フック）。
  この環境では Claude Code の作業規約（初回操作時の事実提示ゲート、push 時の
  サンドボックス無効化など）がここに依存する。別端末で同じ挙動にするには同設定の
  同期が要る。
