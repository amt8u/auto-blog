+++
title       = "Elasticsearch Oracle Indexing से कैसे अलग है"
description = "Elasticsearch पूर्ण-पाठ खोज के लिए उल्टे indexes का उपयोग करता है जबकि Oracle सटीक मिलान के लिए B-tree indexes का उपयोग करता है। जानें कि ये डिज़ाइन क्यों महत्वपूर्ण हैं और प्रत्येक को कब उपयोग करें।"
date        = "2026-06-07T13:20:03+05:30"
slug        = "elasticsearch-vs-oracle-indexing"
tags        = ["Elasticsearch", "डेटाबेस", "इंडेक्सिंग", "खोज"]
keywords    = ["Elasticsearch indexing", "Oracle B-tree index", "inverted index", "डेटाबेस indexes"]
canonical   = "/hi/posts/elasticsearch-vs-oracle-indexing/"
+++

अधिकांश डेवलपर सभी indexes को एक साथ मिला देते हैं — "बस कुछ जो queries को तेज़ बनाता है" — यह समझे बिना कि Elasticsearch और Oracle DB बिल्कुल अलग समस्याओं को हल कर रहे हैं। **वे समान डेटा को मौलिक रूप से विपरीत तरीकों से index करते हैं**, और यह अंतर उनके प्रदर्शन के बारे में सब कुछ निर्धारित करता है।

मुझे आपको दिखाने दीजिए कि Oracle पर पूर्ण-पाठ खोज कठिन क्यों लगती है, जबकि Elasticsearch इसे सरल बना देता है।

## मूल समस्या: दो अलग-अलग उपयोग के मामले

Oracle डेटाबेस ऐसे प्रश्नों का उत्तर देने के लिए बनाए गए हैं: "मुझे वह पंक्ति दें जहाँ user_id = 5" या "सभी आदेश खोजें जनवरी 1 और जनवरी 31 के बीच।" **सटीक मिलान और range queries।** डेटा संरचित है, कॉलम द्वारा indexed है, और queries आमतौर पर सटीक होती हैं।

Elasticsearch इसके लिए बनाया गया था: "मुझे सभी दस्तावेज़ खोजें जिनमें 'microservices' या 'distributed systems' शामिल हैं, और उन्हें प्रासंगिकता के अनुसार रैंक करें।" **बड़े पैमाने पर पूर्ण-पाठ खोज।** डेटा अव्यवस्थित हो सकता है, queries अस्पष्ट हैं, और उपयोगकर्ता परिणामों को प्रासंगिकता के अनुसार क्रमबद्ध देखने की अपेक्षा करते हैं, केवल लौटाया जाना नहीं।

ये केवल विभिन्न उपयोग के मामले नहीं हैं — ये विपरीत उपयोग के मामले हैं। Oracle एक के लिए डिज़ाइन किया गया दूसरे के लिए पूछने पर विफल हो जाता है।

## Oracle का B-Tree: सटीकता के लिए निर्मित

Oracle B-tree (balanced tree) indexes का उपयोग करता है। ये कैसे काम करते हैं [1]:

**B-tree एक क्रमबद्ध, sorted structure है।** एक balanced tree को उल्टा किया गया कल्पना करें। शीर्ष पर branch blocks (interior nodes) हैं जो आपकी खोज को निर्देशित करते हैं। नीचे leaf blocks हैं जो actual key values और ROWIDs (table में rows का physical location) को store करते हैं।

जब आप किसी value की खोज करते हैं, तो डेटाबेस tree के नीचे जाता है: branch block → branch block → leaf block → मिल गया। tree की depth उथली है (आमतौर पर लाखों rows के लिए भी 2-4 levels), इसलिए lookups बेहद तेज़ हैं — tree की height के जितने disk reads।

**प्रत्येक leaf block अगले और पिछले leaf blocks को sorted order में point करता है** [1]। यह Oracle को range scans efficiently करने देता है। क्या आपको 100 से 200 तक IDs वाले सभी users चाहिए? एक बार पहला मिल जाने के बाद, linked leaf blocks के माध्यम से आगे बढ़ें। कोई jumping around नहीं।

