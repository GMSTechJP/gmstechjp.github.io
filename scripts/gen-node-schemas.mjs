#!/usr/bin/env node
// ノードのエディター定義から、検査用の一覧（tests/node-schemas.json）を作る。
//
// scripts/check-node-properties.py は、ガイドのフローの各ノードについて、
// 「選択肢から選ぶ欄に、選択肢に無い値が入っていないか」「必須の欄が空でないか」を調べる。
// その判定のもとになる選択肢と必須の指定を、ノードのエディター HTML から取り出す。
//
//   node scripts/gen-node-schemas.mjs            一覧を作り直す
//   node scripts/gen-node-schemas.mjs --check    作り直した結果が、置いてある一覧と同じか調べる
//   node scripts/gen-node-schemas.mjs --from DIR npm を使わず、DIR にある .tgz から作る
//
// パッケージは npm pack で本体だけを取得する。依存パッケージは入れず、パッケージの
// インストール時のスクリプトも実行しない。取得した .js（実行時のコード）は読まない。
// エディター HTML の <script>（registerType の呼び出し）だけを、RED や $ を何もしない
// 代用品に差し替えた vm の中で評価し、registerType に渡された定義を受け取る。
//
// 取り出すもの:
//   defaults  プロパティごとの既定値・必須の指定・設定ノードの型・検証の種類
//   selects   <select id="node-input-…"> に HTML で書かれている <option> の値
//             （JavaScript で選択肢を足す欄は、選択肢が分からないので対象にしない）
//   typed     値の型を選ぶ欄（typedInput の typeField）と、そこで選べる型
//
// 編集画面を開くときのスクリプト（oneditprepare）が、欠けた値や真偽値を読み替えてから
// 欄に入れるノードがある（Dashboard 2.0 の ui-group の visible など）。HTML を読むだけでは、
// その欄が画面で空になるかどうかを決められない。そこで、欄の値の出し入れだけを再現した
// 模擬の画面で、エディターと同じ順（欄に値を入れる → oneditprepare → change を起こす）に
// 実際のスクリプトを動かし、欄がどうなったかを記録する。
//   missing   プロパティが無いとき: "ok"（スクリプトが値を補う）/ "blank"（空のまま）/
//             "unchecked"（既定はオンのチェックボックスが、オフになる）/
//             "nofield"（画面に欄が無い）/
//             "unknown"（スクリプトが模擬の画面で動かず、決められない）
//             select の欄と、必須の欄、既定がオンのチェックボックスについて記録する
//   bool      真偽値の true / false が入っているとき（select のみ）: 同上
// "unknown" は、検査の側で「空になる」と同じに扱う（見逃すより、確かめさせる）。
//
// ガイドで新しいサードパーティのノードを使うときは、PACKAGES に1行足して作り直す。
// Node-RED や各パッケージの版を上げるときも、ここの版を変えて作り直す。

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

// 定義を取り出すパッケージと版。ガイドが案内している導入コマンドのパッケージに合わせる
const PACKAGES = [
    ["@node-red/nodes", "5.0.7"],
    ["@flowfuse/node-red-dashboard", "1.36.1"],
    ["@flowfuse/node-red-dashboard-2-ui-led", "1.1.1"],
    ["node-red-contrib-modbus", "5.62.1"],
    ["node-red-contrib-buffer-parser", "3.2.2"],
    ["node-red-node-sqlite", "2.0.1"],
    ["node-red-contrib-ftp", "0.0.8"],
    ["node-red-contrib-ftp-server", "1.0.4"],
    ["node-red-node-email", "5.2.5"],
    ["node-red-node-base64", "1.0.0"],
    ["node-red-node-pi-sense-hat", "0.2.0"],
];

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const OUT = path.join(ROOT, "tests", "node-schemas.json");

function fail(message) {
    console.error(message);
    process.exit(2);
}

// ---- パッケージの取得 ----

function tarballName(name, version) {
    return name.replace(/^@/, "").replace("/", "-") + "-" + version + ".tgz";
}

