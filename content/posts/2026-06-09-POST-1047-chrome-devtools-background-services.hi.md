+++
title       = "Chrome DevTools Background Services: संपूर्ण गाइड"
description = "Chrome DevTools Background Services की गहन जानकारी — bfcache, Background Fetch, Background Sync, Speculative Loads, Push Messaging, Reporting API, DBSC, और अधिक।"
date        = "2026-06-09T12:07:41+05:30"
slug        = "chrome-devtools-background-services"
tags        = ["Chrome DevTools", "वेब डेवलपमेंट", "डीबगिंग", "PWA", "परफॉर्मेंस", "सर्विस वर्कर्स", "सुरक्षा"]
keywords    = ["Chrome DevTools बैकग्राउंड सर्विसेज़", "bfcache डीबगिंग", "speculative loads DevTools", "background fetch API", "background sync डीबगिंग", "push messaging DevTools", "Reporting API Chrome", "Device Bound Session Credentials DBSC", "bounce tracking mitigations", "payment handler API डीबग"]
canonical   = "/hi/posts/chrome-devtools-background-services/"
feature_image = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&q=80"
+++

आपका वेब ऐप शायद ऐसे काम कर रहा है जिन्हें आपने कभी वास्तव में डीबग नहीं किया। यूज़र के कुछ भी क्लिक करने से पहले pages prerender हो रहे हैं, form submissions ऑफलाइन रहते हुए चुपचाप queue में जा रहे हैं, push notifications एक सोए हुए service worker पर आ रही हैं, sessions cryptographically hardware keys से bound हैं — यह सब Chrome के background service APIs के ज़रिए होता है, पूरी तरह अदृश्य रूप से। Chrome DevTools का Background Services पैनल वह जगह है जहाँ आप अंततः यह सब देख पाते हैं।

## पैनल खोजना

DevTools खोलें (F12 या राइट-क्लिक > Inspect), **Application** टैब पर जाएं, और बाईं साइडबार को तब तक स्क्रॉल करें जब तक आपको "Background Services" सेक्शन न मिल जाए। आपको एक लिस्ट मिलेगी जो essentially Chrome द्वारा support की जाने वाली हर "अदृश्य" API को कवर करती है:

- Back/forward cache
- Background fetch
- Background sync
- Bounce tracking mitigations
- Notifications
- Payment handler
- Periodic background sync
- Push messaging
- Reporting API
- Device bound sessions

इस पैनल को वास्तव में उपयोगी बनाने वाली बात यह है कि कई टैब्स **तीन दिनों तक events रिकॉर्ड कर सकते हैं, यहाँ तक कि जब DevTools खुला न हो** [1]। एक रिकॉर्डिंग सेट करें, चले जाएं, अगली सुबह वापस आएं — events वहाँ होंगे। यह browser tooling के लिए असामान्य है, और यह बदल देता है कि आप async व्यवहार को कैसे डीबग करते हैं जिसे मांग पर reproduce करना मुश्किल होता है।

![background services panel overview](/images/posts/chrome-devtools-background-services/background-services-panel-overview.svg)

## Back/Forward Cache

back/forward cache (bfcache) उन browser features में से एक है जो 2020 से मौजूद है लेकिन फिर भी developers को आश्चर्यचकित करती है — आमतौर पर जब उन्हें एहसास होता है कि उनका पेज इसका उपयोग *नहीं* कर रहा। विचार यह है: जब कोई यूज़र आपके पेज से नेविगेट करता है, Chrome पूरे पेज को — JavaScript heap, DOM, scroll position, सब कुछ — मेमोरी में frozen रखता है। अगर वे back बटन दबाते हैं, Chrome उसे **तुरंत** thaw करके restore करता है, बिना किसी network round trips, re-rendering, या JS re-execution के [2]।

