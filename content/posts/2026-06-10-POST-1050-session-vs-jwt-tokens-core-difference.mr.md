+++
title       = "Session vs JWT Tokens: मूळ फरक नेमका काय आहे"
description = "Session आणि JWT ऑथेंटिकेशन एकाच समस्येवर अगदी विरुद्ध मार्गांनी उपाय शोधतात. खरा मूळ फरक - stateful विरुद्ध stateless - आणि योग्य पर्याय कसा निवडावा हे इथे जाणून घ्या."
date        = "2026-06-10T11:19:38+05:30"
slug        = "session-vs-jwt-tokens-core-difference"
tags        = ["authentication", "jwt", "web security", "api design"]
keywords    = ["session विरुद्ध jwt", "jwt authentication", "session-based authentication", "stateless authentication", "jwt विरुद्ध session tokens"]
canonical   = "/mr/posts/session-vs-jwt-tokens-core-difference/"
feature_image = "/images/posts/session-vs-jwt-tokens-core-difference/jwt-cover.png"
+++

जेव्हा कोणी मला विचारतं "मी session वापरू की JWT?", तेव्हा या प्रश्नामागे नेमकं काय आहे ते मला माहीत असतं. त्यांनी काही blog posts वाचलेले असतात, "stateless" हा शब्द जणू आपोआप चांगला असतो असा वापरला जाताना पाहिलेला असतो, आणि आता ते गोंधळलेले असतात. तर चला, हे नीट समजून घेऊया - buzzwords ने नाही, तर wire वर आणि तुमच्या सर्व्हरवर प्रत्यक्षात काय घडतं त्याद्वारे.

## Session: "फ्रंट डेस्कवर रेकॉर्ड ठेवतो" पद्धत

session-based auth ला हॉटेलमध्ये चेक-इन करण्यासारखं समजा. तुम्ही फ्रंट डेस्कवर एकदाच तुमचं ID दाखवता, स्टाफ ते verify करतो, आणि तुम्हाला एक रूम की कार्ड देतो. त्या कार्डमध्ये तुमचं नाव, पासपोर्ट नंबर किंवा बुकिंग डिटेल्स नसतात - ते फक्त एक रँडम नंबर असतं. तुमची खरी सगळी माहिती हॉटेलच्या कॉम्प्युटर सिस्टीममध्ये, त्यांच्या डेटाबेसमध्ये, त्या कार्ड नंबरशी लिंक करून साठवलेली असते.

session-based authentication अगदी असंच काम करतं:

1. तुम्ही तुमच्या username आणि password ने लॉग इन करता.
2. सर्व्हर तुमचे credentials तपासतो, एक **session record** तयार करतो (तुमचा user ID, roles, login time, इ.), आणि ते server-side साठवतो - memory मध्ये, database मध्ये, किंवा Redis सारख्या एखाद्या ठिकाणी [2].
3. सर्व्हर एक रँडम **session ID** तयार करतो आणि तो cookie म्हणून परत पाठवतो, सहसा `HttpOnly` flag सोबत जेणेकरून JavaScript त्याला हात लावू शकणार नाही [3].
4. प्रत्येक पुढच्या request वर, तुमचा ब्राउझर आपोआप ती cookie attach करतो.
5. सर्व्हर session ID घेतो, त्याच्या session store मध्ये शोधतो, आणि म्हणतो "अरे हो, हा Amit आहे, तो लॉग इन आहे, ही त्याची माहिती."

इथली महत्त्वाची गोष्ट अशी: **session ID स्वतः काहीच अर्थ ठेवत नाही**. तो फक्त एक pointer आहे. खरं "सत्य" - तुम्ही कोण आहात, तुम्ही काय करू शकता - हे सगळं सर्व्हरवर असतं [1]. जर सर्व्हरचा session store डाउन झाला किंवा क्लिअर झाला, तर लॉग इन असलेला प्रत्येक वापरकर्ता तात्काळ बाहेर फेकला जातो, जरी त्याची cookie technically अजूनही valid असली तरी.

म्हणूनच पारंपरिक server-rendered web apps साठी गेल्या अनेक दशकांपासून session-based auth हा डिफॉल्ट पर्याय राहिला आहे. हे साधं आहे, याची माहिती सर्वांना चांगली आहे, आणि access रद्द करणं अगदी सोपं आहे - फक्त session table मधून ती row delete करायची.

