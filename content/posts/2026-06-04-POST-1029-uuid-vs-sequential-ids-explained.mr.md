+++
title       = "UUID विरुद्ध Sequential IDs: काय, का, आणि कुठले निवडावे"
description = "UUID हे 128-बिट ओळखकर्ते आहेत जे sequential IDs सोडवू शकत नाहीत अशा खऱ्या समस्या सोडवतात — distributed systems, सुरक्षितता, आणि मोठ्या प्रमाणावर. येथे तुम्हाला खरोखर काय माहित असणे आवश्यक आहे."
date        = "2026-06-04T22:06:34+05:30"
slug        = "uuid-vs-sequential-ids-explained"
tags        = ["database", "uuid", "backend", "security", "distributed-systems"]
keywords    = ["UUID", "universally unique identifier", "UUID vs sequential ID", "UUIDv7", "database primary key", "IDOR prevention"]
canonical   = "/mr/posts/uuid-vs-sequential-ids-explained/"
feature_image = "/images/posts/uuid-vs-sequential-ids-explained/uuid-feature.svg"
+++

तुम्ही `/api/orders/1042` सारखा API endpoint उघड करता. तो integer कोणालाही ऐकणाऱ्याला — एखाद्या प्रतिस्पर्ध्याला, आक्रमणकर्त्याला, उत्सुक वापरकर्त्याला — तुमच्याकडे किती orders आहेत ते सांगतो. संख्या 1041 केली, तर तुम्हाला मागील order मिळतो. ती 1 केली, तर तुम्हाला पहिली order मिळते. कोणत्याही auth bypass ची गरज नाही. ID स्वतःच माहितीची गळती आहे.

हा एका परिच्छेदात sequential ID चा प्रश्न आहे. UUID त्याचे निराकरण करण्यासाठी अस्तित्वात आहे — आणि मोठ्या प्रमाणावर महत्त्वाच्या इतर काही गोष्टींसाठी.

## UUID नक्की काय आहे?

**UUID** म्हणजे Universally Unique Identifier. हे एक 128-बिट संख्या आहे, 32 hexadecimal वर्णांनी दर्शविलेले जे hyphens सह पाच गटांमध्ये विभाजित आहेत [1]:

```
550e8400-e29b-41d4-a716-446655440000
```

स्वरूप नेहमी `8-4-4-4-12` असते — हे प्रत्येक गटातील hex वर्णांची संख्या आहे, चार hyphens सह एकूण 36 [2]. 13वा वर्ण version एन्कोड करतो. 17वा वर्ण variant एन्कोड करतो. तर वरील UUID — तिसरा गट `4` ने सुरू होतो, म्हणजे version 4 [3].

UUIDs तयार करण्यासाठी कोणत्याही केंद्रीय अधिकाराची आवश्यकता नाही. कोणतीही database autoincrement sequence नाही. कोणताही cross-server समन्वय नाही. कोणतीही प्रणाली, कुठेही, UUID तयार करू शकते आणि जवळजवळ निश्चित असू शकते की इतर कोणीही तीच तयार केली नाही [1].

## UUID Versions — ते सर्व सारखे नाहीत

बहुतेक लेख versions सूचीबद्ध करतात परंतु ते तुमच्या database साठी का महत्त्वाचे आहे हे स्पष्ट न करता. ते महत्त्वाचे आहे.

| Version | ते कसे तयार केले जाते | Sortable? | गोपनीयता |
|---|---|---|---|
| v1 | Timestamp + MAC address | ✅ होय | ❌ MAC address गळती |
| v3 | namespace + name चा MD5 hash | ✅ Deterministic | N/A |
| v4 | पूर्णपणे random (122 bits) | ❌ नाही | ✅ चांगले |
| v5 | namespace + name चा SHA-1 hash | ✅ Deterministic | N/A |
| v7 | Unix timestamp + random bits | ✅ होय | ✅ चांगले |

**v4 हे आज बहुतेक लोक वापरतात.** Random, सोपे, कोणत्याही गोपनीयतेच्या चिंता नाहीत. परंतु त्याला एक महत्त्वपूर्ण database performance समस्या आहे जी मी पुढे सांगेन [3].

