+++
title       = "क्या आप हर नियम के बिना भी अपने API को RESTful कह सकते हैं?"
description = "REST कहलाने वाले अधिकांश API रॉय फील्डिंग के नियम तोड़ते हैं। तो क्या आप फिर भी अपने API को RESTful कह सकते हैं? यहाँ बताया गया है कि constraints असल में क्या माँगते हैं और किसे छोड़ना ठीक है।"
date        = "2026-06-08T00:03:37+05:30"
slug          = "can-i-call-my-api-restful"
tags          = ["rest", "api-डिज़ाइन", "http", "वेब-डेवलपमेंट"]
keywords      = ["restful api", "rest constraints", "richardson maturity model", "hateoas", "rest बनाम http api"]
canonical     = "/hi/posts/can-i-call-my-api-restful/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=80"
+++

हर कोई अपने API पर "RESTful" का ठप्पा लगा देता है। कोई भी docs पेज खोलिए, मार्केटिंग कॉपी पढ़िए, और वहाँ यह लिखा मिलेगा — "हमारा साफ-सुथरा, RESTful API।" लेकिन यहाँ असहज करने वाली बात यह है: सख्त परिभाषा के अनुसार, इनमें से लगभग कोई भी असल में RESTful नहीं है। तो असल में आप यह पूछ रहे हैं कि अगर आप कुछ नियम तोड़ देते हैं तो क्या उस शब्द का अब भी कोई मतलब रह जाता है। ईमानदारी से कहूँ तो, यहीं से मामला पेचीदा हो जाता है।

पहले संक्षिप्त जवाब, क्योंकि मुझे वे लेख पसंद नहीं जो इसे दबा देते हैं: **हाँ, रोज़मर्रा की बातचीत में आप इसे अब भी RESTful कह सकते हैं, लेकिन नहीं, रॉय फील्डिंग की मूल परिभाषा के अनुसार यह तब तक REST API नहीं है जब तक यह hypertext-driven न हो।** ये दोनों बातें एक साथ सच हैं, और इन दोनों के बीच का फासला ही पूरी कहानी है।

## "REST" का असल मतलब क्या है (और किसने तय किया)

REST कोई protocol नहीं है। यह कोई spec नहीं है जिसे आप डाउनलोड करें। यह एक architectural style है जिसे रॉय फील्डिंग ने अपने 2000 के PhD शोध-प्रबंध में बताया, जहाँ वे मूलतः उन सिद्धांतों को reverse-engineer कर रहे थे जिन्होंने खुद वेब को scale करने लायक बनाया [1]। यह एक अहम नज़रिया है — REST वेब के काम करने के *बाद* आया, इस *बात की* व्याख्या के रूप में कि यह क्यों काम किया।

फील्डिंग ने छह constraints परिभाषित किए। इन सभी को पूरा कर लें तो आपके पास एक RESTful सिस्टम है; गलत वाला छोड़ दें तो, उनकी परिभाषा के अनुसार, नहीं है [2][3]:

- **Client–server** — UI से जुड़ी चिंताओं को डेटा स्टोरेज से जुड़ी चिंताओं से अलग करें ताकि हर एक अपने हिसाब से विकसित हो सके।
- **Stateless** — हर request वह सब साथ लाती है जिसकी सर्वर को ज़रूरत होती है। सर्वर आपकी पिछली request के बारे में कुछ भी संभालकर नहीं रखता।
- **Cacheable** — responses को यह बताना चाहिए कि उन्हें cache किया जा सकता है या नहीं, ताकि clients और intermediaries उन्हें दोबारा इस्तेमाल कर सकें।
- **Uniform interface** — सबसे बड़ा वाला, और वही जिसे हर कोई आधा-अधूरा लागू करता है। इस पर नीचे और बात होगी।
- **Layered system** — एक client यह नहीं बता सकता कि वह असली सर्वर से बात कर रहा है या उसके आगे लगे किसी proxy/load balancer/gateway से।
- **Code on demand** — वैकल्पिक। सर्वर client को बढ़ाने के लिए executable code (जैसे JavaScript) भेज सकता है। यही एकमात्र constraint है जिसे फील्डिंग ने वैकल्पिक बताया।