मापे गए performance gains महत्वपूर्ण हैं। Bfcache restores 100ms से कम में हो सकते हैं — पारंपरिक load optimisation के ज़रिए प्राप्त किसी भी चीज़ से तेज़ [2]। यह essentially back/forward navigation को मुफ़्त बना देता है।

निराशाजनक हिस्सा यह था कि यह जानना मुश्किल था कि आपका पेज वास्तव में eligible है या नहीं। Chrome 123 में दो चीज़ों के साथ यह काफी हद तक सुधरा:

- DevTools में **Test back/forward cache** बटन (Application > Back/forward cache > Run Test)। Chrome आपको दूर नेविगेट करता है और वापस लाता है, फिर स्पष्ट रूप से बताता है कि bfcache काम किया या नहीं — और अगर नहीं किया, तो बिल्कुल क्यों।
- [`notRestoredReasons` API](https://developer.chrome.com/docs/web-platform/bfcache-notrestoredreasons), जो आपको programmatically query करने देता है कि किसी नेविगेशन पर bfcache को क्या blocked किया [3]।

पैनल blockers को "Actionable" (जो आप ठीक कर सकते हैं) या "Not actionable" (browser-level decisions) के रूप में categorise करता है। सामान्य actionable blockers में शामिल हैं:

- पेज पर attached `unload` event listeners — इन्हें `pagehide` handlers से replace करें जो `event.persisted` check करते हैं
- Open IndexedDB transactions जो navigation से पहले close नहीं हुए
- `Cache-Control: no-store` headers — ऐतिहासिक रूप से एक hard block, लेकिन [Chrome ने इन pages के लिए bfcache की अनुमति देना शुरू किया](https://developer.chrome.com/docs/web-platform/bfcache-ccns) सीमित शर्तों के तहत 2025 की शुरुआत में, अप्रैल 2025 में 100% उपयोगकर्ताओं तक इसका पूर्ण rollout पूरा हुआ [4]

अगर test आपके पेज को ineligible flag करता है, तो reasons को ध्यान से पढ़ें। पैनल इतना specific है कि actionable हो — यह बताता है कि कौन सा frame, कौन सी script, कौन सा reason। सिर्फ "blocked" नहीं।

## Speculative Loads

अगर bfcache *back* बटन को optimize करता है, तो Speculative Loads *forward* बटन को target करता है। [Speculation Rules API](https://developer.chrome.com/docs/web-platform/prerender-pages) आपको Chrome को instruct करने देता है कि वह उन pages को prefetch या prerender करे जिन पर user के अगला navigate करने की संभावना है [5]।

दो modes के बीच का अंतर मायने रखता है:

| Mode | Chrome क्या करता है | Resource cost |
|---|---|---|
| **Prefetch** | HTML + कुछ subresources download करता है | कम — कोई JS execution नहीं |
| **Prerender** | पेज को एक hidden background process में fully render करता है | अधिक — पूरा page lifecycle |

Prerender प्रभावशाली है। जब यह काम करता है और user क्लिक करता है, navigation **तुरंत** होता है — पेज पहले से fully rendered है, Largest Contentful Paint पहले ही हो चुका है, JavaScript पहले ही चल चुका है।

Real-world results इसकी पुष्टि करते हैं। Monrif, एक Italian media group, ने 2025 की शुरुआत में अपने highest-traffic article URLs पर prerendering लागू किया और LCP में **17.9% तक का सुधार** और कुछ audience segments में **user engagement में peak 8.9% की वृद्धि** देखी [6]। ये सामान्य performance win numbers नहीं हैं। इस तरह का uplift product dashboards को हिला देता है।

DevTools में debug करने के लिए: Application > Background Services > Speculative loads। सेक्शन में तीन views हैं [7]:

- **Speculative loads** — पेज के लिए current speculative status, plus कौन सी URLs यह preload करने की कोशिश कर रहा है
- **Rules** — पेज पर currently active JSON speculation rule sets
- **Speculations** — हर attempt की एक table जिसमें target URL, action (prefetch या prerender), कौन सा rule triggered हुआ, और current status है

अगर कोई speculation fail होती है, तो Speculations table में उस row को click करने से पूरा failure reason दिखता है। URL mismatches, opted-out origins, या prerender quota limits track करने के लिए उपयोगी। जब एक prerender actively चल रहा होता है, DevTools आपको उसके context में switch करके उस hidden background render को directly inspect करने देता है — उस पेज के अंदर Network, Console, या Performance चलाना जिस पर user अभी navigate नहीं हुआ है।

ध्यान देने योग्य: WordPress 6.8 (मार्च 2025 में released) ने Speculation Rules API को WordPress core में शामिल किया। अगर आप WordPress site चलाते हैं और आपने हाल ही में इस पैनल को नहीं देखा है, तो संभावना है कि speculations पहले से चल रहे हों [7]।

## Background Fetch

Standard `fetch()` requests tab बंद होते ही खत्म हो जाते हैं। यह जानबूझकर किया गया है — यह alarming होगा अगर arbitrary web pages indefinitely background में network requests चला सकते। **Background Fetch इसका explicitly permitted version है** — एक download जो tab closure के बाद भी survive करती है, user-visible progress और native cancellation controls के साथ।

इस API को motivate करने वाले use cases बड़े media files थे: एक podcast app को 300MB episode चाहिए, एक streaming service offline content cache कर रही है, एक game assets pre-load कर रहा है। लेकिन एक नया angle है जो तेजी से relevant हो रहा है। [AI model downloads के लिए Background Fetch use करने पर Web.dev की guidance](https://web.dev/articles/background-fetch-ai) उस case को cover करती है जहाँ model weights कई gigabytes हो सकते हैं — page lifecycle के अंदर download करना पूरी तरह impractical, लेकिन background fetch के रूप में manageable [9]।

Flow service worker के ज़रिए काम करता है:

1. `registration.backgroundFetch.fetch()` को एक ID और resources की list के साथ call करें
2. Browser download handle करता है, native progress UI दिखाता है (users pause या cancel कर सकते हैं)
3. Complete होने पर, browser आपके service worker को downloaded response process करने के लिए wake करता है

Debug करने के लिए: Application > Background Services > Background Fetch > **Record** क्लिक करें। अपने पेज से fetch trigger करें, table में events log होते देखें, किसी भी event को click करके full detail देखें। तीन दिन का recording window मतलब है कि आप एक background download verify कर सकते हैं जो DevTools बंद करने के काफी बाद complete होती है [1]।

एक caveat: Background Fetch एक Chromium-specific feature है [10]। यह Firefox या Safari में मौजूद नहीं है। अगर आप cross-browser build कर रहे हैं, तो एक fallback path plan करें।

## Background Sync

Background Sync इसका counterpart है — यह data reliably भेजने के बारे में है, receive करने के नहीं। Scenario: एक user flaky connection पर form submit करता है, एक message queue करता है, या analytics event fire करता है। Standard fetch चुपचाप fail हो जाता है। **Background Sync request को queue करता है और अगली बार जब device की reliable connection हो तब deliver करता है**, बिना manual retry की ज़रूरत के [8]।

[Workbox Background Sync module](https://developer.chrome.com/docs/workbox/modules/workbox-background-sync) इसे practical बनाता है। इसका `BackgroundSyncPlugin` fetch failure events में hook करता है — specifically, जब network error exception throw करता है, न कि जब आपको 4xx या 5xx response मिलता है — और failed requests को exponential backoff के साथ बाद के retry के लिए IndexedDB में queue करता है।

एक testing mistake जो लोगों को trip करती है: Application panel के Service Workers सेक्शन में "Offline" checkbox **service worker network requests को block नहीं करता**। यह only page-level fetch calls को affect करता है। अगर आप background sync behaviour test कर रहे हैं, तो आपको actually अपना network adapter disable करना होगा या Network panel के throttling presets use करने होंगे। Service worker offline checkbox के साथ testing करने से sync ऐसे काम करते दिखेगा जैसे उसे नहीं करना चाहिए।

Debug करने के लिए: Application > Background Services > Background Sync > **Record** क्लिक करें। Background sync activity trigger करें, table में events populate होते देखें जिसमें tag name, origin, और timestamp होगा।

## Push Messaging और Notifications

ये दोनों साथ काम करते हैं, इसलिए इन्हें side by side देखना समझदारी है। Push Messaging वह तरीका है जिससे आपका server user के browser को message deliver करता है, यहाँ तक कि जब वे आपकी site पर न हों। Notifications वह तरीका है जिससे वह message user को दिखाया जाता है।

Push के साथ debugging problem timing है। आपको एक server चाहिए जो इसे भेजे, delivery asynchronous है, और service worker इसे background में process करता है। **Push Messaging टैब इन events को तीन दिनों तक रिकॉर्ड करता है** — तो आप अपने server से push trigger करने से पहले एक recording सेट कर सकते हैं और exactly inspect कर सकते हैं कि क्या arrived, किस order में, किस payload के साथ [1]।

Notifications के लिए: Application > Background Services > Notifications > **Record** क्लिक करें। जब आपका service worker `self.registration.showNotification()` call करता है, event full detail के साथ log होता है — title, body, icon, badge, actions, हर option जो आपने pass किया।

एक shortcut है जिसके लिए आपके server की बिल्कुल ज़रूरत नहीं: sidebar में Service Workers सेक्शन (Background Services के ठीक ऊपर) में एक **Push** input field और button है। एक payload type करें, Push click करें, और DevTools आपके registered service worker पर एक synthetic push event fire करता है। Server infrastructure खड़ी किए बिना आपके push handler logic verify करने के लिए ideal।

## Payment Handler

[Payment Handler API](https://developer.mozilla.org/en-US/docs/Web/API/Payment_Handler_API) एक web app को standard Web Payments flow के अंदर payment method के रूप में act करने देती है [14]। Users को third-party payment processor पर redirect करने के बजाय, आपका service worker payment request intercept करता है और transaction in-context handle करता है — wallets, buy-now-pay-later services, और web-based payment apps के लिए cleaner UX।

दो service worker events पूरी चीज़ drive करते हैं:

1. **`canmakepayment`** — तब fire होता है जब कोई merchant `new PaymentRequest()` call करता है। आपका service worker respond करता है कि क्या वह इस particular payment को handle कर सकता है।
2. **`paymentrequest`** — तब fire होता है जब user browser payment sheet से आपका payment app select करता है और confirm tap करता है। यहाँ आप actual transaction करते हैं।

Debug करने के लिए: Application > Background Services > Payment Handler > **Record** क्लिक करें। दोनों events table में payment method data और merchant info की full detail के साथ log होते हैं।

Practical local development note: Payment Request API को HTTPS चाहिए, लेकिन Chrome default रूप से `localhost` को exempt करता है। आप self-signed certificate setup किए बिना locally test कर सकते हैं।

## Bounce Tracking Mitigations

ईमानदारी से कहें तो, यह पैनल में सबसे niche टैब है। लेकिन अगर आपका काम analytics, ad tech, SSO flows, या cross-site redirects से जुड़ी किसी भी चीज़ को छूता है, तो आपको इसके बारे में जानना होगा — क्योंकि यह silently उस state को delete कर सकता है जिस पर आप depend करते हैं।

Bounce tracking एक privacy evasion technique है। एक user एक link click करता है, एक सेकंड से कम में transparently एक tracker domain के ज़रिए bounce होता है, और वह tracker first-party context में cookies set या read करता है — यहाँ तक कि third-party cookies पूरी तरह blocked होने पर भी। इसीलिए third-party cookies को block करना अकेले cross-site tracking को solve नहीं करता।

Chrome का mitigation उन sites की identify करता है जो ये patterns exhibit करती हैं और **उनकी stored state को completely delete करता है** — cookies, localStorage, cache storage, सब कुछ [11]। Application > Background Services > Bounce Tracking Mitigations का DevTools टैब आपको deletion check manually force-run करने देता है और exactly देखने देता है कि किन site origins की state remove हुई।

इसे test करने के लिए:

1. `chrome://flags` में, "Bounce Tracking Mitigations" को **Enabled With Deletion** पर set करें
2. Chrome Settings > Privacy and security में third-party cookies block करें
3. Application > Background Services > Bounce Tracking Mitigations > **Force Run** क्लिक करें

Issues टैब suspicious redirect chains के लिए एक warning भी surface करेगा: "Chrome may soon delete state for intermediate websites in a recent navigation chain." अगर आपका OAuth या SSO implementation वह warning trigger करता है, तो आपके पास एक investigation है। Legitimate auth redirects bounce tracking जैसे लग सकते हैं अगर hop timing similar हो।

## Reporting API

[Reporting API](https://developer.chrome.com/docs/capabilities/web-apis/reporting-api) boring लगता है जब तक आपको एहसास न हो कि यह आपको silent production failures की visibility दे रहा है जिन्हें observe करने का आपके पास कोई दूसरा mechanism नहीं है [12]। **API CSP violations, deprecated API calls, network errors, Permission Policy violations, और crash reports collect करता है, फिर उन्हें आपके configure किए गए endpoint पर भेजता है।**

Configuration एक single response header है:

```http
Reporting-Endpoints: default="https://yoursite.com/csp-reports"
```

Chrome reports batch करता है और उस URL पर deliver करता है। DevTools पैनल (Application > Background Services > Reporting API) इसे तीन sections में break करता है:

- **Reports table** — हर pending और sent report, जिसमें type, URL, timestamp, और delivery status है
- **Report body** — full JSON payload देखने के लिए किसी report row को click करें
- **Endpoints** — configured endpoints और क्या Chrome ने उन्हें successfully reach किया, इसका summary

Practice में status column सबसे उपयोगी हिस्सा है। Reports states के ज़रिए flow करती हैं: Queued → Pending → Success (या MarkedForRemoval अगर fail हो)। अगर reports indefinitely "Pending" में बैठी हैं, तो आपके endpoint में कुछ गड़बड़ है — commonly एक CORS misconfiguration, एक 4xx response, या header value में typo।

CSP violations सबसे common use case हैं और शायद Reporting API को wire up करने का सबसे अच्छा argument, यहाँ तक कि अगर आप इसके साथ और कुछ नहीं कर रहे। इसके बिना, आप content security policy deploy करते हैं और production में क्या block हो रहा है इसका zero signal मिलता है। इसके साथ, आपको हर real user session में हर violation का structured log मिलता है।

## Device Bound Sessions

यह पैनल में सबसे नई entry है और arguably सबसे security-significant feature जो Chrome ने वर्षों में ship किया है। Device Bound Session Credentials (DBSC) एक specific, well-understood attack को address करता है: **session cookie theft**।

Attack इस तरह काम करता है। User की machine पर malware, एक compromised browser extension, या local privilege escalation एक attacker को session cookies export करने देता है। वे cookies, attacker की machine से replay किए गए, victim के रूप में authenticate करते हैं — MFA हो या न हो, क्योंकि MFA पहले ही satisfy हो चुका था और cookie *ही* credential है।

DBSC इसे **session को specific physical device से cryptographically bind करके** तोड़ता है [13]। Login पर, Chrome एक key pair generate करता है और private key को device के secure hardware में store करता है — जब available हो तो Trusted Platform Module (TPM)। Sessions short-lived cookies use करते हैं। जब कोई cookie expire होती है, Chrome को server द्वारा नई cookie issue करने से पहले private key के possession का proof देना होगा। एक attacker जो cookie steal करता है वह किसी key के possession का proof नहीं दे सकता जो device कभी नहीं छोड़ी।

DBSC implement करने वाले developers के लिए, server-side changes हैं [14]:

1. अपने login response में एक `Secure-Session-Registration` header include करें, refresh endpoint URL और session configuration specify करते हुए
2. एक refresh endpoint expose करें जो नई cookies issue करने से पहले cryptographic key possession proof validate करता है

DBSC 2026 की शुरुआत में Chrome 146 पर Windows users के लिए generally available हुआ, macOS expansion जल्द बाद announce हुई [14]। एक second origin trial October 2025 में real-world implementation feedback collect करने के लिए खुला।

DevTools में, Application panel का Device Bound Sessions सेक्शन आपको **active DBSC sessions view करने, उनके bound domains inspect करने, और उन्हें delete करने** देता है — यह verify करने के लिए उपयोगी है कि आपका logout flow sessions correctly terminate करता है, और confirm करने के लिए कि session binding expected origin के लिए registered है। Full debugging tooling अभी भी build हो रही है; अभी के लिए, Chrome histograms और network response headers उन gaps को fill करते हैं जो पैनल अभी तक cover नहीं करता।

Underlying spec W3C Web Application Security working group के ज़रिए develop हो रहा है, इसलिए DBSC को eventual cross-browser adoption के लिए design किया जा रहा है — एक permanent Chrome-only feature नहीं।

---

bfcache के near-instant back navigation देने, speculative loads के users के click करने से पहले pages prerender करने, background sync के यह सुनिश्चित करने के बीच कि कोई भी user action flaky connection पर silently drop न हो, और DBSC के session hijacking को hardware level पर prevent करने के साथ — Background Services पैनल quietly Chrome DevTools के सभी sections में सबसे महत्वपूर्ण और सबसे कम-explore किए गए sections में से एक है।

> अंत

## स्रोत
1. [Debug background services | Chrome DevTools](https://developer.chrome.com/docs/devtools/javascript/background-services)
2. [Back/forward cache | web.dev](https://web.dev/articles/bfcache)
3. [Back/forward cache notRestoredReasons API | Chrome for Developers](https://developer.chrome.com/docs/web-platform/bfcache-notrestoredreasons)
4. [Enabling bfcache for Cache-Control: no-store | Chrome for Developers](https://developer.chrome.com/docs/web-platform/bfcache-ccns)
5. [Prerender pages in Chrome for instant page navigations | Chrome for Developers](https://developer.chrome.com/docs/web-platform/prerender-pages)
6. [How Monrif improved engagement by 8.9% and reduced LCP by 17.9% with Speculation Rules prerender | web.dev](https://web.dev/case-studies/monrif-cwv)
7. [Debug speculation rules with Chrome DevTools | Chrome for Developers](https://developer.chrome.com/docs/devtools/application/debugging-speculation-rules)
8. [workbox-background-sync | Chrome for Developers](https://developer.chrome.com/docs/workbox/modules/workbox-background-sync)
9. [Download AI models with the Background Fetch API | web.dev](https://web.dev/articles/background-fetch-ai)
10. [Introducing Background Fetch | Chrome for Developers](https://developer.chrome.com/blog/background-fetch)
11. [Help test bounce tracking mitigations | Chrome for Developers](https://developer.chrome.com/blog/bounce-tracking-mitigations-dev-trial)
12. [Monitor your web application with the Reporting API | Chrome for Developers](https://developer.chrome.com/docs/capabilities/web-apis/reporting-api)
13. [Device Bound Session Credentials (DBSC) | Chrome for Developers](https://developer.chrome.com/docs/web-platform/device-bound-session-credentials)
14. [Device Bound Session Credentials now available on Windows | Chrome for Developers](https://developer.chrome.com/blog/dbsc-windows-announcement)
15. [Web-based Payment Handler API | MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/Payment_Handler_API)