+++
title       = "React प्रत्यक्षात कसं काम करतं: Fiber आणि Batch Rendering समजून घेऊ"
description = "React तुमचं UI कसं render करतं, React Fiber म्हणजे नेमकं काय, आणि चांगल्या performance साठी automatic batching React 16 पासून React 19.2 पर्यंत कशी evolve झाली — याचा सखोल आढावा."
date        = "2026-06-13T17:37:28+05:30"
slug          = "how-react-works-fiber-and-batch-rendering-explained"
tags          = ["react", "javascript", "web-performance", "frontend"]
keywords      = ["react fiber", "react batching", "automatic batching react 18", "react reconciliation", "react rendering process", "react 19 performance"]
canonical     = "/mr/posts/how-react-works-fiber-and-batch-rendering-explained/"
feature_image = "/images/POST-1056-how-react-works-fiber-and-batch-rendering-explained.svg"
+++

तुम्ही कधी React app मध्ये एखादं button क्लिक केलं आहे आणि फक्त... विश्वास ठेवला आहे की UI बरोबर update होईल? हो, मीही, वर्षानुवर्षे. `setState` आणि स्क्रीनवर pixels बदलणे यांच्यामध्ये नक्की काय घडतं याचा मी कधी विचारच केला नाही — जोपर्यंत मी असा एक component debug करायला लागलो जो एका क्लिकवर पाच वेळा re-render होत होता. त्या rabbit hole मुळे मी सरळ Fiber, lanes, आणि React तुमचं app *कधी* re-render करायचं हे कसं ठरवतं याच्या आश्चर्यकारकरित्या मोठ्या history मध्ये पोहोचलो.

हा लेख म्हणजे तोच rabbit hole, व्यवस्थित मांडलेला. आपण बघू की React आतून प्रत्यक्षात कसं काम करतं, React Fiber म्हणजे काय आणि ते का अस्तित्वात आहे, आणि नंतर batching — जे तुमचा component किती वेळा re-render होतो हे ठरवतं — ते प्रत्येक release नंतर कसं बदलत गेलं आहे ते पाहू.

## setState कॉल केल्यावर प्रत्यक्षात काय घडतं?

जवळजवळ कोणीच स्पष्टपणे सांगत नाही ती गोष्ट ही आहे: `setState` (किंवा `useState` मधून मिळणारा state setter) कॉल केल्याने स्क्रीनवर लगेच काहीही बदलत नाही. हे फक्त React ला सांगतं, "अरे, काहीतरी बदललं आहे, तू पुन्हा एकदा हे बघावं."

त्यानंतर एक multi-step प्रोसेस सुरू होते:

1. **Trigger** — काहीतरी घडतं (एक event, network response, किंवा timer) जे एखादा state setter कॉल करतं.
2. **Render** — नवीन UI *कसं* दिसायला हवं हे शोधण्यासाठी React तुमची component functions पुन्हा कॉल करतं. यातून React elements चं एक tree तयार होतं (ज्याला अनेकदा सर्वसाधारणपणे "virtual DOM" म्हटलं जातं).
3. **Reconciliation** — React नवीन tree ची आधीच्या tree शी तुलना करतं आणि किमान कोणते बदल आवश्यक आहेत हे शोधतं.
4. **Commit** — React हे बदल खऱ्या DOM वर लागू करतं, effects चालवतं, आणि browser निकाल paint करतो.

"virtual DOM" हा शब्द खूप वापरला जातो, आणि खरं सांगायचं तर आता हे नाव थोडं चुकीचं वाटतं. React सध्या आतून जे प्रत्यक्षात maintain करतं ते **Fiber nodes** चं एक tree आहे — जे DOM च्या साध्या snapshot पेक्षा खूप जास्त rich structure आहे. आपण याकडे थोड्याच वेळात येऊ, कारण हाच या संपूर्ण लेखाचा गाभा आहे.

## Reconciliation: React ची Diffing Trick

Fiber चा विचार सुरू करण्याआधी, React DOM efficiently update करू शकतं ते *का* हे समजून घेणं उपयुक्त आहे. दोन arbitrary trees ची node-by-node तुलना करणे, computer science च्या दृष्टीने, एक costly समस्या आहे — naive tree diffing साधारणपणे n nodes साठी O(n³) इतकी असते. प्रत्येक keystroke वर चालणाऱ्या UI library साठी हे खूपच slow आहे.

