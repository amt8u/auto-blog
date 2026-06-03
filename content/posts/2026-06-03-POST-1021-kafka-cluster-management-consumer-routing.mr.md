+++
title       = "Kafka क्लस्टर कसे व्यवस्थापित करतो आणि ग्राहकांना योग्य दिशेने कसे मार्गदर्शन करतो"
description = "Kafka ब्रोकर्सचे समन्वय कसे करतो, विभाजने कशी नियुक्त करतो आणि प्रत्येक ग्राहक क्लस्टरमधील अचूक ठिकाणाहून वाचतो याची सखोल माहिती."
date        = "2026-06-03T11:55:22+05:30"
slug          = "kafka-cluster-management-consumer-routing"
tags          = ["kafka", "distributed-systems", "backend"]
keywords      = ["kafka cluster management", "kafka consumer group partition assignment", "kafka broker leader election", "kafka ISR", "kafka bootstrap server"]
canonical     = "/mr/posts/kafka-cluster-management-consumer-routing/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200&auto=format&fit=crop"
+++

Kafka बाहेरून अगदी सरळ-साधा वाटतो — तुम्ही एखाद्या टॉपिकवर प्रकाशित करता, कुणीतरी वाचतो. आतून हे एक बऱ्यापैकी गुंतागुंतीचे वितरित प्रणाली आहे जिथे एकही बाइट वितरित होण्यापूर्वी अनेक भागांनी कोणाचे काय आहे यावर सहमती व्हायला हवी. मी यात बराच वेळ घालवला आणि बहुतेक लेख "विभाजनांमुळे समांतरता मिळते" इथेच थांबतात, वास्तविक हँडशेक समजावून सांगत नाहीत. मला अधिक खोलात जाऊ द्या.

## Kafka क्लस्टर म्हणजे नक्की काय

Kafka क्लस्टर म्हणजे **ब्रोकर्स**चा एक समूह — साधे JVM प्रक्रिया, प्रत्येक स्वतःच्या मशीनवर (किंवा कंटेनरमध्ये) चालत असतात. प्रत्येक ब्रोकर डेटाचा एक भाग साठवतो आणि क्लस्टरच्या उर्वरित भागाबद्दल जाणतो [1].

टॉपिक्स म्हणजे तुम्ही ज्याच्याशी संवाद साधता ती तार्किक एकक. भौतिकदृष्ट्या, एक टॉपिक **विभाजनां**मध्ये विभागला जातो, आणि प्रत्येक विभाजन रेप्लिका म्हणून अनेक ब्रोकर्समध्ये पसरलेले असते. त्या रेप्लिकांपैकी एक **नेता** (leader) असतो — तोच एकमेव त्या विभाजनासाठी वाचन आणि लेखन हाताळतो. बाकी सर्व **अनुगामी** (followers) असतात जे शांतपणे नेत्याचा डेटा प्रतिकृती करतात [1].

तर जेव्हा लोक "Kafka क्षैतिजरित्या विस्तारतो" असे म्हणतात, तेव्हा त्यांचा अर्थ असतो: एखाद्या टॉपिकमध्ये १०० विभाजने असू शकतात, आणि ते १०० विभाजने N ब्रोकर्समध्ये पसरवता येतात — प्रत्येक ब्रोकर वेगळा तुकडा हाताळतो, तुमच्या अॅपमधील प्रत्येक ग्राहक समांतरपणे वेगळा तुकडा वाचतो.

![kafka cluster overview](/images/posts/kafka-cluster-management-consumer-routing/kafka-cluster-overview.svg)

## क्लस्टरचे समन्वय कोण करतो — ZooKeeper विरुद्ध KRaft

इथेच बऱ्याच जुन्या लेखांमुळे लोक गोंधळतात. ऐतिहासिकदृष्ट्या, Kafka ने क्लस्टर समन्वय **ZooKeeper**कडे सोपवले होते. प्रत्येक ब्रोकर ZooKeeper मध्ये एक क्षणिक नोड तयार करण्यासाठी स्पर्धा करत होता; यशस्वी होणारा पहिला ब्रोकर **Controller** ब्रोकर बनत असे — क्लस्टरमधील विभाजन नेत्यांची नियुक्ती करण्याची जबाबदारी ज्याची असे [2].

