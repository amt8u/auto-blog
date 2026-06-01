+++
title       = "JavaScript मॉड्यूल सिस्टम: require, import, .mjs और अधिक"
description = "हर JavaScript मॉड्यूल सिस्टम का संपूर्ण गाइड — CommonJS, AMD, UMD, ESM, .mjs, .cjs — उदाहरणों, तुलना तालिका और 2026 के सर्वोत्तम अभ्यासों के साथ।"
date        = "2026-06-01T16:37:22+05:30"
slug          = "javascript-module-systems-require-import-mjs"
tags          = ["JavaScript", "Node.js", "ES मॉड्यूल", "CommonJS", "वेब डेवलपमेंट"]
keywords      = ["JavaScript मॉड्यूल सिस्टम", "CommonJS require", "ES मॉड्यूल import", "mjs cjs अंतर", "डायनामिक import JavaScript", "AMD UMD JavaScript"]
canonical     = "/hi/posts/javascript-module-systems-require-import-mjs/"
feature_image = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop"
+++

JavaScript में पहले कोड को फ़ाइलों में विभाजित करने का कोई अंतर्निहित तरीका नहीं था — इस सीमा ने प्रतिस्पर्धी मॉड्यूल फॉर्मेट के एक पूरे इकोसिस्टम को जन्म दिया। आज, डेवलपर्स `require()`, `import`, `.mjs`, `.cjs`, AMD और UMD का सामना करते हैं, अक्सर एक ही प्रोजेक्ट में। यह गाइड हर मॉड्यूल सिस्टम को स्पष्ट करता है, बताता है कि प्रत्येक का उपयोग कब करना है, और आगे का स्पष्ट रास्ता दिखाता है।

## JavaScript को मॉड्यूल सिस्टम की आवश्यकता क्यों थी

वेब के शुरुआती दिनों में, JavaScript एक स्क्रिप्टिंग भाषा थी जो सरल पेज इंटरैक्शन के लिए थी। जैसे-जैसे एप्लिकेशन बड़े होते गए, डेवलपर्स सब कुछ ग्लोबल वेरिएबल्स में भरने लगे — जिससे नामकरण टकराव और अप्रबंधनीय "स्पेगेटी" कोड पैदा हुआ [1]। समुदाय ने भाषा के बाहर मॉड्यूल पैटर्न का आविष्कार करके जवाब दिया: पहले प्राइवेट स्कोप बनाने के लिए Immediately Invoked Function Expressions (IIFEs), फिर AMD और CommonJS जैसे औपचारिक मॉड्यूल स्पेसिफिकेशन। केवल 2015 में ही JavaScript को ES6 स्पेसिफिकेशन के माध्यम से एक नेटिव मॉड्यूल सिस्टम मिला [6]।

![js module timeline](/images/posts/javascript-module-systems-require-import-mjs/js-module-timeline.svg)

## CommonJS (CJS) — Node.js का वर्कहॉर्स

CommonJS को 2009 में सर्वर-साइड JavaScript के लिए मॉड्यूल सिस्टम के रूप में पेश किया गया था, और यह आज भी **Node.js में डिफ़ॉल्ट मॉड्यूल फॉर्मेट** बना हुआ है [3]।

### सिंटैक्स

```js
// Exporting
const greet = (name) => `Hello, ${name}!`;
module.exports = { greet };

// Importing
const { greet } = require('./greet');
console.log(greet('World'));
```

### मुख्य विशेषताएं

- **सिंक्रोनस लोडिंग** — `require()` तब तक एक्जीक्यूशन को ब्लॉक करता है जब तक फ़ाइल पूरी तरह लोड नहीं हो जाती, जो सर्वर पर ठीक है लेकिन ब्राउज़र में समस्याजनक है [2]।
- **स्वभाव से डायनामिक** — आप रनटाइम पर `if` ब्लॉक, लूप्स, या फंक्शन के अंदर `require()` कॉल कर सकते हैं [1]।
- **`module.exports` / `exports`** — एक्सपोर्ट किया गया मान एक सामान्य JavaScript ऑब्जेक्ट है, जो रनटाइम पर असाइन होता है।
- **कोई tree-shaking नहीं** — क्योंकि एक्सपोर्ट रनटाइम पर निर्धारित होते हैं, बंडलर्स स्थैतिक रूप से यह निर्धारित नहीं कर सकते कि कौन से हिस्से अप्रयुक्त हैं [4]।