## JWT: "प्रत्येक वेळी ID बॅज दाखवा" पद्धत

आता एक वेगळी सिस्टीम कल्पना करा - डेटाबेस रेकॉर्डकडे निर्देश करणाऱ्या रूम कीऐवजी, तुम्हाला एक लॅमिनेटेड बॅज दिला जातो. त्या बॅजवर तुमचं नाव, फोटो, access level, आणि छेडछाड लगेच उघड होईल असा hologram छापलेला असतो. UV स्कॅनर असलेली कोणतीही व्यक्ती फ्रंट डेस्कला फोन न करता तो hologram खरा आहे का हे verify करू शकते.

हाच JSON Web Token (JWT) आहे. JWT म्हणजे एक self-contained, digitally signed स्ट्रिंग जी तीन भागांची बनलेली असते, डॉट्सने वेगळी केलेली: `header.payload.signature` [4][5].

- **Header**: token चा प्रकार (`JWT`) आणि तो sign करण्यासाठी कोणता algorithm वापरला आहे ते सांगतो, जसं `HS256` किंवा `RS256` [5].
- **Payload**: खऱ्या claims - जसं की `sub` (user ID), `role`, `iat` (issued at), आणि `exp` (expiry time). हे फक्त Base64Url-encoded JSON आहे, **encrypted नाही**, त्यामुळे यात कोणतेही secrets टाकू नका [5][9].
- **Signature**: header आणि payload, hash करून secret key (किंवा private key) ने sign केलेले. token शी छेडछाड झालेली नाही हे हेच सिद्ध करतं [4].

decode केलेला JWT payload असा काहीसा दिसू शकतो:

```json
{
  "sub": "user_8821",
  "name": "Amit Kumar",
  "role": "admin",
  "iat": 1748505600,
  "exp": 1748509200
}
```

लोकांना गोंधळात टाकणारा भाग हा आहे: सर्व्हर हे कुठेही साठवत नाही. तुम्ही लॉग इन करता तेव्हा, सर्व्हर हा payload sign करतो आणि संपूर्ण गोष्ट तुम्हाला देऊन टाकतो. तुमच्या पुढच्या request वर, तुम्ही तो token परत पाठवता (सहसा `Authorization: Bearer <token>` header मध्ये), आणि सर्व्हर फक्त **signature पुन्हा तपासतो**. जर signature valid असेल आणि token expire झालेला नसेल, तर सर्व्हर payload मधील सगळ्यावर विश्वास ठेवतो - कोणतीही database lookup करण्याची गरज नाही [6][1].

