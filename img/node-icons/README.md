# ノードのアイコン

ガイドのノード図（`node-example`）で、ノードの左端（または右端）に表示するアイコン。
図の見た目を Node-RED エディターに合わせるため、各ノードのパッケージに含まれる
アイコンをそのまま使っている。どのノードにどのアイコンを使うかは
`scripts/gen-node-diagram-css.py` の対応表で決める。

## 出典とライセンス

| ファイル | 出典 | ライセンス |
| --- | --- | --- |
| `fa-` で始まらない `.svg`（`inject.svg`、`debug.svg` など。下の行のものを除く） | Node-RED 5.0.7 `@node-red/nodes/icons/` | Apache-2.0 |
| `ui-gauge.svg`、`ui-markdown.svg` | `@flowfuse/node-red-dashboard` 1.32.0 `nodes/widgets/icons/` | Apache-2.0 |
| `fa-*.svg` | Font Awesome 4.7（Node-RED エディターが同梱する `fontawesome-webfont.svg`）のグリフを、40×60 の SVG に変換したもの。Dashboard 2.0 などのノードが `font-awesome/fa-*` で指定するアイコン | SIL OFL 1.1 |
| `parser-base64.png` | `node-red-node-base64` 1.0.0 | Apache-2.0 |
| `sqlite.png` | `node-red-node-sqlite` 2.0.1 | Apache-2.0 |
| `ftp.png` | `node-red-contrib-ftp-server` 1.0.4 | MIT |
| `modbus.png` | `node-red-contrib-modbus` | BSD-3-Clause |

email・pi-sense-hat・ftp（クライアント）の各ノードは、Node-RED 本体のアイコン
（`envelope.svg`、`rpi.svg`、`file.svg`）を使う。

Font Awesome: Copyright Dave Gandy, https://fontawesome.com/v4/license/
