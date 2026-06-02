+++
title       = "प्रोग्रामर जो OOP गलतियाँ बार-बार करते हैं"
description = "God Objects से inheritance के दुरुपयोग तक — वे OOP गलतियाँ जो चुपचाप आपके codebase को बर्बाद कर देती हैं। असली patterns, असली fixes, असली codebases से।"
date        = "2026-06-02T18:48:23+05:30"
slug        = "oop-mistakes-programmers-make"
tags        = ["oop", "प्रोग्रामिंग", "सॉफ्टवेयर-डिज़ाइन", "क्लीन-कोड"]
keywords    = ["OOP गलतियाँ", "ऑब्जेक्ट ओरिएंटेड प्रोग्रामिंग की गलतियाँ", "सामान्य OOP anti-patterns", "inheritance का दुरुपयोग", "God object", "SOLID उल्लंघन"]
canonical   = "/hi/posts/oop-mistakes-programmers-make/"
feature_image = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop"
+++

OOP पचास साल से मौजूद है। Software में हर किसी ने इस पर एक course किया है। अधिकांश ने SOLID, inheritance, encapsulation, polymorphism के बारे में पढ़ा है। और फिर भी — मैं एक के बाद एक codebase में वही design गलतियाँ देखता रहता हूँ, startups से लेकर enterprise projects तक।

Theory जानना अच्छा OOP लिखने के बराबर नहीं है। यहाँ जानते हैं कि वास्तव में कहाँ गलत होता है।

## God Object

एक project शुरू करें, एक `UserService` class बनाएं। कोई उसमें payment logic जोड़ता है। फिर notification handling। फिर authentication checks। छह महीने बाद: एक 2000-line की file जो सब कुछ करती है, सब पर निर्भर करती है, और जब भी कोई उसे छूता है तो टूट जाती है।

**एक class में बदलाव का एक, और केवल एक ही, कारण होना चाहिए।** यह Single Responsibility Principle है [3]। और God Object — एक ऐसी class जो अत्यधिक जिम्मेदारियाँ जमा कर लेती है — इसका सबसे सीधा उल्लंघन है [2]।

असली समस्या यह नहीं है कि class बड़ी है। यह है कि इसे test करना, maintain करना, या किसी को सौंपना असंभव हो जाता है। एक method को unit test करने के लिए आपको आधे application को mock करना पड़ता है। उस class में किसी नए को onboard करने में तीन घंटे की archaeology लगती है। उसमें कुछ भी बदलें और आप निश्चित नहीं होते कि और क्या टूट जाएगा [1]।

Fix है splitting। अगर आपकी class में पूरी तरह अलग-अलग concerns — जैसे persistence और email sending — को handle करने वाले methods हैं, तो वे एक file में बंद दो classes हैं।

![god object split](/images/posts/oop-mistakes-programmers-make/god-object-split.svg)

## Inheritance कोड-शेयरिंग का टूल नहीं है

यह वह है जो मुझे वास्तव में परेशान करता है, क्योंकि इसे अक्सर गलत तरीके से सिखाया जाता है — या कम से कम गलत याद रखा जाता है।

Inheritance को **"is-a" relationship** model करनी चाहिए। एक `Dog` एक `Animal` है। एक `SavingsAccount` एक `BankAccount` है। यही inheritance का उद्देश्य है [1]।

इसके बजाय मैं जो देखता हूँ: एक class में पाँच उपयोगी methods हैं, और design के बारे में सोचने की बजाय, कोई उन methods तक पहुँचने के लिए उसे extend कर लेता है। इसका परिणाम है deep inheritance hierarchies, semantically असंबंधित classes के बीच tight coupling, और ऐसे codebases जहाँ एक function call trace करने में तीस मिनट लगते हैं [1]।

क्लासिक उदाहरण है `Ostrich extends Bird`। `Bird` में `fly()` method है। Ostriches उड़ नहीं सकते, इसलिए `Ostrich` उसे override करके `UnsupportedOperationException` throw करता है। आपने **Liskov Substitution Principle** तोड़ दिया — एक subclass को program तोड़े बिना अपने parent की जगह लेने में सक्षम होना चाहिए [3][2]।

यह real codebases में लगातार आता है, सिर्फ toy examples में नहीं।

**Inheritance की जगह composition को प्राथमिकता दें** [4]। Behavior inherit करने की बजाय, उसे inject करें:

```java
// गलत — contract तोड़ने के लिए override करता है
class Ostrich extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("Ostriches can't fly");
    }
}

// बेहतर — behavior compose किया गया है, inherit नहीं
class Ostrich {
    private MovementBehavior movement;

    public Ostrich() {
        this.movement = new RunningBehavior();
    }
}
```

Hierarchy flatter बन जाती है, behavior swappable बन जाता है, और जब भी requirements बदलती हैं तो आप design से लड़ना बंद कर देते हैं [4]।

## `public` को Default मानना

Encapsulation OOP के चार pillars में से एक है। किसी भी developer को यह दोहराने को कहें और वे सिर हिलाएंगे। फिर उनका code देखें और पाएंगे कि आधे fields `public` हैं और file के ऊपर तीन global variables बैठे हैं [1]।

यह आमतौर पर जानबूझकर नहीं होता। किसी चीज़ को public mark करना यह सोचने से तेज़ है कि उसे वास्तव में किस access level की जरूरत है। लेकिन जैसे ही कुछ public होता है, अन्य classes उसे access करने लगती हैं। अब आपकी class की internal state implicitly बाकी codebase की है और आप इसे बिना चीजें तोड़े बदल नहीं सकते।