**ती आर्किटेक्चर आता राहिलेली नाही.** Kafka 3.3 पासून ती रद्द केली गेली, आणि Kafka 4.0 पासून ती अजिबात समर्थित नाही [3]. त्याच्या जागी **KRaft** (Kafka Raft) आले आहे.

### KRaft: Kafka स्वतःची सहमती चालवतो

KRaft मोडमध्ये, ब्रोकर्सचा एक उपसमूह (किंवा समर्पित नोड्स) **controllers** म्हणून काम करतात आणि Raft quorum तयार करतात. ते Raft सहमती अल्गोरिदम वापरून स्वतःमध्ये एक नेता निवडतात — बहुमत मत, जुने नेते टाळण्यासाठी term numbers, आणि quorum सुसंगत ठेवण्यासाठी लॉग रेप्लिकेशन [4].

सर्व क्लस्टर मेटाडेटा — टॉपिक configs, विभाजन नियुक्त्या, ब्रोकर नोंदणी — `__cluster_metadata` नावाच्या एका अंतर्गत Kafka टॉपिकमध्ये राहतो. सक्रिय controller नेता या लॉगमध्ये इव्हेंट्स लिहितो; follower controllers ते पुन्हा play करतात [3]. ब्रोकर्स या मेटाडेटा स्ट्रीमची सदस्यता घेतात आणि त्यांचे स्थानिक दृश्य अद्ययावत ठेवतात.

हे का महत्त्वाचे आहे? कारण:
- Failover जलद आहे — बाह्य ZooKeeper समन्वय फेरी नाही [2]
- मेटाडेटा लॉग स्वतः Kafka च्या स्वतःच्या हमींसह रेप्लिकेट केला जातो
- तुम्ही कमी हलणारे भाग तैनात करता

## विभाजन नेते कसे निवडले जातात

जेव्हा एखादा ब्रोकर बंद पडतो, तेव्हा कुणाला त्याच्या विभाजन नेतृत्वाचा ताबा घ्यावा लागतो. ती जबाबदारी KRaft controller ची आहे.

नवीन नेता कोण असू शकतो हे ठरवण्यासाठी controller **ISR यादी** (In-Sync Replicas) वापरतो [5]. ISR म्हणजे त्या follower replicas चा संच जे नेत्याशी पूर्णपणे समकालीन आहेत — मागे पडणाऱ्या replicas ISR मधून काढल्या जातात. त्यामुळे नेता बंद पडला तर:

1. Controller ब्रोकर गेल्याचे ओळखतो
2. तो बंद पडलेल्या ब्रोकरने नेतृत्व केलेल्या प्रत्येक विभाजनासाठी ISR पाहतो
3. एक ISR सदस्य निवडतो आणि त्याला नेता म्हणून बढती देतो
4. तो निर्णय `__cluster_metadata` मध्ये लिहितो
5. इतर सर्व ब्रोकर्स मेटाडेटा स्ट्रीममधून नवीन नेता शिकतात

**फक्त ISR सदस्यच नेता निवडणुकीसाठी पात्र आहेत.** हे महत्त्वाचे आहे — हे हमी देते की नवीन नेत्याकडे सर्व commit केलेला डेटा आहे आणि ग्राहकांना कोणतेही अंतर दिसत नाही [5].

## ग्राहक खरोखर योग्य ब्रोकर कसा शोधतो

हा तो भाग आहे जो बहुतेक लोक सरावून टाकतात. ग्राहक फक्त जादुईपणे योग्य ब्रोकरशी जोडत नाही. एक विशिष्ट हँडशेक आहे.

### पायरी १ — Bootstrap (एक-वेळची क्लस्टर शोध)

तुम्ही `bootstrap.servers` मध्ये एक किंवा अधिक ब्रोकर पत्ते configure करता. ही यादी **फक्त प्रारंभिक शोधासाठी** आहे, चालू traffic साठी नाही [6].

Client यादीतील कोणताही पत्ता निवडतो, TCP कनेक्शन उघडतो, आणि **Metadata request** पाठवतो. कोणताही ब्रोकर यावर उत्तर देऊ शकतो — तो संपूर्ण ब्रोकर यादी आणि client ज्या प्रत्येक टॉपिकची काळजी करतो त्याचे विभाजन-ते-नेता mapping परत करतो [6]. त्या एकाच request नंतर, client कडे क्लस्टरचा संपूर्ण नकाशा असतो आणि तो त्याला हव्या असलेल्या नेत्यांशी थेट जोडतो.

