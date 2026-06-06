+++
title       = "UUID बनाम अनुक्रमिक IDs: क्या, क्यों, और कौन सा चुनें"
description = "UUID 128-बिट आइडेंटिफायर हैं जो वास्तविक समस्याओं को हल करते हैं जिन्हें अनुक्रमिक IDs नहीं कर सकते — वितरित प्रणालियाँ, सुरक्षा और स्केल। यहाँ वह सब है जो आपको वास्तव में जानना चाहिए।"
date        = "2026-06-04T22:06:34+05:30"
slug        = "uuid-vs-sequential-ids-explained"
tags        = ["डेटाबेस", "uuid", "बैकएंड", "सुरक्षा", "वितरित-प्रणालियाँ"]
keywords    = ["UUID", "यूनिवर्सली यूनिक आइडेंटिफायर", "UUID बनाम अनुक्रमिक ID", "UUIDv7", "डेटाबेस प्राइमरी की", "IDOR रोकथाम"]
canonical   = "/hi/posts/uuid-vs-sequential-ids-explained/"
feature_image = "/images/posts/uuid-vs-sequential-ids-explained/uuid-feature.svg"
+++

आप एक API एंडपॉइंट `/api/orders/1042` एक्सपोज़ करते हैं। वह इंटीजर किसी को भी — एक प्रतिस्पर्धी, एक हमलावर, एक जिज्ञासु उपयोगकर्ता — बिल्कुल बता देता है कि आपके पास कितने ऑर्डर हैं। नंबर को 1041 में बदलें, तो पिछला ऑर्डर मिल जाता है। इसे 1 में बदलें, तो पहला ऑर्डर मिल जाता है। कोई auth bypass की ज़रूरत नहीं। ID खुद ही जानकारी का रिसाव है।

यही एक पैराग्राफ में अनुक्रमिक ID की समस्या है। UUID इसे ठीक करने के लिए मौजूद है — और कुछ अन्य चीज़ें जो स्केल पर मायने रखती हैं।

## UUID वास्तव में क्या है?

**UUID** का अर्थ है Universally Unique Identifier। यह एक 128-बिट संख्या है, जिसे 32 हेक्साडेसिमल कैरेक्टर के रूप में दर्शाया जाता है, जो पाँच समूहों में हाइफ़न से विभाजित होती है [1]:

```
550e8400-e29b-41d4-a716-446655440000
```

फॉर्मेट हमेशा `8-4-4-4-12` होता है — यह प्रति समूह hex कैरेक्टर की संख्या है, चार हाइफ़न सहित कुल 36 [2]। 13वाँ कैरेक्टर वर्शन एनकोड करता है। 17वाँ कैरेक्टर वेरिएंट एनकोड करता है। तो ऊपर वाले UUID में — तीसरा समूह `4` से शुरू होता है, यानी वर्शन 4 [3]।

UUID उत्पन्न करने के लिए किसी केंद्रीय अधिकारी की ज़रूरत नहीं। कोई डेटाबेस autoincrement सीक्वेंस नहीं। कोई क्रॉस-सर्वर समन्वय नहीं। कोई भी सिस्टम, कहीं भी, एक UUID उत्पन्न कर सकता है और लगभग निश्चित हो सकता है कि किसी और ने वही नहीं बनाया [1]।

## UUID वर्शन — ये सब एक जैसे नहीं हैं

अधिकांश लेख वर्शन सूचीबद्ध करते हैं बिना यह समझाए कि यह आपके डेटाबेस के लिए वास्तव में क्यों मायने रखता है। यह मायने रखता है।

| वर्शन | कैसे उत्पन्न होता है | क्रमबद्ध? | गोपनीयता |
|---|---|---|---|
| v1 | Timestamp + MAC address | ✅ हाँ | ❌ MAC address लीक करता है |
| v3 | namespace + name का MD5 hash | ✅ निर्धारक | N/A |
| v4 | पूरी तरह random (122 bits) | ❌ नहीं | ✅ अच्छा |
| v5 | namespace + name का SHA-1 hash | ✅ निर्धारक | N/A |
| v7 | Unix timestamp + random bits | ✅ हाँ | ✅ अच्छा |

