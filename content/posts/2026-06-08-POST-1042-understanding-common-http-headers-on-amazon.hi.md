+++
title       = "Amazon पर आम HTTP हेडर्स को समझना"
description = "मैंने एक Amazon add-to-cart एंडपॉइंट पर curl चलाया और हर रिस्पॉन्स हेडर पढ़ा। यहाँ बताया गया है कि हर एक क्या करता है, क्यों मायने रखता है, और Amazon के चुनाव कहाँ दिलचस्प हो जाते हैं।"
date        = "2026-06-08T00:25:52+05:30"
slug          = "understanding-common-http-headers-on-amazon"
tags          = ["http", "वेब-सुरक्षा", "हेडर्स", "amazon"]
keywords      = ["http हेडर्स", "amazon http हेडर्स", "रिस्पॉन्स हेडर्स", "सुरक्षा हेडर्स", "cloudfront हेडर्स"]
canonical     = "/hi/posts/understanding-common-http-headers-on-amazon/"
feature_image = "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=1600&q=80"
+++

आप किसी भी वेबसाइट को जो भी रिक्वेस्ट भेजते हैं, उसके साथ मेटाडेटा का एक छोटा-सा ढेर जाता है जिसे आप कभी देखते नहीं। हेडर्स। ये तय करते हैं कि आपका कनेक्शन एन्क्रिप्टेड है या नहीं, कोई पेज iframe में एम्बेड हो सकता है या नहीं, किस CDN एज ने आपको सर्व किया, और ब्राउज़र को कोई कुकी एक साल तक याद रखनी चाहिए या नहीं। मैं देखना चाहता था कि एक असली, व्यस्त प्रोडक्शन साइट क्या भेजती है, तो मैंने एक Amazon एंडपॉइंट पर `curl` चलाया और रिस्पॉन्स हेडर्स डंप कर दिए। पता चला कि समझने के लिए बहुत कुछ है।

## मैंने असल में क्या चलाया

मैंने Amazon India के आंतरिक "add to cart" config एंडपॉइंट्स में से एक पर एक सादी GET रिक्वेस्ट भेजी और curl से सिर्फ़ रिस्पॉन्स हेडर्स प्रिंट करने को कहा:

```bash
curl -s -D - -o /dev/null \
  "https://www.amazon.in/cart/add-to-cart/patc-config?clientName=SiteWideActionExecutor&ref_=ax_patc_cfg" \
  -A "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
```

`-D -` हेडर्स को stdout पर डंप करता है, और `-o /dev/null` बॉडी को फेंक देता है (यहाँ मुझे सिर्फ़ हेडर्स की परवाह है)। मोटे तौर पर यह वापस आया:

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

जो मूलतः एक config एंडपॉइंट है, उसके लिए यह आश्चर्यजनक रूप से सघन रिस्पॉन्स है। मैं इन्हें समूहों में समझाता हूँ, क्योंकि इनमें से कुछ दूसरों से कहीं ज़्यादा मायने रखते हैं।

## उबाऊ-पर-ज़रूरी बुनियादी बातें

### content-type

`content-type: application/json;charset=UTF-8` क्लाइंट को बताता है कि बॉडी में किस तरह का डेटा है और उसे कैसे डिकोड करना है। मामूली लगता है, पर यह भार उठाने वाला है। ब्राउज़र इसका उपयोग यह तय करने के लिए करता है कि रिस्पॉन्स को JSON के रूप में पार्स करे, HTML के रूप में रेंडर करे, या उसे डाउनलोड माने। `charset=UTF-8` हिस्सा कैरेक्टर एन्कोडिंग बताता है ताकि उच्चारण-चिह्न वाले अक्षर और गैर-लैटिन लिपियाँ सही तरीके से आएँ।

बात यह है — अगर कोई सर्वर कंटेंट टाइप के बारे में झूठ बोलता है या अस्पष्ट रहता है, तो पहले ब्राउज़र बॉडी को "सूँघकर" (sniff) अंदाज़ा लगाते थे। यही अंदाज़ा लगाना है जिसे `x-content-type-options: nosniff` (इस पर नीचे और) बंद करने के लिए मौजूद है।

### date और server

`date` बस सर्वर का टाइमस्टैम्प है कि उसने रिस्पॉन्स कब बनाया। कैश इसका उपयोग ताज़गी (freshness) के गणित के लिए करते हैं।

