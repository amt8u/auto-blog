+++
title       = "React असल में कैसे काम करता है: Fiber और Batch Rendering की पूरी समझ"
description = "React आपके UI को कैसे render करता है, React Fiber असल में क्या है, और बेहतर performance के लिए automatic batching React 16 से React 19.2 तक कैसे evolve हुई — इस सबकी एक deep dive।"
date        = "2026-06-13T17:37:28+05:30"
slug          = "how-react-works-fiber-and-batch-rendering-explained"
tags          = ["react", "javascript", "वेब-परफॉर्मेंस", "frontend"]
keywords      = ["react fiber", "react बैचिंग", "react 18 automatic batching", "react रिकॉन्सिलिएशन", "react rendering प्रक्रिया", "react 19 परफॉर्मेंस"]
canonical     = "/hi/posts/how-react-works-fiber-and-batch-rendering-explained/"
feature_image = "/images/POST-1056-how-react-works-fiber-and-batch-rendering-explained.svg"
+++

क्या आपने कभी किसी React app में कोई button क्लिक किया है और बस... भरोसा कर लिया है कि UI सही तरीके से update हो जाएगा? हाँ, मैंने भी, सालों तक। मैंने कभी रुककर यह नहीं सोचा कि `setState` और स्क्रीन पर pixels बदलने के बीच क्या होता है — जब तक मैं एक ऐसे component को debug नहीं करने लगा जो एक ही क्लिक पर पाँच बार re-render हो रहा था। वह rabbit hole मुझे सीधे Fiber, lanes, और इस आश्चर्यजनक रूप से लंबी history में ले गया कि React यह कैसे तय करता है कि आपके app को असल में *कब* re-render करना है।

यह article उसी rabbit hole को organized तरीके से पेश करता है। हम देखेंगे कि React असल में अंदर से कैसे काम करता है, React Fiber क्या है और यह क्यों मौजूद है, और फिर यह समझेंगे कि batching — जो यह control करता है कि आपका component कितनी बार re-render होता है — हर release के साथ कैसे बदलती गई है।

## जब आप setState कॉल करते हैं, तो असल में क्या होता है?

यहाँ वह बात है जो शायद ही कोई साफ़-साफ़ बताता है: `setState` (या `useState` से मिला state setter) कॉल करने से स्क्रीन पर तुरंत कुछ नहीं बदलता। यह बस React को बताता है, "अरे, कुछ बदल गया है, शायद तुम्हें इसे फिर से देखना चाहिए।"

इसके बाद एक multi-step प्रोसेस शुरू होता है:

1. **Trigger** — कुछ होता है (एक event, network response, या timer) जो किसी state setter को कॉल करता है।
2. **Render** — React आपके component functions को फिर से कॉल करता है ताकि यह पता चल सके कि नया UI *कैसा* दिखना चाहिए। इससे React elements का एक tree बनता है (जिसे अक्सर ढीले-ढाले तौर पर "virtual DOM" कहा जाता है)।
3. **Reconciliation** — React नए tree की तुलना पिछले वाले से करता है और यह पता लगाता है कि कम से कम कौन-कौन से बदलाव करने ज़रूरी हैं।
4. **Commit** — React उन बदलावों को असली DOM पर लागू करता है, effects चलाता है, और browser परिणाम को paint करता है।

"virtual DOM" शब्द बहुत इस्तेमाल होता है, और सच कहें तो अब यह नाम थोड़ा भ्रामक हो गया है। आज React असल में अंदर जो maintain करता है वह **Fiber nodes** का एक tree है — जो DOM के एक साधारण snapshot से कहीं ज़्यादा rich structure है। हम इस पर थोड़ी देर में आएंगे, क्योंकि यही असल में इस पूरे article का दिल है।

## Reconciliation: React की Diffing Trick

Fiber की बात आने से पहले, यह समझना ज़रूरी है कि React DOM को इतनी efficiently update *क्यों* कर पाता है। दो arbitrary trees की node-by-node तुलना करना, computer science के नज़रिए से, एक costly समस्या है — naive tree diffing लगभग n nodes के लिए O(n³) है। यह उस UI library के लिए बहुत slow है जिसे हर keystroke पर चलना पड़ता है।

