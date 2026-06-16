+++
title       = "Vite के साथ Module Federation: क्या काम करता है, क्या नहीं"
description = "Vite में Module Federation का एक व्यावहारिक विश्लेषण — @module-federation/vite और vite-plugin-federation वास्तव में क्या कर सकते हैं, और वे अभी भी कहाँ पिछड़ते हैं।"
date        = "2026-06-15T22:53:17+05:30"
slug          = "module-federation-vite-guide"
tags          = ["Vite", "Module Federation", "माइक्रो फ्रंटएंड्स", "JavaScript"]
keywords      = ["module federation vite", "vite माइक्रो फ्रंटएंड्स", "@module-federation/vite", "vite-plugin-federation", "माइक्रो फ्रंटएंड आर्किटेक्चर", "vite-plugin-federation की सीमाएँ"]
canonical     = "/hi/posts/module-federation-vite-guide/"
feature_image = "/images/POST-1062-module-federation-vite-guide.svg"
+++

Module Federation एक ऐसी अवधारणा है जिसे हर कोई तब उठाता है जब किसी मीटिंग में "micro frontends" का जिक्र होता है। बढ़िया लगता है — runtime पर code share करो, टीमों को independently deploy करो। फिर टीम का कोई कहता है "हम webpack पर नहीं, Vite पर हैं" और पूरी बातचीत अजीब हो जाती है। तो जब आप Module Federation को Vite project में लाने की कोशिश करते हैं तो वास्तव में क्या होता है? कुछ हिस्से बेहतरीन तरीके से काम करते हैं। कुछ... वास्तव में नहीं करते, कम से कम अभी तक तो नहीं।

## ठीक है, तो Module Federation क्या है फिर से?

जल्दी से याद दिला देते हैं क्योंकि यह Vite की कहानी समझने के लिए जरूरी है। **Module Federation एक JavaScript application को दूसरे application से runtime पर code load करने देता है**, build time पर नहीं। एक app ("remote") कुछ modules expose करती है — एक component, एक utility, एक पूरा page — और उन्हें एक छोटी entry file में bundle करती है, जिसे आमतौर पर `remoteEntry.js` कहते हैं। दूसरी app ("host") उस entry file को dynamically import करती है और exposed code को normal import की तरह उपयोग करती है।

यह मूल रूप से एक **webpack 5** feature था, webpack के chunk-loading runtime में गहराई से बना हुआ। Webpack इसे first-class concept मानता है — इसका पूरा module graph, code-splitting, और async chunk loader इसी को ध्यान में रखकर बनाया गया था।

Vite, दूसरी ओर, इस idea के आधार पर कभी नहीं बना था। Vite का dev server browser को native ES modules directly serve करता है, और इसके production builds Rollup से होकर जाते हैं। इनमें से किसी में भी "runtime पर एक remote module graph load करो और उसे अपने साथ merge करो" का कोई concept नहीं है। इसलिए **Vite में Module Federation built-in नहीं है — एकदम सीधी बात**। यहाँ आप जो भी करते हैं वह community (या community-turned-official) plugins द्वारा जोड़ा गया है।

## Vite में यह built-in नहीं है — कौन इस कमी को पूरा करता है

दो main players हैं, और honestly, इनके बीच चुनाव ही आपका पहला असली निर्णय है।

