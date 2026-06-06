+++
title       = "Vite समजून घ्या: ते Webpack ला का मागे टाकते आणि पुढे काय?"
description = "Vite म्हणजे काय, त्याचा native ESM दृष्टिकोन dev server startup जवळपास तात्काळ कसा करतो, ते Webpack पेक्षा का चांगले आहे, आणि ते शेवटी तितकेच गुंतागुंतीचे होईल का."
date        = "2026-06-05T14:59:00+05:30"
slug        = "vite-vs-webpack-why-vite-is-fast"
tags        = ["vite", "webpack", "build-tools", "frontend", "javascript"]
keywords    = ["what is vite", "vite vs webpack", "vite build tool", "vite faster than webpack", "vite future"]
canonical   = "/mr/posts/vite-vs-webpack-why-vite-is-fast/"
feature_image = "/images/posts/vite-vs-webpack-why-vite-is-fast/vite-feature.svg"
+++

मला पहिल्यांदा CRA (जे आतून Webpack वापरते) वरून Vite वर प्रोजेक्ट स्विच केल्याचे आठवते. dev server एका सेकंदापेक्षा कमी वेळात सुरू झाला. मी खरोखरच काही क्षण टर्मिनलकडे टक लावून पाहत राहिलो, आणखी काही होण्याची वाट पाहत. काहीच झाले नाही. बस्स तेवढेच होते — ते तयार होते. Webpack वरील ही काही छोटी सुधारणा नाही. हा पूर्णपणे वेगळा अनुभव आहे.

## Vite म्हणजे काय?

Vite (फ्रेंचमध्ये "fast" म्हणजे जलद, उच्चार "वीट") हे Evan You यांनी तयार केलेले frontend build tool आहे — तेच ज्यांनी Vue.js बनवले [1]. ते 2020 मध्ये लॉन्च झाले आणि वेगाने वाढत आहे. 2025 पर्यंत, Vite **दर आठवड्याला 5 कोटी 30 लाख npm downloads** नोंदवतो, Webpack च्या 3 कोटी 60 लाखांच्या तुलनेत [5]. त्याच्या GitHub stars देखील तीच कहाणी सांगतात: 78,000 विरुद्ध Webpack चे 66,000 [5].

प्रत्येक build tool चे दोन मुख्य काम असतात:
- hot module replacement (HMR) सह local development दरम्यान तुमचा code serve करणे
- production साठी output bundle आणि optimize करणे

Vite आणि Webpack दोन्ही हे करतात. *कसे* हे पूर्णपणे वेगळे आहे — आणि हाच फरक आहे ज्यामुळे एक मिलीसेकंदात सुरू होतो आणि दुसरा तुम्हाला वाट पाहायला लावतो.

## Webpack का मंद होतो?

Webpack चा दृष्टिकोन साधा पण खर्चिक आहे: **आधी सर्वकाही bundle करा, मग serve करा**. browser एकही pixel पाहण्यापूर्वी, Webpack तुमच्या project मधील प्रत्येक file वाचतो, प्रत्येक import chain सोडवतो, सर्वकाही compile करतो, आणि एक मोठा `bundle.js` output करतो. मध्यम आकाराच्या React app ला फक्त cold-start होण्यास 15–30 सेकंद लागू शकतात [1].

2014 मध्ये हे योग्य होते. तेव्हाचे browsers ES modules native पद्धतीने हाताळू शकत नव्हते — तुम्हाला त्यांना एक pre-processed file द्यावी लागत होती. Webpack त्या जगासाठी बनवले होते. समस्या ही आहे की browsers अनेक वर्षांपासून native ESM ला support करत असले तरी ते अजूनही मुख्यतः त्याच पद्धतीने काम करते.

HMR हा दुसरा वेदनाबिंदू आहे. जेव्हा तुम्ही एक file बदलता, Webpack bundle चे अंशतः पुनर्निर्माण करतो. मोठ्या projects वर, लहान बदल देखील दिसण्यापूर्वी 2–5 सेकंद लागू शकतात. तो feedback loop लक्ष केंद्रित करण्याची क्षमता नष्ट करतो.

Configuration ची गुंतागुंत हा पूर्णपणे वेगळा प्रश्न आहे. मला Webpack configs मिळाल्या आहेत ज्या 400+ lines लांब होत्या, loaders, plugins, आणि environment-specific overrides च्या थरांनी भरलेल्या, ज्या आता कोणीही पूर्णपणे समजत नव्हते. State of JavaScript survey नुसार, **86% developers अजूनही Webpack वापरतात, पण फक्त 14% ला ते खरोखर आवडते** [8].