इसलिए React कुछ simplifying assumptions के साथ एक heuristic-based algorithm इस्तेमाल करता है [5]:

- **अलग-अलग element types अलग-अलग trees बनाते हैं।** अगर कोई `<div>` `<span>` बन जाता है, तो React उनके children को diff करने की ज़हमत नहीं करता — यह सिर्फ़ पुराने को तोड़कर नया scratch से बना देता है।
- **एक ही element type, एक ही position?** React underlying DOM node को रखता है और सिर्फ़ बदले हुए attributes/props को update करता है।
- **Lists को keys की ज़रूरत होती है।** जब आप `.map()` से कोई list render करते हैं, तो React renders के बीच items को match करने के लिए `key` prop इस्तेमाल करता है। stable keys के बिना (या उससे भी बदतर, जब list reorder हो सकती है तब array index को key के तौर पर इस्तेमाल करने पर), React confuse हो सकता है कि कौन-सा item कौन-सा है — जिससे ऐसे अजीब bugs आते हैं जैसे reorder के बाद form inputs में गलत value रह जाना।

[React के reconciliation process](https://www.geeksforgeeks.org/reactjs/reactjs-reconciliation/) का यही वह हिस्सा है जिसे ज़्यादातर tutorials cover करते हैं [5]। लेकिन reconciliation अपने आप यह नहीं बताता कि एक बड़े update पर React, browser को freeze किए बिना यह सब काम *कैसे* कर लेता है। यहीं पर Fiber आता है — और यह उससे कहीं बड़ी बात है जितना ज़्यादातर लोग समझते हैं।

## Fiber की एंट्री: वह Rewrite जिसने सब कुछ बदल दिया

React 16 से पहले, React वह इस्तेमाल करता था जिसे अब **"stack reconciler"** कहा जाता है। यह काम तो करता था, लेकिन इसमें एक बुनियादी समस्या थी: यह recursive और synchronous था। एक बार जब React किसी tree को render करना शुरू कर देता, तो वह खत्म होने तक रुक नहीं सकता था — JavaScript call stack तब तक बढ़ता रहता जब तक पूरा tree process न हो जाए [3][4]।

छोटे apps के लिए यह ठीक है। आपको कभी फ़र्क महसूस नहीं होगा। लेकिन बड़े component trees के लिए — जैसे हज़ारों rows वाला कोई data grid, या एक complex dashboard — वह synchronous render इतना समय ले सकता था कि main thread दसों milliseconds के लिए block हो जाए। Animations अटकने लगते, scrolling में jank आता, और किसी input में टाइप करना सुस्त लगता, क्योंकि जब तक React अपना काम पूरा नहीं कर लेता, browser कुछ और process ही नहीं कर पाता।

सितंबर 2017 में, React 16 इस core algorithm के पूरे rewrite के साथ आया, जिसे **Fiber** कहा गया [2]। Meta की engineering team ने इसे एक "API-compatible rewrite" बताया — यानी आपके component code को बदलने की ज़रूरत नहीं थी, लेकिन इसके नीचे जो कुछ हो रहा था, वह सब बदल गया [2]।

### असल में Fiber क्या है?

इसे describe करने का सबसे साफ़ तरीका जो मैंने देखा है (React core contributor Andrew Clark के अपने notes से) यह है कि **fiber एक "virtual stack frame"** है [3]। JavaScript call stack पर निर्भर रहने के बजाय — जो बिना रुके top से bottom तक execute होता है — React अपना खुद का data structure बनाता है जो एक stack जैसा बर्ताव करता है, लेकिन जिसे React पूरी तरह control करता है।

हर fiber एक plain JavaScript object होता है जो work की एक unit को represent करता है — मूल रूप से एक component — और इसमें होता है:

- **type और key** — यह बताते हैं कि यह किस तरह का component या DOM element है
- **child, sibling, और return pointers** — जो tree का एक linked-list representation बनाते हैं (एक typical nested-array tree के बजाय)
- **pendingProps और memoizedProps** — आ रहे नए props बनाम पिछली बार के props, यह जांचने के लिए कि असल में कुछ बदला है या नहीं
- **alternate** — इस fiber के "दूसरे version" की तरफ़ इशारा करने वाला pointer (इस पर थोड़ी देर में और बात करेंगे)

सच कहूं तो वह **alternate** pointer ही सबसे clever हिस्सा है। React एक साथ memory में दो trees रखता है: **current tree** (जो अभी असल में स्क्रीन पर है) और **workInProgress tree** (जिसे React अगले update के लिए अभी बना रहा है) [4]। जब work-in-progress tree पूरा हो जाता है, तो React सिर्फ़ एक pointer swap कर देता है — work-in-progress, current tree बन जाता है। इसे कभी-कभी "double buffering" कहा जाता है, और यह वही trick है जो video games आधे-बने frames को दिखाने से बचने के लिए इस्तेमाल करते हैं।

क्योंकि हर fiber खुद work की एक छोटी unit है, React tree को node-by-node process कर सकता है, और हर node खत्म करने के बाद, **रुककर पूछ सकता है: "क्या मेरे पास आगे जारी रखने का समय है, या मुझे control browser को वापस दे देना चाहिए?"** [3][4]। यही एक क्षमता — pause करना, yield करना, और resume करना — बाकी सब कुछ (concurrent rendering, transitions, automatic batching) संभव बनाती है।

### Render Phase बनाम Commit Phase

React इस सारे काम को दो phases में बांटता है, जिनके नियम बहुत अलग हैं:

- **Render phase** — React workInProgress tree पर चलता है, आपके components को कॉल करता है, और पता लगाता है कि क्या बदला है। यह phase **pure** है (कोई DOM mutations नहीं, कोई side effects नहीं) और **interruptible** है — अगर कोई ज़्यादा urgent update आता है, तो React इसे pause कर सकता है, इसके काम को छोड़ सकता है, या इसे फिर से शुरू कर सकता है [3][4]।
- **Commit phase** — React तैयार हो चुके काम को लेकर असल DOM को mutate करता है, layout effects चलाता है, और refs को update करता है। यह phase **synchronous** है और इसे **interrupt नहीं किया जा सकता** — एक बार शुरू होने के बाद, यह पूरा होकर ही खत्म होता है, ताकि यूज़र को कभी आधा-अधूरा updated UI न दिखे [1][4]।

![react render commit pipeline](/images/posts/how-react-works-fiber-and-batch-rendering-explained/react-render-commit-pipeline.svg)

## Scheduler: हर Update को Priority देना

एक बार जब Fiber ने interruptible rendering को संभव बना दिया, तो React को यह तय करने का एक तरीका चाहिए था कि *क्या* interrupt होगा और *क्या* priority पाएगा। यही काम [scheduler](https://github.com/facebook/react/blob/main/packages/scheduler/src/forks/Scheduler.js) का है — एक अलग package जिसे React अपने core के साथ ship करता है [14]।

Scheduler priority levels को define करता है, हर एक के साथ एक internal timeout होता है जो यह तय करता है कि किसी काम को कब तक टाला जा सकता है, इससे पहले कि React उसे जबरन पूरा करवाए [14]:

| Priority | Timeout | उदाहरण use case |
|---|---|---|
| Immediate | -1ms (अभी) | Synchronous, critical updates |
| User-blocking | 250ms | टाइप करना, क्लिक करना, drag करना |
| Normal | 5,000ms | Data fetch के results, non-urgent updates |
| Low | 10,000ms | Analytics, background sync |
| Idle | लगभग कभी नहीं | Offscreen content, hidden tabs |

React 18 में, यह priority system **lanes** के साथ और भी granular हो गया — एक bitmask-based model जिसमें updates को assign करने के लिए 31 तक अलग-अलग priority "lanes" हो सकते हैं [9]। practical असर यह है: अगर आप किसी बड़े, low-priority update को render कर रहे हैं (मान लीजिए, किसी विशाल list को filter करना) और यूज़र किसी button पर क्लिक करता है, तो React **उस low-priority render को pause कर सकता है, क्लिक को तुरंत handle कर सकता है, और बाद में filtering का काम वापस शुरू कर सकता है** [9]। Fiber से पहले, यह architecturally संभव ही नहीं था — एक बार जब React rendering शुरू कर देता, तो वह रुक नहीं सकता था।

यही `useTransition` और `useDeferredValue` की foundation भी है, जिनके बारे में हम जल्द ही बात करेंगे। ये असल में developer के लिए वे levers हैं जिनसे कहा जा सकता है, "कृपया इस particular update को low priority के तौर पर treat करो" [10]।

## Batching: वह खामोश Optimization जिसे बनने में 10 साल लगे

ठीक है, यहीं से चीज़ें असल में दिलचस्प होती हैं — और यहीं ज़्यादातर articles या तो बात को बहुत आसान बना देते हैं या history को पूरी तरह छोड़ देते हैं। **Batching** React की वह strategy है जिसमें कई state updates को साथ में group किया जाता है, ताकि वे कई बार के बजाय *एक* ही re-render trigger करें। सुनने में यह आसान लगता है। लेकिन इसका implementation लगभग हर major React release में चुपचाप evolve होता रहा है।

### React 18 से पहले: Batching सिर्फ़ Event Handlers के अंदर काम करती थी

सालों तक, React की batching उसके synthetic event system से जुड़ी रहती थी। अगर आप किसी React event handler (`onClick`, `onChange`, आदि) के अंदर कई state setters कॉल करते थे, तो React उन्हें एक ही re-render में batch कर देता था। लेकिन उस context से बाहर निकलते ही — किसी `setTimeout`, `Promise.then()`, या raw `addEventListener` में — **batching पूरी तरह काम करना बंद कर देती थी** [1][7]।

```js
// React 17 and earlier
function handleClick() {
  setTimeout(() => {
    setCount(c => c + 1); // triggers a re-render
    setFlag(f => !f);     // triggers ANOTHER re-render
  }, 1000);
}
```

यह conceptually एक logical update के लिए दो पूरे render-and-commit cycles हैं। दो `setState` calls के लिए यह कोई बड़ी बात नहीं है, लेकिन मैंने ऐसे real apps देखे हैं जहां एक ही async callback छह या सात state updates fire कर देता था — और हर एक, एक moderately heavy component tree को re-render कर देता था। यह जुड़ता चला जाता है।

इस limitation की *वजह से* `unstable_batchedUpdates` का अस्तित्व था। यह `react-dom` से export होने वाला एक undocumented API था (इसीलिए वह डरावना `unstable_` prefix था) जो किसी callback को manually React के batching context में wrap कर देता था [6]:

```js
import { unstable_batchedUpdates } from 'react-dom';

setTimeout(() => {
  unstable_batchedUpdates(() => {
    setCount(c => c + 1);
    setFlag(f => !f);
  }); // now only ONE re-render
}, 1000);
```

अगर आपने कभी Redux, MobX, या Zustand इस्तेमाल किया है, तो आपको इसका फायदा बिना जाने ही मिला है — इन libraries ने अपने store update notifications को खास तौर पर `unstable_batchedUpdates` में wrap किया था, ताकि "external state से कई renders" वाली समस्या से बचा जा सके [6]। यह एक ऐसा workaround था जो ecosystem के आधे हिस्से में बेक हो गया था, क्योंकि framework खुद इसे consistently नहीं कर पाता था।

### React 18: हर जगह Automatic Batching

React 18 (मार्च 2022 में release हुआ) ने आखिरकार इसे जड़ से ठीक कर दिया [1]। नए `createRoot` API के साथ, **हर state update अपने-आप, by default batch हो जाता है, चाहे वह कहीं से भी आए** — timeouts, promises, native event listeners, जो भी हो [1][8]।

```js
// React 18+ with createRoot
function handleClick() {
  setTimeout(() => {
    setCount(c => c + 1);
    setFlag(f => !f);
    // Only ONE re-render, automatically
  }, 1000);
}
```

कुछ ज़रूरी details जिनमें लोग अक्सर उलझ जाते हैं:

- **आपको `createRoot` के ज़रिए opt in करना होता है।** अगर आपका app अभी भी legacy `ReactDOM.render()` कॉल करता है, तो आपको automatic batching नहीं मिलती — React backward compatibility के लिए पुराना behavior बनाए रखता है [1]।
- **`unstable_batchedUpdates` एक no-op बन जाता है।** क्योंकि अब सब कुछ automatically batch हो जाता है, वह पुराना API अब... कुछ खास नहीं करता [6][7]।
- **आप अब भी इससे *बाहर* निकल सकते हैं** `react-dom` के `flushSync` का इस्तेमाल करके, उन कुछ rare cases के लिए जहां आपको असल में अगली line of code चलने से पहले DOM को synchronously updated चाहिए (उदाहरण के लिए, state change के ठीक बाद layout measure करना):

```js
import { flushSync } from 'react-dom';

function handleClick() {
  flushSync(() => {
    setCount(c => c + 1);
  });
  // DOM has already updated here
  setFlag(f => !f); // this one batches normally
}
```

सच कहूं तो — React लिखते हुए इन सालों में, मैंने शायद सिर्फ़ दो बार `flushSync` का इस्तेमाल किया है, दोनों बार state-driven layout change के ठीक बाद DOM nodes को measure करने के लिए। यह एक असली escape hatch है, लेकिन अगर आप इसे बार-बार इस्तेमाल कर रहे हैं, तो आम तौर पर इसका मतलब है कि आपके architecture में कुछ और सोचने की ज़रूरत है।

### React 18 के Concurrent Features: Transitions और Deferred Values

Automatic batching renders की *संख्या* कम करती है। लेकिन React 18 ने renders की *priority* control करने के लिए भी tools introduce किए — जो एक related लेकिन अलग optimization है [1]।

- **`startTransition` / `useTransition`** — इससे आप किसी state update को "non-urgent" मार्क कर सकते हैं। React इसे background में render करेगा और अगर कोई ज़्यादा urgent चीज़ (जैसे कोई keystroke) आती है, तो इसे interrupt कर सकता है [1][10]।
- **`useDeferredValue`** — एक value लेता है और आपको उसका एक ऐसा version देता है जो urgent renders के दौरान "पीछे रह जाता है", जो debouncing जैसा ही है, लेकिन किसी arbitrary timer के बिना [1]।

```js
const [query, setQuery] = useState('');
const [isPending, startTransition] = useTransition();

function handleChange(e) {
  setQuery(e.target.value); // urgent: keep the input snappy

  startTransition(() => {
    setSearchResults(filterHugeList(e.target.value)); // low priority
  });
}
```

Batching से इसका फ़र्क subtle लेकिन ज़रूरी है: batching का मतलब है updates को *जोड़कर* कम renders में बदलना, जबकि transitions का मतलब है किसी render को *deprioritize* करना ताकि वह ज़्यादा urgent renders को block न करे [9][10]। दोनों आखिर में इसलिए मौजूद हैं क्योंकि सबसे पहले Fiber ने rendering को interruptible बनाया — उस बुनियादी rewrite के बिना, इनमें से कोई भी संभव नहीं होता।

### React 19 और 19.2: Actions, Compiler, और SSR Batching

React 19 (दिसंबर 2024) ने batching में React 18 जैसा बड़ा बदलाव नहीं किया, लेकिन यह उसी foundation पर आगे बनता रहा [11]:

- **Actions API** (`useActionState`, `useFormStatus`, `useOptimistic`) — इनसे आप async functions को सीधे `<form action={...}>` को pass कर सकते हैं। अंदर ही अंदर, React pending state को automatically manage करता है, उससे बनने वाले updates को batch करता है, और सफल होने पर form को reset कर देता है — और इसके लिए आपको manually loading flags track करने की ज़रूरत नहीं पड़ती [11]।

```js
const [error, submitAction, isPending] = useActionState(
  async (previousState, formData) => {
    const error = await updateName(formData.get('name'));
    if (error) return error;
    return null;
  },
  null,
);
```

- **React Compiler** — यह overall rendering performance के लिए एक बड़ी बात है, भले ही यह strictly "batching" न हो। यह अक्टूबर 2025 में version 1.0 तक पहुंचा [13]। यह compiler build time पर चलता है और automatically memoization डाल देता है — वही optimization जो आप पहले `useMemo`, `useCallback`, और `React.memo` से hand-write करते थे — जिससे components, जब उनके inputs असल में नहीं बदले हों, तो re-render होने को skip कर देते हैं [13]। यह Meta में production में चल रहा है, और React team ने Vite, Next.js, और Expo के साथ partner किया है ताकि नए projects इसे by default चालू कर सकें [13]। सच कहूं तो, यह उस सब चीज़ का स्वाभाविक अंत लगता है जो Fiber ने शुरू की थी: पहले rendering को interruptible और schedulable बनाओ, फिर इसे efficiently batch करो, और आखिर में — बस ज़रूरत से ज़्यादा काम को पूरी तरह skip कर दो।

- **React 19.2** (अक्टूबर 2025) ने batching को server rendering में भी बढ़ा दिया। Streaming SSR के दौरान, **Suspense boundary reveals अब एक छोटी window के लिए batch हो जाते हैं**, ताकि कई boundaries जो आसपास resolve होते हैं उन्हें एक-एक करके भेजने के बजाय client को साथ में भेजा जा सके — जो client के behave करने के तरीके से भी बेहतर मेल खाता है [12]। इस release में नया `<Activity />` component (UI को hide/restore करते हुए state को preserve रखने के लिए), `useEffectEvent`, और "Performance Tracks" भी आए — एक Chrome DevTools integration जो scheduler के priority decisions को सीधे Performance panel में visualize करता है [12]।

## सब कुछ एक साथ: एक नज़र में पूरा Evolution

| Version | साल | Rendering/Batching के लिए क्या बदला |
|---|---|---|
| ≤ React 15 | — | Stack reconciler — synchronous, non-interruptible recursion [3][4] |
| React 16 | 2017 | Fiber rewrite — interruptible render phase, double-buffered tree, priority-aware scheduling [2][3] |
| React 16–17 | 2017–2020 | Batching सिर्फ़ React event handlers के अंदर; manual workaround के तौर पर `unstable_batchedUpdates` [6][7] |
| React 18 | 2022 | हर जगह automatic batching (`createRoot` के ज़रिए), `flushSync` opt-out, lanes-based concurrent rendering, `useTransition`/`useDeferredValue` [1][9] |
| React 19 | 2024 | Actions API async updates के आसपास pending/optimistic state को auto-manage करता है [11] |
| React 19.2 | 2025 | SSR में Suspense boundary reveals batch होते हैं; `<Activity />`, scheduler priorities को visualize करने के लिए Performance Tracks [12] |
| React Compiler 1.0 | 2025 | Build-time automatic memoization — manual `useMemo`/`useCallback` के बिना re-renders skip करता है [13] |

![react batching before after](/images/posts/how-react-works-fiber-and-batch-rendering-explained/react-batching-before-after.svg)

## आपके लिए यह सब क्यों मायने रखता है

अगर आप सिर्फ़ forms और dashboards बना रहे हैं, तो आप सोच सकते हैं, "ठीक है, लेकिन मुझे कभी `flushSync` या `unstable_batchedUpdates` की *ज़रूरत* नहीं पड़ी, तो यह क्यों मायने रखता है?"

बात सही है। लेकिन practice में यह असल में यहां लोगों को परेशान करता है:

- **"यह दो बार render क्यों हुआ?"** को debug करना हर React developer के लिए एक rite of passage है, और इसका जवाब लगभग हमेशा batching behavior में ही छुपा होता है — development में Strict Mode द्वारा effects को double-invoke करना, या किसी batched context के बाहर होने वाला update।
- **`ReactDOM.render()` से `createRoot` पर migrate करना** सिर्फ़ एक version bump नहीं है — यह चुपचाप बदल देता है कि आपका app updates को कैसे batch करता है। अगर आपके app ने कहीं synchronous re-renders पर भरोसा किया था (चाहे जानबूझकर या नहीं), तो automatic batching उन assumptions को सामने ला सकती है।
- **lanes और priorities के बारे में जानने के बाद Performance debugging कहीं ज़्यादा समझ में आती है।** जब आप React DevTools का profiler खोलते हैं — या अब, Chrome DevTools के Performance Tracks [12] — और देखते हैं कि renders interrupt या defer हो रहे हैं, तो यह कोई bug नहीं है। यह scheduler ठीक वही कर रहा है जिसके लिए उसे design किया गया है।
- **`useTransition` और `useDeferredValue` तभी समझ में आते हैं जब आपको पता हो कि React का render phase interruptible है।** Fiber के बिना, इनमें से कोई भी hook मौजूद नहीं हो सकता था — "interrupt" करने के लिए कुछ होता ही नहीं।

इस पूरे arc को पीछे मुड़कर देखने पर मुझे जो बात सबसे ज़्यादा चौंकाती है, वह यह है कि इसमें से ज़्यादातर हिस्सा design से ही invisible है। आप ऐसा कोई code नहीं लिखते जो कहे "use Fiber"। आप explicitly "lanes" को invoke नहीं करते। इस दशक-भर लंबे rewrite का पूरा मकसद यही था कि React, developers से scheduling के बारे में सोचने को कहे बिना ही *तेज़* महसूस हो — और ज़्यादातर मामलों में, यह कामयाब रहा। जो चीज़ें पहले careful manual batching की मांग करती थीं (`unstable_batchedUpdates`, debounced inputs, manual `shouldComponentUpdate` checks), वे अब हर release के साथ बढ़ते-बढ़ते बस... अपने-आप काम करने लगी हैं।

शायद React Compiler के और mature होने के साथ, अगला "दशक-भर लंबा arc" manual memoization को हटाने के बारे में होगा, उसी तरह जैसे React 18 ने manual batching को हटाया था। देखते हैं।

## स्रोत

1. [React v18.0 – React Blog](https://react.dev/blog/2022/03/29/react-v18)
2. [React 16: हमारी frontend UI library के rewrite की एक झलक – Meta Engineering](https://engineering.fb.com/2017/09/26/web/react-16-a-look-inside-an-api-compatible-rewrite-of-our-frontend-ui-library/)
3. [React Fiber Architecture – acdlite/react-fiber-architecture (GitHub)](https://github.com/acdlite/react-fiber-architecture)
4. [Inside Fiber: React के नए reconciliation algorithm का in-depth overview – AG Grid Blog](https://blog.ag-grid.com/inside-fiber-an-in-depth-overview-of-the-new-reconciliation-algorithm-in-react/)
5. [ReactJS Reconciliation – GeeksforGeeks](https://www.geeksforgeeks.org/reactjs/reactjs-reconciliation/)
6. [क्या आप React में unstable_batchedUpdates के बारे में जानते हैं? – DEV Community](https://dev.to/devmoustafa97/do-you-know-unstablebatchedupdates-in-react-enforce-batching-state-update-5cn2)
7. [React 18 में automatic batching जुड़ी – Saeloun Blog](https://blog.saeloun.com/2021/07/22/react-automatic-batching/)
8. [React 18 में Automatic Batching क्या है – GeeksforGeeks](https://www.geeksforgeeks.org/reactjs/what-is-automatic-batching-in-react-18/)
9. [React 18 में Concurrent Rendering और Lane Prioritization – Jim's Blog](https://j1032w.github.io/blog/concurrent-rendering-and-update-priority-in-react18)
10. [useTransition – React Reference Documentation](https://react.dev/reference/react/useTransition)
11. [React 19 – React Blog](https://react.dev/blog/2024/12/05/react-19)
12. [React 19.2 – React Blog](https://react.dev/blog/2025/10/01/react-19-2)
13. [React Compiler v1.0 – React Blog](https://react.dev/blog/2025/10/07/react-compiler-1)
14. [packages/scheduler/src/forks/Scheduler.js – facebook/react (GitHub)](https://github.com/facebook/react/blob/e62a8d754548a490c2a3bcff3b420e5eedaf11c0/packages/scheduler/src/forks/Scheduler.js)