**Private से शुरू करें। Protected या public में तभी promote करें जब जरूरी हो।** अगर आप अनिश्चित हैं कि किसी method को public होना चाहिए या नहीं, तो शायद नहीं होना चाहिए [1]।

Global variables इस समस्या का extreme end हैं। एक बार कुछ global हो जाए, आपने उसका control पूरे application को सौंप दिया। Global कहाँ mutate होता है यह trace करना programming के सबसे अप्रिय debugging अनुभवों में से एक है।

## Fat Interface का जाल

Interface Segregation Principle SOLID परिवार में सबसे कम चर्चित है, और शायद वह जिसे मैं सबसे चुपचाप violated पाता हूँ [3]।

**Clients को ऐसे interfaces implement करने के लिए मजबूर नहीं किया जाना चाहिए जिनका वे उपयोग नहीं करते** [3]। इस discipline के बिना, आप `read()`, `write()`, `delete()`, `archive()`, और `export()` के साथ एक बड़ा `IDataManager` interface बनाते हैं। अब उसे implement करने वाली हर read-only service को `write()`, `delete()`, `archive()`, और `export()` भी implement करनी होगी — भले ही वह उन्हें कभी call न करे।

परिणाम है classes जो empty method stubs या `throw new NotImplementedException()` से भरी हैं। यह एक design problem है जो solution का costume पहने है।

Interface को split करें। `IReader`, `IWriter`, `IArchiver`। हर class केवल वही implement करती है जो उसे वास्तव में चाहिए।

## Copy-Paste Programming

यह उस समय हानिरहित लगता है। दो classes में similar logic है, बस कुछ lines हैं, और इसे extract करना overkill लगता है।

यह हानिरहित नहीं है [5]। एक update, एक missed location, एक inconsistent bug fix — और दो copies diverge हो जाती हैं। अब application के दो हिस्सों में behavior में एक subtle difference है और कोई नहीं जानता यह कैसे आ गया [5]।

**खुद को दोहराएं नहीं।** अगर वही logic दो जगह रहता है, तो वह एक जगह होना चाहिए। और अगर आप classes के बीच copy-paste कर रहे हैं, तो यह आमतौर पर संकेत है कि original design गलत था — एक shared concern है जो अपनी class बनने की प्रतीक्षा कर रही है।

## Abstraction को Over-Engineer करना

ऊपर की हर बात का flip side, और सीधे कहने लायक: SOLID principles और design patterns tools हैं, goals नहीं।

मैंने ऐसे codebases देखे हैं जहाँ दो numbers जोड़ने वाले method को एक `CalculationStrategy` interface, एक `CalculationStrategyFactory`, और एक `CalculationStrategyFactoryProvider` में wrap किया गया है। अतिशयोक्ति नहीं कर रहा [6]।

**Abstractions को अपना अस्तित्व justify करना चाहिए।** बिना किसी concrete कारण के design patterns को over-apply करना code को पढ़ना कठिन बनाता है, आसान नहीं [7]। SOLID को over-apply करने का सबसे बड़ा खतरा यह है कि simple logic को समझने से पहले अब आपको पाँच abstract classes और dependency injection के तीन levels navigate करने पड़ते हैं [7]।

उस complexity के लिए design करें जो आपके पास है। उस complexity के लिए नहीं जो आप theoretically कभी encounter कर सकते हैं।

## Quick Reference

| गलती | कैसी दिखती है | बेहतर तरीका |
|---|---|---|
| God Object | 10+ जिम्मेदारियों वाली एक class | Single Responsibility से split करें |
| Inheritance का दुरुपयोग | Code reuse के लिए class extend करना | Composition या delegation |
| LSP violation | Subclass method को exception से override करती है | Hierarchy को redesign करें |
| No encapsulation | Public fields, हर जगह global state | Default में private |
| Fat interface | 20 methods वाला एक interface | Multiple focused interfaces |
| Copy-paste | Multiple classes में identical logic | Shared component में extract करें |
| Over-abstraction | Simple addition के लिए Strategy factory | Complexity justify होने पर abstraction जोड़ें |

> End

## Sources
1. [3 Common Object-Oriented Programming Mistakes Junior Devs Make — DEV Community](https://dev.to/codemom/3-common-object-oriented-programming-mistakes-junior-devs-make-me2)
2. [OOP Pitfalls in Java – Anti-patterns You Should Avoid](https://prgrmmng.com/oop-pitfalls-java-anti-patterns)
3. [SOLID Design Principles Explained — DigitalOcean](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
4. [Composition over Inheritance — Wikipedia](https://en.wikipedia.org/wiki/Composition_over_inheritance)
5. [Anti-Patterns in OOP: What to Watch Out For — Ahmed Ashraf on Medium](https://medium.com/@ahmedashrafdev99/anti-patterns-in-oop-what-to-watch-out-for-54425fd1fd15)
6. [How the SOLID Principles Guide Object-Oriented Design — Youngjun Kim on Medium](https://medium.com/@youngjun_kim/how-the-solid-principles-guide-object-oriented-design-examples-of-violations-and-their-8bacac9dda23)
7. [When Using SOLID Principles May Not Be Appropriate — Baeldung](https://www.baeldung.com/cs/solid-principles-avoid)
