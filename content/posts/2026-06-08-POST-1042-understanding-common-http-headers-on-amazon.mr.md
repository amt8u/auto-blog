+++
title       = "Amazon वरील सामान्य HTTP Headers समजून घेणे"
description = "मी Amazon च्या add-to-cart endpoint वर curl चालवले आणि प्रत्येक response header वाचले. प्रत्येक header काय करते, ते का महत्त्वाचे आहे, आणि Amazon च्या निवडी कुठे रोचक ठरतात ते इथे आहे."
date        = "2026-06-08T00:25:52+05:30"
slug          = "understanding-common-http-headers-on-amazon"
tags          = ["http", "web-security", "headers", "amazon"]
keywords      = ["http headers", "amazon http headers", "response headers", "security headers", "cloudfront headers"]
canonical     = "/mr/posts/understanding-common-http-headers-on-amazon/"
feature_image = "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=1600&q=80"
+++

तुम्ही एखाद्या वेबसाइटला पाठवलेल्या प्रत्येक request सोबत तुम्हाला कधीही न दिसणारा metadata चा एक छोटा ढीग असतो. Headers. तुमचे connection encrypted आहे की नाही, एखादे page iframe मध्ये embed करता येईल की नाही, कोणत्या CDN edge ने तुम्हाला serve केले, आणि browser ने एखादे cookie वर्षभर लक्षात ठेवावे की नाही — हे सगळे तेच ठरवतात. एखादी खरीखुरी, गजबजलेली production site काय पाठवते हे मला बघायचे होते, म्हणून मी `curl` एका Amazon endpoint कडे रोखले आणि response headers बाहेर काढले. लक्षात आले की उलगडण्यासारखे बरेच काही आहे.

## मी प्रत्यक्षात काय चालवले

मी Amazon India च्या एका internal "add to cart" config endpoint ला साधी GET request पाठवली आणि curl ला फक्त response headers print करायला सांगितले:

```bash
curl -s -D - -o /dev/null \
  "https://www.amazon.in/cart/add-to-cart/patc-config?clientName=SiteWideActionExecutor&ref_=ax_patc_cfg" \
  -A "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
```

`-D -` headers stdout वर काढते, आणि `-o /dev/null` body फेकून देते (मला इथे फक्त headers ची काळजी आहे). साधारणपणे जे परत आले ते इथे आहे:

```http
HTTP/2 200
content-type: application/json;charset=UTF-8
date: Sun, 07 Jun 2026 18:55:58 GMT
server: Server
x-amz-rid: BE1Q4YXSQ0DKN83F4JYQ
set-cookie: session-id=259-8655047-0491149; Domain=.amazon.in; Expires=...; Path=/; Secure
set-cookie: session-id-time=2082787201l; Domain=.amazon.in; Expires=...; Path=/; Secure
set-cookie: i18n-prefs=INR; Domain=.amazon.in; Expires=...; Path=/
set-cookie: lc-acbin=en_IN; Domain=.amazon.in; Expires=...; Path=/
x-content-type-options: nosniff
x-xss-protection: 1;
accept-ch: ect,rtt,downlink,device-memory,...,sec-ch-ua-platform-version
accept-ch-lifetime: 86400
content-security-policy-report-only: default-src 'self' blob: https: data: ...;report-uri https://metrics.media-amazon.com/
content-encoding: gzip
content-security-policy: upgrade-insecure-requests;report-uri https://metrics.media-amazon.com/
strict-transport-security: max-age=47474747; includeSubDomains; preload
vary: X-Amazon-Wtm-Tag-...,Accept-Encoding,User-Agent
x-frame-options: SAMEORIGIN
x-cache: Miss from cloudfront
via: 1.1 db8e720c1e186c4a9d38db72ecaa0492.cloudfront.net (CloudFront)
x-amz-cf-pop: BOM78-P2
alt-svc: h3=":443"; ma=86400
x-amz-cf-id: 4UqtO1tdgZlbHdAUl2W47T2W4MGf7vb-mx2Y-KEevkHqCcCyhE_b0Q==
```

मूलतः एका config endpoint साठी हे आश्चर्यकारकरीत्या दाट response आहे. मी या सगळ्यांना गटांमध्ये विभागून समजावतो, कारण यांतले काही इतरांपेक्षा खूप जास्त महत्त्वाचे आहेत.