**v4 वह है जो अधिकांश लोग आज उपयोग करते हैं।** Random, सरल, कोई गोपनीयता चिंता नहीं। लेकिन इसमें एक महत्वपूर्ण डेटाबेस परफॉरमेंस समस्या है जिस पर मैं बाद में आऊँगा [3]।

**v7 वह है जो आपको नए प्रोजेक्ट्स के लिए उपयोग करना चाहिए।** RFC 9562 (मई 2024 में प्रकाशित) में पेश किया गया, v7 एक 48-बिट Unix मिलीसेकंड timestamp को 74 random bits के साथ जोड़ता है [2]। आपको अपना MAC address लीक किए बिना time-ordering मिलती है।

![uuid format breakdown](/images/posts/uuid-vs-sequential-ids-explained/uuid-format-breakdown.svg)

## Collision का सवाल

"अगर दो सिस्टम एक ही UUID उत्पन्न करें तो?"

Version 4 UUIDs में 122 bits की randomness है। कुल संभावित मान: 2¹²⁸ ≈ 3.4×10³⁸। एक भी collision की 50% संभावना उत्पन्न करने के लिए, आपको **2.71 क्विंटिलियन** v4 UUID उत्पन्न करने होंगे [4]। 1 ट्रिलियन UUID उत्पन्न करने से collision की संभावना लगभग 10⁻¹⁵ होती है [4]। यानी एक क्वाड्रिलियन में से एक संभावना।

आप इस बारे में चिंता नहीं करने वाले।

## अनुक्रमिक IDs की असली समस्या

अनुक्रमिक IDs — `SERIAL` या `AUTO_INCREMENT` — सरल और तेज़ हैं। एक सिंगल सर्वर पर छोटे ऐप के लिए, ये बिल्कुल ठीक हैं। समस्याएं दो विशिष्ट क्षेत्रों में सामने आती हैं।

### सुरक्षा: Enumeration और IDOR

पूर्वानुमानित IDs **Insecure Direct Object Reference (IDOR)** हमलों को बेहद आसान बना देते हैं [5]। IDOR OWASP Top 10 में है — यह एक कारण से सबसे अधिक exploit की जाने वाली vulnerability classes में से एक है [6]।

अनुक्रमिक IDs के साथ, अगर मुझे पता है कि मेरा user ID 4821 है, तो मैं 4820, 4819, 4818... आज़मा सकता हूँ और अन्य उपयोगकर्ताओं के डेटा तक पहुँच सकता हूँ अगर आपके authorization checks कमज़ोर हैं या बिल्कुल नहीं हैं। UUID के साथ, `a47c3f2e-91bb-4d2e-b3f0-c6e88d3f0a1c` का अगला अनुमान लगाना कम्प्यूटेशनल रूप से असंभव है।

मैं यहाँ एक बात स्पष्ट करना चाहता हूँ: **UUID उचित authorization checks का विकल्प नहीं हैं।** अगर आपके ऐप में IDOR vulnerabilities हैं, तो उन्हें authorization layer पर ठीक करना प्राथमिक समाधान है। UUID बस floor को काफी ऊँचा उठा देते हैं [5]।

अनुक्रमिक IDs business intelligence भी लीक करते हैं जो आप शायद नहीं चाहते। एक प्रतिस्पर्धी जनवरी में `/api/invoices/1` और दिसंबर में `/api/invoices/8500` स्क्रैप करके अब पूरे साल का आपका invoice volume जान लेता है। यह वास्तव में होता है।

### वितरित प्रणालियाँ: सिंगल-नोड समस्या

**अनुक्रमिक IDs को केंद्रीकृत generation की ज़रूरत होती है।** एक integer को एक समय में एक नोड पर reliably autoincrement करना काम करता है [7]।

जैसे ही आपके पास एक साथ लिखने वाले कई database replicas हों, regions में data sharding, स्वतंत्र रूप से रिकॉर्ड उत्पन्न करने वाली microservices, या offline-capable mobile clients — अनुक्रमिक IDs एक coordination nightmare बन जाते हैं। अगला integer उत्पन्न करने वाले दो नोड बिना केंद्रीय coordinator के collision करेंगे।

UUID को किसी coordinator की ज़रूरत नहीं। प्रत्येक सर्विस, प्रत्येक region, प्रत्येक डिवाइस स्वतंत्र रूप से IDs उत्पन्न कर सकता है और बाद में बिना conflicts के डेटा merge कर सकता है [1]। यह architecturally महत्वपूर्ण है।

