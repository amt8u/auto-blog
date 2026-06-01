+++
title       = "Favicon का इतिहास: इसे Favicon क्यों कहते हैं?"
description = "Favicon का टैब्स या लोगो से कोई संबंध नहीं था — यह बुकमार्क्स के लिए बनाया गया था। जानिए कैसे एक Microsoft hack एक web standard बन गया।"
date        = "2026-06-01T21:46:38+05:30"
slug          = "history-of-favicon-why-called-favicon"
tags          = ["वेब", "ब्राउज़र", "इतिहास", "html"]
keywords      = ["favicon का इतिहास", "favicon को favicon क्यों कहते हैं", "favicon की उत्पत्ति", "favicon.ico Internet Explorer"]
canonical     = "/hi/posts/history-of-favicon-why-called-favicon/"
feature_image = "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1200&q=80"
+++

आप इसे ब्राउज़र टैब में देखते हैं। आप इसे सर्च रिज़ल्ट्स में साइट के नाम के पास देखते हैं। आप इसे किसी वेबसाइट का लोगो समझते हैं। तो इसे *favicon* क्यों कहते हैं? यह नाम टैब्स या लोगो से कोई संबंध नहीं रखता। और आप सही हैं — इसका कोई संबंध नहीं है। यह नाम उस चीज़ की विरासत है जिसके लिए यह आइकन *मूल रूप से बनाया गया था*, न कि जो यह आज करता है।

## यह कभी टैब्स के लिए नहीं था

"Favicon" नाम दो शब्दों का संयोजन है: **favorite** + **icon** [1]। यानी वह आइकन जो आपके ब्राउज़र की *favourites list* में किसी वेबसाइट के पास दिखता है — जिसे अधिकांश लोग बुकमार्क्स कहते हैं।

यही इस नाम के पीछे की पूरी कहानी है। यह एक बुकमार्क्स आइकन था। टैब आइकन नहीं। साइट लोगो नहीं। ब्राउज़र टैब में इसका उपयोग बहुत बाद में आया, और तब तक यह नाम अटक चुका था।

## एक डेवलपर, एक देर रात, एक चालाक अप्रूवल

साल था 1999। ब्राउज़र वॉर्स पूरे जोरों पर थे। Microsoft, Internet Explorer 5 पर काम कर रहा था और **Bharat Shyam** नाम का एक डेवलपर Favorites फीचर पर काम कर रहा था [2]।

उनका विचार सरल था: जब आप किसी साइट को बुकमार्क करें, तो URL के पास एक छोटा सा आइकन देखना सादे टेक्स्ट लिंक से बेहतर नहीं होगा? तो उन्होंने इसे बनाया — एक 16×16 पिक्सेल का आइकन, जो किसी वेबसाइट के सर्वर की root में रखी `favicon.ico` फ़ाइल से लोड होता था [3]।

मज़ेदार बात यह है। Shyam को पता था कि यह addition सामान्य चैनलों से अप्रूव नहीं हो पाएगी, इसलिए उन्होंने देर शाम का इंतज़ार किया जब एक कम अनुभवी प्रोजेक्ट मैनेजर ड्यूटी पर था — junior PM Ray Sun। उन्होंने Sun को फीचर दिखाया और कोड check in करवा लिया [4]। इस तरह favicon.ico चुपचाप IE5 में शामिल हो गया, जो मार्च 1999 में रिलीज़ हुआ [5]।

सच कहें तो, बहुत से अच्छे वेब फीचर्स शायद इसी तरह से पास हुए होंगे।

## फ़ाइल फॉर्मेट का चुनाव

चूंकि IE5 Windows पर चलता था, Shyam ने `.ico` फॉर्मेट का उपयोग किया — एक Windows-native आइकन फॉर्मेट जिसे Microsoft पहले से पूरी तरह सपोर्ट करता था [2]। अपने वेब सर्वर की root में एक `favicon.ico` फ़ाइल डालें, और IE किसी साइट को user की favorites list में जोड़ने से पहले इसे अपने आप उठा लेता था। कोई HTML टैग की ज़रूरत नहीं। बस एक convention।

यही कारण है कि root में `favicon.ico` 2026 में भी मौजूद है। ब्राउज़र अभी भी डिफ़ॉल्ट रूप से वहाँ देखते हैं, भले ही HTML अब आपको इसे स्पष्ट रूप से declare करने का तरीका देता है।

## W3C जल्दी शामिल हो गया

उसी साल, W3C ने दिसंबर 1999 में HTML 4.01 specification में favicon support को शामिल कर लिया [6]। इसे declare करने का मानक तरीका था:

```html
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
```

ध्यान दें `shortcut icon` — दो शब्द। "Shortcut" बुकमार्क्स के लिए Microsoft की terminology थी (वे Windows desktop पर "shortcuts" का उपयोग करते थे)। इसलिए HTML syntax में भी बुकमार्क्स की उत्पत्ति आगे चली। W3C ने अंततः स्पष्ट किया कि `shortcut` एक valid keyword नहीं है और `rel="icon"` सही रूप है [7], लेकिन आप `shortcut icon` पूरे इंटरनेट पर अभी भी देखेंगे क्योंकि पुरानी आदतें जल्दी नहीं जातीं।

## यह ब्राउज़र टैब्स पर कब आया?

यह वह हिस्सा है जो वास्तव में नाम को भ्रामक लगाता है।

