+++
title       = "JavaScript मॉड्युल सिस्टम्स: require, import, .mjs आणि बरेच काही"
description = "प्रत्येक JavaScript मॉड्युल सिस्टमसाठी संपूर्ण मार्गदर्शक — CommonJS, AMD, UMD, ESM, .mjs, .cjs — उदाहरणांसह, तुलना सारणीसह, आणि 2026 साठी सर्वोत्तम पद्धतींसह."
date        = "2026-06-01T16:37:22+05:30"
slug          = "javascript-module-systems-require-import-mjs"
tags          = ["JavaScript", "Node.js", "ES Modules", "CommonJS", "Web Development"]
keywords      = ["JavaScript module systems", "CommonJS require", "ES modules import", "mjs cjs difference", "dynamic import JavaScript", "AMD UMD JavaScript"]
canonical     = "/mr/posts/javascript-module-systems-require-import-mjs/"
feature_image = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop"
+++

JavaScript मध्ये पूर्वी कोड वेगवेगळ्या फाइल्समध्ये विभाजित करण्याचा कोणताही अंगभूत मार्ग नव्हता — या मर्यादेमुळे स्पर्धात्मक मॉड्युल फॉर्मॅट्सची एक संपूर्ण परिसंस्था निर्माण झाली. आज, डेव्हलपर्स `require()`, `import`, `.mjs`, `.cjs`, AMD, आणि UMD यांना बऱ्याचदा एकाच प्रकल्पात भेटतात. हे मार्गदर्शक प्रत्येक मॉड्युल सिस्टम समजावून सांगते, प्रत्येक केव्हा वापरायचे हे स्पष्ट करते, आणि पुढे जाण्याचा स्पष्ट मार्ग दाखवते.

## JavaScript ला मॉड्युल सिस्टम्सची गरज का पडली

वेबच्या सुरुवातीच्या दिवसांत, JavaScript हे साध्या पृष्ठ संवादांसाठी असलेली एक स्क्रिप्टिंग भाषा होती. जसजशे अॅप्लिकेशन्स वाढले, डेव्हलपर्सनी सर्वकाही ग्लोबल व्हेरिएबल्समध्ये कोंबले — ज्यामुळे नामकरण टकराव आणि अव्यवस्थापित "स्पघेट्टी" कोड निर्माण झाला [1]. समुदायाने भाषेच्या बाहेर मॉड्युल पॅटर्न्स शोधून उत्तर दिले: प्रथम खाजगी स्कोप तयार करण्यासाठी Immediately Invoked Function Expressions (IIFEs), नंतर AMD आणि CommonJS सारख्या औपचारिक मॉड्युल स्पेसिफिकेशन्स. 2015 मध्येच JavaScript ला ES6 स्पेसिफिकेशनद्वारे अखेरीस नेटिव्ह मॉड्युल सिस्टम मिळाली [6].

![js module timeline](/images/posts/javascript-module-systems-require-import-mjs/js-module-timeline.svg)

## CommonJS (CJS) — Node.js चा मुख्य आधार

CommonJS 2009 मध्ये सर्व्हर-साइड JavaScript साठी मॉड्युल सिस्टम म्हणून सादर करण्यात आले, आणि आजही ते **Node.js मधील डीफॉल्ट मॉड्युल फॉर्मॅट** आहे [3].

### सिंटॅक्स

```js
// निर्यात
const greet = (name) => `Hello, ${name}!`;
module.exports = { greet };

// आयात
const { greet } = require('./greet');
console.log(greet('World'));
```

### मुख्य वैशिष्ट्ये

- **समकालिक लोडिंग** — `require()` फाइल पूर्णपणे लोड होईपर्यंत कार्यान्वयन थांबवते, जे सर्व्हरवर ठीक आहे परंतु ब्राउझरमध्ये समस्याजनक आहे [2].
- **स्वभावाने डायनामिक** — तुम्ही `require()` ला रनटाइमवर `if` ब्लॉक्स, लूप्स किंवा फंक्शन्समध्ये कॉल करू शकता [1].
- **`module.exports` / `exports`** — निर्यात केलेले मूल्य एक साधा JavaScript ऑब्जेक्ट आहे, रनटाइमवर नियुक्त केला जातो.
- **ट्री-शेकिंग नाही** — कारण निर्यात रनटाइमवर निर्धारित केले जातात, बंडलर्स स्थिरपणे कोणते भाग वापरले जात नाहीत हे निर्धारित करू शकत नाहीत [4].

CommonJS अजूनही विद्यमान Node.js कोडबेसेस राखताना किंवा ESM बिल्ड न पाठवलेल्या पॅकेजेससह काम करताना योग्य निवड आहे [2].

## AMD — असिंक्रोनस मॉड्युल व्याख्या

AMD 2011 च्या आसपास विशेषतः ब्राउझर परफॉर्मन्स सोडवण्यासाठी उदयास आले: CommonJS च्या विपरीत, ते अवलंबित्व **असिंक्रोनसपणे** लोड करते जेणेकरून पृष्ठ गोठत नाही [5].

