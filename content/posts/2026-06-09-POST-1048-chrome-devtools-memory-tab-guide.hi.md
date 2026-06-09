+++
title       = "Chrome DevTools Memory Tab: एक व्यावहारिक गाइड"
description = "Heap Snapshot, Allocation Sampling, Allocations on Timeline, Detached Elements — जानें कि प्रत्येक टूल वास्तव में क्या करता है और इसे कब उपयोग करना चाहिए।"
date        = "2026-06-09T15:06:38+05:30"
slug          = "chrome-devtools-memory-tab-guide"
tags          = ["डेवटूल्स", "जावास्क्रिप्ट", "परफॉर्मेंस", "डीबगिंग", "मेमोरी"]
keywords      = ["Chrome DevTools Memory tab", "heap snapshot", "allocation sampling", "allocations on timeline", "detached elements", "JavaScript मेमोरी लीक डीबगिंग", "मेमोरी प्रोफाइलिंग"]
canonical     = "/hi/posts/chrome-devtools-memory-tab-guide/"
feature_image = "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200"
+++

आपका ऐप समय के साथ धीमा होता जा रहा है। स्क्रॉल पोज़िशन अचानक बदल जाती है। टैब्स 800 MB RAM खा रहे हैं। आप Task Manager खोलते हैं और देखते हैं कि Chrome मेमोरी ऐसे खा रहा है जैसे बुफे लगी हो। कुछ लीक हो रहा है — लेकिन कहाँ? Chrome DevTools का Memory tab वहीं मौजूद है, और ज़्यादातर डेवलपर्स या तो इसे नज़रअंदाज़ करते हैं या एक बार खोलकर "Shallow Size" और "Retainers" देखकर भ्रमित हो जाते हैं और चुपचाप बंद कर देते हैं। यह गाइड उन लोगों के लिए है जो इसे वास्तव में उपयोग करना चाहते हैं।

## JavaScript में मेमोरी लीक इतनी चालाक क्यों होती हैं

JavaScript गार्बेज कलेक्टेड है। V8 — Chrome का JavaScript इंजन — स्वचालित रूप से मेमोरी मुक्त करता है जब वह तय करता है कि कोई ऑब्जेक्ट अब पहुँच योग्य नहीं है [1]। एल्गोरिदम सिद्धांत में सरल है: यदि कोई भी किसी ऑब्जेक्ट का संदर्भ नहीं रखता, तो उसे एकत्र किया जा सकता है।

समस्या? **JavaScript में संयोग से संदर्भों को जीवित रखना बहुत आसान है।** एक event listener। एक closure जिसने एक वेरिएबल को कैप्चर कर लिया। एक detached DOM node जो अभी भी एक global array द्वारा इंगित है। गार्बेज कलेक्टर यहाँ आपकी मदद नहीं कर सकता — ऑब्जेक्ट्स *पहुँच योग्य हैं*, बस जानबूझकर नहीं। [JavaScript में मेमोरी प्रबंधन](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management) तकनीकी रूप से "स्वचालित" है, लेकिन इसका मतलब लीक-मुक्त नहीं है [1]।

तीन पैटर्न JavaScript मेमोरी लीक की विशाल बहुमत के लिए जिम्मेदार हैं [2]:

- **भूले हुए event listeners** — आप DOM से एक element हटाते हैं लेकिन कभी `removeEventListener` नहीं बुलाते। listener (और उसके closure में सब कुछ) जीवित रहता है।
- **बड़े ऑब्जेक्ट्स रखने वाले Closures** — एक फ़ंक्शन जिसने एक बड़े वेरिएबल को बंद कर लिया, जो जीवित रहता है क्योंकि कोई event या timer अभी भी उस फ़ंक्शन का संदर्भ रखता है।
- **Detached DOM nodes** — पेज से हटाए गए elements लेकिन अभी भी कहीं किसी JavaScript ऑब्जेक्ट द्वारा संदर्भित।