CommonJS अभी भी सही विकल्प है जब मौजूदा Node.js कोडबेस को मेंटेन करना हो या उन पैकेजों के साथ काम करना हो जिन्होंने अभी ESM बिल्ड शिप नहीं किया है [2]।

## AMD — असिंक्रोनस मॉड्यूल डेफिनिशन

AMD लगभग 2011 के आसपास विशेष रूप से ब्राउज़र परफॉर्मेंस को हल करने के लिए उभरा: CommonJS के विपरीत, यह डिपेंडेंसी को **असिंक्रोनस रूप से** लोड करता है ताकि पेज फ्रीज न हो [5]।

```js
// AMD define + require via RequireJS
define(['dependency'], function(dep) {
  return { hello: () => dep.greet() };
});

require(['myModule'], function(mod) {
  mod.hello();
});
```

AMD को **RequireJS** लोडर द्वारा लोकप्रिय बनाया गया था। हालांकि, ES Modules अब हर ब्राउज़र में नेटिव async लोडिंग प्रदान करते हैं, इसलिए नए प्रोजेक्टों के लिए AMD को काफी हद तक अप्रचलित माना जाता है [6]।

## UMD — यूनिवर्सल मॉड्यूल डेफिनिशन

2011 में, UMD एक कम्पैटिबिलिटी शिम के रूप में आया जो CommonJS (Node.js), AMD (ब्राउज़र), और सामान्य ग्लोबल स्क्रिप्ट के बीच की खाई को पाटने के लिए था [5]।

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

**Lodash, Underscore.js, Backbone.js और Moment.js** जैसी प्रमुख लाइब्रेरीज़ ने UMD को सार्वभौमिक रूप से उपभोग्य बनाने के लिए अपनाया [6]। आज, UMD व्यावहारिक रूप से अप्रचलित है क्योंकि ES Modules हर जगह नेटिव रूप से समर्थित हैं — लेकिन आप अभी भी npm पर पुराने पैकेजों में इसे देखेंगे।

## ES Modules (ESM) — आधुनिक मानक

ES2015 (ES6) में पेश किया गया और अब सभी आधुनिक ब्राउज़रों और Node.js ≥ 12 में नेटिव रूप से समर्थित, ESM JavaScript के लिए **आधिकारिक, मानकीकृत मॉड्यूल सिस्टम** है [4]।

### सिंटैक्स

```js
// Named exports
export const add = (a, b) => a + b;
export const PI = 3.14159;

// Default export
export default class Calculator { /* ... */ }

// Importing
import Calculator, { add, PI } from './math.js';
```

### मुख्य विशेषताएं

- **स्टैटिक एनालिसिस** — `import` और `export` स्टेटमेंट टॉप लेवल पर होने चाहिए, जिससे Webpack और Rollup जैसे टूल **tree-shaking** (डेड कोड हटाना) कर सकते हैं [3]।
- **असिंक्रोनस लोडिंग** — ब्राउज़र या Node.js बिना ब्लॉक किए मॉड्यूल को फेच और पार्स करता है [1]।
- **लाइव बाइंडिंग** — इंपोर्ट किए गए मान लाइव रेफरेंस हैं, कॉपी नहीं, इसलिए एक्सपोर्टिंग मॉड्यूल में बदलाव इंपोर्टर में दिखते हैं [8]।
- **टॉप-लेवल `await`** — ESM फ़ाइलें `async` फंक्शन के बाहर `await` का उपयोग कर सकती हैं, एक ऐसी सुविधा जो CJS में नहीं है [2]।
- **स्पष्ट फ़ाइल एक्सटेंशन** — रिलेटिव इंपोर्ट में एक्सटेंशन शामिल होना चाहिए (जैसे, `./utils.js`) [4]।