`server: Server` इस पूरे डंप में मेरा पसंदीदा सूखा मज़ाक है। ज़्यादातर सर्वर गर्व से अपना नाम बताते हैं — `Server: nginx/1.24.0` या `Server: Apache/2.4`। Amazon का फ्रंटएंड बजाय इसके शाब्दिक शब्द `Server` लौटाता है। यह जानबूझकर की गई अस्पष्टता है। किसी हमलावर को ज्ञात CVEs के विरुद्ध मुफ़्त वर्ज़न-नंबर लुकअप क्यों दें? तो वे इसे किसी बेकार चीज़ तक छोटा कर देते हैं। छोटी बात, पर यह बताती है कि किसी ने इस पर सोचा था।

### content-encoding

`content-encoding: gzip` का मतलब है कि बॉडी को भेजने से पहले gzip से कंप्रेस किया गया था। आपका क्लाइंट पारदर्शी रूप से इसे डीकंप्रेस करता है। इसीलिए रिस्पॉन्स तार पर (on the wire) असल JSON से छोटा होता है। कुछ भी अनोखा नहीं, पर यह सीधे आगे आने वाले `Vary` हेडर के साथ जुड़ता है — और यही जोड़ी वह जगह है जहाँ लोग फिसलते हैं।

### x-amz-rid

`x-amz-rid: BE1Q4YXSQ0DKN83F4JYQ` एक Amazon-विशिष्ट रिक्वेस्ट ID है। यह एक आंतरिक कोरिलेशन टोकन है। अगर कुछ टूटता है और आप सपोर्ट टिकट दर्ज करते हैं, तो यही वह स्ट्रिंग है जिसे उनके इंजीनियर अपने लॉग्स में grep करते हैं। आपको यही विचार अंत में CloudFront हेडर्स के साथ दोहराया हुआ दिखेगा — आधुनिक इंफ्रा एक विशिष्ट रिक्वेस्ट को दर्जन भर सिस्टमों के बीच ट्रेस करने में सक्षम होने को लेकर जुनूनी है।

## कुकीज़: चार Set-Cookie हेडर्स

Amazon इस एक ही रिस्पॉन्स में चार कुकीज़ सेट करता है। [`Set-Cookie` हेडर](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) वह तरीका है जिससे सर्वर ब्राउज़र से कोई वैल्यू स्टोर करने और भविष्य की रिक्वेस्ट्स पर वापस भेजने को कहता है। वैल्यू के बाद का हर एट्रिब्यूट यह तय करता है कि कुकी कैसे व्यवहार करे:

| एट्रिब्यूट | यह क्या करता है |
|---|---|
| `Domain=.amazon.in` | कुकी amazon.in **और इसके सभी सबडोमेन** को भेजी जाती है |
| `Expires=...2027...` | स्थायी कुकी — उस तारीख तक ब्राउज़र रीस्टार्ट के बाद भी बची रहती है |
| `Path=/` | साइट के हर पाथ के लिए भेजी जाती है |
| `Secure` | केवल HTTPS पर भेजी जाती है, सादे HTTP पर कभी नहीं |

दो दिलचस्प वाली:

- **`session-id` और `session-id-time`** दोनों में `Secure` फ्लैग है। [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) के अनुसार, एक `Secure` कुकी केवल एन्क्रिप्टेड HTTPS रिक्वेस्ट्स से जुड़ती है, जो किसी ऑन-पाथ हमलावर को इसे गलती से हुई HTTP रिक्वेस्ट से सूँघने से रोकती है। एक सेशन आइडेंटिफ़ायर के लिए — वह चीज़ जो प्रभावी रूप से आपकी लॉग-इन स्थिति *ही है* — यह न्यूनतम है जो आप चाहेंगे।
- **`i18n-prefs=INR` और `lc-acbin=en_IN`** प्रेफ़रेंस कुकीज़ हैं: रुपये में मुद्रा, लोकेल अंग्रेज़ी-भारत। ध्यान दें कि इन दोनों में `Secure` *नहीं* है। यह एक उचित फ़ैसला है — यह जानना कि कोई INR पसंद करता है, संवेदनशील नहीं है, और यह कोई हाइजैकिंग जोखिम नहीं है।

