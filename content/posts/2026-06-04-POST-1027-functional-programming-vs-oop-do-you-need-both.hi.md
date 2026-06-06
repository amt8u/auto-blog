+++
title       = "जब OOP मौजूद है तो Functional Programming क्यों इस्तेमाल करें?"
description = "OOP दशकों से डिफ़ॉल्ट रहा है। यहाँ जानें कि Functional Programming क्यों मायने रखती है, यह OOP को कहाँ मात देती है, और एक ही codebase में दोनों का उपयोग कैसे करें।"
date        = "2026-06-04T16:32:06+05:30"
slug        = "functional-programming-vs-oop-do-you-need-both"
tags        = ["functional-programming", "oop", "software-design", "javascript", "programming"]
keywords    = ["functional programming vs OOP", "functional programming", "OOP and functional programming", "multi-paradigm programming", "pure functions"]
canonical   = "/hi/posts/functional-programming-vs-oop-do-you-need-both/"
feature_image = "/images/posts/functional-programming-vs-oop-do-you-need-both/fp-vs-oop-feature.svg"
+++

OOP 50+ साल पुराना है। Classes, objects, inheritance — यह काम करता है, सब इसे जानते हैं, और लगभग हर लोकप्रिय भाषा इसे support करती है। तो फिर लोग Functional Programming की बात ऐसे क्यों कर रहे हैं जैसे यह कोई नई खोज हो? क्योंकि OOP *चीज़ों* को model करने में बेहतरीन है। FP *बदलावों* (transformations) को model करने में। ज़्यादातर असली software में दोनों होते हैं, और इन दोनों को एक समझना ही असली उलझन की जड़ है।

## Functional Programming वास्तव में क्या है?

"class के अंदर functions" — यह नहीं। वह तो बस functions वाला OOP है।

**Functional Programming** एक paradigm है जहाँ आप software को pure functions को compose करके बनाते हैं — ऐसे functions जो एक ही input पर हमेशा एक ही output देते हैं और अपने बाहर किसी चीज़ को नहीं छूते [1]।

इसे तीन विचार परिभाषित करते हैं:

- **Pure functions** — कोई side effects नहीं, कोई छिपे हुए state changes नहीं। `add(2, 3)` हमेशा `5` ही लौटाता है, चाहे कुछ भी हो।
- **Immutability** — एक बार data बन जाने के बाद उसे बदला नहीं जाता। इसके बजाय नया data बनाया जाता है [2]।
- **Higher-order functions** — ऐसे functions जो दूसरे functions को argument के रूप में लेते हैं या उन्हें return करते हैं। `map`, `filter`, `reduce` इसके पाठ्यपुस्तक उदाहरण हैं [3]।

बाकी सब — monads, functors, currying — इन्हीं तीन के ऊपर बने हैं। FP का फ़ायदा उठाने के लिए इन सबको समझना ज़रूरी नहीं। ज़्यादातर developers कभी monads को नहीं छूते और फिर भी हर रोज़ साफ़-सुथरा functional code लिखते हैं।

## OOP असफल नहीं होता। बस उसके कुछ अंधे कोने हैं।

सीधे बात करूँ: OOP बुरा नहीं है। मैं इसे हर रोज़ इस्तेमाल करता हूँ। लेकिन कुछ खास situations में यह आपकी ज़िंदगी को सच में मुश्किल बना देता है।

### Shared mutable state दुश्मन है

OOP में objects state रखते हैं। उस `UserService` instance में एक `currentUser` field है। आपके `CartManager` में एक `items` array है। App के कई हिस्से इन्हें पढ़ते और लिखते हैं। और फिर किसी बिंदु पर एक ऐसा bug सामने आता है जिसे आप reliably reproduce नहीं कर सकते — क्योंकि state को एक साथ दो जगहों से बदला जा रहा था [4]।

यह कोई काल्पनिक बात नहीं है। यह बड़े OOP codebases की रोज़मर्रा की हकीकत है। Shared state को track करना मुश्किल होता है, और किसी object को दो अलग-अलग जगहों से बदलना async या concurrent code में race conditions की नुस्खा है। FP की immutability bugs की इस पूरी श्रेणी को ही हटा देती है — आप data अंदर डालते हैं, data बाहर आता है, पर्दे के पीछे कुछ भी mutate नहीं होता [5]।

### OOP code को test करना उससे ज़्यादा मेहनत माँगता है जितनी होनी चाहिए

`this.db`, `this.cache`, और `this.config` पर निर्भर किसी method को test करने के लिए आपको mocks चाहिए। एक test के लिए कम से कम तीन mocks। और जब class में 20 methods और 8 dependencies हों, तो आपका test setup असली test से लंबा हो जाता है।

एक pure function को इनमें से कुछ भी नहीं चाहिए। Input दो, output check करो। बस यही test है [1]।

