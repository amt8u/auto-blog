+++
title       = "Chrome DevTools Memory Tab: एक व्यावहारिक मार्गदर्शिका"
description = "Heap Snapshot, Allocation Sampling, Allocations on Timeline, Detached Elements — प्रत्येक टूल नक्की काय करतो आणि कधी वापरायचा ते शिका."
date        = "2026-06-09T15:06:38+05:30"
slug          = "chrome-devtools-memory-tab-guide"
tags          = ["devtools", "javascript", "performance", "debugging", "memory"]
keywords      = ["Chrome DevTools Memory tab", "heap snapshot", "allocation sampling", "allocations on timeline", "detached elements", "JavaScript memory leak debugging", "memory profiling"]
canonical     = "/mr/posts/chrome-devtools-memory-tab-guide/"
feature_image = "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200"
+++

तुमची अ‍ॅप कालांतराने हळू होत आहे. स्क्रोल पोझिशन उडी घेते. टॅब्स ८०० MB RAM वापरत आहेत. तुम्ही Task Manager उघडता आणि Chrome ला मेमरी बफे दिवसासारखी खाताना पाहता. काहीतरी leak होत आहे — पण कुठे? Chrome DevTools Memory tab समोरच आहे, आणि बहुतेक डेव्हलपर्स एकतर ते दुर्लक्षित करतात किंवा एकदा उघडतात, "Shallow Size" आणि "Retainers" पाहून गोंधळतात, आणि शांतपणे बंद करतात. हे मार्गदर्शक त्यांच्यासाठी आहे जे ते खरोखरच वापरायला शिकू इच्छितात.

## JavaScript मध्ये Memory Leaks इतके लपलेले का असतात

JavaScript garbage collected आहे. V8 — Chrome चे JavaScript engine — एखादी object यापुढे reachable नाही असे ठरवल्यावर आपोआप मेमरी मोकळी करते [1]. algorithm तत्त्वतः सोपा आहे: जर कुठलीही गोष्ट एखाद्या object चा reference ठेवत नसेल, तर ती collect केली जाऊ शकते.

समस्या काय? **JavaScript मध्ये references चुकीने जिवंत ठेवणे खूप सोपे आहे.** एक event listener. एक closure ज्याने एक variable capture केला. एक detached DOM node जो अजूनही एका global array ने point केला जात आहे. garbage collector येथे तुम्हाला मदत करू शकत नाही — objects *reachable* आहेत, फक्त हेतुपूर्वक नाहीत. [JavaScript मधील Memory management](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management) तांत्रिकदृष्ट्या "automatic" आहे, परंतु याचा अर्थ leak-free नाही [1].

JavaScript memory leaks च्या बहुतांश प्रकरणांसाठी तीन patterns जबाबदार आहेत [2]:

- **विसरलेले event listeners** — तुम्ही DOM मधून एखादा element काढता पण `removeEventListener` कधीच बोलावत नाही. listener (आणि त्याच्या closure मधील सर्व काही) जिवंत राहतो.
- **मोठ्या objects ठेवणारे Closures** — एक function जे एका मोठ्या variable वर closed, जिवंत ठेवले कारण एखादी event किंवा timer अजूनही त्या function चा reference ठेवते.
- **Detached DOM nodes** — page मधून काढलेले elements पण अजूनही कुठेतरी एखाद्या JavaScript object ने referenced.

Memory tab मध्ये चार वेगळी tools आहेत. प्रत्येक एक वेगळ्या प्रकारची समस्या शोधण्यासाठी optimize केलेले आहे. चुकीचे उघडणे तुमचा वेळ वाया घालवते.

## Memory Tab: एक नाही, चार Tools

DevTools → Memory उघडा. तुम्हाला चार radio buttons दिसतील [3]:

1. **Heap snapshot** — heap वरील सर्व गोष्टींचा एक वेळचा फोटो
2. **Allocation instrumentation on timeline** — वेळेनुसार *होताना* allocations नोंदवते
3. **Allocation sampling** — वरीलचे एक lightweight, statistical version
4. **Detached elements** — orphaned पण अजूनही referenced असलेले DOM nodes सूचीबद्ध करते

प्रत्येक एक वेगळा प्रश्न उत्तर देतो. आपण खोलवर जाण्यापूर्वी येथे एक जलद निर्णय matrix आहे:

| Tool | सर्वोत्तम | Overhead | कालावधी |
|---|---|---|---|
| Heap Snapshot | "आत्ता काय जिवंत आहे?" | जास्त (GC थांबवते) | तात्काळ |
| Allocations on Timeline | "काय allocate झाले आणि कधीच मोकळे झाले नाही?" | मध्यम | लहान session |
| Allocation Sampling | "कोणते functions सर्वाधिक allocate करतात?" | **कमी** | दीर्घ sessions |
| Detached Elements | "कोणते काढलेले DOM nodes अजूनही ठेवले आहेत?" | कमी | तात्काळ |

![memory tab tools overview](/images/posts/chrome-devtools-memory-tab-guide/memory-tab-tools-overview.svg)

## Heap Snapshot

हे बहुतेक लोक आधी वापरतात. हे JavaScript heap चा एका वेळी संपूर्ण snapshot capture करते — प्रत्येक object, प्रत्येक DOM node, प्रत्येक string, प्रत्येक reference [3].

तुम्ही एक घेता, त्याकडे पाहता, आणि जर तुम्ही हे आधी कधीही केले नसेल, तर हजारो constructors आणि numbers पाहून लगेच overwhelmed वाटते. हे सामान्य आहे. खरोखर काय पाहायचे ते येथे आहे.

### Views

snapshot result च्या वरच्या-डाव्या बाजूचा dropdown बदला. तीन views आहेत [4]:

**Summary** — default. heap वर सध्या जिवंत असलेल्या objects तयार करणाऱ्या प्रत्येक constructor function ची यादी करते. महत्त्वाचे columns:
- *Shallow size* — references दुर्लक्षित करून object स्वतः व्यापलेली मेमरी
- *Retained size* — जर हा object (आणि तो एकट्याने जिवंत ठेवत असलेल्या सर्व गोष्टी) garbage collected झाल्यास मोकळी होणारी मेमरी [5]