तुम्ही स्वतः [jwt.io debugger](https://www.jwt.io/introduction) वर खऱ्या tokens सोबत प्रयोग करून पाहू शकता - कोणताही JWT paste करा आणि ते header आणि payload लगेच decode करून दाखवेल [4].

## मूळ फरक: "सत्य" नेमकं कुठे असतं?

ठीक आहे, आता खरी महत्त्वाची गोष्ट येते, आणि हेच टायटलमधल्या प्रश्नाचं उत्तर आहे.

**Session मध्ये, सत्य सर्व्हरवर राहतं. JWT मध्ये, सत्य क्लायंटसोबत प्रवास करतं.**

बाकी सगळं - cookies विरुद्ध headers, scalability वरील वाद, revocation च्या डोकेदुखी - हे सगळं या एका architectural निर्णयाचा परिणाम आहे. Session auth **stateful** आहे: request्स दरम्यान सर्व्हरला तुमच्याबद्दल काहीतरी लक्षात ठेवावं लागतं. JWT auth (बहुतांशी) **stateless** आहे: सर्व्हरला निर्णय घेण्यासाठी लागणारं सगळं काही प्रत्येक request मध्ये असतं, आणि सर्व्हर फक्त cryptographic signature verify करतो [6][1].

![session vs jwt flow](/images/posts/session-vs-jwt-tokens-core-difference/session-vs-jwt-flow.svg)

हा एकच फरक तुम्हाला भेटणाऱ्या जवळपास प्रत्येक practical trade-off मध्ये पसरतो. session lookup आवश्यक असलेल्या request ला Redis किंवा database store विरुद्ध साधारण 15ms लागतात, तर JWT signature verify करायला सुमारे 20ms लागतात पण storage round-trip पूर्णपणे टाळला जातो - आणि मोठ्या प्रमाणावर, JWT-based systems distributed servers वर साधारण 1M requests/sec हाताळताना बेंचमार्क झाल्या आहेत, तर centralized session stores साठी हे साधारण 500K req/sec आहे [11]. मोठ्या प्रमाणावर काम करताना हा काही छोटा फरक नाही.

## Revocation ची डोकेदुखी, जी समस्या होईपर्यंत कोणी बोलत नाही

इथेच गोष्टी गुंतागुंतीच्या होतात, आणि खरं सांगायचं तर, "JWT हेच बेस्ट!" म्हणणारे बहुतेक आर्टिकल्स याकडे दुर्लक्ष करतात.

Session मध्ये, **वापरकर्त्याला लॉग आउट करणं तात्काळ होतं**. तुम्ही त्यांचा session record store मधून delete करता, आणि त्या cookie सोबतची पुढची request लगेच fail होते. security incident मुळे सगळ्यांना force-logout करायचं आहे? session table पूर्णपणे रिकामी करा. झालं [2].

JWT मध्ये, **delete करण्यासाठी कोणताही session record नसतो** - statelessness चा हाच तर मुख्य मुद्दा आहे. एकदा JWT sign करून क्लायंटला दिला की, सर्व्हरकडे तो "परत घेण्याचा" कोणताही built-in मार्ग नसतो. नंतर काहीही झालं तरी तो expire होईपर्यंत valid राहतो [7][8]. वापरकर्त्याने त्याचा compromised password reset केला, किंवा admin ने त्याचं account deactivate केलं, तरीही आधी issue केलेला JWT त्याच्या `exp` claim मध्ये सांगितल्याप्रमाणे expire होईपर्यंत काम करत राहू शकतो [8].

हे काही hypothetical edge case नाही. Redis च्या स्वतःच्या engineering team ने ["JSON Web Tokens (JWT) are dangerous for user sessions"](https://redis.io/blog/json-web-tokens-jwt-are-dangerous-for-user-sessions/) या नावाचा एक लेख लिहिला आहे, ज्यात असं म्हटलं आहे की JWT ला आकर्षक बनवणारी statelessness हीच गोष्ट पारंपरिक login session सारख्या कोणत्याही गोष्टीसाठी त्यांना धोकादायक बनवते [7].

मग खऱ्या systems याला कसं हाताळतात? काही पॅटर्न्स आता प्रमाणित झाले आहेत:

- **Short-lived access tokens** (5-15 मिनिटे) सोबत जास्त काळ टिकणारे **refresh tokens** वापरले जातात. जर access token leak झाला, तर नुकसानीचा कालावधी छोटा राहतो [8].
- **Token families सोबत refresh token rotation** - प्रत्येक refresh वेळी नवीन refresh token issue होतो, आणि जर जुना, आधीच वापरलेला token पुन्हा दिसला, तर संपूर्ण family revoke केली जाते (चोरीचा हा एक मजबूत संकेत आहे) [8].
- **Denylists** - revoke केलेल्या token IDs ची (`jti` claim) यादी, token च्या expiry शी जुळणाऱ्या TTL सोबत Redis सारख्या ठिकाणी server-side ठेवली जाते [8].

लक्षात आलं का? या प्रत्येक "fix" मुळे थोडंसं server-side state पुन्हा येतंच. त्यामुळे प्रत्यक्षात, खरं logout, password-reset invalidation, किंवा permission बदल यांची गरज पडली की **pure stateless JWT auth ही बहुतांशी एक myth आहे**. प्रत्यक्षात तुम्हाला "बहुतांशी stateless, सोबत एक छोटीशी stateful safety net" मिळते. हा JWT वर आरोप नाही - हे फक्त खरं चित्र आहे, आणि OWASP च्या स्वतःच्या मार्गदर्शनात terminate झालेल्या sessions साठी denylist ठेवण्याची स्पष्ट शिफारस केली आहे [9].

## Token कुठे साठवता हे खरंच खूप महत्त्वाचं आहे

लोकांना गोंधळात टाकणारी आणखी एक गोष्ट म्हणजे: **JWT विरुद्ध session हा प्रश्न, ब्राउझरमध्ये token कुठे साठवायचा या प्रश्नापेक्षा वेगळा आहे**, पण हे दोन्ही नेहमी एकमेकांत मिसळले जातात.

- session ID जवळपास नेहमीच cookie मध्ये साठवली जाते, सहसा `HttpOnly` आणि `Secure` सोबत, जेणेकरून client-side JavaScript ती कधीही वाचू शकणार नाही [3].
- JWT `localStorage`, `sessionStorage`, किंवा cookie मध्ये साठवता येतो - आणि या निवडीचे खरे सुरक्षा परिणाम आहेत.

जर तुम्ही JWT `localStorage` मध्ये ठेवला, तर **तुमच्या साईटवर यशस्वी झालेला कोणताही XSS attack तो वाचून थेट बाहेर काढू शकतो** - यासाठी कोणतंही browser-level संरक्षण नाही [10]. `HttpOnly` flag असलेल्या cookies XSS द्वारे चोरणं अवघड आहे कारण JavaScript त्या मुळातच वाचू शकत नाही, तरीही त्यांची स्वतःची एक चिंता आहे: cookies प्रत्येक request सोबत आपोआप पाठवल्या जात असल्यामुळे, `SameSite` cookie attributes किंवा anti-CSRF tokens वापरून CSRF पासून संरक्षण करावं लागतं [10].

अलीकडे लोकप्रिय झालेला पॅटर्न, आणि जर तुम्ही नवीन काही बनवत असाल तर मी खरोखर शिफारस करेन असा पॅटर्न:

- **short-lived access token memory मध्ये** ठेवा (एक JS variable किंवा app state) - कधीही persist करू नका, जेणेकरून page reload झाल्यावर तो आपोआप पुसला जाईल.
- **refresh token `HttpOnly`, `Secure`, `SameSite` cookie मध्ये** ठेवा - JS साठी अगम्य, आणि फक्त तुमच्या auth endpoint कडेच आपोआप पाठवला जाणारा.
- page load होताना, त्या cookie चा वापर करून नवीन access token तयार करण्यासाठी तुमच्या refresh endpoint ला शांतपणे call करा [10].

यासाठी थोडं जास्त सेटअप काम लागतं, पण यामुळे तुम्हाला दोन्हीचे फायदे मिळतात - XSS सहजासहजी एखादा long-lived credential चोरू शकत नाही, आणि CSRF संरक्षण फक्त एका छोट्या, मर्यादित refresh endpoint पुरतंच राहतं.

## Session विरुद्ध JWT: बाजू-बाजूने तुलना

चला, हे सगळं एकत्र मांडूया, कारण आता तुमच्याकडे यांची योग्य प्रकारे तुलना करण्याइतका संदर्भ आहे.

| पैलू | Session-based | JWT-based |
|---|---|---|
| "सत्य" कुठे राहतं | Server-side store (DB/Redis/memory) [1] | signed token च्या आतच [6] |
| State model | Stateful | बहुतांशी stateless (काही अटींसह) [1][8] |
| सामान्य transport | session ID सोबत `HttpOnly` cookie [3] | `Authorization: Bearer` header किंवा cookie [4] |
| Logout / revocation | तात्काळ - session record delete करा [2] | अवघड - short expiry, denylist, किंवा refresh rotation आवश्यक [7][8] |
| Cross-domain / microservices साठी वापर | services मध्ये shared session store आवश्यक [12] | shared key/cert वापरून कोणतीही service स्वतंत्रपणे verify करू शकते [6] |
| wire वरील payload आकार | खूप लहान (फक्त एक ID, ~32 bytes) | मोठा - प्रत्येक request मध्ये संपूर्ण claims पाठवले जातात [5] |
| Load अंतर्गत scalability | centralized store सोबत ~500K req/sec [11] | ~1M req/sec, कोणताही storage round-trip नाही [11] |
| सर्वात योग्य कशासाठी | पारंपरिक server-rendered apps, single-domain साईट्स [13] | SPAs, mobile apps, APIs, distributed/microservice systems [12][6] |

## मग नेमकं काय निवडावं?

खरं सांगायचं तर? बहुतेक "साध्या" web apps साठी - pages render करणारी आणि एकच frontend सर्व्ह करणारी Django, Rails, किंवा Express app - **session्स अजूनही सोपा आणि अधिक सुरक्षित डिफॉल्ट पर्याय आहेत**. यात तात्काळ revocation, लहान attack surface, आणि cryptographically चुकण्याची एक कमी संधी मिळते [1][2].

JWT खरंच उपयोगी ठरतात जेव्हा:

- तुमच्याकडे **अनेक services** आहेत ज्यांना एका auth database वर सतत भार न टाकता स्वतंत्रपणे identity verify करायची आहे [6].
- तुम्ही एक **public API** बनवत आहात जो third parties, mobile apps, किंवा वेगवेगळ्या domains वरील partners वापरतात [12].
- तुम्हाला खरोखरच **horizontally scale** करायचं आहे आणि shared session store तुमचा bottleneck बनू नये असं वाटतं [11].

पण माझं खरं मत हे आहे, आणि हे थोडं वादग्रस्त वाटू शकतं: खूप मोठ्या प्रमाणात प्रोजेक्ट्स JWT कडे वळतात कारण ते "modern" वाटतं किंवा एखाद्या tutorial ने तसं सांगितलं म्हणून, JWT ज्या scaling किंवा cross-service समस्या सोडवतो त्या त्यांच्याकडे प्रत्यक्षात आहेत म्हणून नाही. जर तुमचं app एक Node सर्व्हर एका Postgres database शी बोलत असेल, तर Redis ला store म्हणून वापरणारी session cookie तुम्हाला तितकीच चांगली - कदाचित अधिक चांगली - सेवा देईल, आणि token चोरी व revocation बाबत खूप कमी काळजी करावी लागेल.

बऱ्याच production systems शेवटी एक hybrid पद्धतीवर येतात: प्रत्यक्ष API calls साठी short-lived JWT access tokens (जलद, statelessly verify करता येणारे), आणि त्यामागे server-tracked refresh token जो जवळपास... एका session सारखाच वागतो [8][13]. विचार केला तर हे थोडं गमतीशीर आहे - शेवटी तुम्ही session्सच पुन्हा शोधून काढता, फक्त त्यात अतिरिक्त पायऱ्या आणि वर एक cryptographic signature जोडलेली असते.

कदाचित हाच खरा "मूळ फरक" लक्षात ठेवण्यासारखा आहे: हा प्रश्न पूर्णतः "stateful विरुद्ध stateless" चा नाही, तर तो जास्त करून **तुमचं state तुम्ही कुठे ठेवायला तयार आहात, आणि क्लायंट ते प्रामाणिकपणे वाहून नेईल यावर तुमचा किती विश्वास आहे** याबद्दल आहे.

## स्रोत

1. [JWTs vs. sessions: which authentication approach is right for you?](https://stytch.com/blog/jwts-vs-sessions-which-is-right-for-you/)
2. [Session-Based Authentication - SuperTokens Blog](https://supertokens.com/blog/session-based-authentication)
3. [Session vs Token Based Authentication: Cookies, JWT, & Best Practices - Authgear](https://www.authgear.com/post/session-vs-token-authentication/)
4. [JWT.IO - JSON Web Tokens Introduction](https://www.jwt.io/introduction)
5. [JSON Web Token Structure - Auth0 Docs](https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-token-structure)
6. [Stateless Sessions for Stateful Minds: JWTs Explained - Auth0 Blog](https://auth0.com/blog/stateless-auth-for-stateful-minds/)
7. [JSON Web Tokens (JWT) are dangerous for user sessions - Redis Blog](https://redis.io/blog/json-web-tokens-jwt-are-dangerous-for-user-sessions/)
8. [JWT Token Lifecycle Management: Expiration, Refresh, and Revocation Strategies - skycloak](https://skycloak.io/blog/jwt-token-lifecycle-management-expiration-refresh-revocation-strategies/)
9. [JSON Web Token for Java - OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
10. [LocalStorage vs Cookies: Storing JWT Tokens Securely - Cyber Chief](https://www.cyberchief.ai/2023/05/secure-jwt-token-storage.html)
11. [JWT vs Session Authentication: Real Scaling Differences - LoginRadius](https://www.loginradius.com/blog/identity/jwt-vs-session-based-authentication)
12. [Session-Based Authentication vs. JSON Web Tokens (JWTs) in System Design - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/session-based-authentication-vs-json-web-tokens-jwts-in-system-design/)
13. [JWT vs Session authentication - Logto Blog](https://blog.logto.io/token-based-authentication-vs-session-based-authentication)