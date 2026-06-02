+++
title       = "प्रोग्रामर वारंवार करत राहणाऱ्या OOP चुका"
description = "God Objects पासून inheritance च्या गैरवापरापर्यंत — या OOP चुका तुमचा codebase शांतपणे सडवतात. खऱ्या codebases मधील खरे patterns, खरे fixes."
date        = "2026-06-02T18:48:23+05:30"
slug        = "oop-mistakes-programmers-make"
tags        = ["oop", "programming", "software-design", "clean-code"]
keywords    = ["OOP mistakes", "object oriented programming mistakes", "common OOP anti-patterns", "inheritance misuse", "God object", "SOLID violations"]
canonical   = "/mr/posts/oop-mistakes-programmers-make/"
feature_image = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop"
+++

OOP ला पन्नास वर्षे झाली आहेत. Software क्षेत्रातील प्रत्येकाने यावर एक course केलेला आहे. बहुतेकांनी SOLID, inheritance, encapsulation, polymorphism याबद्दल वाचलेले आहे. तरीही — मला startup पासून enterprise projects पर्यंत, codebase नंतर codebase मध्ये त्याच design चुका दिसत राहतात.

सिद्धांत जाणणे म्हणजे चांगले OOP लिहिणे नव्हे. येथे ते खरोखर कुठे चुकते ते पाहूया.

## The God Object

एखादा project सुरू करा, एक `UserService` class तयार करा. कोणीतरी त्यात payment logic जोडते. मग notification handling. मग authentication checks. सहा महिन्यांनंतर: एक 2000-ओळींची फाईल जी सर्वकाही करते, सर्वांवर अवलंबून असते, आणि कोणी तिला स्पर्श केला की तुटते.

**एका class ला बदलण्याचे एकच, आणि केवळ एकच कारण असावे.** हे Single Responsibility Principle आहे [3]. आणि God Object — एकच class जी जास्त जबाबदाऱ्या साठवते — हे त्याचे सर्वात थेट उल्लंघन आहे [2].

खरी समस्या ही नाही की class मोठी आहे. समस्या ही आहे की ती test करणे, maintain करणे, किंवा हस्तांतरित करणे अशक्य होऊन जाते. एका method ला unit test करण्यासाठी अर्ध्या application ला mock करावे लागते. त्या class मध्ये नव्याने येणाऱ्याला समजून घ्यायला तीन तासांचे उत्खनन लागते. त्यात काहीही बदला आणि इतर काय तुटेल ते नक्की सांगता येत नाही [1].

उपाय म्हणजे विभाजन. जर तुमच्या class मध्ये पूर्णपणे वेगळ्या गोष्टी हाताळणाऱ्या methods आहेत — उदाहरणार्थ, persistence आणि email पाठवणे — तर त्या एका फाईलमध्ये अडकलेल्या दोन classes आहेत.

![god object split](/images/posts/oop-mistakes-programmers-make/god-object-split.svg)

## Inheritance हे Code-Sharing चे साधन नाही

ही एक गोष्ट मला खरोखरच त्रास देते, कारण ती अनेकदा चुकीची शिकवली जाते — किंवा निदान चुकीच्या प्रकारे लक्षात राहते.

Inheritance ने **"is-a" संबंध** दर्शवायला हवा. एक `Dog` हा `Animal` आहे. एक `SavingsAccount` हे `BankAccount` आहे. Inheritance याच कारणासाठी अस्तित्वात आहे [1].

मला त्याऐवजी दिसते: एका class मध्ये पाच उपयुक्त methods आहेत, आणि design बद्दल विचार करण्याऐवजी, कोणी त्या methods मिळवण्यासाठी ती class extend करतो. परिणाम म्हणजे खोल inheritance hierarchies, semantically असंबंधित classes मधील घट्ट coupling, आणि असे codebases जेथे एकाच function call चा मागोवा घ्यायला तीस मिनिटे लागतात [1].