```js
// RequireJS द्वारे AMD define + require
define(['dependency'], function(dep) {
  return { hello: () => dep.greet() };
});

require(['myModule'], function(mod) {
  mod.hello();
});
```

AMD **RequireJS** लोडरद्वारे लोकप्रिय झाले. तथापि, ES Modules आता प्रत्येक ब्राउझरमध्ये नेटिव्ह असिंक लोडिंग प्रदान करत असल्याने, AMD नवीन प्रकल्पांसाठी मोठ्या प्रमाणात कालबाह्य मानले जाते [6].

## UMD — युनिव्हर्सल मॉड्युल व्याख्या

2011 मध्ये, UMD CommonJS (Node.js), AMD (ब्राउझर्स), आणि साध्या ग्लोबल स्क्रिप्ट्समधील अंतर भरून काढण्यासाठी सुसंगतता शिम म्हणून आले [5].

```js
(function(root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);          // AMD
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();   // CommonJS
  } else {
    root.myLib = factory();       // ग्लोबल व्हेरिएबल
  }
}(this, function() {
  return { version: '1.0' };
}));
```

**Lodash, Underscore.js, Backbone.js, आणि Moment.js** सारख्या प्रमुख लायब्ररींनी UMD सार्वत्रिकपणे वापरता यावे म्हणून स्वीकारले [6]. आज, UMD व्यावहारिकदृष्ट्या कालबाह्य आहे कारण ES Modules सर्वत्र नेटिव्हली सपोर्ट केले जातात — परंतु तुम्हाला अजूनही npm वरील जुन्या पॅकेजेसमध्ये ते आढळेल.

## ES Modules (ESM) — आधुनिक मानक

ES2015 (ES6) मध्ये सादर केले गेले आणि आता सर्व आधुनिक ब्राउझर्स आणि Node.js ≥ 12 मध्ये नेटिव्हली सपोर्ट केले गेले, ESM हे JavaScript साठी **अधिकृत, प्रमाणित मॉड्युल सिस्टम** आहे [4].

### सिंटॅक्स

```js
// नाव असलेले exports
export const add = (a, b) => a + b;
export const PI = 3.14159;

// डीफॉल्ट export
export default class Calculator { /* ... */ }

// आयात करणे
import Calculator, { add, PI } from './math.js';
```

### मुख्य वैशिष्ट्ये

- **स्थिर विश्लेषण** — `import` आणि `export` स्टेटमेंट्स टॉप लेव्हलवर असणे आवश्यक आहे, ज्यामुळे Webpack आणि Rollup सारखी साधने **ट्री-शेकिंग** (मृत कोड काढणे) करू शकतात [3].
- **असिंक्रोनस लोडिंग** — ब्राउझर किंवा Node.js ब्लॉक न करता मॉड्युल्स फेच आणि पार्स करते [1].
- **लाइव्ह बाइंडिंग्स** — आयात केलेली मूल्ये लाइव्ह संदर्भ आहेत, कॉपी नाहीत, त्यामुळे निर्यात करणाऱ्या मॉड्युलमधील बदल आयात करणाऱ्यामध्ये प्रतिबिंबित होतात [8].
- **टॉप-लेव्हल `await`** — ESM फाइल्स `async` फंक्शन्सच्या बाहेर `await` वापरू शकतात, एक वैशिष्ट्य जे CJS सपोर्ट करत नाही [2].
- **स्पष्ट फाइल एक्स्टेंशन्स** — सापेक्ष आयातांमध्ये एक्स्टेंशन समाविष्ट असणे आवश्यक आहे (उदा., `./utils.js`) [4].

## डायनामिक `import()` — मागणीनुसार लेझी लोडिंग

`import()` ऑपरेटर (डायनामिक इम्पोर्ट) हे एक **फंक्शन-सदृश एक्स्प्रेशन** आहे जे ES मॉड्युल असिंक्रोनसपणे लोड करते आणि Promise परत करते [7]. हे ESM आणि CJS दोन्ही संदर्भांमध्ये कार्य करते.

```js
// वापरकर्ता बटण क्लिक केल्यावरच मॉड्युल लोड करा
button.addEventListener('click', async () => {
  const { Chart } = await import('./chart.js');
  new Chart(data).render();
});
```

### सामान्य वापर प्रकरणे

- **कोड विभाजन** — वापरकर्त्याला सध्या आवश्यक असलेला JavaScript फक्त पाठवा
- **सशर्त लोडिंग** — फक्त जुन्या ब्राउझर्समध्ये पॉलीफिल लोड करा
- **रनटाइम पाथ बांधणी** — व्हेरिएबल्सपासून मॉड्युल पाथ तयार करा
- **CJS ↔ ESM ब्रिज** — CommonJS कोड `await import()` वापरून ESM पॅकेज आयात करू शकतो [8]

डायनामिक इम्पोर्ट्स सर्व आधुनिक ब्राउझर्स आणि Node.js मध्ये पूर्णपणे सपोर्ट केले जातात [7].