## Vite प्रत्यक्षात कसे काम करते

Vite एक मूलभूत पैज लावते: **आधुनिक browsers ES modules native पद्धतीने समजतात, त्यामुळे development दरम्यान bundle करू नका**.

![vite विरुद्ध webpack esm diagram](/images/posts/vite-vs-webpack-why-vite-is-fast/vite-vs-webpack-esm-diagram.svg)

जेव्हा browser तुमच्या code मध्ये `import` आढळतो, तेव्हा तो Vite dev server ला request पाठवतो. Vite ती request intercept करतो, **esbuild** वापरून फक्त तीच एक file (TypeScript, JSX, जे असेल ते) transform करतो — Go मध्ये लिहिलेला bundler जो JavaScript-based equivalents पेक्षा सुमारे 10–100× जलद आहे — आणि ती परत करतो [3].

एक अडचण आहे: `node_modules` मधील third-party packages अनेकदा CommonJS असतात, ESM नाही. आणि काही libraries मध्ये शेकडो internal imports असतात ज्यामुळे शेकडो HTTP requests निर्माण होतील. त्यामुळे Vite **startup वेळी esbuild वापरून एकदाच dependencies pre-bundle करतो**, त्यांना ESM मध्ये convert करतो, आणि cache करतो. ही पायरी मिलीसेकंद घेते [1]. त्यानंतर, तुमच्या app च्या source files on demand serve केल्या जातात — bundling step अजिबात नाही.

**Vite मधील HMR project वाढत असताना जलद राहतो.** जेव्हा तुम्ही एक file बदलता, Vite फक्त त्या module आणि त्याच्या थेट dependents ला invalidate करतो. इतर कशालाही स्पर्श करत नाही. HMR boundary logic अचूक आहे. म्हणूनच Vite चा HMR 10-file project मध्ये तात्काळ वाटतो आणि 500-file project मध्येही तात्काळ वाटतो — Webpack च्या विपरीत, जिथे codebase मोठा होत असताना HMR speed कमी होते [3].

## Vite विरुद्ध Webpack — तुलनात्मक दृष्टी

| | Vite | Webpack |
|---|---|---|
| Dev server cold start | < 1 सेकंद | 15–30 सेकंद (मध्यम app) |
| HMR speed | कोणत्याही आकारात तात्काळ | project आकारासह कमी होते |
| सुरू करण्यासाठी Config | ~10 lines | अनेकदा शेकडो lines |
| Production bundler | Rollup / Rolldown | Webpack |
| Bundle size (सरासरी) | ~130 KB | ~150 KB |
| दर आठवड्याला npm downloads | 5 कोटी 30 लाख | 3 कोटी 60 लाख |
| सर्वोत्तम साठी | नवीन projects, आधुनिक stacks | Legacy apps, enterprise, custom loaders |

स्रोत: [2][5]

Shopify ने अनेक internal tools Webpack वरून Vite वर migrate केले आणि ~12 सेकंद startup वरून 800 मिलीसेकंदांपेक्षा कमी वेळात आले [2]. हे optimization नाही. ही वेगळी architecture आहे.

## Vite 8 आणि Rolldown — पुढील पाऊल

Vite ला नेहमीच विभाजित व्यक्तिमत्त्व होते: development transforms साठी **esbuild**, production builds साठी **Rollup**. ते वेगवेगळ्या वर्तनासह वेगवेगळी tools आहेत. यामुळे कधीकधी सूक्ष्म bugs येत होते — dev मध्ये काम करणाऱ्या गोष्टी production मध्ये बिघडत होत्या, किंवा उलटे.

हे आता **Rolldown** सह संबोधले जात आहे — VoidZero (Evan You ची कंपनी) ने विकसित केलेला Rust-based bundler जो दोन्हींची जागा घेण्यासाठी तयार केला आहे [6]. 2026 मध्ये प्रकाशित झालेला Vite 8, Rolldown ला default production bundler म्हणून आणतो, dev आणि prod दोन्ही builds ला एकच underlying engine देतो [7].

सुरुवातीचे production build निकाल:
- Excalidraw: 22.9 सेकंद → **1.4 सेकंद** (16× जलद) [8]
- GitLab: 2.5 मिनिटे → **40 सेकंद** [8]
- सामान्य benchmark दावे: मागील Rollup pipeline च्या तुलनेत **10–30× जलद production builds** [7]