एक बारीकी जिसका ज़िक्र करना ज़रूरी है। शुरुआत में बिंदी (dot) के साथ `Domain=.amazon.in` इन कुकीज़ को हर सबडोमेन पर उपलब्ध कराता है — `www.amazon.in`, `sellercentral.amazon.in`, वगैरह। यह उस सेवा के लिए जानबूझकर किया गया है जो कई सबडोमेनों में फैली है, पर यह वैसा ही फ़ैसला है जिसे आप सचेत होकर लेना चाहेंगे, क्योंकि बहुत व्यापक रूप से स्कोप की गई कुकी का ब्लास्ट रेडियस बड़ा होता है अगर कुछ भी लीक होता है। यह सारा व्यवहार [RFC 6265](https://tools.ietf.org/html/rfc6265) स्पेक के तहत आता है अगर आप औपचारिक संस्करण चाहते हैं।

यहाँ ख़ास तौर पर अनुपस्थित: `HttpOnly` और `SameSite`। ये आम तौर पर असल लॉगिन के दौरान सेट होने वाली ज़्यादा संवेदनशील auth कुकीज़ पर दिखते हैं, इस जैसे config एंडपॉइंट पर नहीं। तो *इस* ख़ास रिस्पॉन्स में इनकी अनुपस्थिति में बहुत ज़्यादा मत पढ़िए।

## सुरक्षा हेडर्स — दिलचस्प हिस्सा

यहीं रिस्पॉन्स वाक़ई अध्ययन के लायक हो जाता है, क्योंकि Amazon रक्षात्मक हेडर्स का एक ढेर भेजता है और इनमें से कुछ का इतिहास रहा है।

### strict-transport-security

```http
strict-transport-security: max-age=47474747; includeSubDomains; preload
```

[HSTS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security) ब्राउज़र से कहता है: "अब से, मुझसे केवल HTTPS पर ही बात करना। अगर कोई तुम्हें मेरे लिए कोई `http://` लिंक थमाता है, तो रिक्वेस्ट मशीन से निकलने से पहले ही उसे HTTPS में अपग्रेड कर देना।" यहाँ तीन डायरेक्टिव हैं:

- **`max-age=47474747`** — इस नियम को ~550 दिनों तक याद रखो (वह संख्या बस `47474747` सेकंड है; किसी को दोहराते अंक स्पष्ट रूप से पसंद आए)।
- **`includeSubDomains`** — नियम हर सबडोमेन को भी कवर करता है।
- **`preload`** — Amazon चाहता है कि वह ब्राउज़रों की हार्डकोडेड HSTS सूचियों में बेक हो जाए, ताकि आपकी *सबसे पहली* विज़िट भी HTTPS के लिए मजबूर हो, बिना किसी असुरक्षित पहली रिक्वेस्ट के।

यह इतना मायने क्यों रखता है? HSTS के बिना, `amazon.in` पर आपकी पहली रिक्वेस्ट सादे HTTP के रूप में जा सकती है और HTTPS पर रीडायरेक्ट होने से पहले ही हाइजैक हो सकती है — क्लासिक SSL-stripping हमला। [OWASP HSTS चीट शीट](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html) इस जोखिम को अच्छी तरह समझाती है। एक पेच: अगर HSTS हेडर सादे HTTP पर आता है तो ब्राउज़र उसे *अनदेखा* कर देते हैं, ख़ासतौर पर इसलिए ताकि कोई मैन-इन-द-मिडल कोई फ़र्ज़ी हेडर इंजेक्ट न कर सके। यह केवल तभी गिना जाता है जब यह पहले से सुरक्षित कनेक्शन पर आता है।

### दो Content-Security-Policy हेडर्स

यही वह हिस्सा है जो मुझे सबसे बताने वाला लगा। Amazon **दोनों** भेजता है — एक लागू करने वाली (enforcing) पॉलिसी और एक रिपोर्ट-ओनली पॉलिसी:

```http
content-security-policy: upgrade-insecure-requests;report-uri https://metrics.media-amazon.com/
content-security-policy-report-only: default-src 'self' blob: https: data: ...;report-uri https://metrics.media-amazon.com/
```

लागू करने वाली वाली जानबूझकर छोटी है। [`upgrade-insecure-requests`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/upgrade-insecure-requests) ब्राउज़र से कहता है कि हर `http://` सब-रिसोर्स (इमेज, स्क्रिप्ट, जो भी हो) को फ़ेच करने से पहले `https://` में फिर से लिख दे। इतनी पुरानी साइट पर, जहाँ इतने सारे लेगेसी URLs इधर-उधर तैर रहे हैं, हर एक को मैन्युअली ठीक करना पागलपन होगा — तो वे ब्राउज़र को उन्हें थोक में अपग्रेड करने देते हैं।

दूसरा हेडर चतुर हिस्सा है। [`Content-Security-Policy-Report-Only`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) **कुछ भी ब्लॉक नहीं करता**। यह एक सख़्त परीक्षण पॉलिसी (`default-src 'self' ...`) चलाता है और, जब भी कुछ ब्लॉक *हुआ होता*, तो `report-uri` पर एक JSON उल्लंघन रिपोर्ट POST करता है। एक तंग CSP को बिना लाइव साइट तोड़े रोल आउट करने का यही तरीका है:

1. सख़्त पॉलिसी को रिपोर्ट-ओनली मोड में डिप्लॉय करो।
2. अपने मेट्रिक्स एंडपॉइंट पर आने वाली उल्लंघन रिपोर्ट्स को देखो।
3. जो वैध चीज़ें इससे टकराती हैं उन्हें ठीक करो।
4. एक बार शांत हो जाए, तो इसे लागू करने वाले हेडर में प्रमोट कर दो।

यह मूलतः सख़्त पॉलिसी को असल हवाई जहाज़ से बाँधने से पहले एक विंड टनल में चलाने जैसा है। `report-uri` डायरेक्टिव तकनीकी रूप से [`report-to` के पक्ष में अप्रचलित (deprecated) है](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/report-uri), पर इसे उन कई ब्राउज़रों के लिए रखा गया है जो अब भी इस पर निर्भर हैं।

### x-content-type-options: nosniff

छोटा हेडर, असली दाँत। [`nosniff`](https://www.keycdn.com/support/x-content-type-options) ब्राउज़र से कहता है कि **`Content-Type` पर भरोसा करो और कभी अंदाज़ा मत लगाओ**। इसके बिना, कोई ब्राउज़र `text/plain` के रूप में सर्व की गई फ़ाइल को देखकर तय कर सकता है कि यह HTML या JavaScript "जैसी दिखती है", और उसे चला दे — एक MIME-confusion हमला। अगर कोई हमलावर ऐसी फ़ाइल अपलोड कर सके जो वापस सर्व हो जाए, तो कंटेंट स्निफ़िंग ही वह तरीका है जिससे एक हानिरहित दिखने वाला अपलोड चलने वाली स्क्रिप्ट में बदल जाता है। `nosniff` उस दरवाज़े को बंद कर देता है।

### x-frame-options: SAMEORIGIN

[`X-Frame-Options: SAMEORIGIN`](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html) नियंत्रित करता है कि किसे इस पेज को `<frame>` या `<iframe>` के अंदर लोड करने की अनुमति है। `SAMEORIGIN` का मतलब है कि केवल Amazon पेज ही अन्य Amazon पेजों को फ़्रेम कर सकते हैं — `evil-site.com` नहीं कर सकता। यह **clickjacking** के विरुद्ध मूल बचाव है, जहाँ एक हमलावर अदृश्य रूप से आपके असली पेज को ओवरले कर देता है और आपको "Buy now" या "Confirm" क्लिक करने के लिए छलता है जबकि आपको लगता है कि आप कुछ और क्लिक कर रहे हैं। एक शॉपिंग कार्ट एंडपॉइंट के लिए, आप ठीक-ठीक देख सकते हैं कि वे इसकी परवाह क्यों करते हैं।

### x-xss-protection: 1

अब, `x-xss-protection: 1` अजीब वाला है, और ईमानदारी से यह कुछ हद तक एक अवशेष है। यह पुराने Internet Explorer, Chrome और Safari की एक सुविधा थी जो रिफ़्लेक्टेड XSS का पता लगाने और पेज को ब्लॉक करने की कोशिश करती थी। पेच — और सुरक्षा वाले इस बारे में बेबाक रहे हैं — यह है कि फ़िल्टर का ख़ुद [दुरुपयोग होकर अन्यथा-सुरक्षित पेजों में कमज़ोरियाँ पैदा की जा सकती थीं](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)। आधुनिक मार्गदर्शन यह है कि इसे या तो बंद कर दो (`0`) या बस मत भेजो, और बजाय इसके एक असली Content-Security-Policy पर निर्भर रहो। Amazon अब भी `1` भेजता है, शायद बहुत पुराने ब्राउज़रों की लंबी पूँछ के लिए। मैं इसे किसी नए प्रोजेक्ट में कॉपी नहीं करूँगा।

![amazon security headers](/images/posts/understanding-common-http-headers-on-amazon/amazon-security-headers.svg)

## परफ़ॉर्मेंस और प्रोटोकॉल हेडर्स

### accept-ch और accept-ch-lifetime

```http
accept-ch: ect,rtt,downlink,device-memory,...,sec-ch-ua-platform-version
accept-ch-lifetime: 86400
```

यह [Client Hints](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-CH) है। `Accept-CH` के साथ, सर्वर कह रहा है: "अपनी अगली रिक्वेस्ट्स पर, कृपया मुझे अपनी नेटवर्क स्पीड (`ect`, `rtt`, `downlink`), तुम्हारे पास कितनी डिवाइस मेमोरी है (`device-memory`), और कुछ user-agent विवरण भी बताना।" फिर Amazon तय कर सकता है कि वह क्या सर्व करे — मसलन धीमे `2g` कनेक्शन पर हल्की इमेज।

`accept-ch-lifetime: 86400` कहता है कि इस प्रेफ़रेंस को एक दिन तक याद रखो। जानने लायक बात: `Accept-CH-Lifetime` [अब अनुशंसित नहीं है और काफ़ी हद तक स्पेक से हटा दिया गया है](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-CH), पर बहुत-सी साइटें अब भी इसे संगतता के लिए भेजती हैं। Client Hints केवल सुरक्षित कनेक्शन पर काम करते हैं, और केवल फ़र्स्ट-पार्टी ऑरिजिन को ही भेजे जाते हैं — एक गोपनीयता सुरक्षा-घेरा ताकि कोई भी रैंडम थर्ड पार्टी चुपचाप आपकी डिवाइस को फ़िंगरप्रिंट न कर सके।

### vary

```http
vary: X-Amazon-Wtm-Tag-...,Accept-Encoding,User-Agent
```

[`Vary` हेडर](https://www.fastly.com/blog/best-practices-using-vary-header) वह है जो लोगों के भूल जाने पर चुपचाप कैश को तोड़ देता है। यह Amazon और आपके बीच के हर कैश से कहता है: "यह रिस्पॉन्स इन रिक्वेस्ट हेडर्स पर निर्भर करता है, तो अपनी कैश की हुई कॉपियों को इन पर की (key) करना।"

- **`Accept-Encoding`** — gzip बॉडी और Brotli बॉडी को अलग-अलग याद रखो। इसके बिना, कोई कैश किसी ऐसे क्लाइंट को gzip ब्लॉब थमा सकता है जिसने कुछ और माँगा था। चूँकि रिस्पॉन्स gzip-एन्कोडेड *है*, यह एंट्री असली काम कर रही है।
- **`User-Agent`** — रिस्पॉन्स मोबाइल और डेस्कटॉप ब्राउज़र के बीच अलग हो सकता है, तो उन्हें अलग कैश करो।

एक छोटी सावधानी जो विशेषज्ञ दोहराते रहते हैं: `Vary: User-Agent` एक [भोथरा औज़ार](https://www.smashingmagazine.com/2017/11/understanding-vary-header/) है। बाहर प्रभावी रूप से असीमित User-Agent स्ट्रिंग्स हैं, तो यह हर ब्राउज़र वर्ज़न के लिए लगभग-अद्वितीय कॉपी स्टोर करके आपकी कैश हिट दर को चिथड़े-चिथड़े कर सकता है। अपने ख़ुद के CDN लॉजिक वाली बड़ी साइटें इसे झेल सकती हैं; एक छोटी साइट पर मैं दो बार सोचूँगा।

### alt-svc

```http
alt-svc: h3=":443"; ma=86400
```

[`Alt-Svc`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Alt-Svc) वह हैंडशेक है जो HTTP/3 को बूटस्ट्रैप करता है। यह रिक्वेस्ट HTTP/2 पर वापस आई, पर यह हेडर Amazon की फुसफुसाहट है: "अरे, मैं पोर्ट 443 पर `h3` (QUIC पर HTTP/3) भी बोलता हूँ — अगले 86400 सेकंड के लिए बेझिझक इसका उपयोग करो।" एक सक्षम ब्राउज़र चुपचाप बैकग्राउंड में HTTP/3 आज़माएगा और, अगर वह कनेक्ट हो जाए, तो तेज़, कम-लेटेंसी रिक्वेस्ट्स के लिए उस पर स्विच कर लेगा। जैसा [bagder की HTTP/3 गाइड](https://http3-explained.haxx.se/en/h3/h3-altsvc) कहती है, ऐसे ही यह अपग्रेड उन क्लाइंट्स के लिए कुछ तोड़े बिना होता है जो इसका समर्थन नहीं करते।

## CloudFront की राह

आख़िरी समूह आपको बताता है कि Amazon इसे अपने ख़ुद के CDN, [CloudFront](https://aws.amazon.com/blogs/networking-and-content-delivery/amazon-cloudfront-introduces-response-headers-policies/) के ज़रिए सर्व कर रहा है:

| हेडर | वैल्यू | मतलब |
|---|---|---|
| `x-cache` | `Miss from cloudfront` | एज कैश में नहीं — ऑरिजिन से फ़ेच किया गया |
| `via` | `1.1 ...cloudfront.net (CloudFront)` | एक CloudFront प्रॉक्सी ने रिक्वेस्ट संभाली |
| `x-amz-cf-pop` | `BOM78-P2` | मुंबई (BOM) एज लोकेशन से सर्व किया गया |
| `x-amz-cf-id` | `4UqtO1...` | इस ठीक-ठीक रिक्वेस्ट के लिए अपारदर्शी ट्रेस ID |

यहाँ कुछ बातें जगह पर बैठ जाती हैं:

- **`x-cache: Miss`** समझ में आता है — एक व्यक्तिगत कार्ट-config एंडपॉइंट को कैश करके सबको सर्व नहीं किया जाना चाहिए, तो मिस होना *सही* व्यवहार है, कोई समस्या नहीं।
- **`x-amz-cf-pop: BOM78`** [IATA हवाई-अड्डा कोड](https://http.dev/x-amz-cf-pop) का उपयोग करता है। `BOM` मुंबई है। मैं भारत में हूँ, तो CloudFront ने मुझे निकटतम एज पर रूट किया — ठीक वही जो एक CDN को करना चाहिए। `-P2` प्रत्यय कैश टियर को दर्शाता है।
- **`x-amz-cf-id`** पहले देखे गए `x-amz-rid` का CloudFront भाई-बंधु है — एक [एन्क्रिप्टेड, अपारदर्शी टोकन](https://http.dev/x-amz-cf-id) जिसका मेरे लिए कोई मतलब नहीं है पर जो AWS Support को इस सटीक रिक्वेस्ट को उनके लॉग्स से खींचने देता है। पैटर्न पर ध्यान दें: हर परत अपनी ख़ुद की ट्रेस ID की मुहर लगाती है। यही अतिरेक (redundancy) वह तरीका है जिससे आप एक ऐसी रिक्वेस्ट को डिबग करते हैं जो CDN, फ्रंटएंड और बैकएंड से गुज़री बिना सूत्र खोए।

## तो निष्कर्ष क्या है?

एक फेंकने लायक config रिक्वेस्ट के लिए, Amazon ने वापस भेजा एन्क्रिप्शन प्रवर्तन, XSS/clickjacking बचाव के तीन स्वाद, साथ-साथ चलती दो CSP रणनीतियाँ, कुकी स्कोपिंग, client-hint मोल-तोल, HTTP/3 विज्ञापन, और एक पूरा CDN ट्रेस ट्रेल। इनमें से कुछ भी अनोखा नहीं है — यहाँ हर हेडर [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP) पर प्रलेखित है और ज़्यादातर ऐसी चीज़ें हैं जिन्हें आप ख़ुद चालू कर सकते हैं। फ़र्क़ यह है कि Amazon उन *सभी* को चालू करता है, defence-in-depth शैली में, और अगली कसावट को लागू करने से पहले उसे परखने के लिए एक रिपोर्ट-ओनली CSP तक भेजता है।

अगर आप प्रोडक्शन में कुछ भी चलाते हैं, तो यह डंप एक अच्छी चेकलिस्ट है। preload के साथ HSTS, `nosniff`, एक असली CSP, `X-Frame-Options`, `Secure` कुकीज़, और एक समझदार `Vary` आपको ज़्यादातर रास्ता तय करा देंगे। और शायद — Amazon की तरह — साथ ही अपने `Server` हेडर को कुछ शानदार ढंग से बेकार चीज़ पर सेट कर दीजिए।

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