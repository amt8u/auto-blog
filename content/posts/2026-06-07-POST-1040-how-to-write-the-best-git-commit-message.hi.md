+++
title       = "सबसे अच्छा Git Commit Message कैसे लिखें"
description = "Git commit messages लिखने के लिए एक व्यावहारिक और स्पष्ट राय वाली गाइड, जिसके लिए आपका भविष्य का स्वयं और आपके साथी सचमुच आपको धन्यवाद देंगे। असली नियम, असली उदाहरण।"
date        = "2026-06-07T16:30:26+05:30"
slug          = "how-to-write-the-best-git-commit-message"
tags          = ["git", "वर्शन कंट्रोल", "डेवलपर वर्कफ़्लो", "बेस्ट प्रैक्टिसेज़"]
keywords      = ["git commit message", "अच्छा commit message कैसे लिखें", "conventional commits", "imperative mood commit", "atomic commits"]
canonical     = "/hi/posts/how-to-write-the-best-git-commit-message/"
feature_image = "https://images.unsplash.com/photo-1556075798-4825dfaaf498?auto=format&fit=crop&w=1600&q=80"
feature_image = "/images/POST-1040-how-to-write-the-best-git-commit-message.svg"
+++

किसी भी ऐसे प्रोजेक्ट पर `git log` चलाइए जो एक साल से ज़्यादा पुराना है और आपको किसी टीम की सच्चाई दिख जाएगी। आधे messages में लिखा होगा "fix", "update", "wip", "asdf", या मेरा निजी पसंदीदा — "stuff"। और फिर एक दिन production टूट जाता है, आप गड़बड़ करने वाली line पर `git blame` चलाते हैं, और जिस commit ने यह पेश किया था उसमें बस लिखा है "minor changes"। बढ़िया। बहुत मददगार। शुक्रिया, बीते हुए मुझ।

मैं एक दशक से ज़्यादा से कोड लिख रहा हूँ और मैं ईमानदारी से कहूँगा: शुरुआती कुछ सालों तक मेरे commit messages कचरा थे। तब तक समझ नहीं आया जब तक मुझे किसी और के छह महीने पुराने कोड को debug नहीं करना पड़ा (और फिर एहसास हुआ कि वह "कोई और" मैं ही था)। तब बात समझ में आई। एक diff आपको बताता है कि *क्या* बदला। केवल commit message आपको बता सकता है कि *क्यों*। बस यही पूरा खेल है।

## परेशानी क्यों उठाएँ? वैसे भी इन्हें कोई नहीं पढ़ता

यही वह झूठ है जो हम खुद से बोलते हैं। लोग बिल्कुल commit messages पढ़ते हैं — बस उस समय नहीं जब आप उन्हें लिख रहे होते हैं। वे इन्हें बाद में पढ़ते हैं, दबाव में, जब कुछ आग की तरह जल रहा होता है।

यहाँ एक अच्छा message सचमुच अपनी कीमत वसूल करता है:

- **`git blame`** — कोई कोड की किसी अजीब line की ओर इशारा करता है और commit उसका तर्क समझाता है ताकि आप किसी जान-बूझकर बनाए गए workaround को "fix" न कर दें।
- **onboarding के दौरान `git log`** — एक नया dev इतिहास पढ़कर समझता है कि कोई feature कैसे विकसित हुआ।
- **`git bisect`** — जब आप किसी regression का शिकार ढूँढ रहे होते हैं, तो छोटे और अच्छी तरह वर्णित commits आपको घंटों के बजाय मिनटों में दोषी ढूँढने देते हैं।
- **`git revert`** — जब आपको किसी बदलाव को साफ़-सुथरे ढंग से, असंबंधित चीज़ों को साथ खींचे बिना, पलटना हो।
- **रिलीज़ नोट्स और changelogs** — जो अब तेज़ी से सीधे commits से अपने आप तैयार किए जाते हैं।