कीमत? B-trees **एक बार में एक कॉलम** के लिए निर्मित हैं (जब तक आप composite indexes का उपयोग न करें)। वे lookups के लिए optimized हैं, "इस शब्द को containing कुछ भी खोजें" के लिए नहीं।

## Elasticsearch का उल्टा Index: खोज के लिए निर्मित

Elasticsearch कुछ बिल्कुल अलग उपयोग करता है: **एक उल्टा index** [2]। और यहाँ key insight है — यह उल्टा है कि हम सामान्यतः डेटा के बारे में कैसे सोचते हैं।

**सामान्य तरीका:** दस्तावेज़ → उस दस्तावेज़ में शब्दों की list।  
**उल्टा तरीका:** शब्द → उस शब्द को containing दस्तावेज़ों की list।

यहाँ एक concrete example है। मान लीजिए आपके पास तीन दस्तावेज़ हैं:
- Doc 1: "Elasticsearch तेज़ है"
- Doc 2: "Oracle एक डेटाबेस है"
- Doc 3: "Elasticsearch और Oracle डेटाबेस हैं"

एक उल्टा index इसे इस प्रकार store करता है:

| शब्द | दस्तावेज़ |
|------|-----------|
| elasticsearch | [1, 3] |
| तेज़ | [1] |
| oracle | [2, 3] |
| डेटाबेस | [2, 3] |
| है | [1, 2, 3] |

सभी दस्तावेज़ खोजने के लिए जिनमें "elasticsearch" या "oracle" शामिल हैं, index बस दोनों terms को lookup करता है और उनकी document lists को merge करता है। **कोई table scan नहीं। कोई हर दस्तावेज़ की जांच नहीं।** तुरंत।

Oracle ऐसा efficiently नहीं कर सकता क्योंकि इसने दस्तावेज़ों को document ID से index किया है, उनके अंदर के शब्दों से नहीं। पूर्ण-पाठ खोज एक full table scan बन जाती है [3]।

## Elasticsearch वास्तव में डेटा को कैसे Index करता है

Elasticsearch में indexing एक simple उल्टे index से अधिक complex है [4]:

1. **पाठ को tokenize किया जाता है** — "Elasticsearch तेज़ है" ["elasticsearch", "तेज़", "है"] बन जाता है
2. **Tokens को normalize किया जाता है** — lowercasing, stemming, stop words को हटाना (है, एक, the)
3. **Tokens को उल्टे index में store किया जाता है** — प्रत्येक unique token को document IDs से map करना

Tokenization और filtering indexing के दौरान होते हैं, search के दौरान नहीं। यह है कि खोज इतनी तेज़ क्यों है — heavy lifting पहले से ही किया जाता है।

Elasticsearch में प्रत्येक index को **shards** में विभाजित किया जाता है [5]। एक shard एक self-contained Lucene index है। यदि आपका index बहुत बड़ा हो जाता है, तो Elasticsearch इसे कई shards में विभाजित करता है, और ये shards cluster में विभिन्न nodes (computers) पर रहते हैं। **यह horizontal scaling है** — अधिक दस्तावेज़? अधिक shards जोड़ें। अधिक shards जोड़ें? अधिक nodes जोड़ें।

**Replicas** shards की copies हैं। Node A पर primary shard, node B पर replica [5]। यदि node A मर जाता है, तो node B संभाल लेता है। अधिक replicas का मतलब अधिक read capacity भी है — queries किसी भी replica को hit कर सकते हैं।

Oracle इस तरह काम नहीं करता। आप डेटा को manually shard कर सकते हैं (partition tables), लेकिन यह index के काम करने के तरीके के लिए native नहीं है।

## आमने-सामने: Oracle बनाम Elasticsearch