## UUID वास्तव में कहाँ कमज़ोर पड़ता है

UUID हर स्थिति में सख्ती से बेहतर नहीं हैं। मैं trade-offs के बारे में ईमानदार रहूँगा।

- **Storage cost** — UUID के लिए 16 bytes बनाम integer के लिए 4–8 bytes। सैकड़ों करोड़ rows और multiple foreign key references वाली table पर, यह बढ़ता जाता है [7]।
- **Human-readability** — `42` कहना support call पर `550e8400-e29b-41d4-a716-446655440000` से आसान है। यहाँ अनुक्रमिक IDs हमेशा जीतते हैं।
- **v4 के साथ index performance** — यही वह है जो production में लोगों को परेशान करता है।

जब आप UUID v4 को primary key के रूप में उपयोग करते हैं, तो प्रत्येक insert **B-tree index में एक random position** पर जाता है। डेटाबेस को लगातार rebalance करना पड़ता है। Pages fragment हो जाते हैं। Cache locality प्रभावित होती है। v4 UUIDs के साथ high write volumes पर, index performance अनुक्रमिक integers की तुलना में स्पष्ट रूप से खराब हो जाती है [7][8]।

## v7 परफॉरमेंस समस्या को ठीक करता है

इसीलिए v7 मायने रखता है। millisecond timestamp prefix का मतलब है कि v7 UUID time-ordered हैं। Inserts अधिकांशतः sequential हैं — index एक दिशा में बढ़ता है, fragmentation कम रहती है, cache behavior अच्छा है [2][8]।

अगर आप वर्तमान में high-write tables पर primary keys के रूप में v4 UUID का उपयोग कर रहे हैं, तो v7 में migrate करना विचार करने योग्य है। अधिकांश भाषाओं और platforms की UUID libraries ने RFC 9562 आने के बाद v7 support जोड़ लिया है [2]।

आपको मिलता है:

- UUID का distributed generation लाभ
- सुरक्षा लाभ (non-guessable)
- अनुक्रमिक integers के करीब index performance
- कोई MAC address रिसाव नहीं (v1 के विपरीत)

## अनुक्रमिक IDs अभी भी ठीक कब हैं

बहुत सारे अनुप्रयोगों के लिए, अनुक्रमिक IDs सही विकल्प हैं।

- Internal tools जो कभी बाहरी रूप से exposed नहीं होते
- Reference/lookup tables (status codes, categories) जहाँ ID कभी user-facing नहीं होता
- सिस्टम जो single database node पर चलने की गारंटी है और sharding की कोई योजना नहीं

गलती अनुक्रमिक IDs का उपयोग करना नहीं है — गलती है हर जगह बिना सोचे-समझे डिफ़ॉल्ट रूप से उनका उपयोग करना। 2026 में `/api/users/1` को publicly expose करना और यह नहीं सोचना कि यह क्या leak कर रहा है, बस लापरवाही है।

> End

## स्रोत
1. [Universally unique identifier — Wikipedia](https://en.wikipedia.org/wiki/Universally_unique_identifier)
2. [RFC 9562: Universally Unique IDentifiers (UUIDs) — RFC Editor](https://www.rfc-editor.org/rfc/rfc9562.html)
3. [UUID Versions Explained — UUIDTools.com](https://www.uuidtools.com/uuid-versions-explained)
4. [UUID Collision Probability: Can Two UUIDs Ever Be the Same? — SecureBin](https://securebin.ai/blog/uuid-collision-probability/)
5. [Replace Sequential IDs With UUIDs to Prevent IDOR Vulnerabilities or Scraping — HackerNoon](https://hackernoon.com/replace-sequential-ids-in-your-models-with-uuids-to-prevent-idor-vulnerabilities-or-scraping)
6. [Insecure Direct Object Reference (IDOR) — OWASP Foundation](https://owasp.org/www-community/attacks/insecure_direct_object_reference)
7. [UUID vs. Sequential ID as Primary Key — Baeldung](https://www.baeldung.com/uuid-vs-sequential-id-as-primary-key)
8. [Goodbye to Sequential Integers, Hello UUIDv7! — Buildkite](https://buildkite.com/resources/blog/goodbye-integers-hello-uuids/)