## हर Paradigm वास्तव में कहाँ चमकता है

| स्थिति | बेहतर विकल्प |
|---|---|
| असल दुनिया की चीज़ों को model करना (User, Order, Car) | OOP |
| Data pipelines और transformations | FP |
| Concurrent या parallel code | FP |
| Lifecycle management वाले UI components | OOP |
| Event processing, stream handling | FP |
| कई collaborating actors वाला बड़ा system | OOP (सावधानी के साथ) |
| ETL, analytics, batch jobs | FP |
| GUI frameworks, game entities | OOP |

यह "FP जीतता है" वाली table नहीं है। बहुत सी situations में OOP सही choice है [6]।

## हाँ, आप दोनों का उपयोग कर सकते हैं — और ज़्यादातर Codebases पहले से ऐसा करते हैं

JavaScript, Python, Scala, Kotlin, Java (Java 8 से), यहाँ तक कि C# — ये सब **multi-paradigm languages** हैं [7]। ये आपको एक तरफ़ चुनने पर मजबूर नहीं करतीं।

एक typical JavaScript codebase देखें:

```js
// OOP for structure
class UserRepository {
  constructor(db) {
    this.db = db;
  }

  async findById(id) {
    return this.db.query(`SELECT * FROM users WHERE id = ?`, [id]);
  }
}

// FP for transformation
const formatUsers = (users) =>
  users
    .filter(u => u.isActive)
    .map(u => ({ id: u.id, name: u.name.trim().toLowerCase() }));
```

`UserRepository` classic OOP है। `formatUsers` pure FP है — कोई side effects नहीं, एक ही input हमेशा एक ही output देता है। दोनों एक ही file में, एक ही project में, बिना किसी टकराव के रहते हैं [8]।

यह उलझन में paradigms को मिलाना नहीं है। यह हर काम के लिए सही औज़ार इस्तेमाल करना है।

![fp vs oop paradigm split](/images/posts/functional-programming-vs-oop-do-you-need-both/fp-vs-oop-paradigm-split.svg)

## बिना गड़बड़ी के इन्हें Actually कैसे Mix करें

मेरा नियम: **OOP से अपनी structure और boundaries परिभाषित करें, उन boundaries के अंदर की logic के लिए FP इस्तेमाल करें।**

व्यवहार में:

- Services, repositories, और ऐसे components के लिए classes जिन्हें lifecycle management चाहिए।
- Business logic, data transformations, और validation rules के लिए pure functions।
- Class methods के अंदर भारी transformation logic डालने से बचें — इसे pure functions में निकालें जिन्हें independently test किया जा सके।
- किसी variable को in-place mutate करने वाले `for` loops की जगह `map`, `filter`, `reduce` इस्तेमाल करें।

Python का उदाहरण:

```python
# OOP for the service boundary
class OrderService:
    def __init__(self, db):
        self.db = db

    def get_pending_orders(self, user_id):
        rows = self.db.fetch(user_id)
        return process_orders(rows)  # delegate to a pure function


# FP for the logic — trivial to test in isolation
def process_orders(orders):
    return [
        {**o, "total": o["price"] * o["quantity"]}
        for o in orders
        if o["status"] == "pending"
    ]
```

`process_orders` की database, service, या किसी भी बाहरी चीज़ पर शून्य निर्भरता है। इसे test करना एक function call है, कोई mocks नहीं [8]।

## जिन Languages ने यह फ़ैसला पहले ही कर लिया

Scala को सचमुच इसी के लिए design किया गया था — हर value एक ही साथ object *और* function दोनों है [7]। React का class components से hooks की तरफ़ बदलाव, functionally speaking, UI logic के लिए FP की दिशा में एक कदम था। Redux, JavaScript app के अंदर pure FP है। Java ने Java 8 में `Stream`, `Optional`, lambdas, और `Function<T,R>` को specifically एक OOP language में FP patterns लाने के लिए जोड़ा [3]।

Industry ने पहले ही vote कर दिया है। Multi-paradigm अब default है, exception नहीं।

## एक बात जिस पर ध्यान देना ज़रूरी है

Paradigms को mix करना ठीक है। उन्हें *बिना किसी स्पष्ट convention के* mix करना — यही वह तरीका है जिससे आप ऐसे code के साथ फँस जाते हैं जिसे कोई नहीं समझ सकता। मैंने ऐसे codebases देखे हैं जहाँ कुछ files पूरी तरह OOP हैं, कुछ पूरी तरह functional, और कुछ बिना किसी स्पष्ट कारण के दोनों हैं। Team logic पढ़ने से ज़्यादा समय style decode करने में लगाती है।

**एक convention चुनें: shell के लिए OOP, fill के लिए FP।** इसे एक बार अपनी team की guidelines में लिख दें। बस इतना काफ़ी है।

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