| पहलू | Oracle B-Tree | Elasticsearch उल्टा Index |
|------|---------------|--------------------------|
| **के लिए सर्वश्रेष्ठ** | सटीक मिलान, range queries (WHERE id = 5, WHERE date BETWEEN X AND Y) | पूर्ण-पाठ खोज, प्रासंगिकता ranking, fuzzy queries |
| **खोज प्रकार** | Point lookup | Term lookup |
| **"word X वाले सभी docs खोजें" पर प्रदर्शन** | Full table scan (बड़े पैमाने पर दर्दनाक) | उल्टे index में Hash lookup (nanoseconds) |
| **डेटा structure** | Ordered tree, प्रति index एक column | Flat उल्टा map, term → documents |
| **Scaling** | Vertical (बड़ा server) या manual sharding | Horizontal (अधिक nodes, अधिक shards) |
| **प्रासंगिकता के अनुसार परिणामों को rank करें** | नहीं। Matches को return करता है, ranked नहीं। | हाँ। डिफ़ॉल्ट रूप से TF-IDF और BM25 द्वारा scores करता है। |
| **Update cost** | Rebalance tree nodes (O(log N)) | Rewrite affected posting lists |
| **structured data के लिए उपयुक्त** | हाँ, इसके लिए optimal। | बहुत अच्छा नहीं। Semi-structured / text के लिए बेहतर। |

## यह क्यों महत्वपूर्ण है

मैंने teams को triggers और custom tables का उपयोग करके Oracle पर पूर्ण-पाठ खोज करने की कोशिश करते देखा है। यह काम करता है, मुश्किल से। या वे Oracle की पूर्ण-पाठ indexing (CTXSYS) का उपयोग करते हैं, जो slow और expensive है [1]।

फिर वे एक ही workload को Elasticsearch में move करते हैं और आश्चर्य करते हैं कि यह 100x तेज़ क्यों है। यह magic नहीं है। **यह है क्योंकि Elasticsearch की data structure समस्या के लिए designed है।**

इसके विपरीत, यदि आप ACID transactions और normalized data पर complex joins कर रहे हैं, तो Elasticsearch गलत tool है। यह Oracle की तरह consistency की guarantee नहीं देता। यह eventual-consistent है। कोई transactions नहीं। कोई foreign keys नहीं।

## प्रत्येक को कब उपयोग करें

**निम्नलिखित समय Oracle (या Postgres, MySQL, SQL Server) का उपयोग करें:**
- डेटा structured और relational है
- आपको ACID guarantees की आवश्यकता है
- Queries सटीक हैं (सटीक मिलान, ranges)
- आपके पास < 1TB की hot data है

**निम्नलिखित समय Elasticsearch का उपयोग करें:**
- आप text या logs को index कर रहे हैं
- उपयोगकर्ता keywords के साथ search करते हैं, सटीक values के साथ नहीं
- आपको प्रासंगिकता ranking की आवश्यकता है
- आपको billions के documents के लिए horizontally scale करने की आवश्यकता है

बहुत सारे projects दोनों का उपयोग करते हैं। Transactional data के लिए Oracle, top पर search layer के रूप में Elasticsearch।

भ्रम दोनों को "indexes" कहने से आता है। **ये एक ही चीज़ नहीं हैं।** एक tree है जो values को order करता है। दूसरा एक उल्टा map है जो दस्तावेज़ों को keywords द्वारा group करता है। विभिन्न समस्याएँ, विभिन्न समाधान।

## स्रोत

1. [Oracle B-tree Indexes कैसे काम करते हैं](https://blog.toadworld.com/2017/05/08/how-oracle-b-tree-indexes-work)
2. [Inverted Index & Elasticsearch: आधुनिक खोज कैसे बड़े पैमाने पर काम करती है](https://medium.com/@kavya1234/inverted-index-elasticsearch-e975201d07b1)
3. [Elasticsearch index क्या है? | Elastic Blog](https://www.elastic.co/blog/what-is-an-elasticsearch-index)
4. [Index fundamentals | Elastic Docs](https://www.elastic.co/docs/manage-data/data-store/index-basics)
5. [Clusters, nodes, और shards | Elastic Docs](https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards)
6. [Oracle Indexes और Index-Organized Tables](https://docs.oracle.com/en/database/oracle/oracle-database/26/cncpt/indexes-and-index-organized-tables.html)
7. [Elasticsearch क्या है? कैसे यह काम करता है और संपूर्ण गाइड](https://www.knowi.com/blog/what-is-elastic-search/)