एक diff आपको *क्या* दिखाता है। commit message ही एकमात्र जगह है जहाँ *क्यों* बचा रहता है [1]। कोड खुद को समझा सकता है; इरादा नहीं। अब से छह महीने बाद किसी को याद नहीं रहेगा कि आपने वह retry loop इसलिए हटाया था क्योंकि upstream API ने ग्राहकों से दोगुना चार्ज लेना शुरू कर दिया था। जब तक आपने इसे लिखकर न रखा हो।

तो नहीं, यह नौकरशाही नहीं है। यह उस व्यक्ति के लिए रास्ते के निशान छोड़ना है जिसे इसे maintain करना है — और आँकड़ों के हिसाब से वह व्यक्ति आप ही होंगे।

## वे सात नियम जिन्हें हर कोई दोहराता है (और दोहराना चाहिए)

ज़्यादातर आधुनिक सलाह दो लोगों तक जाती है। Tim Pope ने 2008 की एक ब्लॉग पोस्ट में **50/72 formatting convention** को लोकप्रिय बनाया [2], और Chris Beams ने बाद में इन्हें "एक शानदार commit message के सात नियम" के रूप में [cbea.ms](https://cbea.ms/git-commit/) पर लिखा, जो मूलतः canonical संदर्भ बन गया है [1]। ये रहे, और इन्हें याद कर लेना सार्थक है:

1. **subject को body से एक खाली line द्वारा अलग करें**
2. **subject line को 50 अक्षरों तक सीमित रखें**
3. **subject line को Capital अक्षर से शुरू करें**
4. **subject line को period (पूर्णविराम) से न समाप्त करें**
5. **subject line में imperative mood (आदेशात्मक रूप) का उपयोग करें**
6. **body को 72 अक्षरों पर wrap करें**
7. **body का उपयोग *क्या* और *क्यों* समझाने के लिए करें, *कैसे* के लिए नहीं**

जब तक आप हर एक के पीछे का तर्क न समझें, यह बाल की खाल निकालना लगता है। चलिए मैं गहराई में जाता हूँ, क्योंकि सच कहूँ तो इन नियमों के पीछे का *क्यों* खुद नियमों से ज़्यादा उपयोगी है।

### subject line खास है — Git इसे अलग तरह से मानता है

वह पहली line सिर्फ़ परंपरा नहीं है; Git खुद इसे commit के शीर्षक के रूप में मानता है। `git log --oneline`, `git shortlog`, `git rebase` जैसे tools और लगभग हर GitHub/GitLab UI सारांश में केवल उसी पहली line का उपयोग करते हैं [1]। उसके बाद की खाली line ही वह तरीका है जिससे Git जानता है कि शीर्षक कहाँ खत्म होता है और body कहाँ शुरू होती है। खाली line छोड़ दीजिए और आपकी सुंदर लिखी हुई body आपके इस्तेमाल किए जाने वाले आधे tools में subject के साथ मिल-जुलकर एक हो जाएगी।

### 50 अक्षर ही क्यों?

यह न तो मनमाना है और न ही कोई कठोर सीमा — इसे एक ज़ोरदार धक्के की तरह समझिए। GitHub आपको 50 अक्षरों पर चेतावनी देता है और 72 पर ellipsis (…) के साथ काट देता है [1]। और भी अहम बात, यह बाधा स्पष्टता को मजबूर करती है। अगर आप अपने बदलाव को 50 अक्षरों में वर्णित नहीं कर सकते, तो यह आमतौर पर एक संकेत है कि आपका commit बहुत सारी चीज़ें कर रहा है (इस पर बाद में और)। body 72 पर wrap होती है ताकि Git का डिफ़ॉल्ट indentation 80-कॉलम वाले terminal के भीतर बिना भद्दे ढंग से wrap हुए फिट हो जाए [3]।

### imperative mood वाली बात — हाँ, इससे सचमुच फ़र्क पड़ता है

यह वह नियम है जिस पर लोग सबसे ज़्यादा आँखें घुमाते हैं, तो मैं इसका पक्ष रखता हूँ। लिखिए **"Fix login redirect loop"**, न कि "Fixed", न "Fixes", न "Fixing"।

वह कसौटी जो इसे साफ़ कर देती है: आपका subject इस वाक्य को पूरा करना चाहिए **"If applied, this commit will ___"** (अगर लागू किया जाए, तो यह commit ___ करेगा) [4]।

- ✅ *If applied, this commit will* **Fix login redirect loop**
- ❌ *If applied, this commit will* **Fixed login redirect loop**

दूसरा बेतुका पढ़ने में लगता है। एक गहरा कारण भी है — Git खुद imperative में लिखता है। जब आप merge करते हैं, Git "Merge branch 'feature'" बनाता है। जब आप revert करते हैं, यह "Revert ..." लिखता है। आपके commits को codebase के लिए आदेशों की तरह पढ़ा जाना चाहिए, Git की अपनी आवाज़ के अनुरूप [4]। मज़ेदार बात यह है कि इतने सारे उपदेशों के बावजूद, GitHub पर केवल लगभग 44% commits ही असल में imperative mood का उपयोग करते हैं [5]। तो इसका पालन करने से आप उस अल्पसंख्यक में आ जाते हैं जो दिखता है कि उसे पता है कि वह क्या कर रहा है।

एक त्वरित पहले/बाद:

| ❌ न करें | ✅ करें |
|---|---|
| `fixed the bug.` | `Fix null check in user serializer` |
| `Updating README` | `Document the env setup steps` |
| `changes to api` | `Add pagination to /orders endpoint` |
| `WIP` | `Add failing test for expired tokens` |

### body में क्या जाता है

subject *क्या* बताता है। body वह जगह है जहाँ आप समझाते हैं कि *यह बदलाव क्यों, अभी क्यों, और आपने किन विकल्पों पर विचार किया*। *कैसे* का वर्णन न करें — diff पहले ही दिखा देता है कि कैसे। उस समस्या को समझाइए जिसे आप हल कर रहे थे और अपने दृष्टिकोण के पीछे का तर्क [1]।

एक पूरे message का लगभग-असली उदाहरण:

```
Cap retry attempts on payment webhook

The webhook handler retried indefinitely on a 5xx from the
billing provider. During their outage last Tuesday this hammered
their API and triggered duplicate charge attempts for ~30 users.

Limit retries to 3 with exponential backoff, and log the final
failure so support can reconcile manually. Refunds for the
affected accounts are tracked in TICKET-4821.
```

गौर कीजिए कि backoff *कैसे* implement किया गया है, इस बारे में एक भी line नहीं है। वह कोड दिखाता है। message उस चीज़ को कैद करता है जो वरना आप हमेशा के लिए खो देते — outage, duplicate charges, ticket। यही वह हिस्सा है जिसकी कोई जगह नहीं ले सकता।

एक व्यावहारिक सुझाव: **किसी भी गैर-तुच्छ चीज़ के लिए `git commit -m` का इस्तेमाल बंद कर दीजिए।** `-m` flag चुपचाप आपको one-liners लिखना सिखाता है क्योंकि इसके साथ एक उचित body लिखना तकलीफ़देह है [6]। बस `git commit` चलाइए, अपने editor को खुलने दीजिए, और एक इंसान की तरह लिखिए। अपना editor `git config --global core.editor "code --wait"` (या vim, या जो भी हो) से सेट कर लीजिए और आप तैयार हैं।

## atomic commits लिखें — यही असली राज़ है

यहाँ वह बात है जो लगभग कोई शुरुआती को नहीं बताता: **आपके commit message की गुणवत्ता लगभग पूरी तरह आपके commit की गुणवत्ता पर निर्भर करती है।** अगर आपका commit पंद्रह असंबंधित चीज़ें बदलता है, तो धरती पर कोई message इसे अच्छी तरह सारांशित नहीं कर सकता। आप आख़िरकार "various fixes" लिखेंगे क्योंकि सच में यही एकमात्र ईमानदार विवरण है।

एक **atomic commit** वह सबसे छोटा बदलाव है जो अपने आप में समझ में आता है और codebase को एक काम करने वाली स्थिति में छोड़ता है [7]। एक तार्किक बदलाव। एक bug fix को formatting cleanup के साथ और एक नई feature के साथ मत मिलाइए।

इसके लिए एक बिलकुल सरल गंध-परीक्षण है: **अगर आपकी subject line को "and" शब्द की ज़रूरत है, तो आपका commit शायद दो commits है** [8]। "Add search filter and fix navbar styling" — यह तो ट्रेंच कोट पहने हुए दो commits हैं।

यह अनुशासन इस लायक क्यों है:

- **`git bisect` एक महाशक्ति बन जाता है।** छोटे, केंद्रित commits bisect को ठीक उसी बदलाव पर पहुँचने देते हैं जिसने bug पेश किया [9]।
- **Reverts साफ़ होते हैं।** आप एक feature को बिना गलती से किसी असंबंधित fix को पलटे, जो उसके साथ चली आई थी, undo कर सकते हैं [9]।
- **Code review आसान हो जाता है।** Reviewers एक छोटे, एकल-उद्देश्य वाले बदलाव को 600-line वाले मिले-जुले झोले की तुलना में कहीं तेज़ी से समझते हैं।
- **इतिहास एक कहानी की तरह पढ़ा जाता है।** हर commit इस बात का एक अध्याय है कि प्रोजेक्ट यहाँ तक कैसे पहुँचा [9]।

मेरे लिए जो तरीका काम करता है: `git add -p` (patch mode) से चुनिंदा रूप से stage कीजिए ताकि आप केवल संबंधित hunks ही commit करें, भले ही आपकी working directory में कई असंबंधित बदलाव चल रहे हों। और अगर आप पहले ही local में गड़बड़ कर चुके हैं, तो interactive rebase इसी के लिए है — push करने से पहले squash और split कीजिए।

![atomic बनाम गड़बड़ commits](/images/posts/how-to-write-the-best-git-commit-message/atomic-vs-messy-commits.svg)

## Conventional Commits: मशीनों और इंसानों दोनों के लिए संरचना

एक बार जब आप मूल बातें पकड़ लें, तो एक लोकप्रिय convention है जो इसके ऊपर एक हल्की संरचना जोड़ता है: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)। प्रारूप बेहद सरल है [10]:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

