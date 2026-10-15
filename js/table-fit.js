/*
 * 表の短い列を、折り返さずに 1 行で表示する。
 *
 * 表は幅 100% の自動レイアウトのため、説明文のような長い列があると、ブラウザは
 * すべての列を少しずつ縮める。その結果、項目名のような短い列まで、あと数文字分の
 * 幅が足りずに折り返す（例:「デバイス証明書（…-」で改行される）。
 *
 * このスクリプトは、描画後にセルごとの最大内容幅（折り返さないときの幅）を測り、
 * 列ごとに「1 行に保つ幅」を決める。表の幅の SHORT_RATIO を超える長いセルは
 * 折り返してよいものとし、残りのセルの最大内容幅をその列の幅とする。ただし、長いセルが
 * 列のセルの LONG_CELL_RATIO を超える列（説明文の列など）は、1 行に保たない。
 *
 * 1 行に保つ列は、幅の狭い順に 1 列ずつ試す。試した列のセルに white-space: nowrap を
 * 付け、実際の列の幅を測る。このとき、ほかの候補の列は <col> の幅で元の幅に固定し、
 * 縮める分を長い列（1 行に保てない列）だけに引き受けさせる。固定しないと、ブラウザは
 * 最大内容幅に比例してすべての列から幅を削るため、中くらいの列まで細くなる。
 * 長い列が表の幅の REST_COL_RATIO（その列の最大内容幅がそれより狭ければその幅。
 * もともとそれより細い列は元の幅）より細くなるとき、または表が枠からはみ出すときは、
 * 試した列を戻す。
 *
 * 表の幅が MIN_TABLE_WIDTH 未満（スマートフォンなど）のときは何もしない。
 * 表の幅が変わったとき（画面の幅の変更、<details> を開いたときなど）は選び直す。
 * 対象から外す表には data-table-fit="off" を付ける。
 * スクリプトが動かない環境では、従来どおり折り返して表示される。
 */