जर तुमचा bootstrap ब्रोकर एक तास नंतर बंद पडला, तरी client आधीच ठीक आहे — त्याला उर्वरित क्लस्टर माहीत आहे [6].

### पायरी २ — Group Coordinator शोधणे

ग्राहक कोणत्याही ब्रोकरशी जोडत नाहीत. प्रत्येक **consumer group** एका विशिष्ट **Group Coordinator** ब्रोकरशी जोडलेली असते.

Mapping निश्चित आहे: Kafka `group.id` string ला अंतर्गत `__consumer_offsets` टॉपिकच्या एका विभाजनावर hash करतो, आणि त्या विभाजनाचा नेता Group Coordinator असतो [7]. एकाच `group.id` असलेले सर्व ग्राहक एकाच coordinator शी बोलतात. वेगवेगळे groups वेगवेगळ्या coordinators मध्ये वितरित केले जातात.

ग्राहक कोणत्याही ब्रोकरला `FindCoordinator` request पाठवतो (त्यात `group.id` असतो). तो ब्रोकर hash resolve करतो आणि coordinator चा host आणि port परत देतो [7].

### पायरी ३ — JoinGroup आणि विभाजन नियुक्ती

एकदा group मधील प्रत्येक ग्राहकाने coordinator शोधला की, rebalance protocol सुरू होतो:

1. प्रत्येक ग्राहक coordinator ला `JoinGroup` request पाठवतो
2. Coordinator एका ग्राहकाला **Group Leader** म्हणून नियुक्त करतो — सहसा सर्वात आधी join करणारा
3. Coordinator Group Leader ला संपूर्ण सदस्य यादी पाठवतो
4. Group Leader **विभाजन नियुक्ती strategy** स्थानिकपणे चालवतो आणि निकाल परत पाठवतो
5. Coordinator `SyncGroup` responses द्वारे प्रत्येक सदस्याला नियुक्त्या वितरित करतो [7][8]

Group Leader फक्त एक तात्पुरती तार्किक भूमिका आहे, कायमचा नोड नाही. प्रत्येक rebalance मध्ये बदलतो [7].

### विभाजन नियुक्ती Strategies

Kafka काही built-in strategies सह येतो, `partition.assignment.strategy` द्वारे configure करण्यायोग्य [8]:

| Strategy | कसे कार्य करते | कशासाठी सर्वोत्तम |
|---|---|---|
| **RangeAssignor** | ग्राहकांमध्ये संख्यात्मकरित्या विभाजने विभागतो | प्रति टॉपिक साधे, अंदाजे विभाजन |
| **RoundRobinAssignor** | ग्राहकांमध्ये वर्तुळाकार वितरण | टॉपिक्समध्ये समान वितरण |
| **StickyAssignor** | मागील नियुक्त्या ठेवतो, rebalance वर हालचाल कमीत कमी करतो | warm caches सह stateful ग्राहक |
| **CooperativeStickyAssignor** | Sticky सारखे पण incremental rebalances परवानगी देते (3.0+ मध्ये default) | Production — stop-the-world rebalances टाळतो |

**CooperativeStickyAssignor हे Kafka 3.0 पासून default आहे** कारण ते incremental rebalances करते — फक्त ज्या विभाजनांना खरोखर हलण्याची गरज आहे तेच revoke केले जातात, सर्व एकत्र नाही [8].

## ग्राहक काय वाचू शकतात आणि काय नाही

एक सूक्ष्म गोष्ट: ग्राहक **विभाजन नेत्याकडून** वाचतात, followers कडून नाही [5]. त्यामुळे जरी follower replica तुमच्या ग्राहकाच्या शारीरिकदृष्ट्या जवळ असलेल्या ब्रोकरवर असली, तरी वाचन नेत्याकडेच जाते.

एक अपवाद आहे — **Follower Fetching** (Kafka 2.4 मध्ये सादर केले), जिथे ग्राहकाला जवळच्या replica कडून वाचण्यासाठी configure करता येते. परंतु default म्हणून, फक्त नेत्याकडून वाचन.