उस आखिरी शब्द पर ध्यान दें: *वैकल्पिक*। Code on demand ही एकमात्र है जिसे छोड़ने की आपको स्पष्ट रूप से अनुमति है। बाकी सब, सख्त व्याख्या में, अनिवार्य हैं। तो जब लोग पूछते हैं "क्या मैं कोई नियम छोड़कर भी RESTful रह सकता हूँ," तो ईमानदार जवाब यह है कि नियमों में पहले से ही उनमें से ठीक एक के लिए छूट दी गई है, और वह वो नहीं है जिसे आप छोड़ना चाहते थे।

## Uniform interface वहीं है जहाँ API चुपचाप बिखर जाते हैं

Uniform interface खुद चार उप-constraints में बँट जाता है, और यहीं "RESTful" का ठप्पा डगमगाने लगता है [3]:

1. **Resources की पहचान** — हर चीज़ का एक URI होता है, जैसे `/users/123`।
2. **Representations के ज़रिए हेरफेर** — आपके पास एक representation (JSON, XML) होता है और resource को बदलने या मिटाने के लिए वही काफ़ी होता है।
3. **Self-descriptive messages** — हर message में उसे process करने के लिए पर्याप्त जानकारी होती है (media types, status codes, headers)।
4. **HATEOAS** — Hypermedia As The Engine Of Application State। सर्वर के responses में links होते हैं जो client को बताते हैं कि वह आगे क्या कर सकता है।

अधिकांश API पहले तीन को बखूबी पूरा करते हैं। उनके पास अच्छे `/users/123` URLs होते हैं, वे JSON में बात करते हैं, वे content types और status codes सेट करते हैं। और फिर वे नंबर चार को पूरी तरह नज़रअंदाज़ कर देते हैं। यह कोई छोटी चूक नहीं है — यही वो चीज़ है जिसकी फील्डिंग को सबसे ज़्यादा परवाह थी।

## लकीर खिंच गई: "REST API को hypertext-driven होना ही चाहिए"

2008 में, शोध-प्रबंध के आठ साल बाद, फील्डिंग इतने तंग आ गए कि उन्होंने एक ब्लॉग पोस्ट लिखी जिसके शीर्षक में बहस की ज़्यादा गुंजाइश नहीं छोड़ी गई: ["REST APIs must be hypertext-driven"](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven) [1]। उनके सटीक शब्द:

> "अगर application state का engine (और इसलिए API) hypertext से संचालित नहीं हो रहा, तो वह RESTful नहीं हो सकता और REST API नहीं हो सकता।"

यह दो-टूक है। वे उन ढेर सारे API पर प्रतिक्रिया दे रहे थे जो खुद को REST कह रहे थे जबकि असल में वे HTTP के कपड़े पहने RPC-शैली के कॉल थे [11]। उनकी बात: एक सच्चा REST client को एक entry URL से शुरू होना चाहिए और बाकी सब कुछ उन links का अनुसरण करके *खोजना* चाहिए जो सर्वर उसे सौंपता है — ठीक वैसे ही जैसे आप किसी वेबसाइट को बिना उसका हर URL याद किए ब्राउज़ करते हैं। डेटा फ़ॉर्मेट और link relations client को बताते हैं कि क्या संभव है, न कि कोई out-of-band दस्तावेज़ जो आप किसी wiki पर पढ़ते हैं।

सोचिए कि आप एक सामान्य वेबसाइट कैसे इस्तेमाल करते हैं। आप यह याद नहीं रखते कि checkout पेज `/cart/checkout/step-3` पर है। आप पेज पर मौजूद एक बटन क्लिक करते हैं। पेज *आपको बताता है* कि आप आगे क्या कर सकते हैं। यही hypertext है जो application state को चला रहा है। फील्डिंग का तर्क है कि एक REST API को मशीनों के लिए भी इसी तरह काम करना चाहिए [1]।

उस मानक के हिसाब से, यहाँ एक करारा झटका है: वही Twitter और Facebook API जिनसे सबने "REST" सीखा, hypermedia का इस्तेमाल बिल्कुल नहीं करते [8]। आपके रोज़ के काम के अधिकांश API भी नहीं करते। व्यवहार में, तथाकथित अधिकांश REST API statelessness और uniform interface को लागू करते हैं लेकिन HATEOAS को पूरी तरह नज़रअंदाज़ कर देते हैं [7][8]।

