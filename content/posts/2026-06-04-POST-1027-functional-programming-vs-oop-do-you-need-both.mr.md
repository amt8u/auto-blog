+++
title       = "OOP असताना Functional Programming का वापरायचे?"
description = "OOP दशकांपासून डीफॉल्ट आहे. Functional programming का महत्त्वाचे आहे, ते खरोखर OOP ला कुठे मागे टाकते, आणि एकाच codebase मध्ये दोन्ही कसे वापरायचे."
date        = "2026-06-04T16:32:06+05:30"
slug        = "functional-programming-vs-oop-do-you-need-both"
tags        = ["functional-programming", "oop", "software-design", "javascript", "programming"]
keywords    = ["functional programming vs OOP", "functional programming", "OOP and functional programming", "multi-paradigm programming", "pure functions"]
canonical   = "/mr/posts/functional-programming-vs-oop-do-you-need-both/"
feature_image = "/images/posts/functional-programming-vs-oop-do-you-need-both/fp-vs-oop-feature.svg"
+++

OOP ला ५०+ वर्षे झाली आहेत. Classes, objects, inheritance — हे काम करते, सगळ्यांना माहीत आहे, जवळजवळ प्रत्येक लोकप्रिय भाषा याला support करते. मग लोक functional programming बद्दल अशा प्रकारे का बोलत आहेत जणू ते काही revelation आहे? कारण OOP *गोष्टींचे* modelling करण्यात उत्तम आहे. FP *transformations* चे modelling करण्यात उत्तम आहे. बहुतेक real software मध्ये दोन्ही आहेत, आणि दोन्ही एकत्र करण्याचा प्रयत्न करणे हेच confusion सुरू होण्याचे कारण आहे.

## Functional Programming खरोखर काय आहे?

"class च्या आत functions." हे नाही. तो फक्त functions असलेला OOP आहे.

**Functional programming** हा एक paradigm आहे जिथे तुम्ही pure functions compose करून software तयार करता — असे functions जे, दिलेल्या एकाच input साठी, नेहमी एकच output देतात आणि स्वतःच्या बाहेरील कशालाही स्पर्श करत नाहीत [1].

तीन कल्पना हे परिभाषित करतात:

- **Pure functions** — कोणतेही side effects नाहीत, कोणतेही hidden state बदल नाहीत. `add(2, 3)` नेहमी `5` देते, काहीही असो.
- **Immutability** — एकदा data तयार झाला की, तो बदलला जात नाही. त्याऐवजी नवीन data तयार केला जातो [2].
- **Higher-order functions** — functions जे इतर functions arguments म्हणून घेतात किंवा त्यांना return करतात. `map`, `filter`, `reduce` हे textbook उदाहरणे आहेत [3].

बाकीचे — monads, functors, currying — या तिन्हींवर बनवलेले आहेत. FP चा फायदा घेण्यासाठी तुम्हाला त्या सर्वांना समजून घेण्याची गरज नाही. बहुतेक developers कधीही monads ला स्पर्श करत नाहीत आणि तरीही दररोज clean functional code लिहितात.

## OOP अयशस्वी होत नाही. त्याला फक्त Blind Spots आहेत.

मला स्पष्ट सांगू द्या: OOP वाईट नाही. मी ते दररोज वापरतो. पण काही specific scenarios आहेत जिथे ते तुमचे जीवन अधिक कठीण बनवते.

### Shared mutable state हा शत्रू आहे

OOP मध्ये, objects state ठेवतात. त्या `UserService` instance मध्ये `currentUser` field आहे. तुमच्या `CartManager` मध्ये `items` array आहे. App चे अनेक भाग या वाचतात आणि लिहितात. आणि मग कधीतरी एक bug दिसतो जो तुम्ही विश्वासार्हपणे reproduce करू शकत नाही — कारण एकाच वेळी दोन ठिकाणांहून state बदलला गेला होता [4].

हे काल्पनिक नाही. हे मोठ्या OOP codebases ची रोजची वास्तविकता आहे. Shared state track करणे कठीण आहे, आणि दोन वेगळ्या ठिकाणांहून एका object ला modify करणे म्हणजे कोणत्याही concurrent किंवा async code मध्ये race conditions साठी कारण आहे. FP च्या immutability मुळे bugs ची ही संपूर्ण category नाहीशी होते — तुम्ही data पाठवता, तुम्हाला data मिळतो, तुमच्या मागे काहीही mutate होत नाही [5].

### OOP code test करणे अपेक्षेपेक्षा जास्त काम आहे

`this.db`, `this.cache`, आणि `this.config` वर अवलंबून असलेल्या एखाद्या method ची चाचणी घेण्यासाठी, तुम्हाला mocks हवे आहेत. एका test साठी किमान तीन mocks. आणि जेव्हा class मध्ये 20 methods आणि 8 dependencies असतात, तेव्हा तुमची test setup actual test पेक्षा जास्त लांब होते.

Pure function ला यांची गरज नाही. Input द्या, output तपासा. हीच संपूर्ण test आहे [1].

## प्रत्येक Paradigm खरोखर कुठे चमकतो

| परिस्थिती | अधिक योग्य |
|---|---|
| वास्तविक-जगातील entities चे Modelling (User, Order, Car) | OOP |
| Data pipelines आणि transformations | FP |
| Concurrent किंवा parallel code | FP |
| Lifecycle management सह UI components | OOP |
| Event processing, stream handling | FP |
| अनेक collaborating actors सह मोठ्या system | OOP (काळजीपूर्वक) |
| ETL, analytics, batch jobs | FP |
| GUI frameworks, game entities | OOP |

हे "FP जिंकतो" असे table नाही. OOP अनेक परिस्थितींमध्ये योग्य निवड आहे [6].