function fetchPackage(name, version, work, from) {
    const tgz = path.join(from || work, tarballName(name, version));
    if (!from) {
        execFileSync("npm", ["pack", `${name}@${version}`, "--pack-destination", work, "--silent"],
            { stdio: ["ignore", "ignore", "inherit"], timeout: 180000 });
    }
    if (!fs.existsSync(tgz)) {
        fail(`${name}@${version} の本体（${tgz}）が無い`);
    }
    const dest = path.join(work, "x-" + tarballName(name, version));
    fs.mkdirSync(dest, { recursive: true });
    execFileSync("tar", ["-xzf", tgz, "-C", dest], { timeout: 120000 });
    return path.join(dest, "package");
}

function htmlFiles(dir) {
    const out = [];
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            if (entry.name !== "node_modules") {
                out.push(...htmlFiles(full));
            }
        } else if (entry.name.endsWith(".html")) {
            out.push(full);
        }
    }
    return out.sort();
}

// ---- エディター HTML の読み取り ----

function attr(attrs, name) {
    const m = new RegExp(`(?:^|\\s)${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, "i").exec(attrs);
    return m ? (m[1] ?? m[2] ?? m[3]) : null;
}

function decodeEntities(text) {
    return text.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'").replace(/&amp;/g, "&");
}

function splitScripts(src) {
    const templates = {};
    const codes = [];
    const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
    let m;
    while ((m = re.exec(src)) !== null) {
        const [, attrs, body] = m;
        const type = (attr(attrs, "type") || "text/javascript").toLowerCase();
        const template = attr(attrs, "data-template-name");
        if (template !== null) {
            templates[template] = (templates[template] || "") + body;
        } else if (attr(attrs, "data-help-name") === null && attr(attrs, "src") === null
                   && (type === "text/javascript" || type === "module")) {
            codes.push(body);
        }
    }
    return { templates, codes };
}

// 編集画面の <select> のうち、HTML に <option> が書いてあるものを返す。
// コメントアウトされた欄は、画面に無いので除く。
function staticSelects(template, prefix) {
    const selects = {};
    const html = template.replace(/<!--[\s\S]*?-->/g, "");
    const re = /<select\b([^>]*)>([\s\S]*?)<\/select>/gi;
    let m;
    while ((m = re.exec(html)) !== null) {
        const id = attr(m[1], "id");
        if (!id || !id.startsWith(prefix + "-")) {
            continue;
        }
        const prop = id.slice(prefix.length + 1);
        const values = [];
        const optionRe = /<option\b([^>]*)>([^<]*)/gi;
        let o;
        while ((o = optionRe.exec(m[2])) !== null) {
            const value = attr(o[1], "value");
            values.push(decodeEntities(value !== null ? value : o[2].trim()));
        }
        if (values.length > 0) {
            selects[prop] = { values, multiple: /(?:^|\s)multiple(?:[\s=>]|$)/i.test(m[1]) };
        }
    }
    // 欄の有無と種類。チェックボックスは、エディターが checked に値を入れる。
    // hidden の欄は画面に出ないので、空でも利用者には見えない
    const fields = {};
    const tagRe = /<(input|select|textarea|div|span)\b([^>]*)>/gi;
    while ((m = tagRe.exec(html)) !== null) {
        const id = attr(m[2], "id");
        if (id && id.startsWith(prefix + "-")) {
            const tag = m[1].toLowerCase();
            const type = tag === "input" ? (attr(m[2], "type") || "").toLowerCase() : "";
            fields[id.slice(prefix.length + 1)] = type === "checkbox" || type === "hidden" ? type : tag;
        }
    }
    return { selects, fields };
}

// ---- 代用品（定義の評価に使う） ----

// どう呼んでも、どのプロパティを読んでも、自分自身を返す代用品
function anything() {
    const target = function () {};
    const proxy = new Proxy(target, {
        get(_t, key) {
            if (key === Symbol.toPrimitive) {
                return () => "";
            }
            if (key === "then" || typeof key === "symbol") {
                return undefined;
            }
            return proxy;
        },
        apply() { return proxy; },
        construct() { return proxy; },
        has() { return true; },
    });
    return proxy;
}

function marked(kind, extra) {
    const validator = function () { return true; };
    validator.schemaMark = { kind, ...extra };
    return validator;
}

// ---- 模擬の画面 ----
//
// 欄（id で指定した要素）の値の出し入れ、チェックの状態、change などのイベント、typedInput の
// 型の指定だけを再現する。表示や配置に関わる呼び出しは、何もせずに自分自身を返す。

const CHILD_LOOKUPS = new Set(["find", "children", "parent", "parents", "closest", "next", "prev",
    "siblings", "filter", "not", "first", "last", "eq", "clone", "contents"]);
const EVENT_SHORTCUTS = new Set(["change", "click", "keyup", "keydown", "blur", "focus", "input"]);
const SIZE_GETTERS = new Set(["width", "height", "outerHeight", "outerWidth", "scrollTop", "innerHeight", "innerWidth"]);

class Dom {
    constructor(prefix, fields, selects) {
        this.prefix = prefix;
        this.fields = fields;
        this.selects = selects;
        this.elements = new Map();
        this.depth = 0;
    }

    element(id) {
        if (!this.elements.has(id)) {
            const prop = id.startsWith(this.prefix + "-") ? id.slice(this.prefix.length + 1) : null;
            const select = prop !== null ? this.selects[prop] : null;
            this.elements.set(id, this.wrap({
                id,
                present: prop !== null && prop in this.fields,
                options: select ? select.values : null,
                multiple: select ? select.multiple : false,
                value: "",
                checked: false,
                handlers: {},
                typed: null,
            }));
        }
        return this.elements.get(id);
    }

    field(prop) {
        return this.element(this.prefix + "-" + prop);
    }

    anonymous() {
        return this.wrap({ id: null, present: false, options: null, multiple: false, value: "", checked: false, handlers: {}, typed: null });
    }

    query(selector) {
        if (selector && selector.simulated) {
            return selector;
        }
        if (typeof selector === "function") {
            selector();
            return this.anonymous();
        }
        if (typeof selector === "string") {
            const m = /^\s*#([A-Za-z0-9_-]+)\s*$/.exec(selector);
            if (m) {
                return this.element(m[1]);
            }
        }
        return this.anonymous();
    }

    // jQuery の val() と同じ規則で値を入れる。select は、選択肢に無い値を入れると選択が空になる
    setValue(el, value) {
        if (value == null) {
            value = "";
        }
        if (el.options) {
            if (typeof value === "number") {
                value = String(value);
            }
            if (Array.isArray(value)) {
                const picked = value.map((v) => (v == null ? "" : String(v))).filter((v) => el.options.includes(v));
                el.value = picked.length > 0 ? (el.multiple ? picked : picked[0]) : null;
            } else {
                el.value = typeof value === "string" && el.options.includes(value) ? value : null;
            }
        } else {
            el.value = typeof value === "object" ? value : String(value);
        }
    }

    fire(wrapper, el, event, extra) {
        const name = String(event && event.type ? event.type : event).split(".")[0];
        if (this.depth > 20) {
            return;
        }
        this.depth += 1;
        try {
            for (const handler of [...(el.handlers[name] || [])]) {
                handler.call(wrapper, { type: name, target: wrapper, currentTarget: wrapper, preventDefault() {}, stopPropagation() {} },
                    ...(Array.isArray(extra) ? extra : []));
            }
        } finally {
            this.depth -= 1;
        }
    }

    typedInput(wrapper, el, args) {
        const [first, second] = args;
        if (first && typeof first === "object") {
            const types = (Array.isArray(first.types) ? first.types : [])
                .map((t) => (typeof t === "string" ? t : t && t.value))
                .filter((t) => typeof t === "string");
            let typeField = null;
            if (typeof first.typeField === "string") {
                typeField = this.query(first.typeField);
            } else if (first.typeField && first.typeField.simulated) {
                typeField = first.typeField;
            }
            el.typed = { types, default: typeof first.default === "string" ? first.default : null, typeField };
            return wrapper;
        }
        if (first === "value") {
            if (args.length < 2) {
                return el.value;
            }
            el.value = second == null ? "" : second;
            return wrapper;
        }
        if (first === "type") {
            const field = el.typed && el.typed.typeField;
            if (args.length < 2) {
                return (field && field.value) || (el.typed && (el.typed.default || el.typed.types[0])) || "";
            }
            if (field) {
                field.val(second);
            }
            return wrapper;
        }
        if (first === "types" && el.typed && Array.isArray(second)) {
            el.typed.types = second.map((t) => (typeof t === "string" ? t : t && t.value)).filter((t) => typeof t === "string");
            return wrapper;
        }
        if (first === "validate") {
            return true;
        }
        return wrapper;
    }

    wrap(el) {
        const dom = this;
        const on = (wrapper, events, fn) => {
            if (typeof events === "string" && typeof fn === "function") {
                for (const event of events.split(/\s+/)) {
                    const name = event.split(".")[0];
                    (el.handlers[name] = el.handlers[name] || []).push(fn);
                }
            }
            return wrapper;
        };
        const wrapper = new Proxy(function () {}, {
            get(_t, key) {
                if (typeof key === "symbol") {
                    return key === Symbol.toPrimitive ? () => "" : undefined;
                }
                switch (key) {
                case "simulated": return true;
                case "element": return el;
                case "then": return undefined;
                case "value": return el.value;
                case "checked": return el.checked;
                case "id": return el.id;
                case "length": return el.present ? 1 : 0;
                case "0": return wrapper;
                case "get": return () => wrapper;
                case "val": return (...args) => {
                    if (args.length === 0) {
                        return el.value;
                    }
                    dom.setValue(el, args[0]);
                    return wrapper;
                };
                case "prop": case "attr": return (name, value) => {
                    if (value === undefined && typeof name === "string") {
                        if (name === "checked") { return el.checked; }
                        if (name === "id") { return el.id; }
                        if (name === "type") { return dom.fields[el.id && el.id.slice(dom.prefix.length + 1)] === "checkbox" ? "checkbox" : undefined; }
                        return key === "prop" ? false : undefined;
                    }
                    if (name === "checked") { el.checked = !!value; }
                    return wrapper;
                };
                case "is": return (what) => (/:checked/.test(String(what)) ? !!el.checked : /:visible/.test(String(what)));
                case "on": case "bind": case "one": return (events, ...rest) => on(wrapper, events, rest.find((f) => typeof f === "function"));
                case "trigger": case "triggerHandler": return (event, extra) => { dom.fire(wrapper, el, event, extra); return wrapper; };
                case "each": return (fn) => { if (el.present) { fn.call(wrapper, 0, wrapper); } return wrapper; };
                case "typedInput": return (...args) => dom.typedInput(wrapper, el, args);
                case "data": return (name, value) => {
                    if (value !== undefined) { return wrapper; }
                    return name === "noderedTypedInput" && el.typed ? {} : undefined;
                };
                case "text": case "html": return (value) => (value === undefined ? "" : wrapper);
                case "css": return (name, value) => (value === undefined && typeof name === "string" ? "" : wrapper);
                case "hasClass": return () => false;
                case "index": return () => -1;
                case "toArray": return () => [];
                default:
                }
                if (EVENT_SHORTCUTS.has(key)) {
                    return (fn) => {
                        if (typeof fn === "function") { return on(wrapper, key, fn); }
                        dom.fire(wrapper, el, key);
                        return wrapper;
                    };
                }
                if (CHILD_LOOKUPS.has(key)) {
                    return () => dom.anonymous();
                }
                if (SIZE_GETTERS.has(key)) {
                    return (value) => (value === undefined ? 0 : wrapper);
                }
                return () => wrapper;
            },
            set(_t, key, value) {
                if (key === "value") { dom.setValue(el, value); }
                if (key === "checked") { el.checked = !!value; }
                return true;
            },
        });
        return wrapper;
    }
}

const JQUERY_STATICS = {
    each(target, fn) {
        if (Array.isArray(target)) {
            target.every((v, i) => fn.call(v, i, v) !== false);
        } else if (target && typeof target === "object") {
            Object.keys(target).every((k) => fn.call(target[k], k, target[k]) !== false);
        }
        return target;
    },
    extend(...args) {
        if (args[0] === true) { args.shift(); }
        return Object.assign(args[0] || {}, ...args.slice(1));
    },
    map(target, fn) {
        return Array.isArray(target) ? target.map((v, i) => fn(v, i)).filter((v) => v != null) : [];
    },
    grep(target, fn) { return Array.isArray(target) ? target.filter((v, i) => fn(v, i)) : []; },
    inArray(value, list) { return Array.isArray(list) ? list.indexOf(value) : -1; },
    isArray: Array.isArray,
    isFunction(value) { return typeof value === "function"; },
    isNumeric(value) { return value !== "" && value !== null && !Array.isArray(value) && !Number.isNaN(Number(value)); },
    isEmptyObject(value) { return !value || Object.keys(value).length === 0; },
    isPlainObject(value) { return !!value && Object.getPrototypeOf(value) === Object.prototype; },
    trim(value) { return value == null ? "" : String(value).trim(); },
};

// ---- registerType の呼び出しを受け取る ----

// file（エディター HTML 1つ）の <script> を評価する環境。env.dom に模擬の画面を入れている間だけ、
// $ が欄を返し、setTimeout が後で実行する処理をためる
function makeSandbox(env, registered, file) {
    const stub = anything();
    const validators = {
        number: (blankAllowed) => marked("number", { blank: !!blankAllowed }),
        regex: (re) => (Object.prototype.toString.call(re) === "[object RegExp]"
            ? marked("regex", { source: re.source, flags: re.flags })
            : marked("custom", {})),
        // RED.validators.typedInput("型の欄の名前") か、{ type, typeField, allowBlank, allowUndefined }
        typedInput: (arg) => {
            const options = typeof arg === "string" ? { typeField: arg } : (arg && typeof arg === "object" ? arg : {});
            return marked("typedInput", {
                typeField: typeof options.typeField === "string" ? options.typeField : null,
                type: typeof options.type === "string" ? options.type : null,
                allowBlank: !!options.allowBlank,
                allowUndefined: !!options.allowUndefined,
            });
        },
    };
    const nodes = new Proxy(function () {}, {
        get(_t, key) {
            if (key === "registerType") {
                return (type, def) => { registered.push({ type, def, file }); };
            }
            return typeof key === "symbol" ? undefined : stub;
        },
    });
    const RED = new Proxy(function () {}, {
        get(_t, key) {
            if (key === "nodes") { return nodes; }
            if (key === "validators") { return validators; }
            if (key === "_") { return (text) => String(text); }
            return typeof key === "symbol" ? undefined : stub;
        },
    });
    const jquery = new Proxy(function () {}, {
        apply(_t, _this, args) { return env.dom ? env.dom.query(args[0]) : stub; },
        get(_t, key) {
            if (typeof key === "symbol") { return undefined; }
            return Object.prototype.hasOwnProperty.call(JQUERY_STATICS, key) ? JQUERY_STATICS[key] : stub;
        },
    });
    const later = (fn) => {
        if (env.dom && typeof fn === "function") { env.timers.push(fn); }
        return 0;
    };
    const sandbox = {
        RED, $: jquery, jQuery: jquery, document: stub, navigator: stub, location: stub,
        localStorage: stub, console: { log() {}, warn() {}, error() {}, info() {}, debug() {} },
        setTimeout: later, setInterval() { return 0; }, clearTimeout() {}, clearInterval() {},
        requestAnimationFrame: later,
    };
    sandbox.window = sandbox;
    sandbox.globalThis = sandbox;
    return vm.createContext(sandbox);
}

function jsonable(value) {
    try {
        const text = JSON.stringify(value);
        return text === undefined ? undefined : JSON.parse(text);
    } catch {
        return undefined;
    }
}

function describeDefaults(defaults) {
    const out = {};
    for (const [prop, d] of Object.entries(defaults || {})) {
        const item = {};
        if (d && typeof d === "object") {
            const value = jsonable(d.value);
            if (value !== undefined && typeof d.value !== "function") {
                item.value = value;
            }
            if (typeof d.required === "boolean") {
                item.required = d.required;
            }
            if (typeof d.type === "string") {
                item.type = d.type;
            }
            if (typeof d.validate === "function") {
                item.validate = d.validate.schemaMark || { kind: "custom" };
            }
        }
        out[prop] = item;
    }
    return out;
}

// ---- 編集画面を開く処理の模擬 ----

const MISSING = Symbol("missing");

// エディターの prepareEditDialog と同じ順で動かす（red.js）:
//   1. defaults の各欄に値を入れる（設定ノードを選ぶ欄は除く。チェックボックスは checked）
//   2. oneditprepare を呼ぶ
//   3. defaults の各欄に change を起こす
// 続けて、setTimeout で後回しにされた処理を実行する。
// oneditprepare が例外を出しても、エディターは記録だけして 3 へ進むので、ここでも進む。
function openDialog(type, def, env, prefix, fields, selects, override) {
    const defaults = def.defaults || {};
    const node = { id: "simulated", type, _def: def, _: (text) => String(text), users: [], z: "tab" };
    for (const [prop, d] of Object.entries(defaults)) {
        const value = d && typeof d === "object" ? jsonable(d.value) : undefined;
        if (value !== undefined) {
            node[prop] = value;
        }
    }
    if (def.credentials && typeof def.credentials === "object") {
        // 認証情報を持つノードでは、エディターが credentials を用意してから呼ぶ
        node.credentials = Object.fromEntries(Object.keys(def.credentials).map((key) => [key, ""]));
    }
    for (const [prop, value] of Object.entries(override || {})) {
        if (value === MISSING) {
            delete node[prop];
        } else {
            node[prop] = value;
        }
    }
    const dom = new Dom(prefix, fields, selects);
    for (const [prop, d] of Object.entries(defaults)) {
        if (!(prop in fields) || (d && typeof d.type === "string")) {
            continue;
        }
        const el = dom.field(prop);
        if (fields[prop] === "checkbox") {
            el.prop("checked", node[prop]);
        } else {
            el.val(node[prop] == null ? "" : node[prop]);
        }
    }
    env.dom = dom;
    env.timers = [];
    let error = null;
    const failed = (e) => {
        error = error || e;
        if (process.env.NODE_SCHEMAS_VERBOSE) {
            console.error(`[例外] ${type} ${JSON.stringify(Object.keys(override || {}))}: ${e && e.stack ? e.stack.split("\n").slice(0, 2).join(" | ") : e}`);
        }
    };
    try {
        try {
            if (typeof def.oneditprepare === "function") {
                def.oneditprepare.call(node);
            }
        } catch (e) {
            failed(e);
        }
        for (const prop of Object.keys(defaults)) {
            dom.field(prop).trigger("change");
        }
        for (let i = 0; i < env.timers.length && i < 100; i += 1) {
            env.timers[i]();
        }
    } catch (e) {
        failed(e);
    } finally {
        env.dom = null;
        env.timers = [];
    }
    return { dom, error };
}

// プロパティを value にして編集画面を開いたとき、その欄がどうなるか。
// 既定値のままでも例外が出るノードは、模擬の画面がスクリプトを再現できていないので、
// 決められない（unknown）。既定値では動き、このプロパティを変えたときだけ例外が出るなら、
// 実際のエディターでも同じ例外が出る（例: exec は useSpawn が無いと toString で止まる）。
// そのときは、例外が出た時点の欄の状態を答えにする。
function outcome(type, def, env, prefix, fields, selects, prop, value, baselineOk) {
    if (!baselineOk) {
        return "unknown";
    }
    const { dom } = openDialog(type, def, env, prefix, fields, selects, { [prop]: value });
    const el = dom.field(prop).element;
    if (fields[prop] === "checkbox") {
        return el.checked ? "ok" : "unchecked";
    }
    return el.value === null || el.value === "" ? "blank" : "ok";
}

function describeEditor(type, def, env, prefix, template) {
    const { selects, fields } = staticSelects(template, prefix);
    const defaults = describeDefaults(def.defaults);
    const opened = openDialog(type, def, env, prefix, fields, selects, {});
    const baselineOk = !opened.error;
    const kept = {};
    for (const prop of Object.keys(selects).sort()) {
        if (!(prop in defaults)) {
            continue;
        }
        const select = selects[prop];
        const run = (value) => outcome(type, def, env, prefix, fields, selects, prop, value, baselineOk);
        kept[prop] = {
            values: select.values,
            multiple: select.multiple,
            // 空文字が選択肢にあれば、値が無くても選択は空にならない
            missing: select.values.includes("") ? "ok" : run(MISSING),
            bool: { true: run(true), false: run(false) },
        };
    }
    // 必須の欄と、既定がオンのチェックボックスで、プロパティが無いときに欄がどうなるか
    for (const [prop, item] of Object.entries(defaults)) {
        const checkbox = fields[prop] === "checkbox" && item.value === true;
        if ((item.required !== true && !checkbox) || prop in kept || "type" in item) {
            continue;
        }
        const shown = prop in fields && fields[prop] !== "hidden";
        item.missing = shown ? outcome(type, def, env, prefix, fields, selects, prop, MISSING, baselineOk) : "nofield";
    }
    // 値の型を選ぶ欄（typedInput の typeField）と、そこで選べる型
    const typed = {};
    if (baselineOk) {
        for (const wrapper of opened.dom.elements.values()) {
            const info = wrapper.element.typed;
            const fieldId = info && info.typeField && info.typeField.element.id;
            if (!fieldId || !fieldId.startsWith(prefix + "-") || info.types.length === 0) {
                continue;
            }
            const typeProp = fieldId.slice(prefix.length + 1);
            if (typeProp in defaults) {
                typed[typeProp] = { types: info.types, default: info.default };
            }
        }
    }
    const sortedTyped = {};
    for (const prop of Object.keys(typed).sort()) {
        sortedTyped[prop] = typed[prop];
    }
    return { defaults, selects: kept, typed: sortedTyped };
}

// ---- 一覧を組み立てる ----

function build(from) {
    const work = fs.mkdtempSync(path.join(os.tmpdir(), "node-schemas-"));
    const nodes = {};
    const problems = [];
    try {
        for (const [name, version] of PACKAGES) {
            const dir = fetchPackage(name, version, work, from);
            const actual = JSON.parse(fs.readFileSync(path.join(dir, "package.json"), "utf8"));
            if (actual.name !== name || actual.version !== version) {
                fail(`${name}@${version} を取得したはずが、中身は ${actual.name}@${actual.version}`);
            }
            let count = 0;
            for (const file of htmlFiles(dir)) {
                const src = fs.readFileSync(file, "utf8");
                if (!src.includes("registerType")) {
                    continue;
                }
                const rel = path.relative(dir, file).split(path.sep).join("/");
                const { templates, codes } = splitScripts(src);
                const registered = [];
                const env = { dom: null, timers: [] };
                const context = makeSandbox(env, registered, rel);
                for (const code of codes) {
                    try {
                        vm.runInContext(code, context, { filename: rel, timeout: 5000 });
                    } catch (e) {
                        if (code.includes("registerType")) {
                            problems.push(`${name} ${rel}: 定義を評価できない（${e.message}）`);
                        }
                    }
                }
                for (const { type, def } of registered) {
                    if (typeof type !== "string" || !def || typeof def !== "object") {
                        problems.push(`${name} ${rel}: registerType の引数を読めない`);
                        continue;
                    }
                    if (nodes[type]) {
                        problems.push(`${type} が ${nodes[type].package} と ${name} の両方にある`);
                        continue;
                    }
                    const config = def.category === "config";
                    const prefix = config ? "node-config-input" : "node-input";
                    nodes[type] = {
                        package: name,
                        file: rel,
                        config,
                        ...describeEditor(type, def, env, prefix, templates[type] || ""),
                    };
                    count += 1;
                }
            }
            if (count === 0) {
                problems.push(`${name}@${version} からノードの定義を1つも取り出せなかった`);
            }
        }
    } finally {
        fs.rmSync(work, { recursive: true, force: true });
    }
    if (problems.length > 0) {
        fail(problems.join("\n"));
    }
    const sorted = {};
    for (const type of Object.keys(nodes).sort()) {
        sorted[type] = nodes[type];
    }
    return {
        note: "scripts/gen-node-schemas.mjs が作る。手で編集しない",
        packages: Object.fromEntries(PACKAGES),
        nodes: sorted,
    };
}

function main() {
    const args = process.argv.slice(2);
    const check = args.includes("--check");
    const fromAt = args.indexOf("--from");
    const from = fromAt >= 0 ? args[fromAt + 1] : null;
    if (fromAt >= 0 && !from) {
        fail("--from には .tgz のあるフォルダーを指定する");
    }
    const text = JSON.stringify(build(from), null, 1) + "\n";
    if (check) {
        const current = fs.existsSync(OUT) ? fs.readFileSync(OUT, "utf8") : "";
        if (current !== text) {
            console.error("tests/node-schemas.json が、作り直した結果と違う。node scripts/gen-node-schemas.mjs を実行する");
            process.exit(1);
        }
        console.log("tests/node-schemas.json は最新");
        return;
    }
    fs.writeFileSync(OUT, text);
    const count = Object.keys(JSON.parse(text).nodes).length;
    console.log(`tests/node-schemas.json を書いた（ノード ${count} 種類）`);
}

main();