क्लासिक उदाहरण म्हणजे `Ostrich extends Bird`. `Bird` मध्ये एक `fly()` method आहे. Ostriches उडू शकत नाहीत, म्हणून `Ostrich` ती override करतो आणि `UnsupportedOperationException` फेकतो. तुम्ही नुकतेच **Liskov Substitution Principle** तोडले — एक subclass program न तोडता त्याच्या parent साठी substitutable असायला हवे [3][2].

हे फक्त toy examples मध्येच नाही, तर खऱ्या codebases मध्येही सतत येते.

**Inheritance पेक्षा composition ला प्राधान्य द्या** [4]. Behavior inherit करण्याऐवजी, ते inject करा:

```java
// Wrong — inherits just to override and break the contract
class Ostrich extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("Ostriches can't fly");
    }
}

// Better — behavior is composed, not inherited
class Ostrich {
    private MovementBehavior movement;

    public Ostrich() {
        this.movement = new RunningBehavior();
    }
}
```

Hierarchy अधिक सपाट होते, behavior बदलण्यायोग्य होते, आणि requirements बदलल्यावर प्रत्येक वेळी design शी लढणे बंद होते [4].

## `public` ला Default मानणे

Encapsulation हे OOP च्या चार स्तंभांपैकी एक आहे. कोणत्याही developer ला हे सांगा आणि ते मान डोलावतील. मग त्यांचा code पहा आणि तुम्हाला दिसेल की निम्मे fields `public` आहेत आणि फाईलच्या शीर्षस्थानी तीन global variables बसलेले आहेत [1].

हे सहसा जाणीवपूर्वक नसते. एखाद्या गोष्टीला public म्हणणे हे खरोखर कोणत्या access level ची गरज आहे याचा विचार करण्यापेक्षा जलद असते. पण जसे काही public होते, तसे इतर classes ते access करतात. आता तुमच्या class ची internal state implicitly उर्वरित codebase कडे असते आणि गोष्टी न तोडता ती बदलता येत नाही.

**Private ने सुरू करा. केवळ आवश्यक असेल तेव्हाच protected किंवा public करा.** जर एखाद्या method ला public असणे आवश्यक आहे की नाही याबद्दल तुम्हाला खात्री नसेल, तर बहुधा नसते [1].

Global variables हे या समस्येचा टोकाचा भाग आहे. एखादी गोष्ट global झाल्यावर, तुम्ही तिचे नियंत्रण संपूर्ण application ला दिले आहे. एखादे global कुठे mutate होते ते शोधणे programming मधील सर्वात अप्रिय debugging अनुभवांपैकी एक आहे.

## Fat Interface चा सापळा

Interface Segregation Principle हे SOLID कुटुंबातील सर्वात कमी चर्चा केले जाणारे आहे, आणि कदाचित ते मला सर्वात शांतपणे उल्लंघन केलेले आढळते [3].

**Clients ना त्यांना वापरायच्या नसलेल्या interfaces implement करण्यास भाग पाडू नये** [3]. या शिस्तीशिवाय, तुम्ही `read()`, `write()`, `delete()`, `archive()`, आणि `export()` सह एक मोठी `IDataManager` interface तयार करता. आता ती implement करणाऱ्या प्रत्येक read-only service ला `write()`, `delete()`, `archive()`, आणि `export()` देखील implement करायला लागते — जरी ती कधीही त्यांना call करणार नसेल.

परिणाम म्हणजे रिकाम्या method stubs किंवा `throw new NotImplementedException()` ने भरलेल्या classes. ही एक design समस्या आहे जी उपायाचा वेश घातला आहे.

Interface विभाजित करा. `IReader`, `IWriter`, `IArchiver`. प्रत्येक class फक्त त्याला खरोखर आवश्यक असलेले implement करते.

## Copy-Paste Programming

हे क्षणात निरुपद्रवी वाटते. दोन classes मध्ये समान logic आहे, फक्त काही ओळी आहेत, आणि ते बाहेर काढणे जास्त वाटते.

