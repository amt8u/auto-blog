+++
title       = "JavaScript Module Systems: require, import, .mjs & More"
description = "A complete guide to every JavaScript module system — CommonJS, AMD, UMD, ESM, .mjs, .cjs — with examples, a comparison table, and best practices for 2026."
date        = "2026-06-01T16:37:22+05:30"
slug          = "javascript-module-systems-require-import-mjs"
tags          = ["JavaScript", "Node.js", "ES Modules", "CommonJS", "Web Development"]
keywords      = ["JavaScript module systems", "CommonJS require", "ES modules import", "mjs cjs difference", "dynamic import JavaScript", "AMD UMD JavaScript"]
canonical     = "/posts/javascript-module-systems-require-import-mjs/"
feature_image = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop"
+++

JavaScript once had no built-in way to split code across files — a limitation that spawned an entire ecosystem of competing module formats. Today, developers encounter `require()`, `import`, `.mjs`, `.cjs`, AMD, and UMD, often all in the same project. This guide demystifies every module system, explains when to use each, and maps out the clear path forward.

## Why JavaScript Needed Module Systems

In the early days of the web, JavaScript was a scripting language meant for simple page interactions. As applications grew, developers stuffed everything into global variables — leading to naming collisions and unmaintainable "spaghetti" code [1]. The community responded by inventing module patterns outside the language itself: first Immediately Invoked Function Expressions (IIFEs) to create private scopes, then formal module specifications like AMD and CommonJS. Only in 2015 did JavaScript finally gain a native module system via the ES6 specification [6].

![js module timeline](/images/posts/javascript-module-systems-require-import-mjs/js-module-timeline.svg)

## CommonJS (CJS) — The Node.js Workhorse

CommonJS was introduced in 2009 as the module system for server-side JavaScript, and it remains the **default module format in Node.js** to this day [3].

### Syntax

```js
// Exporting
const greet = (name) => `Hello, ${name}!`;
module.exports = { greet };

// Importing
const { greet } = require('./greet');
console.log(greet('World'));
```

### Key Characteristics

- **Synchronous loading** — `require()` blocks execution until the file is fully loaded, which is fine on a server but problematic in browsers [2].
- **Dynamic by nature** — you can call `require()` inside `if` blocks, loops, or functions at runtime [1].
- **`module.exports` / `exports`** — the exported value is a plain JavaScript object, assigned at runtime.
- **No tree-shaking** — because exports are determined at runtime, bundlers cannot statically determine which parts are unused [4].

CommonJS is still the right choice when maintaining existing Node.js codebases or working with packages that haven't shipped an ESM build [2].

## AMD — Asynchronous Module Definition

AMD emerged around 2011 specifically to solve browser performance: unlike CommonJS, it loads dependencies **asynchronously** so the page doesn't freeze [5].

```js
// AMD define + require via RequireJS
define(['dependency'], function(dep) {
  return { hello: () => dep.greet() };
});

require(['myModule'], function(mod) {
  mod.hello();
});
```

AMD was popularised by the **RequireJS** loader. However, with ES Modules now providing native async loading in every browser, AMD is considered largely obsolete for new projects [6].

## UMD — Universal Module Definition

In 2011, UMD arrived as a compatibility shim to bridge the gap between CommonJS (Node.js), AMD (browsers), and plain global scripts [5].

```js
(function(root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);          // AMD
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();   // CommonJS
  } else {
    root.myLib = factory();       // Global variable
  }
}(this, function() {
  return { version: '1.0' };
}));
```

Major libraries like **Lodash, Underscore.js, Backbone.js, and Moment.js** adopted UMD to be universally consumable [6]. Today, UMD is practically obsolete because ES Modules are natively supported everywhere — but you'll still encounter it in older packages on npm.

## ES Modules (ESM) — The Modern Standard

Introduced in ES2015 (ES6) and now supported natively in all modern browsers and Node.js ≥ 12, ESM is the **official, standardised module system** for JavaScript [4].

### Syntax

```js
// Named exports
export const add = (a, b) => a + b;
export const PI = 3.14159;

// Default export
export default class Calculator { /* ... */ }

// Importing
import Calculator, { add, PI } from './math.js';
```

### Key Characteristics

- **Static analysis** — `import` and `export` statements must be at the top level, enabling tools like Webpack and Rollup to perform **tree-shaking** (removing dead code) [3].
- **Asynchronous loading** — the browser or Node.js fetches and parses modules without blocking [1].
- **Live bindings** — imported values are live references, not copies, so changes in the exporting module are reflected in the importer [8].
- **Top-level `await`** — ESM files can use `await` outside `async` functions, a feature CJS does not support [2].
- **Explicit file extensions** — relative imports must include the extension (e.g., `./utils.js`) [4].

## Dynamic `import()` — Lazy Loading on Demand

The `import()` operator (dynamic import) is a **function-like expression** that loads an ES module asynchronously and returns a Promise [7]. It works in both ESM and CJS contexts.

