+++
title       = "प्रत्येक नियम न पाळताही तुम्ही API ला RESTful म्हणू शकता का?"
description = "REST असे लेबल लावलेले बहुतांश API रॉय फिल्डिंगचे नियम मोडतात. मग तुम्ही तरीही तुमच्या API ला RESTful म्हणू शकता का? या निर्बंधांना प्रत्यक्षात काय आवश्यक आहे आणि काय वगळणे ठीक आहे ते इथे आहे."
date        = "2026-06-08T00:03:37+05:30"
slug          = "can-i-call-my-api-restful"
tags          = ["rest", "api-design", "http", "web-development"]
keywords      = ["restful api", "rest constraints", "richardson maturity model", "hateoas", "rest vs http api"]
canonical     = "/mr/posts/can-i-call-my-api-restful/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=80"
+++

प्रत्येकजण आपल्या API वर "RESTful" असा शिक्का मारतो. कोणतीही docs पेज उघडा, मार्केटिंग मजकूर स्क्रोल करा, आणि तिथे ते असतेच — "आमचे स्वच्छ, RESTful API." पण इथे अडचणीची गोष्ट अशी आहे: काटेकोर व्याख्येनुसार, त्यांपैकी जवळपास एकही प्रत्यक्षात तसे नसते. म्हणून तुम्ही जो खरा प्रश्न विचारत आहात तो असा की काही नियम मोडले तर हा शब्द अजूनही काही अर्थ राखतो का. खरे सांगायचे तर, इथेच गोष्ट किचकट बनते.

आधी थोडक्यात उत्तर, कारण उत्तर शेवटी दडवून ठेवणारे लेख मला आवडत नाहीत: **हो, रोजच्या संभाषणात तुम्ही त्याला अजूनही RESTful म्हणू शकता, पण नाही, रॉय फिल्डिंगच्या मूळ व्याख्येनुसार ते REST API नाही — जोपर्यंत ते hypertext-driven नसेल.** या दोन्ही गोष्टी एकाच वेळी खऱ्या आहेत, आणि त्यांच्यातील अंतर हीच संपूर्ण कथा आहे.

## "REST" चा प्रत्यक्षात अर्थ काय (आणि कोणी ठरवले)

REST हे प्रोटोकॉल नाही. ते तुम्ही डाउनलोड करता असा spec नाही. ती एक आर्किटेक्चरल शैली आहे, जिचे वर्णन रॉय फिल्डिंगने आपल्या २००० सालच्या PhD प्रबंधात केले, जिथे तो मुळात वेबला स्वतःला स्केल करणे शक्य करून देणाऱ्या तत्त्वांचे रिव्हर्स-इंजिनिअरिंग करत होता [1]. ही महत्त्वाची मांडणी आहे — REST हे वेब *चालल्यानंतर* आले, ते *का* चालले याचे स्पष्टीकरण म्हणून.

फिल्डिंगने सहा निर्बंध (constraints) मांडले. ते सर्व पाळा आणि तुमच्याकडे RESTful सिस्टम आहे; चुकीचा एखादा वगळा आणि त्याच्या व्याख्येनुसार तसे नाही [2][3]:

- **Client–server** — UI च्या बाबी डेटा स्टोरेजच्या बाबींपासून वेगळ्या ठेवा, जेणेकरून प्रत्येक स्वतंत्रपणे उत्क्रांत होऊ शकेल.
- **Stateless** — प्रत्येक request सर्व्हरला आवश्यक असलेले सगळे काही घेऊन येते. तुमच्या मागील request बद्दल सर्व्हर काहीही साठवून ठेवत नाही.
- **Cacheable** — responses ने ते cache करता येतात का हे सांगितले पाहिजे, जेणेकरून clients आणि intermediaries त्यांचा पुनर्वापर करू शकतील.
- **Uniform interface** — सर्वात मोठा, आणि प्रत्येकजण अर्धवट अंमलात आणतो तोच. याबद्दल खाली अधिक.
- **Layered system** — client हे खऱ्या सर्व्हरशी बोलत आहे की त्याच्यापुढील proxy/load balancer/gateway शी, हे त्याला सांगता येत नाही.
- **Code on demand** — पर्यायी. सर्व्हर client वाढवण्यासाठी executable code (जसे JavaScript) पाठवू शकतो. फिल्डिंगने पर्यायी म्हणून चिन्हांकित केलेला हा एकमेव निर्बंध आहे.