Memory tab में चार अलग-अलग टूल हैं। प्रत्येक एक अलग प्रकार की समस्या खोजने के लिए अनुकूलित है। गलत टूल खोलना आपका समय बर्बाद करता है।

## Memory Tab: चार टूल, एक नहीं

DevTools → Memory खोलें। आपको चार रेडियो बटन दिखेंगे [3]:

1. **Heap snapshot** — heap पर सब कुछ की एक समय-बिंदु तस्वीर
2. **Allocation instrumentation on timeline** — समय के साथ allocations को *जैसे वे होती हैं* रिकॉर्ड करता है
3. **Allocation sampling** — उपरोक्त का एक हल्का, सांख्यिकीय संस्करण
4. **Detached elements** — DOM nodes की सूची जो अनाथ हैं लेकिन अभी भी संदर्भित हैं

प्रत्येक एक अलग प्रश्न का उत्तर देता है। यहाँ गहराई में जाने से पहले त्वरित निर्णय मैट्रिक्स है:

| टूल | सर्वश्रेष्ठ उपयोग | ओवरहेड | अवधि |
|---|---|---|---|
| Heap Snapshot | "अभी क्या जीवित है?" | अधिक (GC रोकता है) | तत्काल |
| Allocations on Timeline | "क्या allocate हुआ और कभी मुक्त नहीं हुआ?" | मध्यम | छोटा सत्र |
| Allocation Sampling | "कौन से फ़ंक्शन सबसे ज़्यादा allocate करते हैं?" | **कम** | लंबे सत्र |
| Detached Elements | "कौन से हटाए गए DOM nodes अभी भी रखे हैं?" | कम | तत्काल |

![memory tab tools overview](/images/posts/chrome-devtools-memory-tab-guide/memory-tab-tools-overview.svg)

## Heap Snapshot

यह वह है जिसे ज़्यादातर लोग पहले आज़माते हैं। यह एक ही समय बिंदु पर JavaScript heap का एक पूर्ण snapshot कैप्चर करता है — प्रत्येक ऑब्जेक्ट, प्रत्येक DOM node, प्रत्येक string, प्रत्येक संदर्भ [3]।

आप एक लेते हैं, उसे देखते हैं, और यदि आपने पहले कभी ऐसा नहीं किया है, तो आप तुरंत हज़ारों constructors और संख्याओं से अभिभूत महसूस करते हैं। यह सामान्य है। यहाँ वास्तव में क्या देखना है।

### Views

snapshot result के ऊपर-बाईं ओर dropdown बदलें। तीन views हैं [4]:

**Summary** — डिफ़ॉल्ट। heap पर वर्तमान में जीवित ऑब्जेक्ट्स बनाने वाले प्रत्येक constructor फ़ंक्शन की सूची। महत्वपूर्ण कॉलम:
- *Shallow size* — ऑब्जेक्ट द्वारा स्वयं अधिकृत मेमोरी, संदर्भों को अनदेखा करते हुए
- *Retained size* — वह मेमोरी जो मुक्त होगी यदि यह ऑब्जेक्ट (और जो कुछ भी यह अकेले जीवित रखता है) garbage collected हो जाए [5]