तो आपकी subject line एक type से शुरू होती है। आम वाले:

| Type | कब इस्तेमाल करें |
|---|---|
| `feat` | एक नई feature |
| `fix` | एक bug fix |
| `docs` | केवल documentation |
| `style` | formatting, whitespace — कोई logic बदलाव नहीं |
| `refactor` | कोड बदलाव जो न bug fix करे न feature जोड़े |
| `perf` | एक performance सुधार |
| `test` | tests जोड़ना या ठीक करना |
| `build` / `ci` | build system या CI config |
| `chore` | नियमित रखरखाव, deps, tooling |

असल दुनिया के उदाहरण:

```
feat(auth): add passwordless email login
fix(api): handle empty cart on checkout
docs: clarify env setup in README
refactor(parser): extract token validation
```

Breaking changes को दो तरीकों से चिह्नित किया जाता है: colon से पहले एक `!`, या एक `BREAKING CHANGE:` footer [10]:

```
feat!: drop support for Node 16

BREAKING CHANGE: minimum supported runtime is now Node 18.
```

### टीमें इसे क्यों अपनाती हैं

फ़ायदा सौंदर्यपरक नहीं है — यह automation है। चूँकि type machine-readable है, tooling कर सकती है:

- आपके commit इतिहास से **changelogs अपने आप तैयार करना**।
- आपके **semantic version को सही ढंग से bump करना** — `fix` → patch, `feat` → minor, `BREAKING CHANGE` → major [10]।
- CI में बिना किसी इंसान के version तय किए **releases और publish steps को trigger करना**।