```js
// Load a module only when the user clicks a button
button.addEventListener('click', async () => {
  const { Chart } = await import('./chart.js');
  new Chart(data).render();
});
```

### Common Use Cases

- **Code splitting** — ship only the JavaScript a user currently needs
- **Conditional loading** — load a polyfill only in older browsers
- **Runtime path construction** — build module paths from variables
- **CJS ↔ ESM bridge** — CommonJS code can import an ESM package using `await import()` [8]

Dynamic imports are fully supported in all modern browsers and Node.js [7].

## File Extensions: `.js`, `.mjs`, and `.cjs`

The extension you choose tells Node.js (and your bundler) **which module system to use** [4][9].

| Extension | Module System | When to Use |
|-----------|--------------|-------------|
| `.js` | Determined by `package.json` `"type"` field | Default; follows project-wide setting |
| `.mjs` | Always ES Module | Force a single file to be ESM, regardless of `package.json` |
| `.cjs` | Always CommonJS | Force a single file to be CJS inside an ESM-first project |

### The `package.json` `"type"` Field

```json
// All .js files treated as ES Modules
{ "type": "module" }

// All .js files treated as CommonJS (default)
{ "type": "commonjs" }
```

Setting `"type": "module"` in `package.json` makes every `.js` file in that package an ES module [4]. You can override per-file using `.mjs` (force ESM) or `.cjs` (force CJS) extensions regardless of the `"type"` setting [9].

## CJS vs ESM — Full Comparison

| Feature | CommonJS (CJS) | ES Modules (ESM) |
|---|---|---|
| **Syntax** | `require()` / `module.exports` | `import` / `export` |
| **Loading** | Synchronous | Asynchronous |
| **Where it runs** | Node.js (natively) | Browser + Node.js |
| **Tree-shaking** | ❌ Not possible | ✅ Supported |
| **Dynamic imports** | `require()` anywhere | `import()` expression |
| **Top-level `await`** | ❌ | ✅ |
| **Live bindings** | ❌ (copy at load time) | ✅ |
| **File extension** | `.cjs` or `.js` | `.mjs` or `.js` |
| **Status** | Legacy (still widely used) | Modern standard |

## Interoperability: Mixing CJS and ESM

Node.js lets both systems coexist with important rules [8]:

- ✅ **ESM can `import` CommonJS** packages — Node.js wraps `module.exports` as the default export.
- ❌ **CJS cannot `require()` an ESM** file — this throws an `ERR_REQUIRE_ESM` error.
- ✅ **CJS can load ESM** using dynamic `await import()` as a workaround [8].

## Which Module System Should You Use in 2026?

- **New projects** → Use **ES Modules** (`"type": "module"` in `package.json`). ESM is the standard, enables tree-shaking, and works in both browsers and Node.js [1][2].
- **Existing Node.js codebases** → **CommonJS** is still practical and well-supported; migrate incrementally.
- **Library authors** → Ship **dual packages** (both CJS and ESM builds) via the `"exports"` field in `package.json` for maximum compatibility [3].
- **Legacy browser support** → Use a bundler (Vite, Webpack, Rollup) that converts ESM to the target format; AMD/UMD are no longer necessary [6].

The JavaScript module landscape has converged: ESM is the clear winner for new code, but understanding CJS (and even AMD/UMD) is essential for navigating the vast npm ecosystem built on those older foundations.

## Sources
1. [CommonJS vs ES Modules in JavaScript — Syncfusion Blogs](https://www.syncfusion.com/blogs/post/js-commonjs-vs-es-modules)
2. [CommonJS vs. ES Modules — Better Stack Community](https://betterstack.com/community/guides/scaling-nodejs/commonjs-vs-esm/)
3. [CommonJS vs. ES Modules in Node.js — LogRocket Blog](https://blog.logrocket.com/commonjs-vs-es-modules-node-js/)
4. [ECMAScript Modules — Node.js Official Documentation](https://nodejs.org/api/esm.html)
5. [What the heck are CJS, AMD, UMD, and ESM in Javascript? — DEV Community](https://dev.to/iggredible/what-the-heck-are-cjs-amd-umd-and-esm-ikm)
6. [Navigating the module maze: History of JavaScript module systems — Codilime](https://codilime.com/blog/history-of-javascript-module-systems/)
7. [import() — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)
8. [A Deep Dive Into CommonJS and ES Modules in Node.js — AppSignal Blog](https://blog.appsignal.com/2024/12/11/a-deep-dive-into-commonjs-and-es-modules-in-nodejs.html)
9. [What are .mjs, .cjs, .mts, and .cts extensions? — Total TypeScript](https://www.totaltypescript.com/concepts/mjs-cjs-mts-and-cts-extensions)
10. [Understanding MJS and CJS — RGB Studios](https://rgbstudios.org/blog/modules-explained-mjs-cjs)