**Comparison** — कोई क्रिया करने के बाद दूसरा snapshot लें, फिर इसे पहले से तुलना करें। `# New`, `# Deleted`, `# Delta` दिखाता है। यहाँ लीक स्पष्ट हो जाती हैं। [Heap snapshots की तुलना](https://devtoolstips.org/tips/en/find-memory-leaks/) यह पुष्टि करने का सबसे विश्वसनीय तरीका है कि लीक वास्तविक है [6]।

**Containment** — `window` और closures जैसी roots से शुरू होने वाले ऑब्जेक्ट graph का bird's-eye view। तब उपयोगी जब आप पहले से किसी विशिष्ट ऑब्जेक्ट पर संदेह करते हैं और ठीक यह trace करना चाहते हैं कि इसे क्या जीवित रख रहा है [4]।

### Shallow बनाम Retained Size — यह भाग वास्तव में मायने रखता है

सच कहूँ तो, यह इस पूरे panel में सबसे भ्रामक अवधारणा है, लेकिन एक बार समझ में आ जाए तो यह सरल है।

**Shallow size** बस ऑब्जेक्ट स्वयं है। कुछ properties वाला एक plain JS ऑब्जेक्ट `{}` 64 bytes shallow हो सकता है। **Retained size** *वह सब कुछ है जो मुक्त होगा यदि यह ऑब्जेक्ट गायब हो जाए* [5]। यदि वह plain ऑब्जेक्ट 10,000 items की Array का संदर्भ रखता है, तो उसका retained size 64 bytes + उस सारी array memory है।

लीक खोजते समय, **Retained size** के अनुसार sort करें, Shallow के नहीं। 64 bytes shallow लेकिन 50 MB retained वाला ऑब्जेक्ट बिल्कुल वही है जो आप खोज रहे हैं।

### Heap Snapshots के साथ क्लासिक लीक-खोज वर्कफ़्लो

1. Memory tab खोलें, **Heap snapshot** चुनें
2. **Take snapshot** क्लिक करें — यह आपकी baseline है
3. वह क्रिया करें जिस पर आपको लीक का संदेह है (modal खोलें, route navigate करें, बार-बार बटन क्लिक करें)
4. उल्टा करें (modal बंद करें, वापस navigate करें)
5. दूसरा snapshot लें
6. snapshot 2 में, view को **Comparison** में बदलें
7. `# Delta` के अनुसार descending sort करें

यदि वे ऑब्जेक्ट्स जिन्हें एकत्र किया जाना चाहिए था (modal के internal components, route के views) अभी भी क्रिया को उल्टा करने के बाद positive delta दिखाते हैं — आपने अपनी लीक पा ली। नीचे का `Retainers` section आपको बताता है *उन्हें क्या रोक रहा है*।

**Heap Snapshot कब उपयोग करें:** आप पहले से जानते हैं कि कुछ लीक हो रहा है और आप ठीक यह पहचानना चाहते हैं कि वह क्या है। before/after analysis के लिए भी अच्छा — जैसे, "क्या यह refactor वास्तव में मेमोरी उपयोग कम करता है?"

## Allocations on Timeline

Heap snapshots आपको मेमोरी की *स्थिति* दिखाते हैं। Allocation Timeline आपको *कहानी* दिखाती है — क्या allocate हुआ, कब, और क्या वह बचा [7]।

जब आप Record क्लिक करते हैं, DevTools आपके पूरे सत्र में समय-समय पर micro-snapshots लेता है (लगभग हर 50ms)। प्रत्येक allocation एक vertical bar के रूप में दिखाई देती है [7]:

- **नीली bar** — यहाँ allocate किए गए ऑब्जेक्ट रिकॉर्डिंग रोकने पर *अभी भी जीवित* हैं
- **ग्रे bar** — यहाँ allocate किए गए ऑब्जेक्ट बाद में garbage collected हो गए ✓

जिनकी आपको परवाह है वे नीले वाले हैं जो नीले नहीं होने चाहिए। यदि आप बटन क्लिक करते हैं, कोई क्रिया करते हैं, और नीली bars का एक समूह देखते हैं जो कितना भी इंतजार करने पर कभी ग्रे नहीं होता — वे ऑब्जेक्ट मुक्त नहीं हो रहे।

### इसे कैसे उपयोग करें

1. **Allocation instrumentation on timeline** चुनें
2. **Start** दबाएँ
3. संदिग्ध क्रिया करें (scroll, click, navigate)
4. रिकॉर्डिंग रोकें
5. timeline में persistent नीली bars देखें
6. किसी भी bar पर क्लिक करके नीचे Constructor list फ़िल्टर करें — उस window के दौरान allocate किए गए केवल वे ऑब्जेक्ट्स दिखाता है जो अभी भी live हैं

Heap Snapshot से अंतर महत्वपूर्ण है। Timeline आपको बताती है कि allocations *कब* हुईं, जो किसी allocation को किसी विशिष्ट user interaction से जोड़ना बहुत आसान बनाती है। आप हर बार एक निश्चित बटन क्लिक करने पर एक स्पष्ट spike देख सकते हैं — वह आपके दोषी का timestamp है [8]।

**Allocations on Timeline कब उपयोग करें:** आप यह isolate करने की कोशिश कर रहे हैं कि *कौन सा user interaction* वृद्धि का कारण है। आपको एक सामान्य अहसास है कि कुछ लीक हो रहा है लेकिन आप नहीं जानते कि कौन सी क्रिया इसे trigger करती है।

### एक सावधानी

यहाँ overhead वास्तविक है। DevTools हर 50ms पर heap को effectively snapshot कर रहा है [7]। इस टूल से 10 मिनट का सत्र रिकॉर्ड न करें — आपको एक विशाल profile मिलेगी जिसे analyze करना कठिन होगा, और रिकॉर्डिंग के दौरान आपका ऐप उल्लेखनीय रूप से धीमा होगा। रिकॉर्डिंग छोटी रखें और उस विशिष्ट interaction पर केंद्रित रखें जिसकी आप जाँच कर रहे हैं।

## Allocation Sampling

यह वह है जिसे अधिकांश डेवलपर्स छोड़ देते हैं, जो एक गलती है। Allocation Sampling Timeline का हल्का संस्करण है — यह हर allocation रिकॉर्ड करने की बजाय *सांख्यिकीय sampling* का उपयोग करता है [3]।

trade-off: **कम सटीक, लेकिन लगभग शून्य overhead।** आप अपने ऐप के प्रदर्शन को महत्वपूर्ण रूप से प्रभावित किए बिना मिनटों या घंटों के लिए रिकॉर्ड कर सकते हैं। यह महत्वपूर्ण है क्योंकि कुछ मेमोरी वृद्धि क्रमिक होती है — दृश्यमान होने से पहले 20 मिनट के उपयोग की आवश्यकता होती है। Timeline उसके लिए अनुपयोगी होगी। Allocation Sampling उसी के लिए डिज़ाइन किया गया है।

### यह क्या दिखाता है

परिणाम एक flame chart / call tree जैसे दिखते हैं। आपको profile की अवधि में *प्रत्येक फ़ंक्शन द्वारा allocate की गई* heap memory का breakdown मिलता है, जिसमें बाद में मुक्त किए गए allocations भी शामिल हैं [3]। डिफ़ॉल्ट view "Heavy (Bottom Up)" है — सबसे अधिक मेमोरी allocate करने वाले फ़ंक्शन शीर्ष पर सूचीबद्ध हैं।

यह अन्य टूल्स से अलग प्रश्न का उत्तर देता है: **"क्या लीक हुआ" नहीं बल्कि "कौन सा कोड allocation-heavy है।"** एक फ़ंक्शन जो 200 MB allocate करता है, भले ही इसका अधिकांश हिस्सा collect हो जाए, performance दृष्टिकोण से देखने लायक है।

**Allocation Sampling कब उपयोग करें:** लंबे चलने वाले profiling सत्र जहाँ आप Timeline का overhead वहन नहीं कर सकते। जब आप समझना चाहते हैं कि कौन से फ़ंक्शन सबसे बड़े allocators हैं (ज़रूरी नहीं कि लीक हो, बस महंगे)। जब आप लीक hunting की बजाय मेमोरी optimization कर रहे हों।

## Detached Elements

यह दूसरों की तुलना में अधिक targeted है। पूरे heap को दिखाने की बजाय, यह विशेष रूप से **वे DOM nodes खोजता है जिन्हें page के DOM tree से हटाया गया है लेकिन अभी भी JavaScript द्वारा संदर्भित हैं** [9]।

यह क्यों मायने रखता है? जब आप `element.remove()` बुलाते हैं या `innerHTML` साफ करते हैं, तो आप उम्मीद करते हैं कि वे nodes garbage collected हो जाएँगे। लेकिन यदि कोई भी JS variable, array, closure, या event handler अभी भी उस element का संदर्भ रखता है, तो V8 इसे collect नहीं कर सकता [2]। node "detached" है — पेज में अब दृश्यमान नहीं, लेकिन मेमोरी में बहुत जीवित।

यह single-page applications में बेहद सामान्य है। एक ऐसे component framework के बारे में सोचें जो पहले render किए गए elements का cache रखता है, या एक list जो उन rows के संदर्भ संग्रहीत करती है जिन्हें आपने viewport से पहले ही हटा दिया है।

### Detached Elements बनाने वाला सामान्य कोड

```javascript
// Classic detached node scenario
let detachedList = [];

function addAndRemove() {
  const el = document.createElement('div');
  document.body.appendChild(el);
  detachedList.push(el);           // saved the reference
  document.body.removeChild(el);   // removed from DOM
  // el is now detached — detachedList holds it alive
}
```

`detachedList` array हर `div` को जीवित रखता है भले ही वे सब पेज से चले गए हों [2]।

### Detached Elements Profiler का उपयोग

1. **Detached elements** चुनें
2. **Get detached elements** क्लिक करें (या Take snapshot — label Chrome संस्करण के अनुसार भिन्न होता है)
3. परिणामी list आपके JavaScript द्वारा अभी भी संदर्भित प्रत्येक अनाथ DOM node दिखाती है [9]
4. प्रत्येक entry expandable है — आप parent/child nodes देख सकते हैं जो भी retain हो रहे हैं
5. "Analyze" बटन क्लिक करके देखें कि कौन से JS ऑब्जेक्ट उनके संदर्भ रखते हैं

नीचे का "Retainers" panel महत्वपूर्ण है। यह आपको वह सटीक variable या closure दिखाता है जो node को जीवित रख रहा है। वहीं जाकर आप fix लिखते हैं [10]।

**Detached Elements कब उपयोग करें:** जब भी आपको संदेह हो कि DOM nodes साफ नहीं हो रहे। dynamic rendering, virtual lists, या show/hide किए जाने वाले modals वाले SPAs में विशेष रूप से उपयोगी। cleanup logic काम कर रही है यह पुष्टि करने के लिए major refactor के बाद भी चलाएँ [9]।

ध्यान दें — **detached elements हमेशा लीक नहीं होते।** एक framework performance कारणों से कुछ nodes वैध रूप से cache कर सकता है। संदर्भ मायने रखता है। लेकिन यदि आपके पास समय के साथ बढ़ते सैकड़ों detached elements हैं, तो यह एक समस्या है [9]।

## इसे एक साथ रखना: एक वास्तविक Debugging सत्र

आप देखते हैं कि आपके SPA की मेमोरी कुछ मिनटों के उपयोग के बाद 50 MB से 400 MB तक बढ़ जाती है। यहाँ मैं इसे कैसे approach करूँगा:

1. **Heap Snapshot comparison से शुरू करें।** एक baseline snapshot लें, 2 मिनट के लिए ऐप उपयोग करें, दूसरा लें। Comparison view में switch करें, delta के अनुसार sort करें। यदि आप एक स्पष्ट class या constructor type बढ़ते देखते हैं — आप जानते हैं कि क्या investigate करना है।

2. **यदि snapshot DOM nodes बढ़ते दिखाता है,** **Detached Elements** पर switch करें और snapshot लें। यह पुष्टि करता है कि क्या हटाए गए elements जमा हो रहे हैं।

3. **यदि आपको trigger पहचानने की ज़रूरत है,** एक focused 30-second रिकॉर्डिंग के लिए **Allocations on Timeline** का उपयोग करें। एक विशिष्ट interaction करें और नीली bars देखें जो ग्रे नहीं होतीं।

4. **यदि आपको एक लंबे सत्र को profile करने की ज़रूरत है** (जैसे, कई मिनटों तक चलने वाला background polling loop), **Allocation Sampling** का उपयोग करें। इसे चलने दें, रोकें, और देखें कि कौन से फ़ंक्शन सबसे बड़े allocators हैं।

चारों को एक साथ उपयोग करने की कोशिश न करें। वह चुनें जो आपके तत्काल प्रश्न का उत्तर देता है, जो आपको मिले उस पर कार्य करें, फिर re-profile करें।

## कुछ जानने योग्य बातें

**पहले garbage collection force करें।** तुलना के लिए snapshot लेने से पहले, Memory tab में trash-can icon ("Collect garbage") क्लिक करें। यह GC को मैन्युअल रूप से चलाता है ताकि आप ऐसे snapshots की तुलना न करें जो केवल इसलिए अलग हों क्योंकि GC अभी तक नहीं चला [3]।

**Heap Snapshot में `Distance` कॉलम** GC root से ऑब्जेक्ट तक के hops की संख्या दिखाता है। बहुत छोटी Distance (जैसे 2 या 3) वाले ऑब्जेक्ट global scope से सीधे पहुँच योग्य हैं — अक्सर उन globals के संकेत जिन्हें आप साफ करना भूल गए।

**`(string)` और `(array)` constructors** अक्सर Summary view पर हावी होते हैं। यह आमतौर पर सामान्य है। जब तक snapshots के बीच उनका retained size न बढ़े, उनके बारे में घबराएँ नहीं।

**Retainer chains लंबी हो सकती हैं।** कभी-कभी आप किसी चीज़ को जीवित रखने वाले वास्तविक variable तक पहुँचने से पहले 6-7 ऑब्जेक्ट्स की chain का पीछा करेंगे। reference graphs ऐसे ही काम करते हैं। उसका पालन करें।

> समाप्त

## स्रोत
1. [मेमोरी प्रबंधन — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management)
2. [JavaScript में मेमोरी लीक के कारण और उनसे कैसे बचें](https://www.ditdot.hr/en/causes-of-memory-leaks-in-javascript-and-how-to-avoid-them)
3. [Memory panel overview — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory)
4. [Heap snapshots रिकॉर्ड करें — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems/heap-snapshots)
5. [Shallow Size और Retained Size के बीच का अंतर](https://www.jvandemo.com/the-difference-between-shallow-size-and-retained-size-in-the-chrome-devtools-memory-panel/)
6. [Heap snapshots की तुलना करके मेमोरी लीक खोजें — DevTools Tips](https://devtoolstips.org/tips/en/find-memory-leaks/)
7. [Allocation Timeline Tool का उपयोग कैसे करें — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems/allocation-profiler)
8. [Chrome के Allocation Timeline से मेमोरी लीक isolate करना — LogRocket](https://blog.logrocket.com/isolating-memory-leaks-with-chromes-allocation-timeline-244fa9c48e8e/)
9. [मेमोरी लीक की जाँच के लिए detached DOM elements प्राप्त करें — DevTools Tips](https://devtoolstips.org/tips/en/get-detached-elements/)
10. [DOM मेमोरी लीक debug करें — Microsoft Edge DevTools](https://learn.microsoft.com/en-us/microsoft-edge/devtools-guide-chromium/memory-problems/dom-leaks-memory-tool-detached-elements)
11. [मेमोरी समस्याएँ ठीक करें — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems)
12. [मेमोरी शब्दावली — Chrome DevTools](https://developer.chrome.com/docs/devtools/memory-problems/get-started)