पुराना और अधिक battle-tested वाला है [`@originjs/vite-plugin-federation`](https://github.com/originjs/vite-plugin-federation) [1]। यह एक virtual module (`virtual:__federation__`) के आसपास बना अपना runtime ship करता है, और इसे explicitly webpack के Module Federation से आने वाले लोगों को familiar feel कराने के लिए design किया गया था — `exposes`, `remotes`, और `shared` का वही mental model।

नया वाला है [`@module-federation/vite`](https://www.npmjs.com/package/@module-federation/vite) [2], जिसे Module Federation 2.0 के पीछे की वही टीम maintain करती है। खुद का runtime बनाने की बजाय, यह Vite को directly `@module-federation/runtime` से जोड़ता है, वही runtime जो webpack और Rspack implementations को power करता है। यह इसलिए मायने रखता है क्योंकि Module Federation 2.0 को specifically किसी भी particular bundler से runtime को decouple करने के लिए rebuild किया गया था — लक्ष्य यह था कि Rspack से बना एक remote और Vite से बना एक host एक ही protocol का उपयोग करके एक दूसरे से बात कर सकें [3]।

अब एक तीसरा नाम भी floating around है: एक standalone `vite-plugin-federation` package जो 1.0 release के साथ खुद को "production era" option के रूप में position कर रहा है, manifest-first approach (`mf-manifest.json`, `mf-stats.json`, `mf-debug.json`) और built-in governance features जैसे circuit breakers और SRI verification के साथ [4]। यह जानना worth है कि यह exist करता है, लेकिन इस नई चीज के साथ "चलो देखते हैं यह wild में कैसे टिकता है" का healthy dose रखना उचित होगा।

यहाँ बताता हूँ मैं इस choice को कैसे frame करूँगा:

| | `@originjs/vite-plugin-federation` | `@module-federation/vite` |
|---|---|---|
| Runtime | अपना, webpack-MF-inspired | `@module-federation/runtime` (webpack/Rspack के साथ shared) |
| परिपक्वता | पुराना, widely used, GitHub issues already triaged | नया, कम battle scars, actively developed |
| Cross-bundler interop | ज्यादातर Vite-to-Vite | Rspack/webpack remotes के साथ interoperate करने के लिए designed [3] |
| TypeScript type sharing | Limited | MF 2.0 features जैसे dynamic type hints के आसपास built [3] |
| सबसे उपयुक्त | Existing OriginJS-style setups, simple host/remote pairs | नए projects, खासकर जो पहले से wider Module Federation ecosystem को touch कर रहे हों |

अगर आप आज fresh start कर रहे हैं और कोई भी chance है कि आप आगे bundlers mix करेंगे, तो `@module-federation/vite` की तरफ lean करें। अगर आप बस सबसे simple possible "host imports a button from a remote" setup चाहते हैं और बड़े ecosystem की परवाह नहीं है, तो `@originjs/vite-plugin-federation` अभी भी ठीक काम करता है और इसके बारे में अधिक Stack Overflow answers लिखे गए हैं।

## एक basic host + remote सेट करना (वो हिस्सा जो वास्तव में काम करता है)

यह वो हिस्सा है जो genuinely बस काम करता है, और honestly पहली बार देखने पर यह कुछ magical लगता है। यहाँ एक minimal remote app है जो एक component expose करती है:

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

और host जो इसे consume करता है:

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

फिर host में, आप इसे किसी भी lazy component की तरह consume करते हैं:

```tsx
const RemoteButton = React.lazy(() =>
  import('remote_app/Button')
)
```

आप **पहले remote build करते हैं** (`vite build`), `dist` folder को कहीं serve करते हैं, और फिर host run करते हैं। यही पूरा magic trick है — host network पर `remoteEntry.js` fetch करता है, पता लगाता है कि क्या exposed है, और code को on demand pull करता है। कोई iframe नहीं, कोई अलग React root अजीब तरीके से mount नहीं — यह बस... वहाँ है, एक component के रूप में।

![module federation vite architecture](/images/posts/module-federation-vite-guide/module-federation-vite-architecture.svg)

## Vite में Module Federation के साथ आप क्या कर सकते हैं

एक बार wired up हो जाने पर, webpack-era promise का आश्चर्यजनक रूप से बड़ा हिस्सा सच साबित होता है। यहाँ है जो व्यावहारिक रूप से काम करता है:

- **Separately built और deployed apps में runtime पर components, hooks, और utilities expose और consume करना** — core use case, और यह काम करता है।
- **React, Vue, या एक design-system package जैसी singleton dependencies share करना** ताकि host और remotes अपनी-अपनी copy ship न करें [7]। `singleton: true` के साथ `shared` config एक shared instance पर resolve होता है।
- **Remotes को तभी lazy-load करना जब जरूरत हो**, जो admin panel या checkout flow जैसी चीजों के लिए बढ़िया है जिन्हें ज्यादातर users कभी touch नहीं करते।
- **Frameworks mix करना** — एक Vue host technically एक React remote load कर सकता है (या vice versa) इसे एक wrapper component में mount करके, क्योंकि federation बस एक module देता है, framework contract नहीं।
- **Manifests generate करना** (`mf-manifest.json` और similar) जो describe करते हैं कि प्रत्येक remote क्या expose करता है, जो CI pipelines के लिए genuinely useful है जो deploy करने से पहले compatibility verify करना चाहती हैं [4]।
- **Remotes के लिए TypeScript type hints use करना**, एक Module Federation 2.0 feature जो remote modules के लिए `.d.ts` files generate और download करता है ताकि आपका editor बस `any` पर guess न करे [3]।
- **Runtime plugins** — loading lifecycle में hooks (before request, after resolve, on error) जो आपको application code touch किए बिना logging, retries, या fallback URLs add करने देते हैं [3]।
- **Independent deploys** — एक बार दोनों apps federation contract पर agree कर लें, आप सच में host को redeploy किए बिना remote ship कर सकते हैं, जो इस exercise का पूरा point है।

आखिरी वाला असली payoff है। अगर आपके org में multiple teams एक monorepo में एक-दूसरे के रास्ते में आ रही हैं, तो "checkout" मंगलवार को और "profile" गुरुवार को release coordinate किए बिना deploy करने में सक्षम होना एक real win है — जब यह काम करता है।

## यह कहाँ टूटता है: dev mode ही असली समस्या है

यहाँ यह tricky हो जाता है, और honestly, यही वो चीज है जो पहली बार में लगभग हर किसी को trip करती है।

**केवल host side को proper Vite dev server experience मिलती है।** Remote को पहले build किया जाना होता है — host उन्हें import करने से पहले उसके `remoteEntry.js` और exposed chunks को static files के रूप में exist करना होता है [5]। "दोनों apps full HMR के साथ `vite dev` run कर रहे हैं एक-दूसरे से live बात कर रहे हैं" का कोई equivalent नहीं है।

दिन-प्रतिदिन इसका क्या मतलब है:

1. आप remote के exposed component में कुछ बदलते हैं।
2. Vite का dev server (सिर्फ remote के लिए चल रहा है, अपनी सुविधा के लिए) host की कोई मदद नहीं करता।
3. आपको remote पर फिर से `vite build` run करना होगा।
4. Host को फिर new `remoteEntry.js` pick up करने के लिए hard refresh की जरूरत है।

यह "fast feedback loop" नहीं है, यह है "हर बार shared code touch करने पर context switch"। कुछ teams इसके आसपास remote का `vite build --watch` एक terminal में run करके काम करती हैं और बस refresh के साथ जीती हैं — यह elegant नहीं है, लेकिन host team के लिए workable है। Remote team जो actively अपना UI develop कर रही है, वे typically बस अपना app standalone (federation के बिना) normal Vite dev का उपयोग करके run करती हैं, और केवल कभी-कभी federated integration test करती हैं।

![module federation vite dev vs build](/images/posts/module-federation-vite-guide/module-federation-vite-dev-vs-build.svg)

कुछ और चीजें जो काम नहीं करतीं, या केवल आधी काम करती हैं:

- **`build.rollupOptions.output.manualChunks` effectively off-limits है।** Federation plugin खुद chunk graph manage करता है, और custom chunk grouping उस bootstrap order को break कर सकती है जिस पर federation runtime निर्भर करता है [2]।
- **Vite/Rollup remotes को webpack hosts के साथ mix करना (या vice versa) fragile है।** कोई guarantee नहीं है कि Rollup और webpack CommonJS dependencies के लिए same chunk shape produce करेंगे, जो silently `shared` resolution को break कर सकता है [1]।
- **`baseUrl` / custom base paths में real bugs रहे हैं।** अगर आपका remote एक subpath से serve होता है (enterprise setups में reverse proxy के पीछे common), तो ऐसे issues रहे हैं जहाँ Vite 5+ के तहत federation plugin `remoteEntry.js` को correctly resolve नहीं करता [6]।
- **Non-ESM output formats second-class हैं।** Plugin docs frankly कहते हैं कि ESM well-tested path है; UMD/CJS-style remotes में "complete test cases की कमी है" [1]।

## CSS की वह गड़बड़ी जिसके बारे में कोई नहीं बताता

यह मुझे पहली बार hard bit किया, और यह basically हर किसी को eventually bite करता है। Dev mode में, आपके remote की styles ठीक load होती हैं क्योंकि Vite उन्हें अपने dev server के माध्यम से inject करता है। Production में, Vite default रूप से **CSS code-splitting** करता है — प्रत्येक chunk को अपनी CSS file मिलती है, जो एक `<link>` tag के माध्यम से load होती है जो *page* को जाननी चाहिए।

समस्या? जब एक host dynamically एक remote का component import करता है, तो कुछ भी host के HTML को remote की CSS file load करने के लिए नहीं बताता। इसलिए आपको एक perfectly functional, completely unstyled component मिलता है। एक developer ने इसे बिल्कुल सही describe किया: production में यह "एक unstyled wireframe जैसा दिखा" जबकि locally बढ़िया काम कर रहा था [10]।

लोग जो fixes पर land करते हैं:

- Remote पर `build.cssCodeSplit: false` set करें ताकि उसके सभी CSS एक single file में bundle हो जाएं जिसे आप reliably reference कर सकते हैं।
- CSS को directly JS bundle में inline करने के लिए `vite-plugin-css-injected-by-js` जैसा plugin use करें — ugly है, लेकिन यह guarantee करता है कि styles component के साथ travel करें [10]।
- कुछ teams और आगे जाती हैं और CSS Modules या `:host`/Shadow DOM-style scoping use करती हैं यह सुनिश्चित करने के लिए कि remote की styles accidentally host की global styles में leak नहीं हो सकती (या clobbered नहीं हो सकती) — एक अलग लेकिन related headache, क्योंकि Vite के अपने CSS Modules `composes` handling में खुद duplication quirks रहे हैं।

इनमें से कोई भी exotic नहीं है, लेकिन यह exactly वो तरह की चीज है जो आपकी machine पर perfectly काम करती है और deployed build खुलते ही QA पर fail हो जाती है।

## Shared dependencies और singleton का जाल

Module Federation अपनी असली value `shared` config में earn करता है — या वहाँ quietly आपका दिन बर्बाद करता है। Idea simple है: हर remote अपनी React की copy ship करने की बजाय, आप इसे `shared` mark करते हैं, और ideally `singleton: true`, ताकि पूरे federated app के लिए exactly एक React instance हो [7]।

व्यावहारिक रूप में, **version mismatches federated setups में single most common production bug हैं** [8]। अगर host React 18.2 expect करता है और एक remote React 18.3 के खिलाफ build हुआ था, तो आप वैसे भी दो React instances के साथ end up कर सकते हैं — और React के hooks rules इसे absolutely forgive नहीं करते। Classic symptom है "Invalid hook call" errors जो तब तक कोई sense नहीं बनाते जब तक आपको एहसास नहीं होता कि memory में दो Reacts हैं।

यहाँ जानने लायक कुछ चीजें:

- `singleton: true` runtime को बताता है कि **एक** version pick करे और सभी को उसे use करने के लिए force करे — भले ही यह technically सभी के `requiredVersion` के साथ compatible न हो [7]। यह एक "best effort, don't crash" setting है, correctness की guarantee नहीं।
- `strictVersion: true` उसे flip करता है — version silently pick करने की बजाय, यह incompatibility होने पर throw करता है। Production में discover करने से बेहतर है CI में problems catch करने के लिए।
- Version strings के बारे में real bugs रहे हैं जिनमें build metadata या pre-release suffixes हैं (जैसे `18.2.0-release.99`) जो semver ranges के खिलाफ correctly resolve नहीं होते, जो silently पूरे shared-singleton mechanism को defeat कर सकते हैं [9]।
- Multiple remotes एक shared lib के slightly different versions pull कर रहे हैं इसके opposite problem भी cause कर चुके हैं — dependencies multiple times fetch और bundle हो रहे हैं बजाय deduplicated होने के, खासकर more complex routing setups में `react-router-dom` के साथ [15]।

मेरा honest take: **`shared` config जरूरी है लेकिन पर्याप्त नहीं।** आपको अभी भी teams में real dependency-version discipline चाहिए — ideally एक shared `package.json` या कम से कम एक documented "ये pinned versions हैं जिन्हें हर कोई target करता है" doc। Module Federation duplication reduce करता है; यह alignment enforce नहीं करता।

## क्या यह झंझट करने लायक है? जानने योग्य विकल्प

यह वो question है जो मैं एक भी line of federation config लिखने से पहले पूछूँगा: **क्या आपको वास्तव में इसकी जरूरत है, या आपको independent deploys चाहिए और एक simpler tool काम करेगा?**

कुछ alternatives जो 2026 की conversations में बहुत आते हैं:

- **Import Maps.** एक real web standard (Chrome में 2021 से) जो browser को खुद एक JSON map के माध्यम से versioned URLs पर module specifiers resolve करने देता है — कोई bundler-specific runtime required नहीं [11]। अगर आपके "micro frontends" वास्तव में बस कुछ independently versioned ES modules हैं, तो import maps बहुत कम tooling के साथ आपको ज्यादातर रास्ते तक पहुँचा सकते हैं।
- **Native Federation.** Angular Architects team द्वारा specifically Vite/esbuild-style toolchains के लिए बनाया गया, यह Module Federation *concept* को implement करता है import maps और native ESM का उपयोग करके बजाय custom runtime के [12]। Framework-agnostic, और notably webpack-derived approach से lighter weight।
- **Rspack के माध्यम से Module Federation 2.0।** अगर आपकी team bundlers switch करने के लिए open है (सिर्फ plugin add करने के लिए नहीं), तो Rspack का native Module Federation support Vite ecosystem में किसी भी चीज से ज्यादा mature है, और यह वही MF 2.0 protocol बोलता है जो `@module-federation/vite` use करता है — यानी specific remotes के लिए gradual Vite-to-Rspack migration realistic है [13][3]।
- **Runtime federation के बिना shared packages के साथ एक monorepo।** कभी-कभी actual requirement है "इस Button component को duplicate करना बंद करो," और एक published internal npm package बिना किसी runtime complexity के उसे solve करता है। Boring, लेकिन boring एक feature है।

अगर आपका main goal "independently deployable" है बजाय "must work exactly like our old webpack setup" के, तो मैं genuinely पहले import maps या Native Federation consider करूँगा। Vite federation plugins उससे कठिन problem solve कर रहे हैं जितनी उन्हें करनी चाहिए बहुत सारे cases में, purely क्योंकि teams webpack के साथ API parity चाहती हैं।

## इसे अपनाने से पहले मेरी ईमानदार checklist

अगर आप यह शुरू करने वाले हैं, तो पहली `federation()` config लिखने से पहले यह stuff nail down करें:

| प्रश्न | यह क्यों मायने रखता है |
|---|---|
| क्या remotes को host के release cycle से independently deploy होना है? | अगर नहीं, तो शायद आपको federation की जरूरत नहीं — एक monorepo package simpler हो सकता है |
| क्या आपकी team development के दौरान "rebuild remote, refresh host" tolerate कर सकती है? | यही दोनों major plugins के साथ dev-mode reality है अभी [5] |
| क्या आप `target: 'esnext'` पर हैं और `manualChunks` से बच रहे हैं? | दोनों plugins इसकी require/expect करते हैं; इसके खिलाफ लड़ने से obscure build failures होती हैं [2] |
| क्या teams में shared dependency versions के लिए आपका कोई plan है? | `singleton: true` help करता है लेकिन version discipline की जगह नहीं लेता [8][9] |
| क्या remotes को non-root base के साथ subpath/CDN से serve किया जाएगा? | `remoteEntry.js` resolution bugs का known source [6] |
| क्या आपने production builds test किए हैं, सिर्फ dev नहीं, CSS के लिए? | Styles जो dev में काम करती हैं वो prod में silently गायब हो जाती हैं बहुत लोगों के लिए [10] |
| क्या Native Federation या import maps आपकी actual requirement cover कर सकते हैं? | कभी-कभी simpler standard 20% complexity के साथ 80% काम करता है [11][12] |

चीजें जहाँ खड़ी हैं उनका honest summary: Module Federation Vite के साथ **काम करता है**, और core "runtime पर एक remote component load करो, एक singleton dependency share करो" use case के लिए, यह अच्छी तरह काम करता है। Rough edges तब दिखते हैं जब आप production की तरफ push करते हैं — CSS, dev-mode parity, version drift, और non-root deployments। इनमें से कोई भी dealbreaker नहीं है, लेकिन इनमें से हर एक एक debugging session खाएगा अगर आपको पहले से पता नहीं है कि वे आ रहे हैं। Module Federation 2.0 का bundler-agnostic runtime की तरफ push [3] सबसे promising sign है कि Vite story में सुधार होता रहेगा — लेकिन "improving" और "solved" अभी भी दो अलग-अलग words हैं।

## स्रोत
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