## कंटाळवाण्या-पण-अत्यावश्यक मूलभूत गोष्टी

### content-type

`content-type: application/json;charset=UTF-8` client ला सांगते की body मध्ये कोणत्या प्रकारचा data आहे आणि तो कसा decode करायचा. ऐकायला किरकोळ वाटते, पण ते load-bearing आहे. response JSON म्हणून parse करायचे, HTML म्हणून render करायचे, की download म्हणून हाताळायचे हे ठरवण्यासाठी browser याचा वापर करते. `charset=UTF-8` हा भाग character encoding ठरवतो जेणेकरून accented characters आणि non-Latin scripts बरोबर येतात.

मुद्दा हा आहे — server जर content type बद्दल खोटे बोलला किंवा अस्पष्ट राहिला, तर पूर्वी browsers body "sniff" करून अंदाज लावायचे. तो अंदाज लावणे थांबवण्यासाठीच `x-content-type-options: nosniff` (याबद्दल खाली अधिक) अस्तित्वात आहे.

### date आणि server

`date` म्हणजे server ने response तयार केल्याचा त्याचा timestamp इतकेच आहे. Caches याचा वापर freshness च्या गणितासाठी करतात.

`server: Server` हा या संपूर्ण dump मधला माझा आवडता रुक्ष विनोद आहे. बहुतेक servers अभिमानाने स्वतःची घोषणा करतात — `Server: nginx/1.24.0` किंवा `Server: Apache/2.4`. Amazon चे frontend त्याऐवजी अक्षरशः `Server` हा शब्द परत करते. ती जाणूनबुजून केलेली obfuscation आहे. एखाद्या attacker ला ज्ञात CVEs विरुद्ध फुकटात version-number lookup का द्यायचा? म्हणून ते ते एका निरुपयोगी गोष्टीपर्यंत कापून टाकतात. छोटी गोष्ट आहे, पण कोणीतरी याबद्दल विचार केला हे ती सांगते.

### content-encoding

`content-encoding: gzip` म्हणजे body पाठवण्यापूर्वी gzip ने compress केली होती. तुमचे client ती पारदर्शकपणे decompress करते. म्हणूनच wire वर response हे प्रत्यक्ष JSON पेक्षा लहान असते. काही विलक्षण नाही, पण ते पुढे येणाऱ्या `Vary` header सोबत थेट जोडले जाते — आणि ती जोडी जिथे लोक अडखळतात ती आहे.

### x-amz-rid

`x-amz-rid: BE1Q4YXSQ0DKN83F4JYQ` हे Amazon-विशिष्ट request ID आहे. हे एक internal correlation token आहे. काही बिघडले आणि तुम्ही support ticket दाखल केले, तर त्यांचे engineers त्यांच्या logs मध्ये grep करतात ती हीच string असते. शेवटी CloudFront headers सोबत याच कल्पनेची पुनरावृत्ती तुम्हाला दिसेल — आधुनिक infra एका विशिष्ट request ला डझनभर systems मधून trace करता येण्याच्या वेडाने झपाटलेले आहे.

## Cookies: चार Set-Cookie headers

Amazon या एकाच response मध्ये चार cookies set करते. [`Set-Cookie` header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) ही अशी पद्धत आहे जिथे server browser ला एखादे value साठवायला आणि पुढच्या requests वर ते परत पाठवायला सांगते. value नंतरचे प्रत्येक attribute cookie कसे वागते ते tune करते:

| Attribute | ते काय करते |
|---|---|
| `Domain=.amazon.in` | Cookie amazon.in **आणि त्याच्या सर्व subdomains** ला पाठवले जाते |
| `Expires=...2027...` | Persistent cookie — त्या तारखेपर्यंत browser restarts टिकून राहते |
| `Path=/` | Site वरील प्रत्येक path साठी पाठवले जाते |
| `Secure` | फक्त HTTPS वर पाठवले जाते, कधीही plain HTTP वर नाही |

दोन रोचक:

- **`session-id` आणि `session-id-time`** दोघांकडेही `Secure` flag आहे. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) नुसार, `Secure` cookie फक्त encrypted HTTPS requests सोबतच जोडले जाते, जे एखाद्या on-path attacker ला चुकून झालेल्या HTTP request मधून ते sniff करण्यापासून रोखते. session identifier साठी — जे प्रत्यक्षात तुमची logged-in state *आहे* — हे तुम्हाला हवे असलेले किमान आहे.
- **`i18n-prefs=INR` आणि `lc-acbin=en_IN`** ही preference cookies आहेत: चलन Rupees मध्ये, locale English-India. लक्षात घ्या की या दोघांकडे `Secure` *नाही*. हा वाजवी निर्णय आहे — कोणाला INR आवडते हे जाणून घेणे संवेदनशील नाही, आणि तो hijacking चा धोका नाही.

एक बारकावा नमूद करण्यासारखा आहे. आरंभी ठिपका असलेले `Domain=.amazon.in` या cookies ला प्रत्येक subdomain वर उपलब्ध करते — `www.amazon.in`, `sellercentral.amazon.in`, वगैरे. अनेक subdomains वर पसरलेल्या service साठी ते हेतुपुरस्सर आहे, पण तो असाही निर्णय आहे जो तुम्हाला जाणीवपूर्वक घ्यायचा असतो, कारण खूप व्यापकपणे scope केलेले cookie काही leak झाल्यास मोठ्या blast radius चे ठरते. तुम्हाला औपचारिक आवृत्ती हवी असेल तर [RFC 6265](https://tools.ietf.org/html/rfc6265) spec हे सर्व वर्तन नियंत्रित करते.

इथे लक्षणीयरीत्या अनुपस्थित: `HttpOnly` आणि `SameSite`. ते सहसा प्रत्यक्ष login दरम्यान set होणाऱ्या अधिक संवेदनशील auth cookies वर दिसतात, यासारख्या config endpoint वर नाही. म्हणून *या* विशिष्ट response मधल्या त्यांच्या अनुपस्थितीत फार अर्थ शोधू नका.

## Security headers — रोचक भाग

इथे response खरोखर अभ्यास करण्यासारखे होते, कारण Amazon defensive headers चा एक stack पाठवते आणि त्यांतल्या दोघांना इतिहास आहे.

### strict-transport-security

```http
strict-transport-security: max-age=47474747; includeSubDomains; preload
```

[HSTS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security) browser ला सांगते: "आतापासून, माझ्याशी फक्त HTTPS वरच बोल. कोणी तुला माझ्यासाठी `http://` link दिली, तर request machine सोडण्याआधीच ती HTTPS वर upgrade कर." इथे तीन directives आहेत:

- **`max-age=47474747`** — हा नियम ~550 दिवस लक्षात ठेव (तो आकडा फक्त `47474747` seconds आहे; कोणाला तरी पुनरावृत्त अंक स्पष्टपणे आवडले).
- **`includeSubDomains`** — नियम प्रत्येक subdomain ला सुद्धा लागू.
- **`preload`** — Amazon ला browsers च्या hardcoded HSTS lists मध्ये बसवायचे आहे, जेणेकरून तुमची *अगदी पहिली* भेट सुद्धा कोणत्याही insecure पहिल्या request शिवाय HTTPS वर सक्तीने होते.

हे इतके का महत्त्वाचे आहे? HSTS शिवाय, `amazon.in` ला तुमची पहिली request plain HTTP म्हणून जाऊ शकते आणि HTTPS कडे redirect होण्याआधी hijack होऊ शकते — क्लासिक SSL-stripping attack. [OWASP HSTS cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html) हा धोका चांगला समजावतो. एक अडचण: HSTS header plain HTTP वर आला तर browsers त्याकडे *दुर्लक्ष* करतात, खास म्हणजे जेणेकरून एखादा man-in-the-middle बनावट header inject करू शकत नाही. ते फक्त आधीच secure असलेल्या connection वर आल्यासच गणले जाते.

### दोन Content-Security-Policy headers

हा भाग मला सर्वात बोलका वाटला. Amazon enforcing policy आणि report-only policy **दोन्ही** पाठवते:

```http
content-security-policy: upgrade-insecure-requests;report-uri https://metrics.media-amazon.com/
content-security-policy-report-only: default-src 'self' blob: https: data: ...;report-uri https://metrics.media-amazon.com/
```

enforcing वाली जाणूनबुजून अगदी छोटी आहे. [`upgrade-insecure-requests`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/upgrade-insecure-requests) browser ला सांगते की fetch करण्यापूर्वी प्रत्येक `http://` sub-resource (images, scripts, काहीही) `https://` वर rewrite कर. इतकी जुनी आणि इतक्या legacy URLs तरंगणाऱ्या site वर, प्रत्येक एक हाताने fixing करणे वेडेपणा ठरेल — म्हणून ते browser ला ते सगळे एकत्रितपणे upgrade करू देतात.

दुसरे header हा हुशार भाग आहे. [`Content-Security-Policy-Report-Only`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) **काहीही block करत नाही**. ते एक कडक trial policy (`default-src 'self' ...`) चालवते आणि, जेव्हा जेव्हा काहीतरी block *झाले असते*, तेव्हा `report-uri` वर JSON violation report POST करते. live site न मोडता घट्ट CSP असे roll out करायची पद्धत हीच आहे:

1. कडक policy report-only mode मध्ये deploy करा.
2. violation reports तुमच्या metrics endpoint मध्ये येताना बघा.
3. त्याला अडवणाऱ्या वैध गोष्टी fix करा.
4. एकदा ते शांत झाले की, ते enforcing header मध्ये promote करा.

मूलतः खऱ्या विमानाला बांधण्यापूर्वी कडक policy एका wind tunnel मध्ये चालवण्यासारखे हे आहे. `report-uri` directive तांत्रिकदृष्ट्या [`report-to` च्या बाजूने deprecated](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/report-uri) आहे, पण अजूनही त्यावर अवलंबून असलेल्या अनेक browsers साठी ते ठेवले आहे.

### x-content-type-options: nosniff

लहान header, खरे दात. [`nosniff`](https://www.keycdn.com/support/x-content-type-options) browser ला सांगते की **`Content-Type` वर विश्वास ठेव आणि कधीही अंदाज लावू नकोस**. त्याशिवाय, browser `text/plain` म्हणून serve केलेली file बघून ती "HTML किंवा JavaScript सारखी दिसते" असे ठरवून ती execute करू शकते — एक MIME-confusion attack. एखादा attacker परत serve होणारी file upload करू शकत असेल, तर content sniffing हीच ती पद्धत जिथे निरुपद्रवी दिसणारे upload running script बनते. `nosniff` तो दरवाजा धाडकन बंद करते.

### x-frame-options: SAMEORIGIN

[`X-Frame-Options: SAMEORIGIN`](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html) हे page `<frame>` किंवा `<iframe>` मध्ये कोणाला load करता येईल हे नियंत्रित करते. `SAMEORIGIN` म्हणजे फक्त Amazon pages च इतर Amazon pages ला frame करू शकतात — `evil-site.com` करू शकत नाही. हे **clickjacking** विरुद्धचे मुख्य संरक्षण आहे, जिथे attacker तुमच्या खऱ्या page वर अदृश्यपणे overlay करतो आणि तुम्ही दुसरे काहीतरी click करत आहात असे वाटत असताना तुम्हाला "Buy now" किंवा "Confirm" click करायला फसवतो. shopping cart endpoint साठी, त्यांना का काळजी आहे हे तुम्हाला नेमके दिसते.

### x-xss-protection: 1

आता, `x-xss-protection: 1` हे विसंगत आहे, आणि प्रामाणिकपणे ते थोडे अवशेष आहे. हे जुन्या Internet Explorer, Chrome आणि Safari चे एक feature होते जे reflected XSS शोधून page block करायचा प्रयत्न करायचे. अडचण — आणि security मंडळी याबद्दल स्पष्ट राहिली आहेत — ती की filter स्वतःच अन्यथा-सुरक्षित pages मध्ये [vulnerabilities आणण्यासाठी गैरवापर होऊ शकतो](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html). आधुनिक मार्गदर्शन असे की एकतर ते बंद करा (`0`) किंवा ते पाठवूच नका, आणि त्याऐवजी खऱ्या Content-Security-Policy वर भिस्त ठेवा. Amazon अजूनही `1` पाठवते, बहुधा प्राचीन browsers च्या long tail साठी. मी हे नवीन project मध्ये copy करणार नाही.

![amazon security headers](/images/posts/understanding-common-http-headers-on-amazon/amazon-security-headers.svg)

## Performance आणि protocol headers

### accept-ch आणि accept-ch-lifetime

```http
accept-ch: ect,rtt,downlink,device-memory,...,sec-ch-ua-platform-version
accept-ch-lifetime: 86400
```

हे [Client Hints](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-CH) आहे. `Accept-CH` सोबत, server म्हणत आहे: "तुझ्या पुढच्या requests वर, कृपया मला तुझा network speed (`ect`, `rtt`, `downlink`), तुझ्याकडे किती device memory आहे (`device-memory`), आणि काही user-agent तपशील सुद्धा सांग." मग Amazon ते काय serve करते ते tailor करू शकते — उदाहरणार्थ, slow `2g` connection वर हलकी images.

`accept-ch-lifetime: 86400` म्हणजे ही प्राधान्यता एक दिवस लक्षात ठेव. जाणून घेण्यासारखे: `Accept-CH-Lifetime` हे [यापुढे शिफारस केलेले नाही आणि spec मधून बहुतांश काढले आहे](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-CH), पण compatibility साठी पुष्कळ sites अजूनही ते पाठवतात. Client Hints फक्त secure connection वरच काम करतात, आणि फक्त first-party origin ला पाठवले जातात — एक privacy guardrail जेणेकरून यादृच्छिक third parties तुमच्या device चे चुपचाप fingerprint करू शकत नाहीत.

### vary

```http
vary: X-Amazon-Wtm-Tag-...,Accept-Encoding,User-Agent
```

[`Vary` header](https://www.fastly.com/blog/best-practices-using-vary-header) हे तेच आहे जे लोक विसरले की चुपचाप caches मोडते. ते Amazon आणि तुमच्यामधल्या प्रत्येक cache ला सांगते: "हे response या request headers वर अवलंबून आहे, म्हणून तुझ्या cached प्रती त्यांवर key कर."

- **`Accept-Encoding`** — gzip body आणि Brotli body वेगवेगळे लक्षात ठेव. याशिवाय, cache एका client ला gzip blob देऊ शकते ज्याने वेगळे काहीतरी मागितले होते. response हे gzip-encoded *असल्याने*, ही नोंद खरे काम करत आहे.
- **`User-Agent`** — mobile आणि desktop browser मध्ये response वेगळे असू शकते, म्हणून त्यांना वेगवेगळे cache कर.

तज्ञ पुन्हा पुन्हा सांगणारी एक छोटी सावधगिरी: `Vary: User-Agent` हे एक [बोथट हत्यार](https://www.smashingmagazine.com/2017/11/understanding-vary-header/) आहे. तिथे प्रत्यक्षात अमर्याद User-Agent strings आहेत, म्हणून प्रत्येक browser version मागे जवळपास-अद्वितीय प्रत साठवून हे तुमचा cache hit rate फाडून टाकू शकते. स्वतःची CDN logic असलेल्या मोठ्या sites ला ते परवडते; छोट्या site वर मी दोनदा विचार करेन.

### alt-svc

```http
alt-svc: h3=":443"; ma=86400
```

[`Alt-Svc`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Alt-Svc) हा handshake आहे जो HTTP/3 ला bootstrap करतो. ही request HTTP/2 वर परत आली, पण हे header म्हणजे Amazon ची कुजबुज: "अरे, मी port 443 वर `h3` (QUIC वरील HTTP/3) सुद्धा बोलतो — पुढच्या 86400 seconds साठी ते बिनधास्त वापर." सक्षम browser पार्श्वभूमीत चुपचाप HTTP/3 चा प्रयत्न करेल आणि, ते connect झाले तर, अधिक जलद, कमी-latency requests साठी त्यावर switch होईल. [bagder च्या HTTP/3 guide](https://http3-explained.haxx.se/en/h3/h3-altsvc) मध्ये म्हटल्याप्रमाणे, जे clients ते support करत नाहीत त्यांच्यासाठी काहीही न मोडता upgrade असे घडते.

## CloudFront ची पाऊलवाट

शेवटचा गठ्ठा तुम्हाला सांगतो की Amazon हे स्वतःच्या CDN, [CloudFront](https://aws.amazon.com/blogs/networking-and-content-delivery/amazon-cloudfront-introduces-response-headers-policies/) मार्फत serve करत आहे:

| Header | Value | अर्थ |
|---|---|---|
| `x-cache` | `Miss from cloudfront` | edge cache मध्ये नाही — origin वरून fetch केले |
| `via` | `1.1 ...cloudfront.net (CloudFront)` | एका CloudFront proxy ने request हाताळली |
| `x-amz-cf-pop` | `BOM78-P2` | Mumbai (BOM) edge location वरून serve केले |
| `x-amz-cf-id` | `4UqtO1...` | या नेमक्या request साठी opaque trace ID |

इथे काही गोष्टी जागेवर बसतात:

- **`x-cache: Miss`** अर्थपूर्ण आहे — personalised cart-config endpoint cache होऊन प्रत्येकाला serve होऊ नये, म्हणून miss होणे हे *बरोबर* वर्तन आहे, समस्या नाही.
- **`x-amz-cf-pop: BOM78`** [IATA airport codes](https://http.dev/x-amz-cf-pop) वापरते. `BOM` म्हणजे Mumbai. मी भारतात आहे, म्हणून CloudFront ने मला सर्वात जवळच्या edge कडे route केले — CDN ने जे करायला हवे तेच नेमके. `-P2` suffix cache tier दर्शवते.
- **`x-amz-cf-id`** हे आधीच्या `x-amz-rid` चे CloudFront भावंड आहे — एक [encrypted, opaque token](https://http.dev/x-amz-cf-id) ज्याचा मला काही अर्थ नाही पण AWS Support ला त्यांच्या logs मधून ही नेमकी request काढायला देतो. pattern लक्षात घ्या: प्रत्येक layer स्वतःचा trace ID शिक्का मारतो. CDN, frontend, आणि backend मधून गेलेली request धागा न गमावता debug करण्याची पद्धत ती अतिरिक्तता आहे.

## तर सारांश काय?

एका टाकाऊ config request साठी, Amazon ने encryption ची सक्ती, XSS/clickjacking संरक्षणाचे तीन प्रकार, बाजूबाजूला चालणाऱ्या दोन CSP strategies, cookie scoping, client-hint negotiation, HTTP/3 ची जाहिरात, आणि संपूर्ण CDN trace trail परत पाठवले. यांतले काहीही विलक्षण नाही — इथले प्रत्येक header [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP) वर documented आहे आणि बहुतेक अशा गोष्टी आहेत ज्या तुम्ही स्वतः switch on करू शकता. फरक हा की Amazon *सगळे* चालू करते, defence-in-depth शैलीत, आणि पुढची आवळणी enforce होण्याआधी ती test करण्यासाठी एक report-only CSP सुद्धा पाठवते.

तुम्ही production मध्ये काही चालवत असाल, तर हा dump एक चांगली checklist आहे. preload सोबत HSTS, `nosniff`, एक खरी CSP, `X-Frame-Options`, `Secure` cookies, आणि एक समजूतदार `Vary` तुम्हाला बहुतांश वाटचाल करवून देतील. आणि कदाचित — Amazon प्रमाणे — त्याच ओघात तुमचे `Server` header एखाद्या भव्यपणे निरुपयोगी गोष्टीला set करा.

## स्रोत
1. [Strict-Transport-Security header - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security)
2. [HTTP Strict Transport Security - OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html)
3. [Content-Security-Policy: upgrade-insecure-requests - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/upgrade-insecure-requests)
4. [Content Security Policy (CSP) Guide - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
5. [Content-Security-Policy: report-uri directive - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/report-uri)
6. [HTTP Headers Cheat Sheet - OWASP](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
7. [X-Content-Type-Options HTTP Header - KeyCDN](https://www.keycdn.com/support/x-content-type-options)
8. [Accept-CH header - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-CH)
9. [Set-Cookie header - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
10. [RFC 6265 - HTTP State Management Mechanism](https://tools.ietf.org/html/rfc6265)
11. [Best practices for using the Vary header - Fastly](https://www.fastly.com/blog/best-practices-using-vary-header)
12. [Understanding The Vary Header - Smashing Magazine](https://www.smashingmagazine.com/2017/11/understanding-vary-header/)
13. [Alt-Svc header - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Alt-Svc)
14. [Bootstrap with Alt-Svc - HTTP/3 explained](https://http3-explained.haxx.se/en/h3/h3-altsvc)
15. [X-Amz-Cf-Pop - http.dev](https://http.dev/x-amz-cf-pop)
16. [X-Amz-Cf-Id - http.dev](https://http.dev/x-amz-cf-id)
17. [Amazon CloudFront Response Headers Policies - AWS](https://aws.amazon.com/blogs/networking-and-content-delivery/amazon-cloudfront-introduces-response-headers-policies/)