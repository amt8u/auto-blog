+++
title       = "Vite सोबत Module Federation: काय काम करते, काय नाही"
description = "Vite मध्ये Module Federation चे व्यावहारिक विश्लेषण — @module-federation/vite आणि vite-plugin-federation प्रत्यक्षात काय करू शकतात, आणि ते अजूनही कुठे कमी पडतात."
date        = "2026-06-15T22:53:17+05:30"
slug          = "module-federation-vite-guide"
tags          = ["Vite", "Module Federation", "Micro Frontends", "JavaScript"]
keywords      = ["module federation vite", "vite micro frontends", "@module-federation/vite", "vite-plugin-federation", "micro frontend architecture", "vite-plugin-federation limitations"]
canonical     = "/mr/posts/module-federation-vite-guide/"
feature_image = "/images/POST-1062-module-federation-vite-guide.svg"
+++

Module Federation हा एक असा विषय आहे जो कोणत्याही बैठकीत "micro frontends" चा उल्लेख होताच सगळे बोलू लागतात. छान, runtime वर कोड शेअर करा, टीम्स स्वतंत्रपणे deploy करा, हे ऐकायला खूप चांगले वाटते. पण मग टीममधला कोणीतरी म्हणतो "आपण Vite वापरतो, webpack नाही" आणि संपूर्ण संभाषण अवघड होऊन जाते. मग खरोखर काय होते जेव्हा तुम्ही Vite प्रोजेक्टमध्ये Module Federation आणण्याचा प्रयत्न करता? काही भाग खूप चांगला काम करतो. काही भाग... खरोखरच करत नाही, निदान अजून तरी नाही.

## बरं, Module Federation म्हणजे नक्की काय?

थोडी पुनरावृत्ती कारण Vite ची कहाणी समजून घेण्यासाठी हे महत्त्वाचे आहे. **Module Federation एका JavaScript ऍप्लिकेशनला दुसऱ्या ऍप्लिकेशनमधून runtime वर कोड लोड करण्याची परवानगी देते**, build वेळी नव्हे. एक ऍप (the "remote") काही modules उघड करतो — एक component, एक utility, एक संपूर्ण page — आणि त्यांना एका लहान entry file मध्ये bundle करतो, सामान्यतः `remoteEntry.js` म्हणतात. दुसरा ऍप (the "host") ती entry file dynamically import करतो आणि उघड केलेल्या कोडचा वापर सामान्य import प्रमाणे करतो.

हे मूळतः **webpack 5** चे एक वैशिष्ट्य होते, webpack च्या chunk-loading runtime मध्ये खोलवर रुजलेले. Webpack याला प्रथम-श्रेणीची संकल्पना म्हणून वागवते — त्याचा संपूर्ण module graph, code-splitting, आणि async chunk loader हे सर्व याच गोष्टी लक्षात ठेवून डिझाइन केले गेले.

Vite, दुसरीकडे, कधीही या कल्पनेभोवती तयार केले गेले नाही. Vite चा dev server native ES modules थेट browser ला serve करतो, आणि त्याचे production builds Rollup मधून जातात. त्यापैकी कोणत्याहीला "runtime वर एक remote module graph लोड करा आणि माझ्याशी merge करा" अशी कोणतीही संकल्पना नाही. त्यामुळे **Vite मध्ये Module Federation built in नाही — पूर्णविराम**. येथे तुम्ही जे काही करता ते community (किंवा community-turned-official) plugins द्वारे जोडले जाते.

## Vite मध्ये हे built in नाही — कोण ही जागा भरतो ते पाहूया

येथे दोन मुख्य पर्याय आहेत, आणि खरे सांगायचे तर त्यापैकी एक निवडणे हा पहिला खरा निर्णय असेल जो तुम्ही घ्याल.