dev/prod parity समस्या देखील नाहीशी होते. हे वर्षानुवर्षे bugs चे एक कमी लेखलेले स्रोत होते.

## Vite शेवटी Webpack सारखे होईल का?

हे सर्वजण विचार करत आहेत पण थेट बोलत नाहीत. Webpack सुरुवातीला तसे राक्षसी नव्हते. ते वाढले. Teams नी loaders जोडले, custom plugins लिहिले, environment-specific overrides चे थर लावले, आणि legacy workarounds सोडले जे कोणी काढायचे धाडस करत नव्हते. वीस config files आणि एक senior engineer जो "build setup जाणतो" — हे प्रत्येक मध्यम आकाराच्या कंपनीने अनुभवले आहे.

Vite त्याच मार्गाने जाऊ शकते का? प्रामाणिकपणे, काही प्रमाणात — होय. मोठ्या teams मोठ्या configs बनवतील. SSR setups मध्ये आधीच edge cases आहेत. Enterprise projects Vite 6+ मधील नवीन Environment API ला अशा प्रकारे push करतील ज्यासाठी खोल Vite ज्ञान आवश्यक आहे [5].

पण एक structural कारण आहे की ते बहुधा तितके वाईट होणार नाही. **Webpack ची गुंतागुंत मुख्यतः अनावधानाने आली होती** — जुन्या browsers साठी compatibility layers, CommonJS-to-ESM conversions, हजारो plugins edge cases patch करत होते जे native tooling ने आता सोडवले आहेत. Vite फक्त आधुनिक environments आवश्यक करून यातील बहुतेकांना टाळते. हे "या विचित्र legacy गोष्टीसाठी मला custom loader हवा आहे" या संपूर्ण category ला तोडते.

Vite चे plugin system हे Rollup च्या API चा एक जाणूनबुजून superset आहे [1]. नवीन config format तयार करण्याऐवजी, ते एक चांगल्या प्रकारे समजलेले interface पुन्हा वापरते. हे एक चांगले चिन्ह आहे — याचा अर्थ ecosystem ज्ञान transfer होते, वेगळ्याने जमत नाही.

Vite जी गुंतागुंत जमवेल ती बहुतेक **हेतुपूर्ण** असेल — advanced users custom SSR pipelines, multi-environment setups, किंवा framework-level tooling बनवत आहेत. हा वेगळ्या प्रकारचा गोंधळ आहे. तुम्ही सहसा तुम्ही न लिहिलेली Vite config समजू शकता. बहुतेक inherited Webpack configs बद्दल तेच म्हणता येत नाही जे मी पाहिले आहेत.

पाच वर्षांनी Vite आज Webpack दिसते तितके भीतीदायक दिसेल का — मला शंका आहे. पण "Webpack इतके वाईट नाही" यातही खूप जागा उरते.

> समाप्त

## स्रोत
1. [Vite का — Vite अधिकृत दस्तऐवज](https://vite.dev/guide/why)
2. [2025 मध्ये React Apps साठी Vite विरुद्ध Webpack: एका Senior Engineer चा दृष्टिकोन — LogRocket](https://blog.logrocket.com/vite-vs-webpack-react-apps-2025-senior-engineer/)
3. [Vite चे मूळ जादू: esbuild आणि Native ESM Frontend Development कसे पुन्हा परिभाषित करतात — Leapcell](https://leapcell.io/blog/vite-s-core-magic-how-esbuild-and-native-esm-reinvent-frontend-development)
4. [Vite विरुद्ध Webpack: थेट तुलना — Kinsta](https://kinsta.com/blog/vite-vs-webpack/)
5. [Webpack विरुद्ध Vite: आधुनिक Frontend Development साठी योग्य Bundler निवडणे — Syncfusion](https://www.syncfusion.com/blogs/post/webpack-vs-vite-bundler-comparison)
6. [Rolldown-Vite ची घोषणा — VoidZero](https://voidzero.dev/posts/announcing-rolldown-vite)
7. [Vite आवृत्ती 8: एकीकृत Rust-Based Bundler आणि 30 पट जलद Builds — InfoQ](https://www.infoq.com/news/2026/05/vite-v8-rust/)
8. [Rolldown-Vite Beta: Rust-Powered Bundler 16 पट पर्यंत Build वेळ कमी करतो — Progosling](https://progosling.com/en/dev-digest/rolldown-vite-beta)