**v7 हे नवीन projects साठी तुम्ही वापरायला हवे.** RFC 9562 मध्ये सादर केलेले (मे 2024 मध्ये प्रकाशित), v7 एक 48-बिट Unix millisecond timestamp ला 74 random bits सह एकत्र करते [2]. तुम्हाला MAC address गळती न करता time-ordering मिळते.

![uuid format breakdown](/images/posts/uuid-vs-sequential-ids-explained/uuid-format-breakdown.svg)

## Collision चा प्रश्न

"जर दोन systems एकच UUID तयार करतात तर काय होते?"

Version 4 UUIDs मध्ये 122 bits of randomness आहे. एकूण शक्य मूल्ये: 2¹²⁸ ≈ 3.4×10³⁸. एका collision ची 50% शक्यता निर्माण करण्यासाठी, तुम्हाला **2.71 quintillion** v4 UUIDs तयार करणे आवश्यक आहे [4]. 1 trillion UUIDs तयार केल्यास collision probability अंदाजे 10⁻¹⁵ होते [4]. ही एक quadrillion मधील एक शक्यता आहे.

तुम्ही याबद्दल काळजी करत नाही.

## Sequential IDs सह खरी समस्या

Sequential IDs — `SERIAL` किंवा `AUTO_INCREMENT` — सोपे आणि जलद आहेत. एकाच server वरील एका छोट्या app साठी, ते पूर्णपणे ठीक आहेत. समस्या दोन विशिष्ट क्षेत्रांमध्ये दिसतात.

### सुरक्षितता: Enumeration आणि IDOR

अंदाजे IDs **Insecure Direct Object Reference (IDOR)** हल्ले अत्यंत सोपे करतात [5]. IDOR OWASP Top 10 मध्ये आहे — एका कारणासाठी सर्वात सामान्यपणे exploit केलेल्या vulnerability वर्गांपैकी एक आहे [6].

Sequential IDs सह, जर मला माहित असेल की माझी user ID 4821 आहे, तर मी 4820, 4819, 4818... प्रयत्न करू शकतो आणि जर तुमचे authorization checks कमकुवत असतील किंवा अजिबात नसतील तर इतर वापरकर्त्यांचा डेटा access करू शकतो. UUIDs सह, पुढे `a47c3f2e-91bb-4d2e-b3f0-c6e88d3f0a1c` अंदाज करणे computationally अशक्य आहे.

येथे मला एका गोष्टीबद्दल स्पष्ट असायचे आहे: **UUIDs योग्य authorization checks साठी पर्याय नाहीत.** जर तुमच्या app मध्ये IDOR vulnerabilities असतील, तर त्या authorization layer वर दुरुस्त करणे हे प्राथमिक निराकरण आहे. UUIDs फक्त मर्यादा लक्षणीयरीत्या वाढवतात [5].

Sequential IDs व्यावसायिक माहिती देखील गळवतात जी तुम्हाला कदाचित गळवायची नसेल. जानेवारीत `/api/invoices/1` आणि डिसेंबरमध्ये `/api/invoices/8500` scrape करणाऱ्या प्रतिस्पर्ध्याला आता वर्षासाठी तुमची invoice मात्रा माहित आहे. हे खरोखर घडते.

### Distributed Systems: एकल-Node समस्या

**Sequential IDs ला केंद्रीकृत निर्मितीची आवश्यकता असते.** एका वेळी एकाच node वर integer autoincrement करणे विश्वासूपणे कार्य करते [7].

ज्या क्षणी तुमच्याकडे एकाच वेळी लिहिणाऱ्या multiple database replicas, regions मध्ये data sharding, स्वतंत्रपणे records तयार करणाऱ्या microservices, किंवा offline-capable mobile clients असतात — sequential IDs समन्वयाची दुःस्वप्न बनतात. पुढील integer तयार करणारे दोन nodes केंद्रीय coordinator शिवाय collide होतील.

UUIDs ला कोणत्याही coordinator ची गरज नाही. प्रत्येक service, प्रत्येक region, प्रत्येक device स्वतंत्रपणे IDs तयार करू शकते आणि नंतर conflicts शिवाय data merge करू शकते [1]. हे architecturally महत्त्वपूर्ण आहे.