## डायनामिक `import()` — मांग पर लेज़ी लोडिंग

`import()` ऑपरेटर (डायनामिक import) एक **फंक्शन-जैसा एक्सप्रेशन** है जो ES मॉड्यूल को असिंक्रोनस रूप से लोड करता है और एक Promise लौटाता है [7]। यह ESM और CJS दोनों संदर्भों में काम करता है।

```js
// Load a module only when the user clicks a button
button.addEventListener('click', async () => {
  const { Chart } = await import('./chart.js');
  new Chart(data).render();
});
```

### सामान्य उपयोग के मामले

- **कोड स्प्लिटिंग** — केवल वही JavaScript शिप करें जो उपयोगकर्ता को अभी चाहिए
- **कंडीशनल लोडिंग** — केवल पुराने ब्राउज़रों में पॉलीफिल लोड करें
- **रनटाइम पाथ कंस्ट्रक्शन** — वेरिएबल से मॉड्यूल पाथ बनाएं
- **CJS ↔ ESM ब्रिज** — CommonJS कोड `await import()` का उपयोग करके ESM पैकेज इंपोर्ट कर सकता है [8]

डायनामिक इंपोर्ट सभी आधुनिक ब्राउज़रों और Node.js में पूरी तरह समर्थित हैं [7]।

## फ़ाइल एक्सटेंशन: `.js`, `.mjs` और `.cjs`

आप जो एक्सटेंशन चुनते हैं वह Node.js (और आपके बंडलर) को बताता है **कौन सा मॉड्यूल सिस्टम उपयोग करना है** [4][9]।

| एक्सटेंशन | मॉड्यूल सिस्टम | कब उपयोग करें |
|-----------|--------------|-------------|
| `.js` | `package.json` के `"type"` फ़ील्ड द्वारा निर्धारित | डिफ़ॉल्ट; प्रोजेक्ट-वाइड सेटिंग का पालन करता है |
| `.mjs` | हमेशा ES Module | `package.json` की परवाह किए बिना एक फ़ाइल को ESM बनाएं |
| `.cjs` | हमेशा CommonJS | ESM-फर्स्ट प्रोजेक्ट में एक फ़ाइल को CJS बनाएं |

### `package.json` का `"type"` फ़ील्ड

```json
// All .js files treated as ES Modules
{ "type": "module" }

// All .js files treated as CommonJS (default)
{ "type": "commonjs" }
```

`package.json` में `"type": "module"` सेट करने से उस पैकेज की हर `.js` फ़ाइल ES मॉड्यूल बन जाती है [4]। आप `"type"` सेटिंग की परवाह किए बिना `.mjs` (ESM फोर्स) या `.cjs` (CJS फोर्स) एक्सटेंशन का उपयोग करके प्रति-फ़ाइल ओवरराइड कर सकते हैं [9]।

## CJS बनाम ESM — पूर्ण तुलना

| फ़ीचर | CommonJS (CJS) | ES Modules (ESM) |
|---|---|---|
| **सिंटैक्स** | `require()` / `module.exports` | `import` / `export` |
| **लोडिंग** | सिंक्रोनस | असिंक्रोनस |
| **कहाँ चलता है** | Node.js (नेटिव रूप से) | Browser + Node.js |
| **Tree-shaking** | ❌ संभव नहीं | ✅ समर्थित |
| **डायनामिक इंपोर्ट** | `require()` कहीं भी | `import()` एक्सप्रेशन |
| **टॉप-लेवल `await`** | ❌ | ✅ |
| **लाइव बाइंडिंग** | ❌ (लोड टाइम पर कॉपी) | ✅ |
| **फ़ाइल एक्सटेंशन** | `.cjs` या `.js` | `.mjs` या `.js` |
| **स्टेटस** | लीगेसी (अभी भी व्यापक रूप से उपयोग) | आधुनिक मानक |