## होय, तुम्ही दोन्ही वापरू शकता — आणि बहुतेक Codebases आधीच करतात

JavaScript, Python, Scala, Kotlin, Java (Java 8 पासून), अगदी C# — हे सर्व **multi-paradigm languages** आहेत [7]. ते तुम्हाला एक बाजू निवडण्यास भाग पाडत नाहीत.

एका typical JavaScript codebase कडे पाहा:

```js
// संरचनेसाठी OOP
class UserRepository {
  constructor(db) {
    this.db = db;
  }

  async findById(id) {
    return this.db.query(`SELECT * FROM users WHERE id = ?`, [id]);
  }
}

// transformation साठी FP
const formatUsers = (users) =>
  users
    .filter(u => u.isActive)
    .map(u => ({ id: u.id, name: u.name.trim().toLowerCase() }));
```

`UserRepository` हे classic OOP आहे. `formatUsers` हे pure FP आहे — कोणतेही side effects नाहीत, एकाच input साठी नेहमी एकच output मिळतो. दोन्ही एकाच file मध्ये, एकाच project मध्ये राहतात, कोणताही conflict नाही [8].

हे confusion मुळे paradigms मिसळणे नाही. हे प्रत्येक कामासाठी योग्य साधन वापरणे आहे.

![fp विरुद्ध oop paradigm विभाजन](/images/posts/functional-programming-vs-oop-do-you-need-both/fp-vs-oop-paradigm-split.svg)

## गोंधळ न करता त्यांना खरोखर कसे मिसळायचे

मी जे rule follow करतो: **तुमची structure आणि boundaries परिभाषित करण्यासाठी OOP वापरा, त्या boundaries च्या आत logic साठी FP वापरा**.

प्रत्यक्षात:

- Lifecycle management आवश्यक असलेल्या services, repositories, आणि components साठी Classes.
- Business logic, data transformations, आणि validation rules साठी Pure functions.
- Class methods च्या आत heavy transformation logic टाकणे टाळा — ते pure functions मध्ये extract करा जे independently test केले जाऊ शकतात.
- एखाद्या variable ला जागेवर mutate करणाऱ्या `for` loops ऐवजी `map`, `filter`, `reduce` वापरा.

Python उदाहरण:

```python
# service boundary साठी OOP
class OrderService:
    def __init__(self, db):
        self.db = db

    def get_pending_orders(self, user_id):
        rows = self.db.fetch(user_id)
        return process_orders(rows)  # pure function कडे delegate करा


# logic साठी FP — isolation मध्ये test करणे सोपे
def process_orders(orders):
    return [
        {**o, "total": o["price"] * o["quantity"]}
        for o in orders
        if o["status"] == "pending"
    ]
```

`process_orders` ला database, service, किंवा कोणत्याही बाहेरील गोष्टीवर शून्य dependencies आहेत. याची चाचणी घेणे म्हणजे एक function call, कोणतेही mocks आवश्यक नाहीत [8].

## ज्या Languages नी आधीच हा निर्णय घेतला

Scala हे खरोखरच यासाठी designed केले होते — प्रत्येक value एकाच वेळी एक object *आणि* एक function आहे [7]. React च्या class components पासून hooks कडे झालेला बदल, functionally speaking, UI logic साठी FP कडे जाणे होते. Redux हे JavaScript app च्या आत pure FP आहे. Java ने Java 8 मध्ये `Stream`, `Optional`, lambdas, आणि `Function<T,R>` विशेषत: FP patterns एका OOP language मध्ये आणण्यासाठी जोडले [3].

Industry ने आधीच मतदान केले. Multi-paradigm आता default आहे, exception नाही.

## एक गोष्ट लक्षात ठेवा

Paradigms मिसळणे ठीक आहे. त्यांना *स्पष्ट convention शिवाय* मिसळणे म्हणजे तुम्ही असा code तयार करता जो कोणीही follow करू शकत नाही. मी असे codebases पाहिले आहेत जिथे काही files पूर्णपणे OOP आहेत, काही पूर्णपणे functional आहेत, आणि काही उघड कारण नसताना दोन्ही आहेत. Team logic वाचण्यापेक्षा style decode करण्यात जास्त वेळ घालवते.

**एक convention निवडा: shell साठी OOP, fill साठी FP.** तुमच्या team च्या guidelines मध्ये एकदा लिहा. एवढे पुरेसे आहे.

> समाप्त

## स्रोत
1. [Functional programming vs object-oriented programming (OOP) — CircleCI](https://circleci.com/blog/functional-vs-object-oriented-programming/)
2. [Functional Programming Paradigm — GeeksforGeeks](https://www.geeksforgeeks.org/blogs/functional-programming-paradigm/)
3. [What is Functional Programming? Explained in Python, JS, and Java — Educative](https://www.educative.io/blog/what-is-functional-programming-python-js-java)
4. [Functional programming vs OOP: comparing paradigms — Imaginary Cloud](https://www.imaginarycloud.com/blog/functional-programming-vs-oop)
5. [Functional Programming vs Object-Oriented Programming in Data Analysis — DataCamp](https://www.datacamp.com/tutorial/functional-programming-vs-object-oriented-programming)
6. [Harnessing the Power of OOP and FP Paradigms in Software Development — DEV Community](https://dev.to/adityabhuyan/harnessing-the-power-of-object-oriented-and-functional-programming-paradigms-in-software-development-4m6h)
7. [Top 5 Functional Programming Languages — Coursera](https://www.coursera.org/articles/functional-programming-languages)
8. [Combining Object-Oriented and Functional Programming in Large Projects — DEV Community](https://dev.to/adityabhuyan/combining-object-oriented-and-functional-programming-in-large-projects-6m2)