जुना आणि अधिक परीक्षित पर्याय म्हणजे [`@originjs/vite-plugin-federation`](https://github.com/originjs/vite-plugin-federation) [1]. तो एका virtual module (`virtual:__federation__`) भोवती बांधलेला स्वतःचा runtime घेऊन येतो, आणि तो स्पष्टपणे webpack च्या Module Federation मधून येणाऱ्या लोकांना परिचित वाटण्यासाठी डिझाइन केला गेला होता — `exposes`, `remotes`, आणि `shared` चे तेच mental model.

नवीन पर्याय म्हणजे [`@module-federation/vite`](https://www.npmjs.com/package/@module-federation/vite) [2], जो Module Federation 2.0 च्या मागे असलेल्या त्याच टीमद्वारे maintain केला जातो. स्वतःचा runtime शोधण्याऐवजी, ते Vite ला थेट `@module-federation/runtime` शी जोडते, तोच runtime जो webpack आणि Rspack implementations ला शक्ती देतो. हे महत्त्वाचे आहे कारण Module Federation 2.0 विशेषतः runtime ला कोणत्याही विशिष्ट bundler पासून वेगळे करण्यासाठी पुनर्बांधणी केली गेली — Rspack सोबत built remote आणि Vite सोबत built host एकाच protocol वापरून एकमेकांशी बोलू शकतील हे ध्येय आहे [3].

आता आणखी एक तिसरे नाव फिरत आहे: एक standalone `vite-plugin-federation` package जे स्वतःला "production era" पर्याय म्हणून 1.0 release सह ठेवत आहे, manifest-first approach (`mf-manifest.json`, `mf-stats.json`, `mf-debug.json`) आणि circuit breakers आणि SRI verification सारख्या built-in governance वैशिष्ट्यांसह [4]. हे अस्तित्वात आहे हे जाणून घेणे योग्य आहे, परंतु मी इतक्या नवीन कोणत्याही गोष्टीला "चला पाहूया ते प्रत्यक्षात कसे टिकते" अशा निरोगी दृष्टिकोनाने वागवतो.

निवड कशी करायची ते असे मांडतो:

| | `@originjs/vite-plugin-federation` | `@module-federation/vite` |
|---|---|---|
| Runtime | स्वतःचा, webpack-MF-inspired | `@module-federation/runtime` (webpack/Rspack सोबत shared) |
| परिपक्वता | जुना, व्यापकपणे वापरलेला, GitHub issues आधीच triaged | नवीन, कमी battle scars, सक्रियपणे विकसित |
| Cross-bundler interop | प्रामुख्याने Vite-to-Vite | Rspack/webpack remotes सोबत interoperate करण्यासाठी डिझाइन केलेले [3] |
| TypeScript type sharing | मर्यादित | MF 2.0 वैशिष्ट्यांभोवती बांधलेले जसे dynamic type hints [3] |
| सर्वोत्तम वापर | विद्यमान OriginJS-style setups, साधे host/remote pairs | नवीन प्रोजेक्ट, विशेषतः जे आधीच Module Federation ecosystem ला स्पर्श करत आहेत |

जर तुम्ही आज नव्याने सुरुवात करत आहात आणि भविष्यात bundlers मिक्स करण्याची कोणतीही शक्यता आहे, तर `@module-federation/vite` कडे झुका. जर तुम्हाला फक्त सर्वात सोपे "host एका remote मधून button import करतो" setup हवे आहे आणि मोठ्या ecosystem ची काळजी नाही, तर `@originjs/vite-plugin-federation` अजूनही ठीक काम करतो आणि त्याबद्दल Stack Overflow वर अधिक उत्तरे आहेत.

## एक basic host + remote सेट करणे (जो भाग खरोखर काम करतो)

हा तो भाग आहे जो खरोखरच काम करतो, आणि प्रामाणिकपणे सांगायचे तर पहिल्यांदा बघताना ते जादुई वाटते. एक component उघड करणारे minimal remote app असे दिसते:

```ts
// remote/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'remote_app',
      filename: 'remoteEntry.js',
      exposes: {
        './Button': './src/components/Button.tsx',
      },
      shared: ['react', 'react-dom'],
    }),
  ],
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: false,
  },
})
```

आणि ते consume करणारा host:

```ts
// host/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'host_app',
      remotes: {
        remote_app: 'http://localhost:5001/assets/remoteEntry.js',
      },
      shared: ['react', 'react-dom'],
    }),
  ],
  build: { target: 'esnext' },
})
```

मग host मध्ये, तुम्ही ते कोणत्याही lazy component प्रमाणे consume करता:

```tsx
const RemoteButton = React.lazy(() =>
  import('remote_app/Button')
)
```

तुम्ही **आधी remote build करता** (`vite build`), `dist` folder कुठेतरी serve करता, आणि मग host चालवता. हीच संपूर्ण जादू आहे — host network वर `remoteEntry.js` fetch करतो, काय उघड केले आहे ते शोधतो, आणि मागणीनुसार कोड आत खेचतो. कोणताही iframe नाही, कोणताही वेगळा React root विचित्रपणे mount केलेला नाही — ते फक्त... तिथे आहे, एक component म्हणून.

![module federation vite architecture](/images/posts/module-federation-vite-guide/module-federation-vite-architecture.svg)

## Vite मध्ये Module Federation सोबत तुम्ही काय करू शकता

एकदा ते जोडले गेले की, webpack युगातील खूप मोठ्या प्रमाणात वचन खरे ठरते. प्रत्यक्षात काय काम करते ते येथे आहे:

- **runtime वर components, hooks, आणि utilities उघड करा आणि consume करा** स्वतंत्रपणे built आणि deployed ऍप्समध्ये — मुख्य use case, आणि ते काम करते.
- **Singleton dependencies शेअर करा** जसे React, Vue, किंवा design-system package जेणेकरून host आणि remotes प्रत्येकी स्वतःची copy पाठवणार नाहीत [7]. `singleton: true` सह `shared` config एका shared instance ला resolve करते.
- **फक्त आवश्यक तेव्हाच remotes lazy-load करा**, जे admin panel किंवा checkout flow सारख्या गोष्टींसाठी उत्तम आहे जे बहुतेक users कधीही वापरत नाहीत.
- **Frameworks मिक्स करा** — Vue host तांत्रिकदृष्ट्या एक React remote लोड करू शकतो (किंवा उलट) wrapper component मध्ये mount करून, कारण federation फक्त एक module देते, framework contract नाही.
- **Manifests generate करा** (`mf-manifest.json` आणि तत्सम) जे प्रत्येक remote काय उघड करते ते वर्णन करतात, जे CI pipelines साठी खरोखर उपयुक्त आहे ज्यांना deploy करण्यापूर्वी compatibility तपासायची आहे [4].
- **Remotes मध्ये TypeScript type hints वापरा**, Module Federation 2.0 चे एक वैशिष्ट्य जे remote modules साठी `.d.ts` files generate आणि download करते जेणेकरून तुमचा editor फक्त `any` चा अंदाज करत नाही [3].
- **Runtime plugins** — loading lifecycle मधील hooks (request आधी, resolve नंतर, error वर) जे तुम्हाला application कोड न बदलता logging, retries, किंवा fallback URLs जोडण्याची परवानगी देतात [3].
- **स्वतंत्र deploys** — एकदा दोन्ही ऍप्स federation contract वर सहमत झाले की, तुम्ही खरोखरच host पुन्हा deploy न करता remote ship करू शकता, जे या प्रयोगाचा संपूर्ण मुद्दा आहे.

शेवटचे ते खरे फळ आहे. जर तुमच्या संस्थेत एकाच monorepo मध्ये अनेक टीम्स एकमेकांवर पाय ठेवत आहेत, तर मंगळवारी "checkout" आणि गुरुवारी "profile" release coordinate न करता deploy करण्यास सक्षम असणे हा एक खरा विजय आहे — जेव्हा ते काम करते.

## ते कुठे तुटते: dev mode हा खोलीतील हत्ती आहे

इथेच ते अवघड होते, आणि प्रामाणिकपणे सांगायचे तर, हीच गोष्ट पहिल्यांदा जवळजवळ प्रत्येकाला अडखळवते.

**फक्त host बाजूला योग्य Vite dev server अनुभव मिळतो.** Remote आधी build करावे लागते — त्याचे `remoteEntry.js` आणि उघड केलेले chunks host import करण्यापूर्वी static files म्हणून अस्तित्वात असणे आवश्यक आहे [5]. "दोन्ही ऍप्स full HMR सह `vite dev` चालवत आहेत आणि एकमेकांशी live बोलत आहेत" असे कोणतेही समतुल्य नाही.

दैनंदिन जीवनात याचा अर्थ:

1. तुम्ही remote च्या उघड केलेल्या component मध्ये काहीतरी बदल करता.
2. Vite चा dev server (फक्त remote साठी, तुमच्या सोयीसाठी चालत आहे) host ला अजिबात मदत करत नाही.
3. तुम्हाला remote वर `vite build` पुन्हा चालवावे लागते.
4. Host ला मग नवीन `remoteEntry.js` घेण्यासाठी hard refresh आवश्यक आहे.

हे "fast feedback loop" नाही, हे "shared code ला स्पर्श केल्यावर प्रत्येक वेळी context switch" आहे. काही टीम्स एका terminal मध्ये remote चे `vite build --watch` चालवून आणि refresh सोबत जगून याचा उपाय करतात — ते elegant नाही, परंतु host टीमसाठी काम करते. Remote टीमसाठी जी सक्रियपणे स्वतःची UI develop करत आहे, ते सामान्यतः फक्त त्यांचा ऍप standalone (federation शिवाय) सामान्य Vite dev वापरून चालवतात, आणि फक्त अधूनमधून federated integration तपासतात.

![module federation vite dev vs build](/images/posts/module-federation-vite-guide/module-federation-vite-dev-vs-build.svg)

आणखी काही गोष्टी ज्या काम करत नाहीत, किंवा फक्त अर्ध्याने काम करतात:

- **`build.rollupOptions.output.manualChunks` प्रभावीपणे off-limits आहे.** Federation plugin स्वतः chunk graph manage करतो, आणि custom chunk grouping federation runtime ज्यावर अवलंबून असतो तो bootstrap order तोडू शकतो [2].
- **Vite/Rollup remotes ला webpack hosts सोबत (किंवा उलट) मिक्स करणे fragile आहे.** Rollup आणि webpack CommonJS dependencies साठी समान chunk आकार produce करतील याची कोणतीही हमी नाही, जे शांतपणे `shared` resolution तोडू शकते [1].
- **`baseUrl` / custom base paths मध्ये खरे bugs आले आहेत.** जर तुमचा remote subpath वरून serve केला जात असेल (reverse proxy मागे enterprise setups मध्ये सामान्य), Vite 5+ खाली federation plugin `remoteEntry.js` योग्यरित्या resolve करत नाही असे issues आले आहेत [6].
- **Non-ESM output formats दुय्यम दर्जाचे आहेत.** Plugin docs स्पष्टपणे सांगतात की ESM हा चांगला परीक्षित मार्ग आहे; UMD/CJS-style remotes मध्ये "पूर्ण test cases नाहीत" [1].

## CSS गोंधळ जो कोणी सांगत नाही

हे पहिल्यांदा मला जड वाटले, आणि हे मूलतः प्रत्येकाला शेवटी चावते. Dev mode मध्ये, तुमच्या remote च्या styles ठीक लोड होतात कारण Vite त्यांना त्याच्या dev server द्वारे inject करतो. Production मध्ये, Vite default रूपाने CSS code-splitting करतो — प्रत्येक chunk ला स्वतःची CSS file मिळते, एका `<link>` tag द्वारे लोड केली जाते ज्याबद्दल *page* ला माहित असणे आवश्यक आहे.

समस्या? जेव्हा host dynamically एका remote च्या component import करतो, तेव्हा host च्या HTML ला remote च्या CSS file लोड करण्यास सांगण्यासाठी काहीही नाही. त्यामुळे तुम्हाला एक परिपूर्ण functional, पूर्णपणे unstyled component मिळतो. एका developer ने हे अगदी योग्य वर्णन केले: ते locally ठीक काम करूनही production मध्ये "unstyled wireframe सारखे दिसत होते" [10].

लोक ज्या fixes वर पोहोचतात:

- Remote वर `build.cssCodeSplit: false` सेट करा जेणेकरून त्याची सर्व CSS एकाच file मध्ये bundle होईल जिला तुम्ही विश्वासाने reference करू शकता.
- CSS थेट JS bundle मध्ये inline करण्यासाठी `vite-plugin-css-injected-by-js` सारखे plugin वापरा — कुरूप, परंतु हे हमी देते की styles component सोबत प्रवास करतात [10].
- काही टीम्स पुढे जाऊन CSS Modules किंवा `:host`/Shadow DOM-style scoping वापरतात जेणेकरून remote च्या styles चुकून host च्या global styles मध्ये leak होणार नाहीत (किंवा त्यांच्याकडून overwrite होणार नाहीत) — एक वेगळी परंतु संबंधित डोकेदुखी, कारण Vite च्या स्वतःच्या CSS Modules `composes` handling मध्ये स्वतःचे duplication quirks आहेत.

यापैकी काहीही exotic नाही, परंतु हे नेमके असे प्रकार आहेत जे तुमच्या machine वर परिपूर्ण काम करतात आणि QA deployed build उघडताच कोसळतात.

## Shared dependencies आणि singleton trap

`shared` config हे ते ठिकाण आहे जिथे Module Federation स्वतःचे महत्त्व सिद्ध करते — किंवा जिथे ते शांतपणे तुमचा दिवस बरबाद करते. कल्पना सोपी आहे: प्रत्येक remote स्वतःची React ची copy पाठवण्याऐवजी, तुम्ही ते `shared` म्हणून चिन्हांकित करता, आणि आदर्शतः `singleton: true`, जेणेकरून संपूर्ण federated ऍपसाठी एकच React instance असेल [7].

व्यवहारात, **version mismatches हे federated setups मधील एकमेव सर्वात सामान्य production bug आहेत** [8]. जर host React 18.2 अपेक्षित आहे आणि एक remote React 18.3 च्या विरूद्ध built केले गेले, तर तुम्हाला दोन React instances मिळू शकतात — आणि React च्या hooks नियम हे कधीही माफ करत नाहीत. क्लासिक लक्षण म्हणजे "Invalid hook call" errors जे कोणताच अर्थ काढत नाहीत जोपर्यंत तुम्हाला memory मध्ये दोन Reacts आहेत हे समजत नाही.

येथे काही गोष्टी जाणून घेण्यासारख्या आहेत:

- `singleton: true` runtime ला एक version निवडण्यास आणि प्रत्येकाला ते वापरण्यास भाग पाडण्यास सांगते — जरी ते तांत्रिकदृष्ट्या प्रत्येकाच्या `requiredVersion` शी सुसंगत नसले तरी [7]. हे "best effort, crash नको" setting आहे, correctness ची हमी नाही.
- `strictVersion: true` हे उलट करते — शांतपणे version निवडण्याऐवजी, जर incompatibility असेल तर ते throws करते. Production मध्ये शोधण्यापेक्षा CI मध्ये समस्या पकडण्यासाठी चांगले.
- Build metadata किंवा pre-release suffixes (जसे `18.2.0-release.99`) सह version strings semver ranges च्या विरूद्ध योग्यरित्या resolve न होण्याबद्दल खरे bugs आले आहेत, जे शांतपणे संपूर्ण shared-singleton यंत्रणा हरवू शकतात [9].
- अनेक remotes shared lib च्या थोड्या वेगळ्या versions खेचताना उलट समस्या देखील निर्माण झाली आहे — विशेषतः अधिक complex routing setups मध्ये `react-router-dom` सह dependencies deduplicated होण्याऐवजी अनेक वेळा fetch आणि bundle होत आहेत [15].

माझे प्रामाणिक मत: **`shared` config आवश्यक आहे परंतु पुरेसे नाही.** तुम्हाला अजूनही टीम्समध्ये खरी dependency-version शिस्त आवश्यक आहे — आदर्शतः एक shared `package.json` किंवा किमान एक documented "हे pinned versions आहेत ज्यावर प्रत्येकजण लक्ष्य ठेवतो" doc. Module Federation duplication कमी करते; ते alignment enforce करत नाही.

## तुम्ही याची तसदी घ्यावी का? जाणून घेण्यासारखे पर्याय

हा तो प्रश्न आहे जो मी federation config ची एकही ओळ लिहिण्यापूर्वी विचारेन: **तुम्हाला खरोखर हे हवे आहे का, किंवा तुम्हाला स्वतंत्र deploys हवे आहेत आणि एक सोपे tool काम करेल?**

2026 च्या संभाषणांमध्ये खूप येणारे काही पर्याय:

- **Import Maps.** एक खरा web standard (Chrome 2021 पासून) जो browser ला JSON map द्वारे module specifiers ला versioned URLs ला resolve करण्यास देतो — कोणताही bundler-specific runtime आवश्यक नाही [11]. जर तुमचे "micro frontends" खरोखरच काही स्वतंत्रपणे versioned ES modules आहेत, तर import maps तुम्हाला खूप कमी tooling सह तेथे बहुतेक मार्गाने पोहोचवू शकतात.
- **Native Federation.** Angular Architects टीमने विशेषतः Vite/esbuild-style toolchains साठी built, ते Module Federation संकल्पना custom runtime ऐवजी import maps आणि native ESM वापरून implement करते [12]. Framework-agnostic, आणि webpack-derived approach पेक्षा लक्षणीयरित्या lighter weight.
- **Rspack द्वारे Module Federation 2.0.** जर तुमची टीम bundlers बदलण्यास (फक्त plugin जोडण्यापलीकडे) तयार आहे, Rspack चा native Module Federation support सध्या Vite ecosystem मधील कोणत्याहीपेक्षा अधिक परिपक्व आहे, आणि तो `@module-federation/vite` वापरत असलेल्या MF 2.0 protocol बोलतो — म्हणजे specific remotes साठी gradual Vite-to-Rspack migration व्यावहारिक आहे [13][3].
- **Shared packages सह monorepo आणि runtime federation अजिबात नाही.** काही वेळा वास्तविक आवश्यकता "हा Button component duplicate करणे बंद करा" अशी असते, आणि एक published internal npm package runtime complexity शिवाय ते सोडवते. कंटाळवाणे, परंतु कंटाळवाणे हे एक वैशिष्ट्य आहे.

जर तुमचे मुख्य ध्येय "independently deployable" आहे "आमच्या जुन्या webpack setup प्रमाणेच काम करणे आवश्यक आहे" ऐवजी, तर मी खरोखर आधी import maps किंवा Native Federation विचार करेन. Vite federation plugins बऱ्याच प्रकरणांमध्ये आवश्यकतेपेक्षा कठीण समस्या सोडवत आहेत, पूर्णपणे कारण टीम्सना webpack सोबत API parity हवी आहे.

## यावर commit करण्यापूर्वी माझी प्रामाणिक checklist

जर तुम्ही हे सुरू करणार असाल, तर पहिली `federation()` config लिहिण्यापूर्वी मी या गोष्टी निश्चित करेन:

| प्रश्न | हे का महत्त्वाचे आहे |
|---|---|
| Remotes ला host च्या release cycle पासून स्वतंत्रपणे deploy करणे आवश्यक आहे का? | नसेल तर, तुम्हाला federation अजिबात नको असेल — monorepo package सोपे असू शकते |
| तुमची टीम विकासादरम्यान "rebuild remote, refresh host" सहन करू शकते का? | सध्या दोन्ही major plugins सोबत dev-mode वास्तविकता हीच आहे [5] |
| तुम्ही `target: 'esnext'` वर आहात आणि `manualChunks` टाळत आहात का? | दोन्ही plugins हे require/expect करतात; याच्याशी लढल्यास obscure build failures होतात [2] |
| टीम्समध्ये shared dependency versions साठी तुमच्याकडे plan आहे का? | `singleton: true` मदत करते परंतु version शिस्त replace करत नाही [8][9] |
| Remotes non-root base सह subpath/CDN वरून serve केले जातील का? | `remoteEntry.js` resolution bugs चे ज्ञात कारण [6] |
| CSS साठी तुम्ही फक्त dev नाही तर production builds तपासल्या आहेत का? | Dev मध्ये काम करणाऱ्या styles अनेक लोकांसाठी prod मध्ये शांतपणे नाहीशा होतात [10] |
| Native Federation किंवा import maps तुमची वास्तविक आवश्यकता पूर्ण करू शकतात का? | कधीकधी सोपे standard 20% complexity साठी 80% काम करते [11][12] |

गोष्टी कुठे आहेत याचा प्रामाणिक सारांश: Module Federation Vite सोबत **काम करते**, आणि मुख्य "runtime वर remote component लोड करा, singleton dependency शेअर करा" use case साठी, ते चांगले काम करते. जड कडा तेव्हा दिसतात जेव्हा तुम्ही production कडे ढकलता — CSS, dev-mode parity, version drift, आणि non-root deployments. यापैकी कोणतेही dealbreakers नाहीत, परंतु जर तुम्हाला माहित नसेल की ते येत आहेत तर यापैकी प्रत्येकजण एक debugging session खाईल. Module Federation 2.0 चे bundler-agnostic runtime कडे ढकलणे [3] हे सर्वात आशादायक चिन्ह आहे की Vite ची कहाणी सुधारत राहील — परंतु "सुधारणे" आणि "सोडवले" अजूनही दोन वेगळे शब्द आहेत.

## Sources
1. [originjs/vite-plugin-federation on GitHub](https://github.com/originjs/vite-plugin-federation)
2. [@module-federation/vite on npm](https://www.npmjs.com/package/@module-federation/vite)
3. [Module Federation 2.0 Reaches Stable Release with Wider Support outside of Webpack - InfoQ](https://www.infoq.com/news/2026/04/module-federation-2-stable/)
4. [vite-plugin-federation 1.0: Bringing Module Federation Into the Production Era for Vite - DEV Community](https://dev.to/unadlib/vite-plugin-federation-10-bringing-module-federation-into-the-production-era-for-vite-2bff)
5. [Support dev server remote entry file · Issue #525 · originjs/vite-plugin-federation](https://github.com/originjs/vite-plugin-federation/issues/525)
6. [Module Federation + base url · Issue #580 · originjs/vite-plugin-federation](https://github.com/originjs/vite-plugin-federation/issues/580)
7. [Shared configuration - Module Federation docs](https://module-federation.io/configure/shared)
8. [Getting Out of Version-Mismatch-Hell with Module Federation - ANGULARarchitects](https://www.angulararchitects.io/en/blog/getting-out-of-version-mismatch-hell-with-module-federation/)
9. [Module Federation Fails to Share Singleton Dependencies with Version Postfixes · Issue #4078 · module-federation/core](https://github.com/module-federation/core/issues/4078)
10. [How I Finally Got My Vite + Module Federation Styles to Load in Production](https://medium.com/@krishan101090/how-i-finally-got-my-vite-module-federation-styles-to-load-in-production-and-how-you-can-too-23ab3aab3f27)
11. [You Might Not Need Module Federation: Orchestrate your Microfrontends at Runtime with Import Maps - Mercedes-Benz.io](https://www.mercedes-benz.io/2023/01/05/you-might-not-need-module-federation-orchestrate-your-microfrontends-at-runtime-with-import-maps/)
12. [Announcing Native Federation 1.0 - ANGULARarchitects](https://www.angulararchitects.io/en/blog/announcing-native-federation-1-0/)
13. [Module Federation 2.0: webpack vs Rspack vs Vite 2026 - PkgPulse Guides](https://www.pkgpulse.com/guides/module-federation-2-webpack-rspack-vite-micro-frontends-2026)
14. [module-federation/vite on GitHub](https://github.com/module-federation/vite)
15. [Bug Report: Multiple Instances of React and React-Router-DOM in Host and Remote · Issue #650 · originjs/vite-plugin-federation](https://github.com/originjs/vite-plugin-federation/issues/650)