यह कोई आला (niche) चीज़ भी नहीं है। शीर्ष 381 NPM libraries की एक समीक्षा में पाया गया कि लगभग 95% Conventional Commits formatting का उपयोग करती थीं, जिनमें से आधी से ज़्यादा अपने पूरे इतिहास में 80%+ अनुपालन तक पहुँचीं [11]। अगर आप एक library maintain करते हैं, तो यह अब लगभग बुनियादी अपेक्षा है।

हालाँकि सच कहूँ — क्या यह सबके लिए है? किसी solo प्रोजेक्ट या छोटे internal app पर, जहाँ आप कुछ भी auto-release नहीं कर रहे, वहाँ `feat:`/`fix:` prefixes सिर्फ़ औपचारिकता के लिए औपचारिकता जैसे लग सकते हैं। पहले बताए गए सात नियम prefix से कहीं ज़्यादा मायने रखते हैं। Conventional Commits का उपयोग तब कीजिए जब automation उस अनुशासन की कीमत चुका दे। किसी लोकप्रिय repo के करने भर से इसकी नकल मत कीजिए।

## anti-patterns — एक commit message को क्या बुरा बनाता है

चलिए नाम लेकर बताता हूँ। ये वे हैं जो मुझे लगातार दिखते हैं, और ये क्यों चुभते हैं [12][8]:

- **"Fix bug"** — कौन-सा bug? आपको याद नहीं रहेगा। bug का नाम बताइए।
- **"Update", "changes", "stuff", "wip"** — शून्य जानकारी। diff ने पहले ही बता दिया कि *कुछ* बदला है।
- **files की सूची बनाना: "Update user.rb and helper.js"** — `git show` पहले ही files की सूची दे देता है। message को बदलाव के *अर्थ* को समझाना चाहिए, न कि file की सूची की नकल करनी चाहिए [12]।
- **subject में "and"** — लगभग हमेशा इसका मतलब है कि commit को split किया जाना चाहिए [8]।
- **भूतकाल / गलत mood** — "Fixed", "Added", "Changing"। imperative चुनिए और उस पर टिके रहिए।
- **one-liners की एक दीवार** — दस commits जिनमें सब "updates" कहते हैं। यही वह है जो `git commit -m` के अति-उपयोग से पैदा होता है [12]।
- **subject का स्पष्ट बात को दोहराना** — "Make changes to the changes file"। बताइए क्या और क्यों।

enter दबाने से पहले एक आत्म-जाँच: **अपनी subject line को "If applied, this commit will ___" के रूप में वापस पढ़िए और खुद से पूछिए कि क्या कोई ऐसा व्यक्ति जो वहाँ मौजूद नहीं था, इसे छह महीने बाद समझ पाएगा।** अगर जवाब नहीं है, तो अतिरिक्त तीस सेकंड खर्च कीजिए। यह आपके भविष्य की समझदारी में किया गया अब तक का सबसे सस्ता निवेश है।

## वह tooling जो आपको ईमानदार रखती है

केवल इच्छाशक्ति से अनुशासन बनाए रखना कठिन है, तो इसके बजाय मशीनों को आपको टोकने दीजिए:

- **Commit message template** — अपने ही नियमों की एक याददहानी सेट कीजिए:
  ```
  git config --global commit.template ~/.gitmessage.txt
  ```
  उस file में एक ढाँचा (subject याददहानी, खाली line, body याददहानी) डाल दीजिए और यह हर बार commit करते समय दिख जाएगा।