## तो क्या आपका API RESTful है? मिलिए Richardson Maturity Model से

लेनार्ड रिचर्डसन ने एक मॉडल पेश किया जिसे मार्टिन फ़ाउलर ने [लोकप्रिय बनाया](https://martinfowler.com/articles/richardsonMaturityModel.html), और आपके सवाल का जवाब देने के लिए यह सबसे उपयोगी उपकरण है क्योंकि यह "RESTful" को हाँ/नहीं मानना बंद कर देता है और इसे एक सीढ़ी में बदल देता है [4][5]। इसमें चार स्तर हैं, 0 से 3 तक [13]।

| स्तर | नाम | यह क्या इस्तेमाल करता है | इसमें क्या कमी है |
|-------|------|--------------|-------------------|
| 0 | The Swamp of POX | एक URI, एक verb (आमतौर पर POST) | सब कुछ। यह RPC/SOAP-शैली है। |
| 1 | Resources | कई URIs, हर resource के लिए एक | HTTP verbs का अब भी गलत इस्तेमाल |
| 2 | HTTP Verbs | URIs + सही GET/POST/PUT/DELETE + status codes | HATEOAS |
| 3 | Hypermedia | ऊपर का सब कुछ + HATEOAS links | कुछ नहीं — यह "पूर्ण" REST है |

यहाँ हक़ीक़त का सामना कराने वाली बात है जो आपको बेहतर महसूस करा देगी: जो API गर्व से खुद को RESTful कहते हैं, उनमें से अधिकांश **स्तर 2** पर बैठे हैं [6][8]। उनके पास साफ-सुथरे resource URLs हैं, वे सही HTTP methods इस्तेमाल करते हैं, वे समझदारी भरे status codes लौटाते हैं। बस वे navigational links embed नहीं करते। और स्तर 2 सचमुच अच्छी इंजीनियरिंग है — यह रहने के लिए एक बिल्कुल समझदार जगह है।

फ़ाउलर खुद यहाँ सावधान हैं। वे कहते हैं कि यह मॉडल REST के तत्वों के बारे में *सोचने* का एक उपयोगी तरीका है, न कि इस बात की सख्त परिभाषा कि आपको वह शब्द कब इस्तेमाल करने की अनुमति है [4]। दूसरी ओर, फील्डिंग कहेंगे कि केवल स्तर 3 ही इस नाम का हक़दार है। दोनों नज़रिए असल दुनिया में मौजूद हैं, और यही तनाव इसकी ठीक वजह है कि आपके सवाल का कोई साफ-सुथरा जवाब नहीं है।

![rest maturity ladder](/images/posts/can-i-call-my-api-restful/rest-maturity-ladder.svg)

## HTTP API बनाम REST API — ये एक ही चीज़ नहीं हैं

यह बहुत से लोगों को उलझाता है, तो मुझे इसे साफ़-साफ़ कहने दें। **सभी REST API, HTTP पर चलते हैं, लेकिन हर HTTP API, REST API नहीं होता** [10]। web API श्रेणी बहुत बड़ी है — जो कुछ भी आप HTTP पर कॉल कर सकते हैं, वह इसमें आता है। REST उसी श्रेणी के *भीतर* एक विशिष्ट architectural style है जिसमें वे छह constraints होते हैं [8]।

जब आपका API resources के इर्द-गिर्द संरचित होता है, verbs को सही इस्तेमाल करता है, और JSON लौटाता है, लेकिन hypermedia नहीं करता, तो असल में आपके पास एक **HTTP API है जो REST conventions का पालन करता है** [10]। कुछ लोग इसे "REST-like" कहते हैं, कुछ इसे "pragmatic REST" कहते हैं, और कुछ बस इसे RESTful कहते रहते हैं क्योंकि यही वह शब्द है जिसे हर कोई समझता है [9]। आम बोलचाल में इनमें से कोई भी गलत नहीं है। वे बस इस बारे में ज़्यादा ईमानदार हैं कि आप सीढ़ी पर कहाँ खड़े हैं।

बेन मॉरिस का [pragmatic REST पर एक ठोस लेख](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/) है जो तर्क देता है कि hypermedia छोड़ना अधिकांश टीमों के लिए एक सोचा-समझा, उचित trade-off है, न कि कोई नाकामी [9]। मैं इससे सहमत होने को झुका हूँ, और मैं बताऊँगा कि क्यों।

## लगभग कोई भी पूर्ण HATEOAS क्यों नहीं करता

अगर स्तर 3 ही "असली" REST है, तो लगभग पूरा उद्योग स्तर 2 पर ही क्यों रुक जाता है? कुछ ईमानदार वजहें:

- **Clients असल में dynamically navigate नहीं करते।** HATEOAS का सपना एक generic client है जो runtime पर links का अनुसरण करके API को खोजता है। हक़ीक़त में, आपकी frontend टीम एक ज्ञात contract के विरुद्ध ज़रूरी endpoints को hardcode कर देती है। links वहीं बेकार पड़े रहते हैं।
- **यह अस्पष्ट फ़ायदे के लिए ज़्यादा काम है।** हर जगह `_links` embed करना, HAL जैसा कोई hypermedia format चुनना, relation types को संगत रखना — यह असली मेहनत है [8]। अगर कोई consumer behaviour चलाने के लिए links इस्तेमाल नहीं करता, तो आपने बेवजह बोझ बढ़ा लिया।
- **Documentation और tooling जीत गए।** OpenAPI/Swagger clients को runtime links के बजाय एक spec फ़ाइल के ज़रिए discoverability देता है। यह वह नहीं है जो फील्डिंग के मन में था, लेकिन इसने लोगों की व्यावहारिक समस्या हल कर दी।
- **बड़े खिलाड़ियों ने इसे कभी नहीं किया।** जब धरती के सबसे ज़्यादा नक़ल किए जाने वाले API hypermedia छोड़ देते हैं [8], तो वह de facto मानक बन जाता है, चाहे शोध-प्रबंध कुछ भी कहे।

हालाँकि एक असली विरोधाभासी पक्ष भी है, और मैं उसके साथ अन्याय नहीं करना चाहता। API स्तर 3 पर *मौजूद* हैं, और कुछ बड़े उस ओर झुकते हैं — GitHub का API मशहूर रूप से अपने responses में ही संबंधित resources के URLs embed करता है ताकि आप खुद URLs बनाने के बजाय उनका अनुसरण कर सकें। जब आपके पास सचमुच कई स्वतंत्र clients हों जिन्हें आप नियंत्रित नहीं करते, या एक लंबे समय तक चलने वाला API जहाँ आप सबको तोड़े बिना resources को इधर-उधर करना चाहते हों, तो hypermedia अपनी कीमत वसूल कर लेता है। फील्डिंग जिस decoupling की बात करते थे वह कोई किताबी चीज़ नहीं है — यही वह तरीका है जिससे सर्वर एक समन्वित client redeploy के बिना URLs बदलने की आज़ादी बनाए रखता है [1][12]। अधिकांश internal API को बस उस आज़ादी की इतनी बुरी तरह कभी ज़रूरत नहीं पड़ती कि उसकी कीमत चुकाई जाए।

## एक ठोस नज़र: एक ही endpoint, तीन स्तर

मुझे इसे कम अमूर्त बनाने दें। मान लीजिए आप एक order fetch कर रहे हैं। हर maturity स्तर मोटे तौर पर ऐसा दिखता है।

**स्तर 0 — दलदल।** एक endpoint, हर चीज़ के लिए POST, verbs body में रहते हैं:

```
POST /api
{ "action": "getOrder", "id": 42 }
```

**स्तर 2 — जहाँ अधिकांश "RESTful" API रहते हैं।** असली resource URL, असली verb, असली status code:

```
GET /orders/42

200 OK
{ "id": 42, "status": "shipped", "customerId": 7 }
```

**स्तर 3 — hypertext-driven।** वही डेटा, लेकिन response client को बताता है कि वह आगे क्या कर सकता है:

```
GET /orders/42

200 OK
{
  "id": 42,
  "status": "shipped",
  "_links": {
    "self":     { "href": "/orders/42" },
    "customer": { "href": "/customers/7" },
    "cancel":   { "href": "/orders/42/cancel" }
  }
}
```

फ़र्क़ देखा? स्तर 3 पर, client को यह *जानने* की ज़रूरत नहीं कि cancel करना `/orders/42/cancel` पर रहता है। सर्वर ने उसे बता दिया। और सबसे अहम, अगर order पहले ही shipped हो चुका है, तो सर्वर बस `cancel` link को *छोड़* सकता है — अब उपलब्ध actions state से संचालित हैं, जो "hypermedia as the engine of application state" का अक्षरशः मतलब है [1][8]। यही वो सचमुच चतुर हिस्सा है जो लोग चूक जाते हैं। यह responses को links से सजाने के बारे में नहीं है। यह सर्वर के इस नियंत्रण के बारे में है कि आगे क्या संभव है।

## तो आपको असल में अपने API को क्या कहना चाहिए?

ये चीज़ें बनाने के सालों बाद यहाँ मेरी राय वाली बात है।

- **अगर यह स्तर 2 है, तो आम लेखन में इसे "RESTful" कहना ठीक है।** हर कोई समझता है कि आपका क्या मतलब है, और पूरे उद्योग के इस्तेमाल से लड़ना हारी हुई लड़ाई है। शब्द का अर्थ बहक गया है, और यह ठीक है।
- **अगर आप तकनीकी रूप से सटीक होना चाहते हैं, तो कहें "REST-like" या "REST conventions का पालन करने वाला HTTP API।"** Hacker News के पंडित फिर भी बहस करेंगे, लेकिन आप सही होंगे [7]।
- **"REST API" शब्द को बिना झेंपे केवल स्तर 3 के लिए रखें।** अगर कोई सख़्ती बरत रहा हो और पूछे "क्या यह एक *REST* API है," और आप hypermedia नहीं करते, तो ईमानदार जवाब है "नहीं, यह REST-like है" [1][7]।

जिस बात का मैं सबसे ज़ोरदार विरोध करूँगा वह है नियमों के *होने का ही दिखावा* करना। बहुत-सी टीमें किसी चीज़ को RESTful कहती हैं बिना यह जाने कि एक HATEOAS constraint है जिसे वे छोड़ रहे हैं। इसे जान-बूझकर छोड़ना एक अच्छा इंजीनियरिंग फ़ैसला है। इसे इसलिए छोड़ना क्योंकि आपको कभी पता ही नहीं था कि यह मौजूद है, बस अच्छी मार्केटिंग के साथ की गई अज्ञानता है।

## वे नियम जिन्हें आपको सचमुच नहीं तोड़ना चाहिए

सभी constraints बराबर नहीं हैं, और यहीं मैं इस बारे में दो-टूक रहूँगा कि एक चालू API के लिए असल में क्या मायने रखता है बनाम क्या छोड़ना सुरक्षित है।

- **Statelessness — इसे मत तोड़िए।** जिस पल आपका सर्वर requests के बीच client state याद रखना शुरू करता है, आप horizontal scaling खो देते हैं, layered-system के फ़ायदे खो देते हैं, और आपने सचमुच REST को इस तरह पीछे छोड़ दिया है जो परिचालन के लिहाज़ से आपको नुकसान पहुँचाता है [2][12]। इसमें असली दम है।
- **HTTP verbs और status codes का सही इस्तेमाल — इसे भी मत तोड़िए।** एक GET जो डेटा बदल दे, एक असली बग है जो होने का इंतज़ार कर रहा है, क्योंकि caches और crawlers मानते हैं कि GET सुरक्षित है। यह स्तर 1-से-2 की बात है और यह बुनियादी ज़रूरत है।
- **Cacheability — इसका सम्मान करें।** सही cache headers सेट करना कम मेहनत है और यह उन चीज़ों में से एक है जिन्होंने वेब को scale करने लायक बनाया। इसे नज़रअंदाज़ करना performance को यूँ ही गँवाना है [3]।
- **HATEOAS — जान-बूझकर छोड़ना ठीक है।** यही वो है जिसे लगभग हर कोई छोड़ देता है, और अधिकांश API के लिए यह एक बचाव-योग्य trade-off है [9]। बस ऐसा करते हुए पूर्ण REST होने का दावा मत कीजिए।

पैटर्न देखा? जो constraints *परिचालन* गुणों की रक्षा करते हैं — statelessness, caching, सही verbs — वही हैं जिन्हें तोड़ने पर आप असल में दर्द महसूस करते हैं। जो constraint विशुद्ध रूप से *विकासशीलता और discoverability* के बारे में है — HATEOAS — वही है जिसके बिना आप आमतौर पर गुज़ारा कर सकते हैं। यह कोई संयोग नहीं है। यही वजह है कि उद्योग जहाँ टिका वहीं टिका।

## इससे आप कहाँ खड़े होते हैं

"RESTful" शब्द बहुत पहले ही द्विआधारी (binary) होना बंद कर चुका है। फील्डिंग की एक सख़्त परिभाषा है जो कहती है hypertext या कुछ नहीं [1], और डेवलपर दुनिया का एक बड़ा हिस्सा चुपचाप उसे नज़रअंदाज़ करता है क्योंकि स्तर 2 उनकी समस्याएँ बखूबी हल कर देता है [7][8]। कोई भी पक्ष झूठ नहीं बोल रहा — वे एक ही शब्द को दो अलग मानकों के लिए इस्तेमाल कर रहे हैं।

तो क्या आप अपने API को अब भी RESTful कह सकते हैं अगर वह सभी नियमों का पालन नहीं करता? व्यवहार में, हाँ, और आप भारी बहुमत में होंगे। बस यह जान लीजिए कि आप कौन-सा नियम छोड़ रहे हैं, यह जान लीजिए कि एक शुद्धतावादी आपको टोकेगा, और यह जान लीजिए कि जिसे आप शायद छोड़ रहे हैं — HATEOAS — वही ठीक वो है जिसके बारे में रॉय फील्डिंग ने कहा था कि आप इसे छोड़ नहीं सकते। यह आपको परेशान करता है या नहीं, यह पूरी तरह इस पर निर्भर करता है कि आप एक सख़्त architecture review के लिए लिख रहे हैं या ऐसा सॉफ़्टवेयर भेज रहे हैं जिसे लोग सचमुच इस्तेमाल करते हैं।

मुझे पता है कि मैं आमतौर पर किस पक्ष में होता हूँ। लेकिन मुझे कम से कम यह पता है कि मैं क्या छोड़ रहा हूँ।

> समाप्त

## स्रोत
1. [REST APIs must be hypertext-driven — Roy T. Fielding](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven)
2. [The Six Constraints — REST API Tutorial](https://www.restapitutorial.com/introduction/restconstraints)
3. [REST Architectural Constraints — restfulapi.net](https://restfulapi.net/rest-architectural-constraints/)
4. [Richardson Maturity Model — Martin Fowler](https://martinfowler.com/articles/richardsonMaturityModel.html)
5. [Richardson Maturity Model — restfulapi.net](https://restfulapi.net/richardson-maturity-model/)
6. [Know how RESTful your API is: An Overview of the Richardson Maturity Model — Red Hat Developer](https://developers.redhat.com/blog/2017/09/13/know-how-restful-your-api-is-an-overview-of-the-richardson-maturity-model)
7. [Most RESTful APIs aren't really RESTful — Florian Krämer](https://florian-kraemer.net/software-architecture/2025/07/07/Most-RESTful-APIs-are-not-really-RESTful.html)
8. [When Is an API Truly REST vs REST-Like? — Nordic APIs](https://nordicapis.com/when-is-an-api-truly-rest-vs-rest-like/)
9. [Pragmatic REST: APIs without hypermedia and HATEOAS — Ben Morris](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/)
10. [REST over HTTP, or why your HTTP API isn't RESTful — Christophe Maillard](https://medium.com/@sp00m/rest-over-http-or-why-your-http-api-isnt-restful-94fd92a0e6d4)
11. [REST APIs Must be Hypertext-driven — Stefan Tilkov, INNOQ](https://www.innoq.com/blog/st/2008/10/rest-apis-must-be-hypertext-driven/)
12. [REST — Wikipedia](https://en.wikipedia.org/wiki/REST)
13. [Richardson Maturity Model — Wikipedia](https://en.wikipedia.org/wiki/Richardson_Maturity_Model)
14. [Roy Fielding on Versioning, Hypermedia, and REST — InfoQ](https://www.infoq.com/articles/roy-fielding-on-versioning/)