ग्राहक **high-water mark** च्या पलीकडे डेटाही वाचू शकत नाहीत — सर्व ISR replicas ने acknowledge केलेला नवीनतम offset [5]. हे ग्राहकांना असा डेटा वाचण्यापासून प्रतिबंधित करते जो rollback होऊ शकतो जर followers catch up होण्यापूर्वी नेता बंद पडला.

## ब्रोकर मध्ये-वाचन बंद पडला तर काय होते

समजा एक ग्राहक विभाजन १ वाचत आहे, आणि त्याचा नेता ब्रोकर crash होतो:

1. KRaft controller ब्रोकर failure ओळखतो
2. तो विभाजन १ साठी ISR मधून नवीन नेता निवडतो
3. तो `__cluster_metadata` अपडेट करतो
4. ग्राहकाची पुढील fetch request जुन्या ब्रोकरकडून `NOT_LEADER_OR_FOLLOWER` error मिळवते (किंवा timeout)
5. ग्राहक आपोआप त्याचा metadata refresh करतो आणि fetch पुन्हा करतो — आता नवीन नेत्याकडे [6]

ग्राहकाला manual intervention ची गरज नाही. Client library retry आणि metadata refresh पारदर्शकपणे हाताळते. तुमच्या application code च्या दृष्टिकोनातून, थोडा brief pause असेल, परंतु messages गमावले जात नाहीत किंवा duplicate होत नाहीत (योग्य offset commit settings गृहीत धरून).

## एका Flow मध्ये संपूर्ण चित्र

![kafka consumer flow](/images/posts/kafka-cluster-management-consumer-routing/kafka-consumer-flow.svg)

- **Bootstrap broker** — फक्त एकदाच वापरला जातो, संपूर्ण क्लस्टर नकाशा मिळवण्यासाठी
- **Group Coordinator** — consumer group साठी join/sync/heartbeat हाताळतो
- **Partition Leader** — ज्या ब्रोकरकडून ग्राहक खरोखर messages fetch करतो

हे तीन वेगवेगळे ब्रोकर असू शकतात, किंवा एकच. Kafka ला फरक पडत नाही.

## ही Design का टिकते

आर्किटेक्चर एकदा संपूर्णपणे पाहिले की खरोखरच सुंदर आहे. Metadata discovery समन्वयापासून वेगळे आहे जे डेटा transfer पासून वेगळे आहे. प्रत्येक layer ला एक स्पष्ट मालक आहे — क्लस्टर state साठी KRaft, consumer group state साठी Group Coordinator, डेटासाठी Partition Leader.

कोणत्याही layer वर failures साठी defined fallback paths आहेत. एक बंद bootstrap broker startup नंतर irrelevant आहे. एक बंद Group Coordinator `FindCoordinator` retry trigger करतो. एक बंद Partition Leader metadata refresh आणि reconnect trigger करतो.

implement करणे सोपे नाही — परंतु operator म्हणून reason करायला खूप clean आहे.

> शेवट

## स्रोत
1. [Kafka Topics, Partitions, and Brokers: Core Architecture — Conduktor](https://www.conduktor.io/glossary/kafka-topics-partitions-brokers-core-architecture)
2. [ZooKeeper and Apache Kafka® Explained: From Legacy to KRaft — Confluent](https://www.confluent.io/learn/zookeeper-kafka/)
3. [KRaft vs ZooKeeper — Apache Kafka Official Docs](https://kafka.apache.org/42/getting-started/zk2kraft/)
4. [KRaft Explained: How Kafka Implements Raft Consensus — Medium](https://medium.com/@prakashpsgcse/kraft-explained-how-kafka-implements-raft-consensus-209f5b0dc45e)
5. [Understanding In-Sync Replicas (ISR) in Apache Kafka — GeeksforGeeks](https://www.geeksforgeeks.org/apache-kafka/understanding-in-sync-replicas-isr-in-apache-kafka/)
6. [What is a Kafka Bootstrap Server? — Confluent](https://www.confluent.io/learn/kafka-bootstrap-server/)
7. [Apache Kafka® Internal Architecture — Consumer Group Protocol — Confluent Developer](https://developer.confluent.io/courses/architecture/consumer-group-protocol/)
8. [How to Implement Kafka Consumer Assignment Strategies — OneUptime](https://oneuptime.com/blog/post/2026-01-30-kafka-consumer-assignment-strategies/view)