तो शेवटचा शब्द लक्षात घ्या: *पर्यायी*. Code on demand हा एकमेव असा आहे जो तुम्हाला स्पष्टपणे वगळण्याची परवानगी आहे. बाकी सगळे, काटेकोर वाचनानुसार, अनिवार्य आहेत. म्हणून जेव्हा लोक विचारतात "मी एखादा नियम वगळून तरीही RESTful राहू शकतो का," तेव्हा प्रामाणिक उत्तर असे की या नियमांमध्ये नेमक्या एकासाठी आधीच एक अंगभूत opt-out आहे, आणि तो नेमका तुम्हाला वगळायचा होता तो नाही.

## Uniform interface जिथे API शांतपणे कोसळतात

Uniform interface स्वतः चार उप-निर्बंधांमध्ये विभागला जातो, आणि इथेच "RESTful" लेबल डळमळीत होते [3]:

1. **Identification of resources** — प्रत्येक गोष्टीला URI असते, जसे `/users/123`.
2. **Manipulation through representations** — तुमच्याकडे एक representation (JSON, XML) असते आणि resource बदलण्यासाठी किंवा हटवण्यासाठी ते पुरेसे असते.
3. **Self-descriptive messages** — प्रत्येक message मध्ये त्यावर प्रक्रिया करण्यासाठी पुरेशी माहिती असते (media types, status codes, headers).
4. **HATEOAS** — Hypermedia As The Engine Of Application State. सर्व्हरच्या responses मध्ये client पुढे काय करू शकतो हे सांगणाऱ्या links असतात.

बहुतांश API पहिल्या तीन गोष्टी अचूक करतात. त्यांच्याकडे सुंदर `/users/123` URLs असतात, ते JSON बोलतात, ते content types आणि status codes सेट करतात. आणि मग ते क्रमांक चार पूर्णपणे दुर्लक्षित करतात. ही काही किरकोळ चूक नाही — फिल्डिंगला सर्वाधिक काळजी होती तीच ही गोष्ट आहे.

## ठाम रेषा: "REST APIs must be hypertext-driven"

२००८ मध्ये, प्रबंधाच्या आठ वर्षांनंतर, फिल्डिंग इतका वैतागला की त्याने एक ब्लॉग पोस्ट लिहिली ज्याच्या शीर्षकात फारशी वादाला जागा नाही: ["REST APIs must be hypertext-driven"](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven) [1]. त्याचे नेमके शब्द:

> "If the engine of application state (and hence the API) is not being driven by hypertext, then it cannot be RESTful and cannot be a REST API."

हे स्पष्ट आहे. तो HTTP च्या कपड्यांत सजवलेल्या RPC-शैलीतील कॉल असूनही स्वतःला REST म्हणवणाऱ्या API च्या लोंढ्यावर प्रतिक्रिया देत होता [11]. त्याचा मुद्दा: खऱ्या REST client ने एका entry URL पासून सुरुवात करावी आणि सर्व्हर देणाऱ्या links चे अनुसरण करून बाकी सगळे *शोधावे* — अगदी तसेच जसे तुम्ही प्रत्येक URL लक्षात न ठेवता वेबसाइट ब्राउझ करता. कोणत्या गोष्टी शक्य आहेत ते data format आणि link relations client ला सांगतात, तुम्ही wiki वर वाचलेले एखादे out-of-band documentation नव्हे.