IE5 केवल favourites list में और जब आप किसी साइट पर होते थे तो address bar में favicons दिखाता था। ब्राउज़र टैब का उपयोग तब आया जब **tabbed browsing** 2000 के दशक की शुरुआत से मध्य तक मुख्यधारा में आई — Firefox, Opera, Safari सभी ने favicon को उठाया और इसे टैब पर ही रेंडर करने लगे [2]।

![favicon evolution timeline](/images/posts/history-of-favicon-why-called-favicon/favicon-evolution-timeline.svg)

उस समय, favicon अपने मूल संदर्भ से पूरी तरह बाहर निकल चुका था। अब यह हर विज़िट के लिए एक स्थायी visual identity बन गया था — बुकमार्क हो या न हो। लेकिन किसी ने इसका नाम नहीं बदला। "Favicon" चलता रहा, भले ही तब तक इसे "tab icon" या "site icon" कहना कहीं अधिक उचित होता।

## मोबाइल का विस्तार

जब Apple ने 2007 में पहला iPhone लॉन्च किया, तो उन्होंने **Apple Touch Icon** नाम की चीज़ पेश की — एक उच्च रिज़ॉल्यूशन आइकन जो iOS home screen पर webpage save करने पर दिखता है [2]। यह बिल्कुल ऐप आइकन जैसा दिखता है।

Android ने 2010 के आसपास इसका अनुसरण किया। फिर Progressive Web Apps आए, जिन्हें install scenarios के लिए पूरे `manifest.json` में आइकन की ज़रूरत होती है।

तो अब एक वेबसाइट से यह अपेक्षा की जाती है कि वह बनाए रखे:

- Legacy browsers के लिए `favicon.ico`
- Modern browsers के लिए PNG favicon (आमतौर पर 32×32 या 96×96)
- Apple Touch Icons (वर्तमान iOS के लिए 180×180)
- PWAs के लिए Web App Manifest icons (192×192, 512×512)

सामान्य भाषा में ये सभी "favicon" हैं। इनमें से कोई भी अब बुकमार्क्स आइकन नहीं है।

## क्या यह नाम भ्रामक है?

कुछ हद तक, लेकिन वास्तव में नहीं — यह बस पुराना हो गया है।

जब Bharat Shyam ने 1999 में "favicon" गढ़ा, तो नाम बिल्कुल सटीक था। यह शाब्दिक रूप से आपके favorites के लिए एक आइकन था। समस्या यह है कि आइकन का *कार्य* 25 वर्षों में बड़े पैमाने पर बढ़ा जबकि *नाम* 1999 में ही रुक गया। टेक में यह बहुत होता है — "wireless" का मतलब radio हुआ करता था, "desktop" का मतलब अभी भी आपका computer है भले ही फोन वही काम करते हों।

"Favicon" नाम **भ्रामक नहीं है, यह कालबाह्य है**। फर्क है। कोई आपको भ्रमित करने की कोशिश नहीं कर रहा था — उपयोग का मामला बस मूल इरादे से बहुत आगे बढ़ गया।

## फॉर्मेट का विकास

| युग | फॉर्मेट | आकार | कहाँ |
|---|---|---|---|
| 1999 | `.ico` | 16×16 | Favourites list |
| 2000 का दशक | `.ico` / `.png` | 16×16, 32×32 | Address bar, tabs |
| 2007+ | `.png` | 57×57 – 180×180 | iOS home screen |
| 2010 का दशक | `.png` | 192×192, 512×512 | Android, PWA |
| अभी | `.svg` | Scalable | सभी modern browsers |

SVG favicons आज सबसे अच्छा विकल्प हैं — एक फ़ाइल, असीमित रूप से scalable, बिना किसी pixel-hunting के retina screens पर काम करती है [2]। लेकिन root में `.ico` कहीं नहीं जा रहा। Browsers इसे ढूंढते रहते हैं।

## एक-फ़ाइल Convention जो अपने कारण से आगे निकल गई

`favicon.ico` convention — web root में एक फ़ाइल डालें और browsers इसे अपने आप खोज लेते हैं — कभी औपचारिक रूप से standardised नहीं हुई। यह बस वही था जो IE5 ने किया, और बाकी सभी ने इसे copy किया [3]। आज भी, बड़ी संख्या में browsers किसी भी पेज पर जाने पर चुपचाप `GET /favicon.ico` request करते हैं, भले ही HTML में कोई `<link rel="icon">` declare न हो।

यह 1999 की एक implementation detail है जिसे दुनिया का हर web server 2026 में भी handle करता है। काफी उल्लेखनीय है।

> समाप्त

## स्रोत
1. [How We Got the Favicon - The History of the Web](https://thehistoryoftheweb.com/how-we-got-the-favicon/)
2. [Favicon - Wikipedia](https://en.wikipedia.org/wiki/Favicon)
3. [A brief history of favicon - RealFaviconGenerator](https://realfavicongenerator.net/favicon-guides/favicon-history)
4. [Inventing Favicon.ico - Take the First](https://ruthlessray.wordpress.com/2013/09/02/inventing-favicon-ico/)
5. [Favicon - Web Design Museum](https://www.webdesignmuseum.org/web-design-history/favicon-1999)
6. [A Quick History of Favicon - Medium](https://medium.com/@whosale/a-quick-history-of-favicon-41e51e146184)
7. [How to Add a Favicon to your Site - W3C](https://www.w3.org/2005/10/howto-favicon)