**Comparison** — काही action केल्यानंतर दुसरा snapshot घ्या, नंतर पहिल्याशी तुलना करा. `# New`, `# Deleted`, `# Delta` दाखवते. हे जिथे leaks स्पष्ट होतात. [heap snapshots ची तुलना करणे](https://devtoolstips.org/tips/en/find-memory-leaks/) leak खरी आहे हे पुष्टी करण्याचा सर्वात विश्वासार्ह मार्ग आहे [6].

**Containment** — `window` आणि closures सारख्या roots पासून सुरू होणाऱ्या object graph चे bird's-eye view. तुम्हाला आधीच एखाद्या specific object बद्दल संशय असल्यास आणि ते नक्की काय जिवंत ठेवत आहे हे trace करायचे असल्यास चांगले [4].

### Shallow vs Retained Size — हा भाग खरोखरच महत्त्वाचा आहे

प्रामाणिकपणे, हे या संपूर्ण panel मधील सर्वात गोंधळात टाकणारी संकल्पना आहे, परंतु एकदा ती समजली की ती सोपी आहे.

**Shallow size** फक्त object स्वतःच आहे. काही properties सह एक plain JS object `{}` shallow मध्ये ६४ bytes असू शकतो. **Retained size** म्हणजे *हा object गेल्यास मोकळे होणारे सर्व काही* [5]. जर त्या plain object ने १०,००० items च्या Array चा reference ठेवला, तर त्याचा retained size ६४ bytes + ती सर्व array memory आहे.

Leaks शोधताना, Shallow ने नाही तर **Retained size** नुसार sort करा. ६४ bytes shallow पण ५० MB retained असलेला object हेच तुम्ही शोधत आहात.

### Heap Snapshots सह Classic Leak-Hunting Workflow

1. Memory tab उघडा, **Heap snapshot** निवडा
2. **Take snapshot** क्लिक करा — हे तुमचे baseline आहे
3. तुम्हाला ज्याबद्दल संशय आहे ती action करा (modal उघडा, route navigate करा, button वारंवार क्लिक करा)
4. उलट करा (modal बंद करा, परत navigate करा)
5. दुसरा snapshot घ्या
6. Snapshot 2 मध्ये, view **Comparison** मध्ये बदला
7. `# Delta` नुसार descending sort करा

जर action उलट केल्यानंतर collect व्हायला हवे असलेले objects (modal चे internal components, route चे views) अजूनही positive delta दाखवत असतील — तुम्हाला तुमची leak सापडली. खाली असलेला `Retainers` section तुम्हाला सांगतो *काय ते ठेवत आहे*.

**Heap Snapshot कधी वापरायचे:** तुम्हाला आधीच माहित आहे की काहीतरी leak होत आहे आणि ते नक्की काय आहे ते ओळखायचे आहे. Before/after विश्लेषणासाठी देखील चांगले — उदा., "हा refactor खरोखरच memory usage कमी करतो का?"

## Allocations on Timeline

Heap snapshots तुम्हाला memory ची *अवस्था* दाखवतात. Allocation Timeline तुम्हाला *कथा* दाखवते — काय allocate झाले, केव्हा, आणि ते टिकले का [7].

तुम्ही Record क्लिक केल्यावर, DevTools तुमच्या session दरम्यान नियमितपणे micro-snapshots घेते (सुमारे दर ५०ms). प्रत्येक allocation एक vertical bar म्हणून दिसते [7]:

- **निळी bar** — येथे allocate केलेले objects तुम्ही recording थांबवल्यावर *अजूनही जिवंत* आहेत
- **राखाडी bar** — येथे allocate केलेले objects नंतर garbage collected झाले ✓

तुम्हाला काळजी असणाऱ्या गोष्टी म्हणजे निळ्या bars ज्या निळ्या नसायला हव्या होत्या. जर तुम्ही एखादे button क्लिक करता, एक action करता, आणि निळ्या bars चा एक cluster दिसतो जो कितीही वेळ थांबला तरी राखाडी होत नाही — ते objects मोकळे होत नाहीत.

### ते कसे वापरायचे

1. **Allocation instrumentation on timeline** निवडा
2. **Start** दाबा
3. संशयास्पद action करा (scroll, click, navigate)
4. Recording थांबवा
5. Timeline मध्ये persistent निळ्या bars पहा
6. त्याखाली Constructor list filter करण्यासाठी कोणत्याही bar वर क्लिक करा — त्या window दरम्यान allocate झालेल्या आणि अजूनही live असलेल्या objects फक्त दाखवते

Heap Snapshot मधील फरक महत्त्वाचा आहे. Timeline तुम्हाला सांगते allocations *कधी* झाले, ज्यामुळे allocation ला specific user interaction शी जोडणे खूप सोपे होते. तुम्ही प्रत्येक वेळी एखादे button क्लिक केल्यावर एक स्पष्ट spike दिसू शकता — तो तुमच्या culprit चा timestamp आहे [8].

**Allocations on Timeline कधी वापरायचे:** तुम्ही *कोणती user interaction* growth कारणीभूत आहे ते isolate करण्याचा प्रयत्न करत आहात. तुम्हाला सर्वसाधारण अर्थाने माहित आहे की काहीतरी leak होत आहे पण कोणती action ते trigger करते हे माहित नाही.

### एक Gotcha

येथे overhead खरा आहे. DevTools effectively दर ५०ms ला heap snapshot घेत आहे [7]. या tool सह १०-मिनिटांचे session record करू नका — तुम्हाला एक मोठे profile मिळेल जे analyze करणे वेदनादायक आहे, आणि recording दरम्यान तुमची app लक्षणीयपणे हळू होईल. Recordings लहान ठेवा आणि तुम्ही investigate करत असलेल्या specific interaction वर focus करा.

## Allocation Sampling

येथे तो आहे जो बहुतेक developers skip करतात, जी एक चूक आहे. Allocation Sampling हे Timeline चे lightweight version आहे — प्रत्येक allocation नोंदवण्याऐवजी ते *statistical sampling* वापरते [3].

Trade-off: **कमी precise, पण जवळपास शून्य overhead.** तुम्ही तुमच्या app च्या performance वर लक्षणीय परिणाम न करता मिनिटे किंवा तास record करू शकता. हे महत्त्वाचे आहे कारण काही memory growth हळूहळू होते — ते visible होण्यापूर्वी २० मिनिटे वापर लागतो. Timeline त्यासाठी unusable असेल. Allocation Sampling त्यासाठी designed आहे.

### ते काय दाखवते

Results एक flame chart / call tree सारखे दिसतात. Profile च्या कालावधीत *प्रत्येक function ने* allocate केलेल्या heap memory चे breakdown मिळते, नंतर मोकळे केलेल्या allocations सहित [3]. default view "Heavy (Bottom Up)" आहे — सर्वाधिक memory allocate केलेल्या functions वरच्या बाजूस सूचीबद्ध आहेत.

हे इतर tools पेक्षा वेगळा प्रश्न उत्तर देते: **"काय leak झाले" नाही तर "कोणता code allocation-heavy आहे."** एक function जे २०० MB allocate करते जरी बहुतांश collect झाले तरी performance च्या दृष्टिकोनातून पाहण्यासारखे आहे.

**Allocation Sampling कधी वापरायचे:** दीर्घकालीन profiling sessions जिथे तुम्ही Timeline चा overhead afford करू शकत नाही. जेव्हा तुम्हाला समजायचे असते कोणते functions सर्वाधिक allocators आहेत (necessarily leaking नाही, फक्त expensive). जेव्हा तुम्ही leak hunting ऐवजी memory optimization करत आहात.

## Detached Elements

हे इतरांपेक्षा अधिक targeted आहे. Whole heap दाखवण्याऐवजी, हे specifically **DOM nodes शोधते जे page च्या DOM tree मधून काढले गेले आहेत पण अजूनही JavaScript ने referenced आहेत** [9].

हे का महत्त्वाचे आहे? जेव्हा तुम्ही `element.remove()` बोलावता किंवा `innerHTML` clear करता, तेव्हा तुम्हाला वाटते ते nodes garbage collected होतील. परंतु जर कोणताही JS variable, array, closure, किंवा event handler अजूनही त्या element चा reference ठेवत असेल, तर V8 ते collect करू शकत नाही [2]. node "detached" आहे — page मध्ये यापुढे दृश्यमान नाही, पण मेमरीत मात्र जिवंत आहे.

Single-page applications मध्ये हे अत्यंत सामान्य आहे. अशा component framework चा विचार करा जे आधी rendered केलेल्या elements चे cache ठेवते, किंवा एक list जे viewport मधून काढलेल्या rows चे references store करते.

### Detached Elements तयार करणारा Common Code

```javascript
// Classic detached node scenario
let detachedList = [];

function addAndRemove() {
  const el = document.createElement('div');
  document.body.appendChild(el);
  detachedList.push(el);           // reference saved केला
  document.body.removeChild(el);   // DOM मधून काढला
  // el आता detached आहे — detachedList ते जिवंत ठेवते
}
```

`detachedList` array प्रत्येक `div` जिवंत ठेवतो जरी ते सर्व page वरून गेले असले तरी [2].

### Detached Elements Profiler वापरणे

1. **Detached elements** निवडा
2. **Get detached elements** क्लिक करा (किंवा Take snapshot — label Chrome version नुसार बदलते)
3. परिणामी list तुमच्या JavaScript ने अजूनही referenced असलेल्या प्रत्येक orphaned DOM node दाखवते [9]
4. प्रत्येक entry expandable आहे — तुम्ही parent/child nodes देखील पाहू शकता जे retained आहेत
5. त्यांचे references कोणते JS objects ठेवतात हे पाहण्यासाठी "Analyze" button क्लिक करा

खालील "Retainers" panel key आहे. हे तुम्हाला नक्की कोणता variable किंवा closure node जिवंत ठेवत आहे ते दाखवते. तिथेच तुम्ही fix लिहायला जाता [10].

**Detached Elements कधी वापरायचे:** जेव्हाही तुम्हाला संशय असतो की DOM nodes साफ होत नाहीत. Dynamic rendering, virtual lists, किंवा create/destroy ऐवजी show/hide केल्या जाणाऱ्या modals सह SPAs मध्ये विशेषतः उपयुक्त. Major refactor नंतर cleanup logic काम करत आहे हे confirm करण्यासाठी देखील चालवा [9].

नोंद — **detached elements नेहमी leak नसतात.** एक framework performance कारणांसाठी काही nodes legitimately cache करू शकतो. Context महत्त्वाचा आहे. परंतु जर तुमच्याकडे कालांतराने वाढणारे शेकडो detached elements असतील, तर ती एक समस्या आहे [9].

## हे एकत्र ठेवणे: एक Real Debugging Session

तुम्ही लक्षात घेता की तुमच्या SPA ची memory काही मिनिटांच्या वापरानंतर ५० MB वरून ४०० MB पर्यंत चढते. मी कसे approach करेन ते येथे आहे:

1. **Heap Snapshot comparison ने सुरुवात करा.** एक baseline snapshot घ्या, 2 मिनिटे app वापरा, दुसरे घ्या. Comparison view वर switch करा, delta नुसार sort करा. जर तुम्हाला एक स्पष्ट class किंवा constructor type वाढताना दिसत असेल — तुम्हाला माहित आहे काय investigate करायचे.

2. **जर snapshot DOM nodes वाढत असल्याचे दाखवत असेल,** **Detached Elements** वर switch करा आणि snapshot घ्या. काढलेले elements पडत आहेत का हे confirm करते.

3. **जर तुम्हाला trigger ओळखणे आवश्यक असेल,** focused ३०-सेकंदाच्या recording साठी **Allocations on Timeline** वापरा. एक specific interaction करा आणि राखाडी न होणाऱ्या निळ्या bars साठी पहा.

4. **जर तुम्हाला longer session profile करणे आवश्यक असेल** (म्हणा, कित्येक मिनिटे चालणारे background polling loop), **Allocation Sampling** वापरा. ते चालू द्या, थांबवा, आणि कोणते functions सर्वाधिक allocators आहेत ते पहा.

सर्व चार एकाच वेळी वापरण्याचा प्रयत्न करू नका. तुमच्या तात्काळ प्रश्नाचे उत्तर देणारा एक निवडा, तुम्हाला जे सापडते त्यावर कार्य करा, नंतर पुन्हा profile करा.

## जाणण्यासारख्या काही गोष्टी

**आधी garbage collection force करा.** तुलनासाठी snapshot घेण्यापूर्वी, Memory tab मधील trash-can icon ("Collect garbage") क्लिक करा. हे GC manually चालवते जेणेकरून तुम्ही फक्त GC अजून चालला नाही यामुळे वेगळ्या snapshots ची तुलना करत नाही [3].

**Heap Snapshot मधील `Distance` column** GC root पासून object पर्यंतच्या hops ची संख्या दाखवते. खूप कमी Distance (२ किंवा ३ सारखा) असलेले objects global scope मधून थेट reachable आहेत — अनेकदा globals चे signs जे तुम्ही साफ करायला विसरलात.

**`(string)` आणि `(array)` constructors** अनेकदा Summary view मध्ये dominate करतात. हे सहसा सामान्य आहे. त्यांच्याबद्दल घाबरू नका जोपर्यंत त्यांचा retained size snapshots दरम्यान वाढत नाही.

**Retainer chains लांब असू शकतात.** कधीकधी एखादी गोष्ट जिवंत ठेवणाऱ्या actual variable पर्यंत पोहोचण्यापूर्वी तुम्ही ६-७ objects च्या chain मागे जाल. Reference graphs अशाच काम करतात. त्याचा पाठपुरावा करा.

> शेवट

## स्रोत
1. [Memory management — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management)
2. [Causes of Memory Leaks in JavaScript and How to Avoid Them](https://www.ditdot.hr/en/causes-of-memory-leaks-in-javascript-and-how-to-avoid-them)
3. [Memory panel overview — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory)
4. [Record heap snapshots — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots)
5. [The difference between Shallow Size and Retained Size](https://www.jvandemo.com/the-difference-between-shallow-size-and-retained-size-in-the-chrome-devtools-memory-panel/)
6. [Find memory leaks by comparing heap snapshots — DevTools Tips](https://devtoolstips.org/tips/en/find-memory-leaks/)
7. [How to Use the Allocation Timeline Tool — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems/allocation-profiler)
8. [Isolating memory leaks with Chrome's Allocation Timeline — LogRocket](https://blog.logrocket.com/isolating-memory-leaks-with-chromes-allocation-timeline-244fa9c48e8e/)
9. [Get detached DOM elements to investigate memory leaks — DevTools Tips](https://devtoolstips.org/tips/en/get-detached-elements/)
10. [Debug DOM memory leaks — Microsoft Edge DevTools](https://learn.microsoft.com/en-us/microsoft-edge/devtools-guide-chromium/memory-problems/dom-leaks-memory-tool-detached-elements)
11. [Fix memory problems — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems)
12. [Memory terminology — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems/get-started)