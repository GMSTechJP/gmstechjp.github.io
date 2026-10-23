#!/usr/bin/env bash
# 空の Node-RED を起動し、scripts/test-flows.py でガイドのフローを実際に動かす（CI 用）。
#
# 手元で CI と同じ手順を試すときは、使っている Node-RED や読み込み済みのフローと
# 重ならないよう、エディターのポートと TCP・UDP のポートをずらす。
#   NODE_RED_PORT=18800 PORT_OFFSET=20000 bash scripts/ci-flow-tests.sh
#
# 終了コードは test-flows.py と同じ（0 = 合格、1 = 不合格、2 = 実行できなかった）。
set -euo pipefail

NODE_RED_VERSION=5.0.7
NODE_RED_PORT="${NODE_RED_PORT:-1880}"
PORT_OFFSET="${PORT_OFFSET:-0}"
WORK="$(mktemp -d "${RUNNER_TEMP:-${TMPDIR:-/tmp}}/node-red.XXXXXX")"
LOG="$WORK/node-red.log"

# 指定のポートで別の Node-RED（普段使っているものなど）が動いていると、その応答を
# 起動した Node-RED のものと取り違え、テスト用のフローを追加してしまう。起動の前に止める
if curl -s -m 2 -o /dev/null "http://localhost:$NODE_RED_PORT/"; then
    echo "ポート $NODE_RED_PORT は使用中。NODE_RED_PORT で空いているポートを指定する"
    exit 2
fi

npm install --prefix "$WORK/app" --no-audit --no-fund --loglevel=error "node-red@$NODE_RED_VERSION"

"$WORK/app/node_modules/.bin/node-red" --userDir "$WORK/user" --port "$NODE_RED_PORT" > "$LOG" 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT

# 管理 API が応答するまで待つ（最大 60 秒）
for _ in $(seq 1 60); do
    if curl -sf -m 2 "http://localhost:$NODE_RED_PORT/settings" > /dev/null; then
        break
    fi
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "Node-RED が起動しなかった"
        cat "$LOG"
        exit 2
    fi
    sleep 1
done
if ! curl -sf -m 2 "http://localhost:$NODE_RED_PORT/settings" > /dev/null; then
    echo "Node-RED が 60 秒たっても応答しない"
    cat "$LOG"
    exit 2
fi
# 応答したのが、起動した版の Node-RED で、そのプロセスがまだ動いていることを確かめる
VERSION="$(curl -sf -m 2 "http://localhost:$NODE_RED_PORT/settings" \
    | python3 -c 'import json, sys; print(json.load(sys.stdin).get("version", ""))')"
if [ "$VERSION" != "$NODE_RED_VERSION" ] || ! kill -0 "$PID" 2>/dev/null; then
    echo "応答した Node-RED が、起動したもの（$NODE_RED_VERSION）でない（版: ${VERSION:-不明}）"
    cat "$LOG"
    exit 2
fi

status=0
python3 scripts/test-flows.py --url "http://localhost:$NODE_RED_PORT" --port-offset "$PORT_OFFSET" || status=$?
if [ "$status" -ne 0 ]; then
    echo "----- Node-RED のログ -----"
    cat "$LOG"
fi
exit "$status"