## UUID खरोखर कुठे कमी पडते

UUIDs प्रत्येक परिस्थितीत कठोरपणे चांगले नाहीत. trade-offs बद्दल प्रामाणिक असूया.

- **Storage खर्च** — UUID साठी 16 bytes विरुद्ध integer साठी 4–8 bytes. शेकडो दशलक्ष rows आणि multiple foreign key references असलेल्या table वर, हे जमा होते [7].
- **मानव-वाचनीयता** — `42` हे `550e8400-e29b-41d4-a716-446655440000` पेक्षा support call वर सांगणे सोपे आहे. Sequential IDs येथे नेहमी जिंकतात.
- **v4 सह Index performance** — हे production मध्ये लोकांना त्रास देते.

जेव्हा तुम्ही UUID v4 ला primary key म्हणून वापरता, प्रत्येक insert **B-tree index मधील random position** वर येतो. Database ला सतत rebalance करावे लागते. Pages fragment होतात. Cache locality खराब होते. v4 UUIDs सह उच्च write volumes वर, sequential integers च्या तुलनेत index performance लक्षणीयरीत्या खराब होते [7][8].

## v7 Performance समस्या ठीक करते

म्हणूनच v7 महत्त्वाचे आहे. millisecond timestamp prefix म्हणजे v7 UUIDs time-ordered आहेत. Inserts मुख्यतः sequential असतात — index एका दिशेने वाढतो, fragmentation कमी राहते, cache behavior चांगले असते [2][8].

जर तुम्ही सध्या high-write tables वर primary keys म्हणून v4 UUIDs वापरत असाल, तर v7 वर migrate करणे विचार करण्यासारखे आहे. बहुतेक languages आणि platforms मधील UUID libraries नी RFC 9562 लागू झाल्यापासून v7 support जोडले आहे [2].

तुम्हाला मिळते:

- UUIDs चा distributed generation फायदा
- सुरक्षितता फायदे (अंदाज न करण्यायोग्य)
- sequential integers च्या जवळ index performance
- MAC address गळती नाही (v1 विपरीत)

## Sequential IDs अजूनही ठीक कधी असतात

बऱ्याच applications साठी, sequential IDs योग्य निर्णय आहेत.

- बाहेरून कधीही उघड न केलेली internal tools
- Reference/lookup tables (status codes, categories) जेथे ID कधीही user-facing नसते
- एकाच database node वर चालण्याची हमी असलेल्या systems ज्यांना shard करण्याच्या कोणत्याही योजना नाहीत

चूक sequential IDs वापरणे नाही — ती त्यांचा विचार न करता सर्वत्र default म्हणून वापरणे आहे. 2026 मध्ये `/api/users/1` सार्वजनिकपणे उघड करणे आणि ते काय गळवते याचा विचार न करणे फक्त निष्काळजीपणा आहे.

> समाप्त

## स्रोत
1. [Universally unique identifier — Wikipedia](https://en.wikipedia.org/wiki/Universally_unique_identifier)
2. [RFC 9562: Universally Unique IDentifiers (UUIDs) — RFC Editor](https://www.rfc-editor.org/rfc/rfc9562.html)
3. [UUID Versions Explained — UUIDTools.com](https://www.uuidtools.com/uuid-versions-explained)
4. [UUID Collision Probability: Can Two UUIDs Ever Be the Same? — SecureBin](https://securebin.ai/blog/uuid-collision-probability/)
5. [Replace Sequential IDs With UUIDs to Prevent IDOR Vulnerabilities or Scraping — HackerNoon](https://hackernoon.com/replace-sequential-ids-in-your-models-with-uuids-to-prevent-idor-vulnerabilities-or-scraping)
6. [Insecure Direct Object Reference (IDOR) — OWASP Foundation](https://owasp.org/www-community/attacks/insecure_direct_object_reference)
7. [UUID vs. Sequential ID as Primary Key — Baeldung](https://www.baeldung.com/uuid-vs-sequential-id-as-primary-key)
8. [Goodbye to Sequential Integers, Hello UUIDv7! — Buildkite](https://buildkite.com/resources/blog/goodbye-integers-hello-uuids/)