एखादी सामान्य वेबसाइट तुम्ही कशी वापरता याचा विचार करा. checkout पेज `/cart/checkout/step-3` वर असते हे तुम्ही लक्षात ठेवत नाही. तुम्ही पेजवर असलेले एक बटण क्लिक करता. पेज तुम्हाला *सांगते* की तुम्ही पुढे काय करू शकता. तेच hypertext application state चालवते. फिल्डिंगचा युक्तिवाद असा की REST API ने मशीनसाठी तसेच काम केले पाहिजे [1].

त्या मानकानुसार, इथे धक्का बसवणारी गोष्ट: प्रत्येकाने ज्यांच्याकडून "REST" शिकले ते Twitter आणि Facebook चे API hypermedia अजिबात वापरत नाहीत [8]. तुमच्या रोजच्या कामातील बहुतांश API ही वापरत नाहीत. प्रत्यक्षात, तथाकथित बहुतांश REST API statelessness आणि uniform interface अंमलात आणतात पण HATEOAS पूर्णपणे दुर्लक्षित करतात [7][8].

## मग तुमचे API RESTful आहे का? भेटा Richardson Maturity Model ला

लिओनार्ड रिचर्डसनने एक मॉडेल मांडले जे मार्टिन फाउलरने [लोकप्रिय केले](https://martinfowler.com/articles/richardsonMaturityModel.html), आणि तुमच्या प्रश्नाचे उत्तर देण्यासाठी हे सर्वात उपयुक्त साधन आहे, कारण ते "RESTful" ला होय/नाही म्हणून न पाहता त्याला एक शिडी बनवते [4][5]. यात चार पातळ्या आहेत, ० ते ३ [13].

| पातळी | नाव | ते काय वापरते | त्यात काय कमी आहे |
|-------|------|--------------|-------------------|
| 0 | The Swamp of POX | एकच URI, एकच verb (सहसा POST) | सगळेच. हे RPC/SOAP-शैलीतील आहे. |
| 1 | Resources | अनेक URIs, प्रत्येक resource साठी एक | HTTP verbs अजूनही चुकीचे वापरले जातात |
| 2 | HTTP Verbs | URIs + योग्य GET/POST/PUT/DELETE + status codes | HATEOAS |
| 3 | Hypermedia | वरील सगळे + HATEOAS links | काहीही नाही — हे "संपूर्ण" REST आहे |

इथे एक वास्तवाचा धडा जो तुम्हाला बरे वाटू देईल: जे API अभिमानाने स्वतःला RESTful म्हणवतात त्यांपैकी बहुसंख्य **पातळी २** वर बसले आहेत [6][8]. त्यांच्याकडे स्वच्छ resource URLs आहेत, ते योग्य HTTP methods वापरतात, ते समजूतदार status codes परत करतात. ते फक्त navigational links अंतर्भूत करत नाहीत. आणि पातळी २ हे खरोखरच चांगले engineering आहे — ही असण्यासाठी पूर्णपणे समंजस जागा आहे.

फाउलर स्वतः इथे सावध आहे. तो नमूद करतो की हे मॉडेल REST च्या घटकांबद्दल *विचार* करण्याचा एक उपयुक्त मार्ग आहे, तुम्हाला हा शब्द कधी वापरण्याची परवानगी आहे याची काटेकोर व्याख्या नव्हे [4]. दुसरीकडे, फिल्डिंग म्हणेल की फक्त पातळी ३ हेच नाव कमावते. हे दोन्ही दृष्टिकोन प्रत्यक्षात अस्तित्वात आहेत, आणि तोच ताण नेमका हेच कारण आहे की तुमच्या प्रश्नाला स्वच्छ उत्तर नाही.

![rest maturity ladder](/images/posts/can-i-call-my-api-restful/rest-maturity-ladder.svg)

## HTTP API वि REST API — ते एकच गोष्ट नाहीत

यामुळे बरेच लोक गोंधळतात, म्हणून मला हे स्पष्टपणे सांगू द्या. **सर्व REST API HTTP वर चालतात, पण प्रत्येक HTTP API हे REST API नसते** [10]. web API ची श्रेणी प्रचंड आहे — HTTP वर तुम्ही जे काही कॉल करू शकता ते सगळे पात्र ठरते. REST ही त्या श्रेणीच्या *आत* असलेली, त्या सहा निर्बंधांसह असलेली एक विशिष्ट आर्किटेक्चरल शैली आहे [8].

जेव्हा तुमचे API resources भोवती रचलेले असते, verbs योग्यरीत्या वापरते, आणि JSON परत करते, पण hypermedia करत नाही, तेव्हा तुमच्याकडे प्रत्यक्षात असते एक **REST conventions पाळणारे HTTP API** [10]. काही लोक त्याला "REST-like" म्हणतात, काही "pragmatic REST" म्हणतात, आणि काही फक्त त्याला RESTful म्हणत राहतात कारण तोच शब्द सर्वांना समजतो [9]. अनौपचारिक वापरात यातील एकही चुकीचे नाही. ते फक्त तुम्ही शिडीवर कुठे बसला आहात याबद्दल अधिक प्रामाणिक आहेत.

बेन मॉरिसचा [pragmatic REST वरील एक भक्कम लेख](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/) आहे, जो असा युक्तिवाद करतो की hypermedia वगळणे हे बहुतांश टीमसाठी एक जाणीवपूर्वक, वाजवी तडजोड आहे, अपयश नव्हे [9]. मला सहमत व्हावेसे वाटते, आणि का ते मी सांगतो.

## जवळपास कोणीही संपूर्ण HATEOAS का करत नाही

जर पातळी ३ हेच "खरे" REST असेल, तर मुळात संपूर्ण उद्योग पातळी २ वरच का थांबतो? काही प्रामाणिक कारणे:

- **Clients प्रत्यक्षात गतिमानपणे navigate करत नाहीत.** HATEOAS चे स्वप्न म्हणजे असा एक सामान्य client जो links चे अनुसरण करून runtime ला API शोधतो. प्रत्यक्षात, तुमची frontend टीम एका ज्ञात contract नुसार आवश्यक endpoints हार्डकोड करते. links तिथे न वापरता पडून राहतात.
- **अस्पष्ट फायद्यासाठी अधिक काम.** सगळीकडे `_links` अंतर्भूत करणे, HAL सारखे hypermedia format निवडणे, relation types सुसंगत ठेवणे — हे खरे प्रयत्न आहेत [8]. जर कोणताही consumer वर्तन चालवण्यासाठी links वापरत नसेल, तर तुम्ही विनाकारण वजन वाढवले आहे.
- **Documentation आणि tooling जिंकले.** OpenAPI/Swagger clients ला runtime links ऐवजी एका spec फाइलद्वारे discoverability देते. फिल्डिंगच्या मनात जे होते ते हे नाही, पण लोकांच्या व्यावहारिक समस्येचे यामुळे निराकरण झाले.
- **मोठ्या खेळाडूंनी ते कधीच केले नाही.** जेव्हा पृथ्वीवरील सर्वाधिक कॉपी केले जाणारे API hypermedia वगळतात [8], तेव्हा प्रबंध काहीही म्हणत असला तरी तेच वास्तविक मानक बनते.

तरीही एक खरा प्रतिमुद्दा आहे, आणि मला त्याच्याशी अन्याय करायचा नाही. पातळी ३ वर API *अस्तित्वात आहेत*, आणि काही मोठे त्या दिशेने झुकतात — GitHub चे API प्रसिद्धपणे आपल्या responses मध्येच संबंधित resources ची URLs अंतर्भूत करते जेणेकरून तुम्ही स्वतः URLs बनवण्याऐवजी त्यांचे अनुसरण करू शकता. जेव्हा तुमच्याकडे खरोखरच असे अनेक स्वतंत्र clients असतात जे तुमच्या नियंत्रणात नाहीत, किंवा असे दीर्घकाळ टिकणारे API असते जिथे तुम्हाला प्रत्येकाला न तोडता resources इकडेतिकडे हलवायचे असतात, तेव्हा hypermedia आपली किंमत वसूल करते. फिल्डिंगने ज्या decoupling बद्दल सांगितले ते शैक्षणिक नाही — समन्वित client redeploy शिवाय URLs बदलण्याचे स्वातंत्र्य सर्व्हर असेच राखतो [1][12]. बहुतांश अंतर्गत API ला त्या स्वातंत्र्याची इतकी गरज कधी पडतच नाही की त्यासाठी किंमत मोजावी.

## एक ठोस दृष्टिक्षेप: एकच endpoint, तीन पातळ्या

हे थोडे कमी अमूर्त करू द्या. समजा तुम्ही एखादी order आणत आहात. प्रत्येक maturity पातळी साधारणपणे कशी दिसते ते इथे आहे.

**पातळी ० — दलदल.** एकच endpoint, सगळे POST, verbs body मध्ये राहतात:

```
POST /api
{ "action": "getOrder", "id": 42 }
```

**पातळी २ — जिथे बहुतांश "RESTful" API राहतात.** खरी resource URL, खरा verb, खरा status code:

```
GET /orders/42

200 OK
{ "id": 42, "status": "shipped", "customerId": 7 }
```

**पातळी ३ — hypertext-driven.** तोच डेटा, पण response client ला पुढे काय करता येईल ते सांगते:

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

फरक दिसतो का? पातळी ३ वर, cancelling `/orders/42/cancel` वर असते हे client ला *माहीत* असण्याची गरज नाही. सर्व्हरने त्याला सांगितले. आणि महत्त्वाचे म्हणजे, जर order आधीच shipped असेल, तर सर्व्हर फक्त `cancel` link *वगळू* शकतो — आता उपलब्ध actions state नुसार चालवल्या जातात, हाच "hypermedia as the engine of application state" चा अक्षरशः अर्थ आहे [1][8]. लोकांकडून निसटणारा खरोखरच हुशार भाग तोच आहे. हे responses ला links नी सजवण्याबद्दल नाही. हे पुढे काय शक्य आहे ते सर्व्हर नियंत्रित करण्याबद्दल आहे.

## मग तुम्ही तुमच्या API ला प्रत्यक्षात काय म्हणावे?

या गोष्टी अनेक वर्षे बनवल्यानंतर हे माझे ठाम मत.

- **जर ते पातळी २ असेल, तर अनौपचारिक लेखनात त्याला "RESTful" म्हणणे ठीक आहे.** तुम्हाला काय म्हणायचे आहे ते प्रत्येकाला समजते, आणि संपूर्ण उद्योगाच्या वापराशी झगडणे ही हरणारी लढाई आहे. शब्दाचा अर्थ बदलला आहे, आणि ते ठीक आहे.
- **तांत्रिकदृष्ट्या अचूक राहायचे असेल, तर "REST-like" किंवा "REST conventions पाळणारे HTTP API" म्हणा.** Hacker News वरील पंडित अजूनही वाद घालतील, पण तुम्ही बरोबर असाल [7].
- **गंभीर चेहऱ्याने "REST API" हे फक्त पातळी ३ साठी राखून ठेवा.** जर कोणी काटेकोर असेल आणि विचारेल "हे *REST* API आहे का," आणि तुम्ही hypermedia करत नसाल, तर प्रामाणिक उत्तर आहे "नाही, ते REST-like आहे" [1][7].

ज्याला मी सर्वात कडाडून विरोध करेन ते म्हणजे नियम अस्तित्वातच नाहीत असे *भासवणे*. बऱ्याच टीम एखाद्या गोष्टीला RESTful म्हणतात, हे माहीत नसताना की त्या एक HATEOAS निर्बंध वगळत आहेत. तो जाणीवपूर्वक वगळणे हा एक उत्तम engineering निर्णय आहे. तो अस्तित्वात आहे हे कधी कळलेच नाही म्हणून वगळणे म्हणजे फक्त चांगल्या मार्केटिंगसह अज्ञान.

## जे नियम तुम्ही खरोखर मोडू नयेत

सर्व निर्बंध समान नाहीत, आणि इथे मी स्पष्टपणे सांगेन की चालत्या API साठी प्रत्यक्षात काय महत्त्वाचे आहे आणि काय वगळणे सुरक्षित आहे.

- **Statelessness — हे मोडू नका.** ज्या क्षणी तुमचा सर्व्हर requests दरम्यान client state लक्षात ठेवू लागतो, त्या क्षणी तुम्ही horizontal scaling गमावता, layered-system चे फायदे गमावता, आणि तुम्ही REST ला अशा रीतीने मागे सोडले आहे की जे तुम्हाला operationally दुखावते [2][12]. याला खरोखर दात आहेत.
- **HTTP verbs आणि status codes चा योग्य वापर — हे ही मोडू नका.** डेटा बदलणारे GET हे एक प्रत्यक्ष bug आहे जे घडण्याची वाट पाहत आहे, कारण caches आणि crawlers गृहीत धरतात की GET सुरक्षित आहे. ही पातळी १-ते-२ ची गोष्ट आहे आणि ती किमान अपेक्षा आहे.
- **Cacheability — याचा आदर करा.** योग्य cache headers सेट करणे कमी कष्टाचे आहे आणि वेबला स्केल करू देणाऱ्या गोष्टींपैकी ती एक आहे. त्याकडे दुर्लक्ष करणे म्हणजे performance फुकट सोडणे [3].
- **HATEOAS — जाणीवपूर्वक वगळणे ठीक आहे.** हाच तो आहे जो जवळपास प्रत्येकजण वगळतो, आणि बहुतांश API साठी ती एक बचावता येणारी तडजोड आहे [9]. फक्त तसे करताना संपूर्ण REST असल्याचा दावा करू नका.

नमुना लक्षात येतो का? जे निर्बंध *operational* गुणधर्मांचे रक्षण करतात — statelessness, caching, योग्य verbs — तेच मोडल्यावर तुम्हाला प्रत्यक्षात वेदना जाणवते. जो निर्बंध केवळ *evolvability आणि discoverability* बद्दल आहे — HATEOAS — त्याशिवाय तुम्ही सहसा जगू शकता. हा योगायोग नाही. उद्योग जिथे स्थिरावला तिथे का स्थिरावला याचे कारण तेच आहे.

## हे तुम्हाला कुठे आणून सोडते

"RESTful" हा शब्द फार पूर्वीच binary राहिलेला नाही. फिल्डिंगकडे एक काटेकोर व्याख्या आहे जी म्हणते hypertext किंवा काहीच नाही [1], आणि विकसकांच्या जगाचा बराच मोठा भाग शांतपणे त्याकडे दुर्लक्ष करतो कारण पातळी २ त्यांच्या समस्या व्यवस्थित सोडवते [7][8]. दोन्ही बाजू खोटे बोलत नाहीत — त्या एकाच शब्दाचा वापर दोन वेगवेगळ्या पातळ्यांसाठी करत आहेत.

तर सर्व नियम पाळले नाहीत तरी तुम्ही तुमच्या API ला अजूनही RESTful म्हणू शकता का? प्रत्यक्षात, हो, आणि तुम्ही प्रचंड बहुमतात असाल. फक्त तुम्ही कोणता नियम वगळत आहात हे जाणा, हे जाणा की एखादा शुद्धतावादी तुम्हाला खडसावेल, आणि हे जाणा की तुम्ही जो वगळत असाल — HATEOAS — तोच नेमका तो आहे जो रॉय फिल्डिंगने म्हटले की तुम्ही वगळू शकत नाही. ते तुम्हाला त्रासदायक वाटते की नाही हे पूर्णपणे यावर अवलंबून आहे की तुम्ही एका काटेकोर आर्किटेक्चर रिव्ह्यूसाठी लिहीत आहात की लोक प्रत्यक्षात वापरतील असे सॉफ्टवेअर पाठवत आहात.

मी सहसा कोणत्या बाजूला असतो हे मला माहीत आहे. पण मी काय वगळत आहे हे तरी मला माहीत आहे.

> End

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