त्यामुळे React काही simplifying assumptions सह heuristic-based algorithm वापरतं [5]:

- **वेगवेगळे element types वेगवेगळे trees तयार करतात.** जर `<div>` `<span>` बनला, तर React त्यांच्या children ला diff करण्याच्या भानगडीत पडत नाही — ते फक्त जुना भाग पाडून नवीन भाग सुरुवातीपासून तयार करतं.
- **तोच element type, तीच position?** React underlying DOM node तसाच ठेवतं आणि फक्त बदललेले attributes/props update करतं.
- **Lists ला keys लागतात.** जेव्हा तुम्ही `.map()` वापरून एक list render करता, तेव्हा React renders मध्ये items जुळवण्यासाठी `key` prop वापरतं. stable keys नसतील (किंवा त्याहूनही वाईट, जेव्हा list reorder होऊ शकते तेव्हा array index ला key म्हणून वापरलं तर), React गोंधळून जाऊ शकतं की कोणता item कोणता आहे — ज्यामुळे reorder नंतर form inputs मध्ये चुकीची value राहणे यासारखे विचित्र bugs येतात.

[React च्या reconciliation process](https://www.geeksforgeeks.org/reactjs/reactjs-reconciliation/) चा हाच भाग आहे जो बहुतेक tutorials मध्ये कव्हर केला जातो [5]. पण reconciliation स्वतःहून हे सांगत नाही की मोठ्या update वर React browser ला freeze न करता हे सगळं काम *कसं* करतं. इथेच Fiber येतं — आणि ही बाब बहुतेकांना वाटते त्यापेक्षा खूप मोठी आहे.

## Fiber चं आगमन: सर्वकाही बदलून टाकणारा Rewrite

React 16 च्या आधी, React जे वापरत होतं त्याला आता **"stack reconciler"** म्हणतात. ते काम तर करत होतं, पण त्यात एक मूलभूत समस्या होती: ते recursive आणि synchronous होतं. एकदा React एखादं tree render करायला सुरुवात केली, की ते पूर्ण होईपर्यंत थांबू शकत नसे — संपूर्ण tree process होईपर्यंत JavaScript call stack फक्त वाढतच जात असे [3][4].

छोट्या apps साठी हे ठीक आहे. तुम्हाला फरक कधीच जाणवणार नाही. पण मोठ्या component trees साठी — हजारो rows असलेला data grid, किंवा एक complex dashboard — तो synchronous render main thread ला दहा-दहा milliseconds इतका वेळ block करू शकत होता. Animations अडखळायच्या, scrolling मध्ये jank यायचा, आणि कुठल्या input मध्ये टाइप करणं सुस्त वाटायचं, कारण जोपर्यंत React आपलं काम पूर्ण करत नाही तोपर्यंत browser दुसरं काहीही process करू शकत नसे.

सप्टेंबर 2017 मध्ये, React 16 या core algorithm च्या संपूर्ण rewrite सह आलं, ज्याला **Fiber** म्हटलं गेलं [2]. Meta च्या engineering team ने याला "API-compatible rewrite" असं वर्णन केलं — म्हणजे तुमच्या component code मध्ये बदल करण्याची गरज नव्हती, पण त्याखाली घडणारं सगळं काही बदललं [2].

### Fiber म्हणजे प्रत्यक्षात काय?

मी पाहिलेलं सर्वात स्पष्ट वर्णन (React core contributor Andrew Clark च्या स्वतःच्या notes मधून) हे आहे की **fiber हा एक "virtual stack frame"** आहे [3]. JavaScript call stack वर अवलंबून राहण्याऐवजी — जो न थांबता top पासून bottom पर्यंत execute होतो — React आपली स्वतःची data structure तयार करतं जी stack सारखी वागते, पण ज्यावर React चं पूर्ण नियंत्रण असतं.

प्रत्येक fiber हा एक plain JavaScript object असतो जो work च्या एका unit ला represent करतो — मुळात एक component — आणि त्यात असतं:

- **type आणि key** — हे कोणत्या प्रकारचं component किंवा DOM element आहे ते सांगतात
- **child, sibling, आणि return pointers** — जे tree चं linked-list representation तयार करतात (typical nested-array tree च्या ऐवजी)
- **pendingProps आणि memoizedProps** — येणारे नवीन props विरुद्ध मागच्या वेळचे props, काही प्रत्यक्षात बदललं आहे का हे तपासण्यासाठी वापरले जातात
- **alternate** — या fiber च्या "दुसऱ्या version" कडे जाणारा pointer (याबद्दल थोड्याच वेळात अधिक)

खरं सांगायचं तर तो **alternate** pointer हाच सर्वात clever भाग आहे. React एकाच वेळी memory मध्ये दोन trees ठेवतं: **current tree** (जे आत्ता प्रत्यक्षात स्क्रीनवर आहे) आणि **workInProgress tree** (जे React सध्या पुढच्या update साठी तयार करत आहे) [4]. work-in-progress tree पूर्ण झाल्यावर, React फक्त एक pointer swap करतं — work-in-progress हे current tree बनतं. याला कधीकधी "double buffering" म्हणतात, आणि अर्धवट काढलेले frames दाखवणं टाळण्यासाठी video games हीच trick वापरतात.

प्रत्येक fiber ही स्वतःची एक छोटी work unit असल्यामुळे, React tree ला node-by-node process करू शकतं, आणि प्रत्येक node पूर्ण केल्यानंतर, **थांबून विचारू शकतं: "मला पुढे सुरू ठेवायला वेळ आहे का, की मी control browser ला परत द्यायला हवा?"** [3][4]. हीच एक क्षमता — pause करणे, yield करणे, आणि resume करणे — बाकी सगळं (concurrent rendering, transitions, automatic batching) शक्य करते.

### Render Phase विरुद्ध Commit Phase

React हे सगळं काम अगदी वेगळ्या नियमांच्या दोन phases मध्ये विभागतं:

- **Render phase** — React workInProgress tree वरून जातं, तुमची components कॉल करतं, आणि काय बदललं आहे ते शोधतं. हा phase **pure** आहे (कोणतेही DOM mutations नाहीत, कोणतेही side effects नाहीत) आणि **interruptible** आहे — जर अधिक urgent update आलं, तर React हा phase pause करू शकतं, केलेलं काम टाकून देऊ शकतं, किंवा पुन्हा सुरू करू शकतं [3][4].
- **Commit phase** — React पूर्ण झालेलं काम घेतं आणि प्रत्यक्ष DOM mutate करतं, layout effects चालवतं, आणि refs update करतं. हा phase **synchronous** आहे आणि **interrupt केला जाऊ शकत नाही** — एकदा सुरू झाल्यावर, तो पूर्ण होऊनच थांबतो, जेणेकरून user ला कधीही अर्धवट update झालेलं UI दिसणार नाही [1][4].

![react render commit pipeline](/images/posts/how-react-works-fiber-and-batch-rendering-explained/react-render-commit-pipeline.svg)

## Scheduler: प्रत्येक Update ला Priority देणे

एकदा Fiber ने interruptible rendering शक्य केल्यावर, React ला *काय* interrupt होईल आणि *काय* priority मिळेल हे ठरवण्याचा एक मार्ग हवा होता. हे काम [scheduler](https://github.com/facebook/react/blob/main/packages/scheduler/src/forks/Scheduler.js) चं आहे — एक वेगळं package जे React त्याच्या core सोबत ship करतं [14].

Scheduler priority levels define करतं, प्रत्येकाला एक internal timeout असतो जो ठरवतो की एखादं काम किती वेळ पुढे ढकलता येतं, त्याआधी React ते जबरदस्तीने पूर्ण करतं [14]:

| Priority | Timeout | उदाहरण वापर |
|---|---|---|
| Immediate | -1ms (आत्ता) | Synchronous, critical updates |
| User-blocking | 250ms | टाइप करणे, क्लिक करणे, drag करणे |
| Normal | 5,000ms | Data fetch चे results, non-urgent updates |
| Low | 10,000ms | Analytics, background sync |
| Idle | जवळजवळ कधीच नाही | Offscreen content, hidden tabs |

React 18 मध्ये, हा priority system **lanes** मुळे आणखी granular झाला — एक bitmask-based model ज्यात updates ला assign करण्यासाठी 31 पर्यंत वेगळ्या priority "lanes" असू शकतात [9]. याचा practical परिणाम असा: जर तुम्ही एक मोठं, low-priority update render करत असाल (समजा, एक खूप मोठी list filter करणे) आणि user एका button वर क्लिक करतो, तर React **त्या low-priority render ला pause करू शकतं, क्लिक लगेच handle करू शकतं, आणि नंतर filtering चं काम पुन्हा सुरू करू शकतं** [9]. Fiber च्या आधी, हे architecturally शक्यच नव्हतं — एकदा React render करायला सुरुवात केली की ते थांबू शकत नसे.

हीच `useTransition` आणि `useDeferredValue` ची देखील foundation आहे, ज्यांबद्दल आपण लवकरच बघू. हे मुळात developer साठीचे असे levers आहेत ज्यातून सांगता येतं, "कृपया या specific update ला low priority म्हणून treat करा" [10].

## Batching: 10 वर्षं लागलेला एक शांत Optimization

ठीक आहे, इथून खरंच गोष्टी रंजक होतात — आणि इथेच बहुतेक लेख एकतर खूप सोपं करून सांगतात किंवा history पूर्णपणे वगळतात. **Batching** ही React ची अशी strategy आहे ज्यात अनेक state updates एकत्र group केले जातात, जेणेकरून ते अनेक वेळा ऐवजी *एकच* re-render trigger करतील. ऐकायला हे सोपं वाटतं. पण याची implementation जवळपास प्रत्येक major React release मध्ये शांतपणे evolve होत आली आहे.

### React 18 च्या आधी: Batching फक्त Event Handlers च्या आत काम करत होती

अनेक वर्षं, React ची batching त्याच्या synthetic event system शी जोडलेली होती. जर तुम्ही एका React event handler (`onClick`, `onChange`, इत्यादी) च्या आत अनेक state setters कॉल केले, तर React ते एका single re-render मध्ये batch करत होतं. पण त्या context च्या बाहेर गेलं की — एखाद्या `setTimeout`, `Promise.then()`, किंवा raw `addEventListener` मध्ये — **batching पूर्णपणे काम करणं थांबवत असे** [1][7].

```js
// React 17 and earlier
function handleClick() {
  setTimeout(() => {
    setCount(c => c + 1); // triggers a re-render
    setFlag(f => !f);     // triggers ANOTHER re-render
  }, 1000);
}
```

conceptually एका logical update साठी हे दोन पूर्ण render-and-commit cycles आहेत. दोन `setState` calls साठी ही फार मोठी गोष्ट नाही, पण मी असे real apps पाहिले आहेत जिथे एक single async callback सहा किंवा सात state updates fire करत होता — आणि प्रत्येक वेळी एक moderately heavy component tree re-render होत होता. हे जमा होत जातं.

या limitation मुळेच `unstable_batchedUpdates` अस्तित्वात होतं. हे `react-dom` मधून export होणारं एक undocumented API होतं (म्हणूनच तो भीतीदायक `unstable_` prefix), जो एखाद्या callback ला manually React च्या batching context मध्ये wrap करत असे [6]:

```js
import { unstable_batchedUpdates } from 'react-dom';

setTimeout(() => {
  unstable_batchedUpdates(() => {
    setCount(c => c + 1);
    setFlag(f => !f);
  }); // now only ONE re-render
}, 1000);
```

जर तुम्ही कधी Redux, MobX, किंवा Zustand वापरलं असेल, तर तुम्हाला याचा फायदा माहीत नसतानाच मिळाला आहे — या libraries नी "external state मुळे अनेक renders" ही समस्या टाळण्यासाठी विशेषतः त्यांच्या store update notifications ला `unstable_batchedUpdates` मध्ये wrap केलं होतं [6]. हे एक असं workaround होतं जे ecosystem च्या निम्म्या भागात बेक झालेलं होतं, कारण framework स्वतः हे consistently करू शकत नव्हतं.

### React 18: सगळीकडे Automatic Batching

React 18 (मार्च 2022 मध्ये release झालं) ने अखेर हे मूळापासून ठीक केलं [1]. नवीन `createRoot` API सोबत, **प्रत्येक state update by default batch होतो, तो कुठूनही आला तरी** — timeouts, promises, native event listeners, काहीही [1][8].

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

काही महत्त्वाच्या गोष्टी ज्यात लोक अनेकदा गोंधळतात:

- **तुम्हाला `createRoot` द्वारे opt in करावं लागतं.** जर तुमचं app अजूनही legacy `ReactDOM.render()` कॉल करत असेल, तर तुम्हाला automatic batching मिळणार नाही — React backward compatibility साठी जुना behavior ठेवतं [1].
- **`unstable_batchedUpdates` एक no-op बनतं.** कारण आता सगळं automatically batch होतं, त्यामुळे ते जुनं API आता... काही विशेष करत नाही [6][7].
- **तुम्ही अजूनही यातून *बाहेर* जाऊ शकता**, `react-dom` मधल्या `flushSync` चा वापर करून, अशा rare cases साठी जिथे तुम्हाला पुढची line of code चालण्याआधी खरंच DOM synchronously update झालेलं हवं असतं (उदाहरणार्थ, state change नंतर लगेच layout मोजणे):

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

खरं सांगायचं तर — React लिहिण्याच्या या वर्षांमध्ये, मी `flushSync` कदाचित दोनच वेळा वापरलं आहे, दोन्ही वेळा state-driven layout change नंतर लगेच DOM nodes मोजण्यासाठी. हे एक खरं escape hatch आहे, पण जर तुम्ही ते वारंवार वापरत असाल, तर साधारणपणे याचा अर्थ असा होतो की तुमच्या architecture मधल्या आणखी कशाचा तरी पुनर्विचार करायची गरज आहे.

### React 18 चे Concurrent Features: Transitions आणि Deferred Values

Automatic batching renders ची *संख्या* कमी करते. पण React 18 ने renders ची *priority* नियंत्रित करण्यासाठीही tools आणली — जी एक related पण वेगळी optimization आहे [1].

- **`startTransition` / `useTransition`** — यामुळे तुम्ही एखादं state update "non-urgent" म्हणून मार्क करू शकता. React ते background मध्ये render करेल आणि जर काहीतरी अधिक urgent (जसे की एखादा keystroke) आलं, तर ते interrupt करू शकेल [1][10].
- **`useDeferredValue`** — एक value घेतं आणि तुम्हाला त्याची अशी एक आवृत्ती परत देतं जी urgent renders दरम्यान "मागे राहते", जे debouncing सारखंच आहे पण कोणत्याही arbitrary timer शिवाय [1].

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

batching पासूनचा फरक subtle पण महत्त्वाचा आहे: batching म्हणजे updates एकत्र *जोडून* कमी renders मध्ये बदलणे, तर transitions म्हणजे एखाद्या render ला *deprioritize* करणे जेणेकरून तो अधिक urgent renders ला block करणार नाही [9][10]. दोन्ही अखेरीस अस्तित्वात आहेत कारण सर्वप्रथम Fiber ने rendering ला interruptible बनवलं — त्या मूलभूत rewrite शिवाय, यातलं काहीही शक्य नसतं.

### React 19 आणि 19.2: Actions, Compiler, आणि SSR Batching

React 19 (डिसेंबर 2024) ने batching मध्ये React 18 सारखा मोठा बदल केला नाही, पण ते त्याच foundation वर पुढे बांधत राहिलं [11]:

- **Actions API** (`useActionState`, `useFormStatus`, `useOptimistic`) — यामुळे तुम्ही async functions थेट `<form action={...}>` ला pass करू शकता. आतून, React pending state automatically manage करतं, त्यातून निर्माण होणारे updates batch करतं, आणि यश मिळाल्यावर form reset करतं — आणि यासाठी तुम्हाला manually loading flags track करण्याची गरज नसते [11].

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

- **React Compiler** — हे rendering performance साठी एकंदरीत एक मोठी गोष्ट आहे, जरी ती strictly "batching" नसली तरी. ऑक्टोबर 2025 मध्ये हे version 1.0 पर्यंत पोहोचलं [13]. हा compiler build time वर चालतो आणि automatically memoization टाकतो — जी optimization तुम्ही आधी `useMemo`, `useCallback`, आणि `React.memo` वापरून hand-write करत होता — ज्यामुळे components चे inputs प्रत्यक्षात बदलले नसतील तेव्हा ते re-render होणं skip करतात [13]. हे Meta मध्ये production मध्ये चालू आहे, आणि React team ने Vite, Next.js, आणि Expo सोबत partnership केली आहे जेणेकरून नवीन projects हे by default चालू करू शकतील [13]. खरं सांगायचं तर, Fiber ने जे काही सुरू केलं त्याचा हा नैसर्गिक अंत वाटतो: सर्वप्रथम rendering ला interruptible आणि schedulable बनवा, नंतर ते efficiently batch करा, आणि अखेरीस — गरज नसलेलं काम पूर्णपणे skip करा.

- **React 19.2** (ऑक्टोबर 2025) ने batching ला server rendering मध्येही वाढवलं. Streaming SSR दरम्यान, **Suspense boundary reveals आता थोड्या window साठी batch होतात**, जेणेकरून जवळपास एकाच वेळी resolve होणारे अनेक boundaries एक-एक करून पाठवण्याऐवजी client ला एकत्र पाठवले जाऊ शकतील — जे client कसा behave करतो याच्याशीही अधिक चांगलं जुळतं [12]. या release मध्ये नवीन `<Activity />` component (state टिकवून ठेवताना UI hide/restore करण्यासाठी), `useEffectEvent`, आणि "Performance Tracks" देखील आलं — एक Chrome DevTools integration जे scheduler च्या priority decisions ला थेट Performance panel मध्ये visualize करतं [12].

## सगळं एकत्र: Evolution एका दृष्टीक्षेपात

| Version | वर्ष | Rendering/Batching साठी काय बदललं |
|---|---|---|
| ≤ React 15 | — | Stack reconciler — synchronous, non-interruptible recursion [3][4] |
| React 16 | 2017 | Fiber rewrite — interruptible render phase, double-buffered tree, priority-aware scheduling [2][3] |
| React 16–17 | 2017–2020 | Batching फक्त React event handlers च्या आत; manual workaround म्हणून `unstable_batchedUpdates` [6][7] |
| React 18 | 2022 | सगळीकडे automatic batching (`createRoot` द्वारे), `flushSync` opt-out, lanes-based concurrent rendering, `useTransition`/`useDeferredValue` [1][9] |
| React 19 | 2024 | Actions API async updates च्या आसपास pending/optimistic state auto-manage करते [11] |
| React 19.2 | 2025 | SSR मध्ये Suspense boundary reveals batch होतात; `<Activity />`, scheduler priorities visualize करण्यासाठी Performance Tracks [12] |
| React Compiler 1.0 | 2025 | Build-time automatic memoization — manual `useMemo`/`useCallback` शिवाय re-renders skip करते [13] |

![react batching before after](/images/posts/how-react-works-fiber-and-batch-rendering-explained/react-batching-before-after.svg)

## हे सगळं तुमच्यासाठी का महत्त्वाचं आहे

जर तुम्ही फक्त forms आणि dashboards बनवत असाल, तर तुम्ही विचार करत असाल, "ठीक आहे, पण मला कधीच `flushSync` किंवा `unstable_batchedUpdates` ची *गरज* पडली नाही, तर हे का महत्त्वाचं आहे?"

बरोबर आहे. पण practice मध्ये ही गोष्ट लोकांना नेमकं इथे त्रास देते:

- **"हे दोनदा का render झालं?"** हे debug करणे प्रत्येक React developer साठी एक rite of passage आहे, आणि याचं उत्तर जवळजवळ नेहमी batching behavior मध्येच असतं — development मध्ये Strict Mode मुळे effects चं double-invoke होणे, किंवा batched context च्या बाहेर होणारं update.
- **`ReactDOM.render()` वरून `createRoot` कडे migrate करणे** हे फक्त एक version bump नाही — यामुळे तुमचं app updates कसे batch करतं हे शांतपणे बदलतं. जर तुमचं app कुठेतरी synchronous re-renders वर अवलंबून असेल (मुद्दाम किंवा अनवधानाने), तर automatic batching त्या assumptions ला उघड करू शकते.
- **lanes आणि priorities बद्दल माहीत असल्यावर Performance debugging खूप जास्त समजायला लागतं.** जेव्हा तुम्ही React DevTools चं profiler उघडता — किंवा आता, Chrome DevTools मधील Performance Tracks [12] — आणि renders interrupt किंवा defer होताना दिसतात, तेव्हा ते bug नाही. ते scheduler नेमकं तेच करत आहे ज्यासाठी ते design केलं गेलं आहे.
- **`useTransition` आणि `useDeferredValue` तेव्हाच अर्थपूर्ण वाटतात जेव्हा तुम्हाला कळतं की React चा render phase interruptible आहे.** Fiber शिवाय, हे दोन्ही hooks अस्तित्वातच असू शकले नसते — "interrupt" करण्यासाठी काहीच नसतं.

या संपूर्ण arc कडे मागे वळून पाहताना मला सर्वात जास्त जे जाणवतं ते हे की यातलं बरंच काही design नेच invisible आहे. तुम्ही असा कोणताही code लिहीत नाही जो म्हणतो "use Fiber." तुम्ही explicitly "lanes" invoke करत नाही. या दशकभर चाललेल्या rewrite चा संपूर्ण उद्देश हाच होता की React ला developers ला scheduling बद्दल विचारच न करायला लावता *जलद* वाटावं — आणि बहुतांश बाबतीत, हे यशस्वी झालं. ज्या गोष्टींना आधी काळजीपूर्वक manual batching लागत असे (`unstable_batchedUpdates`, debounced inputs, manual `shouldComponentUpdate` checks), त्या आता प्रत्येक release नंतर वाढत्या प्रमाणात फक्त... स्वतःहून, automatically काम करतात.

कदाचित React Compiler आणखी mature झाल्यावर, पुढचा "दशकभराचा arc" manual memoization काढून टाकण्याबद्दल असेल, ज्याप्रमाणे React 18 ने manual batching काढून टाकलं. बघू.

## स्रोत

1. [React v18.0 – React Blog](https://react.dev/blog/2022/03/29/react-v18)
2. [React 16: आमच्या frontend UI library च्या rewrite ची एक झलक – Meta Engineering](https://engineering.fb.com/2017/09/26/web/react-16-a-look-inside-an-api-compatible-rewrite-of-our-frontend-ui-library/)
3. [React Fiber Architecture – acdlite/react-fiber-architecture (GitHub)](https://github.com/acdlite/react-fiber-architecture)
4. [Inside Fiber: React च्या नवीन reconciliation algorithm चा in-depth overview – AG Grid Blog](https://blog.ag-grid.com/inside-fiber-an-in-depth-overview-of-the-new-reconciliation-algorithm-in-react/)
5. [ReactJS Reconciliation – GeeksforGeeks](https://www.geeksforgeeks.org/reactjs/reactjs-reconciliation/)
6. [तुम्हाला React मधील unstable_batchedUpdates बद्दल माहिती आहे का? – DEV Community](https://dev.to/devmoustafa97/do-you-know-unstablebatchedupdates-in-react-enforce-batching-state-update-5cn2)
7. [React 18 मध्ये automatic batching जोडली – Saeloun Blog](https://blog.saeloun.com/2021/07/22/react-automatic-batching/)
8. [React 18 मध्ये Automatic Batching म्हणजे काय – GeeksforGeeks](https://www.geeksforgeeks.org/reactjs/what-is-automatic-batching-in-react-18/)
9. [React 18 मधील Concurrent Rendering आणि Lane Prioritization – Jim's Blog](https://j1032w.github.io/blog/concurrent-rendering-and-update-priority-in-react18)
10. [useTransition – React Reference Documentation](https://react.dev/reference/react/useTransition)
11. [React 19 – React Blog](https://react.dev/blog/2024/12/05/react-19)
12. [React 19.2 – React Blog](https://react.dev/blog/2025/10/01/react-19-2)
13. [React Compiler v1.0 – React Blog](https://react.dev/blog/2025/10/07/react-compiler-1)
14. [packages/scheduler/src/forks/Scheduler.js – facebook/react (GitHub)](https://github.com/facebook/react/blob/e62a8d754548a490c2a3bcff3b420e5eedaf11c0/packages/scheduler/src/forks/Scheduler.js)