- **commitlint + Husky** — एक git hook जो ऐसे commits को अस्वीकार कर देता है जो Conventional Commits का पालन नहीं करते। टीमों के लिए बढ़िया।
- **Commitizen** — एक interactive prompt जो आपको एक ठीक से formatted commit बनाने में कदम-दर-कदम मार्गदर्शन करता है।
- **Editor integration** — ज़्यादातर editors (और [GitKraken](https://www.gitkraken.com/learn/git/best-practices/git-commit-message) जैसे tools) तब उजागर करते हैं जब आपका subject 50 अक्षरों से आगे निकल जाता है [13]।

इनमें से कोई भी आपके लिए एक *अच्छा* message नहीं लिखता — वे बस आकार लागू करते हैं। सोचना अब भी आपका काम है। और आजकल एक AI assistant आपके diff से एक ठीक-ठाक message का मसौदा बना सकता है, जो सचमुच उपयोगी है, लेकिन इसे एक junior के पहले मसौदे की तरह समझिए। यह देख सकता है कि *क्या* बदला; यह पिछले मंगलवार के outage या ticket नंबर को नहीं देख सकता। वह संदर्भ केवल आपके दिमाग में रहता है, और इसे message में डालना ही पूरा उद्देश्य है।

## एक ऐसा workflow जिस पर आप सचमुच टिके रह सकते हैं

सबको एक साथ जोड़कर, एक समझदार commit आदत रोज़मर्रा में ऐसी दिखती है:

1. **एक तार्किक बदलाव कीजिए।** अगर आप असंबंधित edits में भटक गए हैं, तो `git add -p` से चुनिंदा रूप से stage कीजिए।
2. **`git commit` चलाइए** (बिना `-m`) ताकि आपका editor खुले।
3. **~50 अक्षरों से कम का subject लिखिए, imperative mood, Capital अक्षर, कोई period नहीं।** अगर आपकी टीम Conventional Commits का उपयोग करती है तो एक type prefix जोड़िए।
4. **खाली line, फिर एक body** जो *क्यों* समझाए — लेकिन केवल तभी जब बदलाव को संदर्भ की ज़रूरत हो। तुच्छ commits को body की ज़रूरत नहीं होती।
5. **tickets या issues का संदर्भ दीजिए** footer में (`Refs #421`, `Closes #88`)।
6. सहेजने से पहले **इसे "If applied, this commit will ___" परीक्षण के साथ दोबारा पढ़िए।**

बस इतना ही। यह प्रति commit शायद एक मिनट जोड़ता है और बाद में घंटों बचाता है। ज़्यादा उदाहरणों के साथ एक गहरे विवरण के लिए, freeCodeCamp की [step-by-step guide](https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/) एक ठोस साथी पठन है [14]।

सबसे अच्छा commit message न तो सबसे चतुर होता है न सबसे लंबा। यह वह होता है जो उस सवाल का जवाब देता है जिसे आपका भविष्य का साथी स्क्रीन पर चिल्लाने वाला है: *"आख़िर यह बदला ही क्यों गया?"* इसका जवाब दे दीजिए, और आपने काम कर दिया।

> समाप्त

## स्रोत
1. [How to Write a Git Commit Message - Chris Beams](https://cbea.ms/git-commit/)
2. [Mastering Git Commit Messages: Tim Pope's 50/72 Formatting Guide](https://www.w3tutorials.net/blog/git-commit-messages-50-72-formatting/)
3. [The 50/72 Rule of Git – DevIQ](https://deviq.com/practices/50-72-rule/)
4. [Imperative Git commit messages in the active tense or mood - TheServerSide](https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/git-commit-message-imperative-mood-past-tense-convention-standards-best-practice-subject)
5. [What % of Git commit messages use the imperative mood? - InitialCommit](https://initialcommit.com/blog/Git-Commit-Message-Imperative-Mood)
6. [Best Practices for Git Commit Message - Baeldung on Ops](https://www.baeldung.com/ops/git-commit-messages)
7. [Mastering Atomic Commits - LeanIX Engineering](https://engineering.leanix.net/blog/atomic-commit/)
8. ["and" as anti-pattern in git commit subject - Kosta Harlan](https://www.kostaharlan.net/posts/and-commit-message-anti-pattern/)
9. [How atomic Git commits dramatically increased my productivity - DEV Community](https://dev.to/samuelfaure/how-atomic-git-commits-dramatically-increased-my-productivity-and-will-increase-yours-too-4a84)
10. [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
11. [Conventional Commits Specification - Wikipedia](https://en.wikipedia.org/wiki/Conventional_Commits_Specification)
12. [Git Commit Message Anti-Patterns - AMC](https://amcaplan.ninja/blog/2016/12/26/git-commit-message-anti-patterns/)
13. [How to Write a Good Git Commit Message - GitKraken](https://www.gitkraken.com/learn/git/best-practices/git-commit-message)
14. [How to Write Better Git Commit Messages – freeCodeCamp](https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/)