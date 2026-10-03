/*
 * ノード図（node-example）の配線を、Node-RED エディターと同じ曲線で描く。
 *
 * CSS（css/node-diagram.css）だけでは、配線は水平な直線でしか描けない。そのため、
 * 次の配線をこのスクリプトが SVG の曲線で描き直す。
 *   - 分岐（.branch）: 直前のノードの出力ポートから、各行（.branch-row）の先頭へ。
 *     ノードの出力ポートが複数あれば、行ごとに別のポートから出す（data-port で指定）
 *   - 合流（.merge）: 各行（.merge-row）の末尾から、直後のノードの入力ポートへ
 *   - 出力ポートが複数あるノードの直後の配線（.arrow）: data-port のポートから、次のノードへ
 * 出力ポートの数は CSS の --node-outputs（exec などの決まった数、または outputs-N）から読む。
 * 曲線の形はエディターの view.js（generateLinkPath）に合わせている。
 * スクリプトが動かない環境では、CSS の直線の表示のまま残る。
 */
(function () {
    "use strict";

    var SVG_NS = "http://www.w3.org/2000/svg";
    var PORT_GAP = 13;      // 出力ポートの間隔（エディターと同じ）
    var PORT_OUT = 5;       // ノードの右端から、出力ポートの右端まで
    var NODE_WIDTH = 100;   // 曲線の膨らみの基準（エディターの node_width）
    var CURVE_SCALE = 0.75; // エディターの lineCurveScale

    function isNode(el) {
        return el && el.classList && el.classList.contains("node");
    }

    function outputCount(node) {
        var n = parseInt(getComputedStyle(node).getPropertyValue("--node-outputs"), 10);
        return n > 1 ? n : 1;
    }

    function hasOutputPort(node) {
        return getComputedStyle(node, "::after").content !== "none";
    }

    // 出力ポート k（1 始まり）の右端の位置。ポートの無いノードは右端の中央
    function portPoint(node, k, origin) {
        var r = node.getBoundingClientRect();
        var n = outputCount(node);
        var y = r.top + r.height / 2;
        if (n > 1) {
            k = Math.min(Math.max(k || 1, 1), n);
            y += (k - 1 - (n - 1) / 2) * PORT_GAP;
        }
        var x = hasOutputPort(node) ? r.right + PORT_OUT : r.right;
        return { x: x - origin.x, y: y - origin.y };
    }

    // 入力ポートの左端の位置
    function inputPoint(node, origin) {
        var r = node.getBoundingClientRect();
        return { x: r.left - PORT_OUT - origin.x, y: r.top + r.height / 2 - origin.y };
    }

    function edgePoint(el, side, origin) {
        var r = el.getBoundingClientRect();
        return { x: (side === "left" ? r.left : r.right) - origin.x, y: r.top + r.height / 2 - origin.y };
    }

    // エディターの generateLinkPath と同じ形のベジェ曲線
    function linkPath(a, b) {
        var dx = b.x - a.x;
        var dy = b.y - a.y;
        var delta = Math.sqrt(dx * dx + dy * dy);
        var scale = CURVE_SCALE;
        if (delta < NODE_WIDTH) {
            scale = CURVE_SCALE - CURVE_SCALE * ((NODE_WIDTH - delta) / NODE_WIDTH);
        }
        var c = scale * NODE_WIDTH;
        return "M " + a.x + " " + a.y +
            " C " + (a.x + c) + " " + a.y + " " + (b.x - c) + " " + b.y + " " + b.x + " " + b.y;
    }

    function rowPort(row, index, source) {
        var p = parseInt(row.getAttribute("data-port"), 10);
        if (p > 0) return p;
        return outputCount(source) > 1 ? index + 1 : 1;
    }

    function draw(example) {
        var old = example.querySelector(":scope > svg.node-wires");
        if (old) old.remove();
        example.classList.add("wired");

        var box = example.getBoundingClientRect();
        // 枠線とスクロール量を考慮して、SVG の座標の原点（example の内容の左上）を求める
        var origin = {
            x: box.left + example.clientLeft - example.scrollLeft,
            y: box.top + example.clientTop - example.scrollTop
        };
        var paths = [];

        function add(a, b, dashed) {
            paths.push({ d: linkPath(a, b), dashed: dashed });
        }

        Array.prototype.forEach.call(example.querySelectorAll(".branch"), function (branch) {
            var source = branch.previousElementSibling;
            if (!isNode(source)) return;
            var dashed = branch.classList.contains("dashed");
            var rows = branch.querySelectorAll(":scope > .branch-row");
            Array.prototype.forEach.call(rows, function (row, i) {
                var first = row.firstElementChild;
                if (!first) return;
                add(portPoint(source, rowPort(row, i, source), origin), edgePoint(first, "left", origin), dashed);
            });
        });

        Array.prototype.forEach.call(example.querySelectorAll(".merge"), function (merge) {
            var target = merge.nextElementSibling;
            if (!isNode(target)) return;
            var rows = merge.querySelectorAll(":scope > .merge-row");
            Array.prototype.forEach.call(rows, function (row) {
                var last = row.lastElementChild;
                if (!last) return;
                add(edgePoint(last, "right", origin), inputPoint(target, origin), false);
            });
        });

        // 出力ポートが複数あるノードの直後の配線
        Array.prototype.forEach.call(example.querySelectorAll(".node"), function (node) {
            if (outputCount(node) < 2) return;
            var wire = node.nextElementSibling;
            if (!wire || !wire.classList.contains("arrow")) return;
            var target = wire.nextElementSibling;
            if (!isNode(target)) return;
            // 曲線の余白を広げてから（.redrawn）、前回のずらし量を消して位置を測る
            // （getBoundingClientRect は transform 後の位置を返すため、消さないと再描画のたびにずれる）
            wire.classList.add("redrawn");
            wire.style.transform = "";
            var a = portPoint(node, parseInt(wire.getAttribute("data-port"), 10) || 1, origin);
            var b = inputPoint(target, origin);
            // msg の印（.multi）や ✗ を、曲線の中ほどの高さへ寄せる
            var w = edgePoint(wire, "left", origin);
            wire.style.transform = "translateY(" + ((a.y + b.y) / 2 - w.y) + "px)";
            add(a, b, wire.classList.contains("delayed"));
        });

        if (!paths.length) return;
        var svg = document.createElementNS(SVG_NS, "svg");
        svg.setAttribute("class", "node-wires");
        svg.setAttribute("aria-hidden", "true");
        svg.setAttribute("width", example.scrollWidth);
        svg.setAttribute("height", example.scrollHeight);
        paths.forEach(function (p) {
            var path = document.createElementNS(SVG_NS, "path");
            path.setAttribute("d", p.d);
            path.setAttribute("fill", "none");
            path.setAttribute("stroke", "#999999");
            path.setAttribute("stroke-width", "3");
            if (p.dashed) path.setAttribute("stroke-dasharray", "6 4");
            svg.appendChild(path);
        });
        example.insertBefore(svg, example.firstChild);
    }

    function needsWires(example) {
        if (example.querySelector(".branch, .merge")) return true;
        return Array.prototype.some.call(example.querySelectorAll(".node"), function (n) {
            return outputCount(n) > 1;
        });
    }

    function init() {
        var examples = Array.prototype.filter.call(document.querySelectorAll(".node-example"), needsWires);
        examples.forEach(function (example) {
            // 曲線を描く前に余白を広げる（.wired）ので、描画は2回目のレイアウトで行う
            example.classList.add("wired");
            draw(example);
            if (window.ResizeObserver) {
                var last = "";
                new ResizeObserver(function () {
                    var size = example.clientWidth + "x" + example.clientHeight;
                    if (size !== last) {
                        last = size;
                        draw(example);
                    }
                }).observe(example);
            }
        });
        // アイコンや Web フォントの読み込みで幅が変わったら描き直す
        window.addEventListener("load", function () { examples.forEach(draw); });
        window.addEventListener("resize", function () { examples.forEach(draw); });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