## फाइल एक्स्टेंशन्स: `.js`, `.mjs`, आणि `.cjs`

तुम्ही निवडलेले एक्स्टेंशन Node.js (आणि तुमच्या बंडलरला) **कोणती मॉड्युल सिस्टम वापरायची** हे सांगते [4][9].

| एक्स्टेंशन | मॉड्युल सिस्टम | केव्हा वापरावे |
|-----------|--------------|-------------|
| `.js` | `package.json` च्या `"type"` फील्डद्वारे निर्धारित | डीफॉल्ट; प्रकल्प-व्यापी सेटिंग अनुसरते |
| `.mjs` | नेहमी ES Module | `package.json` कशाही असो, एकाच फाइलला ESM करण्यासाठी |
| `.cjs` | नेहमी CommonJS | ESM-प्रथम प्रकल्पात एकाच फाइलला CJS करण्यासाठी |

### `package.json` चे `"type"` फील्ड

```json
// सर्व .js फाइल्स ES Modules म्हणून मानल्या जातात
{ "type": "module" }

// सर्व .js फाइल्स CommonJS म्हणून मानल्या जातात (डीफॉल्ट)
{ "type": "commonjs" }
```

`package.json` मध्ये `"type": "module"` सेट केल्याने त्या पॅकेजमधील प्रत्येक `.js` फाइल ES मॉड्युल बनते [4]. `"type"` सेटिंग कशाही असो तुम्ही प्रति-फाइल `.mjs` (ESM सक्ती) किंवा `.cjs` (CJS सक्ती) एक्स्टेंशन वापरून ओव्हरराइड करू शकता [9].

## CJS वि ESM — संपूर्ण तुलना

| वैशिष्ट्य | CommonJS (CJS) | ES Modules (ESM) |
|---|---|---|
| **सिंटॅक्स** | `require()` / `module.exports` | `import` / `export` |
| **लोडिंग** | समकालिक | असिंक्रोनस |
| **कुठे चालते** | Node.js (नेटिव्हली) | Browser + Node.js |
| **ट्री-शेकिंग** | ❌ शक्य नाही | ✅ सपोर्टेड |
| **डायनामिक इम्पोर्ट्स** | `require()` कुठेही | `import()` एक्स्प्रेशन |
| **टॉप-लेव्हल `await`** | ❌ | ✅ |
| **लाइव्ह बाइंडिंग्स** | ❌ (लोड वेळी कॉपी) | ✅ |
| **फाइल एक्स्टेंशन** | `.cjs` किंवा `.js` | `.mjs` किंवा `.js` |
| **स्थिती** | लेगसी (अजूनही मोठ्या प्रमाणात वापरात) | आधुनिक मानक |

## इंटरऑपरेबिलिटी: CJS आणि ESM मिश्रण

Node.js दोन्ही सिस्टम्सना महत्त्वाच्या नियमांसह एकत्र राहण्याची परवानगी देते [8]:

- ✅ **ESM CommonJS** पॅकेजेस `import` करू शकते — Node.js `module.exports` ला डीफॉल्ट एक्सपोर्ट म्हणून गुंडाळते.
- ❌ **CJS ESM** फाइल `require()` करू शकत नाही — यामुळे `ERR_REQUIRE_ESM` त्रुटी येते.
- ✅ **CJS ESM लोड करू शकते** डायनामिक `await import()` ला उपाय म्हणून वापरून [8].

## 2026 मध्ये कोणती मॉड्युल सिस्टम वापरावी?

- **नवीन प्रकल्प** → **ES Modules** वापरा (`package.json` मध्ये `"type": "module"`). ESM मानक आहे, ट्री-शेकिंग सक्षम करते, आणि ब्राउझर्स आणि Node.js दोन्हीमध्ये कार्य करते [1][2].
- **विद्यमान Node.js कोडबेसेस** → **CommonJS** अजूनही व्यावहारिक आणि चांगले सपोर्टेड आहे; हळूहळू स्थलांतर करा.
- **लायब्ररी लेखक** → जास्तीत जास्त सुसंगततेसाठी `package.json` मधील `"exports"` फील्डद्वारे **दुहेरी पॅकेजेस** (CJS आणि ESM दोन्ही बिल्ड) पाठवा [3].
- **लेगसी ब्राउझर सपोर्ट** → ESM ला लक्ष्य फॉर्मॅटमध्ये रूपांतरित करणारा बंडलर (Vite, Webpack, Rollup) वापरा; AMD/UMD आता आवश्यक नाहीत [6].

JavaScript मॉड्युल लँडस्केप एकत्र आले आहे: नवीन कोडसाठी ESM स्पष्ट विजेता आहे, परंतु त्या जुन्या पायावर बांधलेल्या विशाल npm परिसंस्थेत मार्गक्रमण करण्यासाठी CJS (आणि AMD/UMD देखील) समजणे आवश्यक आहे.

## स्रोत
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