ते निरुपद्रवी नाही [5]. एक update, एक चुकलेली जागा, एक असंगत bug fix — आणि दोन copies वेगळ्या होतात. आता application च्या दोन भागांमध्ये behavior मध्ये एक सूक्ष्म फरक आहे आणि तो कसा आला हे कोणालाच माहीत नाही [5].

**स्वतःची पुनरावृत्ती करू नका.** जर समान logic दोन ठिकाणी आहे, तर ते एकाच ठिकाणी असायला हवे. आणि जर तुम्ही classes दरम्यान copy-paste करत असाल, तर हे सहसा एक संकेत आहे की मूळ design चुकीचे होते — एक shared concern स्वतःची class होण्याची वाट पाहत आहे.

## Abstraction चे Over-Engineering

वरील सर्व गोष्टींची दुसरी बाजू, आणि थेट सांगण्यासारखे: SOLID principles आणि design patterns ही साधने आहेत, ध्येय नाहीत.

मी असे codebases पाहिले आहेत जेथे दोन संख्या जोडणाऱ्या method ला `CalculationStrategy` interface, `CalculationStrategyFactory`, आणि `CalculationStrategyFactoryProvider` मध्ये wrapped केले जाते. अतिशयोक्ती नाही [6].

**Abstractions ना त्यांचे अस्तित्व कमवायला हवे.** ठोस कारणाशिवाय design patterns जास्त वापरल्याने code वाचणे कठीण होते, सोपे नाही [7]. SOLID जास्त वापरण्याचा सर्वात मोठा धोका म्हणजे simple logic समजण्यापूर्वी आता पाच abstract classes आणि dependency injection च्या तीन levels मधून navigate करावे लागते [7].

तुमच्याकडे असलेल्या complexity साठी design करा. त्या complexity साठी नाही जी तुम्हाला सैद्धांतिकदृष्ट्या कधीतरी येऊ शकते.

## द्रुत संदर्भ

| चूक | ते कसे दिसते | चांगला उपाय |
|---|---|---|
| God Object | 10+ जबाबदाऱ्यांसह एक class | Single Responsibility नुसार विभाजन |
| Inheritance चा गैरवापर | Code पुनर्वापरासाठी class extend करणे | Composition किंवा delegation |
| LSP उल्लंघन | Subclass exception सह method override करते | Hierarchy पुन्हा तयार करा |
| Encapsulation नाही | Public fields, सर्वत्र global state | Default म्हणून Private |
| Fat interface | 20 methods सह एक interface | अनेक focused interfaces |
| Copy-paste | अनेक classes मध्ये identical logic | Shared component मध्ये काढा |
| Over-abstraction | Simple addition साठी Strategy factory | Complexity justify करेल तेव्हाच abstraction जोडा |

> समाप्त

## स्रोत
1. [Junior Devs करत असलेल्या 3 सामान्य Object-Oriented Programming चुका — DEV Community](https://dev.to/codemom/3-common-object-oriented-programming-mistakes-junior-devs-make-me2)
2. [Java मधील OOP Pitfalls – टाळायचे Anti-patterns](https://prgrmmng.com/oop-pitfalls-java-anti-patterns)
3. [SOLID Design Principles Explained — DigitalOcean](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
4. [Composition over Inheritance — Wikipedia](https://en.wikipedia.org/wiki/Composition_over_inheritance)
5. [OOP मधील Anti-Patterns: काय लक्ष द्यावे — Ahmed Ashraf on Medium](https://medium.com/@ahmedashrafdev99/anti-patterns-in-oop-what-to-watch-out-for-54425fd1fd15)
6. [SOLID Principles Object-Oriented Design कसे मार्गदर्शन करतात — Youngjun Kim on Medium](https://medium.com/@youngjun_kim/how-the-solid-principles-guide-object-oriented-design-examples-of-violations-and-their-8bacac9dda23)
7. [SOLID Principles वापरणे कधी योग्य नसेल — Baeldung](https://www.baeldung.com/cs/solid-principles-avoid)