(function () {
    "use strict";

    var NOWRAP = "table-fit-nowrap";
    var PIN = "data-table-fit-pin"; // このスクリプトが足した <colgroup> の印
    var MIN_TABLE_WIDTH = 600;  // これより狭い表は、従来どおり折り返す
    var SHORT_RATIO = 0.45;     // 最大内容幅が表の幅のこの割合を超えるセルは、折り返してよい
    var LONG_CELL_RATIO = 0.25; // 長いセルがこの割合を超える列は、1 行に保たない
    var REST_COL_RATIO = 0.25;  // ほかの列に残す幅（表の幅の割合）。これより細くしない

    // 行と列の位置を、rowspan と colspan を考慮して求める。colspan が 1 のセルだけを列に数える
    function columns(table) {
        var cols = [];
        var occupied = [];
        var rows = table.rows;
        for (var r = 0; r < rows.length; r++) {
            occupied[r] = occupied[r] || [];
            var c = 0;
            var cells = rows[r].cells;
            for (var i = 0; i < cells.length; i++) {
                var cell = cells[i];
                while (occupied[r][c]) {
                    c++;
                }
                var cs = cell.colSpan || 1;
                var rs = cell.rowSpan || 1;
                for (var y = 0; y < rs; y++) {
                    occupied[r + y] = occupied[r + y] || [];
                    for (var x = 0; x < cs; x++) {
                        occupied[r + y][c + x] = true;
                    }
                }
                if (cs === 1) {
                    (cols[c] = cols[c] || []).push(cell);
                }
                c += cs;
            }
        }
        return cols;
    }

    // 列ごとの [セル, 最大内容幅（左右の padding と枠線を含む）] の一覧。中身の複製を、
    // セルの中に幅 max-content で置いて測る。セルの中に置くので、文字の大きさやフォントは
    // 同じになる。複製をすべて置いてから幅をまとめて読み、レイアウトを 1 回で済ませる
    function measure(table) {
        var cols = columns(table);
        var probes = [];
        for (var c = 0; c < cols.length; c++) {
            cols[c] = cols[c] || [];
            for (var i = 0; i < cols[c].length; i++) {
                var cell = cols[c][i];
                var probe = document.createElement("div");
                probe.style.cssText = "position:absolute;left:-99999px;top:0;" +
                    "width:max-content;visibility:hidden;";
                for (var n = cell.firstChild; n; n = n.nextSibling) {
                    probe.appendChild(n.cloneNode(true));
                }
                cell.appendChild(probe);
                probes.push(probe);
            }
        }
        var result = [];
        var k = 0;
        for (var c2 = 0; c2 < cols.length; c2++) {
            var list = [];
            for (var j = 0; j < cols[c2].length; j++) {
                var st = getComputedStyle(cols[c2][j]);
                var w = probes[k++].getBoundingClientRect().width +
                    parseFloat(st.paddingLeft) + parseFloat(st.paddingRight) +
                    parseFloat(st.borderLeftWidth) + parseFloat(st.borderRightWidth);
                list.push([cols[c2][j], w]);
            }
            result.push(list);
        }
        for (var r = 0; r < probes.length; r++) {
            probes[r].parentNode.removeChild(probes[r]);
        }
        return result;
    }

    // このスクリプトが付けた印を外す。入れ子の表の印には触れない
    function clear(table) {
        var marked = table.querySelectorAll("." + NOWRAP);
        for (var i = 0; i < marked.length; i++) {
            if (marked[i].closest("table") === table) {
                marked[i].classList.remove(NOWRAP);
            }
        }
        var group = table.querySelector(":scope > colgroup[" + PIN + "]");
        if (group) {
            table.removeChild(group);
        }
    }

    function fit(table) {
        clear(table);
        var width = table.getBoundingClientRect().width;
        if (width < MIN_TABLE_WIDTH) {
            return;
        }
        // 画面の幅でフォントの大きさや padding が変わるページがあるため、毎回測る
        var cols = measure(table);
        if (cols.length < 2) {
            return;
        }

        var full = [];   // 列の最大内容幅
        var target = []; // 1 行に保つときの列の幅（保てない列は null）
        var total = 0;
        for (var c = 0; c < cols.length; c++) {
            var max = 0;
            var shortMax = 0;
            var longCount = 0;
            for (var i = 0; i < cols[c].length; i++) {
                var w = cols[c][i][1];
                max = Math.max(max, w);
                if (w > width * SHORT_RATIO) {
                    longCount++;
                } else {
                    shortMax = Math.max(shortMax, w);
                }
            }
            full.push(max);
            total += max;
            var fits = cols[c].length && longCount <= cols[c].length * LONG_CELL_RATIO;
            target.push(fits ? shortMax : null);
        }
        if (total <= width) {
            return; // どのセルも折り返していない
        }

        var order = [];
        for (var k = 0; k < cols.length; k++) {
            if (target[k] !== null) {
                order.push(k);
            }
        }
        order.sort(function (a, b) { return target[a] - target[b]; });

        // 狭い順に 1 列ずつ 1 行に保ってみて、実際の列の幅を測る。
        // 1 行に保つ列が広がると、ブラウザはほかの列から幅を削る。削る量は最大内容幅に
        // 比例するため、中くらいの列（「原因」など）まで細くなる。そこで、1 行に保つ候補の
        // うち選ばなかった列は、<col> の幅で元の幅に固定し、長い列だけに縮める分を
        // 引き受けさせる。長い列が細くなりすぎる（表の幅の REST_COL_RATIO 未満。もともと
        // それより細い列は元の幅未満）とき、または表が枠からはみ出すときは、その列を戻す
        if (table.querySelector(":scope > colgroup")) {
            return; // 作者が列の幅を決めている表には手を出さない
        }
        var original = columnWidths(cols);
        var group = document.createElement("colgroup");
        group.setAttribute(PIN, "");
        for (var g = 0; g < cols.length; g++) {
            group.appendChild(document.createElement("col"));
        }
        table.insertBefore(group, table.firstChild);
        if (table.caption) {
            table.insertBefore(table.caption, group);
        }

        var chosen = {};
        function pin(except) {
            for (var p = 0; p < cols.length; p++) {
                var fixed = target[p] !== null && !chosen[p] && p !== except;
                group.children[p].style.width = fixed ? original[p] + "px" : "";
            }
        }
        for (var j = 0; j < order.length; j++) {
            var col = order[j];
            pin(col);
            var marked = [];
            for (var m = 0; m < cols[col].length; m++) {
                if (cols[col][m][1] <= width * SHORT_RATIO) {
                    cols[col][m][0].classList.add(NOWRAP);
                    marked.push(cols[col][m][0]);
                }
            }
            var after = columnWidths(cols);
            var keep = table.getBoundingClientRect().width <= width + 0.5; // 表がはみ出さない
            for (var q = 0; q < cols.length && keep; q++) {
                if (target[q] === null) {
                    var reserve = Math.min(full[q], width * REST_COL_RATIO);
                    if (after[q] < Math.min(original[q], reserve) - 0.5) {
                        keep = false;
                    }
                }
            }
            if (keep) {
                chosen[col] = true;
            } else {
                for (var u = 0; u < marked.length; u++) {
                    marked[u].classList.remove(NOWRAP);
                }
            }
        }
        if (Object.keys(chosen).length) {
            pin(-1);
        } else {
            clear(table); // 1 行に保てる列が無ければ、元のまま
        }
    }

    // 列ごとの現在の幅（列の最初のセルの幅）
    function columnWidths(cols) {
        var widths = [];
        for (var c = 0; c < cols.length; c++) {
            widths.push(cols[c].length ? cols[c][0][0].getBoundingClientRect().width : 0);
        }
        return widths;
    }

    function init() {
        var tables = [];
        var all = document.querySelectorAll("table");
        for (var i = 0; i < all.length; i++) {
            if (all[i].getAttribute("data-table-fit") !== "off") {
                tables.push(all[i]);
            }
        }
        if (!tables.length) {
            return;
        }
        var style = document.createElement("style");
        style.textContent = "." + NOWRAP + " { white-space: nowrap; }";
        document.head.appendChild(style);

        // 文字の幅はフォントの読み込みで変わるため、読み込み後に測り直す
        function refitAll() {
            for (var k = 0; k < tables.length; k++) {
                fit(tables[k]);
            }
        }

        if (typeof ResizeObserver === "function") {
            // 表の幅が変わったときだけ選び直す。閉じた <details> の中の表は幅が 0 で、
            // 開いたときに幅が変わるので、そこで選ぶ。1 行に保つ列を選んでも、
            // 幅 100% の表の幅は変わらないため、繰り返さない
            var last = new WeakMap();
            var observer = new ResizeObserver(function (entries) {
                for (var e = 0; e < entries.length; e++) {
                    var table = entries[e].target;
                    var w = Math.round(entries[e].contentRect.width);
                    if (last.get(table) !== w) {
                        last.set(table, w);
                        fit(table);
                    }
                }
            });
            for (var t = 0; t < tables.length; t++) {
                observer.observe(tables[t]);
            }
        } else {
            refitAll();
        }
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(refitAll);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