## इंटरऑपरेबिलिटी: CJS और ESM का मिश्रण

Node.js दोनों सिस्टमों को महत्वपूर्ण नियमों के साथ सह-अस्तित्व में रहने देता है [8]:

- ✅ **ESM CommonJS पैकेज को `import` कर सकता है** — Node.js `module.exports` को डिफ़ॉल्ट एक्सपोर्ट के रूप में रैप करता है।
- ❌ **CJS ESM फ़ाइल को `require()` नहीं कर सकता** — यह `ERR_REQUIRE_ESM` त्रुटि फेंकता है।
- ✅ **CJS डायनामिक `await import()` का उपयोग करके ESM लोड कर सकता है** एक वर्कअराउंड के रूप में [8]।

## 2026 में आपको कौन सा मॉड्यूल सिस्टम उपयोग करना चाहिए?

- **नए प्रोजेक्ट** → **ES Modules** (`package.json` में `"type": "module"`) का उपयोग करें। ESM मानक है, tree-shaking सक्षम करता है, और ब्राउज़र और Node.js दोनों में काम करता है [1][2]।
- **मौजूदा Node.js कोडबेस** → **CommonJS** अभी भी व्यावहारिक और अच्छी तरह से समर्थित है; धीरे-धीरे माइग्रेट करें।
- **लाइब्रेरी लेखक** → अधिकतम कम्पैटिबिलिटी के लिए `package.json` के `"exports"` फ़ील्ड के माध्यम से **दोहरे पैकेज** (CJS और ESM दोनों बिल्ड) शिप करें [3]।
- **लीगेसी ब्राउज़र समर्थन** → एक बंडलर (Vite, Webpack, Rollup) का उपयोग करें जो ESM को लक्ष्य फॉर्मेट में परिवर्तित करता है; AMD/UMD अब आवश्यक नहीं हैं [6]।

JavaScript मॉड्यूल परिदृश्य एकत्रित हो गया है: नए कोड के लिए ESM स्पष्ट विजेता है, लेकिन उन पुरानी नींवों पर बने विशाल npm इकोसिस्टम को नेविगेट करने के लिए CJS (और यहां तक कि AMD/UMD) को समझना आवश्यक है।

## स्रोत
1. [JavaScript में CommonJS बनाम ES Modules — Syncfusion Blogs](https://www.syncfusion.com/blogs/post/js-commonjs-vs-es-modules)
2. [CommonJS बनाम ES Modules — Better Stack Community](https://betterstack.com/community/guides/scaling-nodejs/commonjs-vs-esm/)
3. [Node.js में CommonJS बनाम ES Modules — LogRocket Blog](https://blog.logrocket.com/commonjs-vs-es-modules-node-js/)
4. [ECMAScript Modules — Node.js आधिकारिक दस्तावेज़ीकरण](https://nodejs.org/api/esm.html)
5. [JavaScript में CJS, AMD, UMD और ESM क्या हैं? — DEV Community](https://dev.to/iggredible/what-the-heck-are-cjs-amd-umd-and-esm-ikm)
6. [मॉड्यूल भूलभुलैया नेविगेट करना: JavaScript मॉड्यूल सिस्टम का इतिहास — Codilime](https://codilime.com/blog/history-of-javascript-module-systems/)
7. [import() — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import)
8. [Node.js में CommonJS और ES Modules की गहरी जानकारी — AppSignal Blog](https://blog.appsignal.com/2024/12/11/a-deep-dive-into-commonjs-and-es-modules-in-nodejs.html)
9. [.mjs, .cjs, .mts और .cts एक्सटेंशन क्या हैं? — Total TypeScript](https://www.totaltypescript.com/concepts/mjs-cjs-mts-and-cts-extensions)
10. [MJS और CJS को समझना — RGB Studios](https://rgbstudios.org/blog/modules-explained-mjs-cjs)