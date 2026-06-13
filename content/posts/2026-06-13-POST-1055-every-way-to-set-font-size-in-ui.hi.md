+++
title       = "UI में Font Size सेट करने के हर तरीके (और कौन सा जीतता है)"
description = "px और rem से लेकर clamp() और container query units तक — यहाँ हैं UI में font size सेट करने के सभी तरीके, और कौन से असल में accessibility का सम्मान करते हैं।"
date        = "2026-06-13T08:16:18+05:30"
slug          = "every-way-to-set-font-size-in-ui"
tags          = ["css", "फ्रंटेंड", "एक्सेसिबिलिटी", "यूआई-डिज़ाइन"]
keywords      = ["css font-size units", "rem बनाम px", "रिस्पॉन्सिव टाइपोग्राफी", "css clamp font-size", "css units गाइड", "एक्सेसिबल font-size"]
canonical     = "/hi/posts/every-way-to-set-font-size-in-ui/"
feature_image = "/images/POST-1055-every-way-to-set-font-size-in-ui.svg"
+++

क्या आपने कभी किसी प्रोजेक्ट का CSS खोला है और पाया है कि font sizes `px`, `em`, `rem`, `%`, और `vw` में सेट हैं — सब एक ही फ़ाइल में, कभी-कभी एक ही element पर? हाँ, मेरे साथ भी ऐसा हुआ है। Font size, CSS की सबसे boring property लगती है, जब तक आपको यह पता नहीं चलता कि इसे express करने के कम से कम **आठ अलग-अलग तरीके** हैं, और गलत तरीका चुनने से आपके यूज़र्स के एक हिस्से के लिए accessibility चुपचाप टूट जाती है, बिना एक भी error दिखाए।

## इस article की ज़रूरत आखिर क्यों है

मैं सोचता था कि `font-size: 16px;` ही पूरी कहानी है। एक नंबर चुनो, उस पर `px` लगाओ, हो गया। मुझे यह समझने में एक support ticket लगा, जो एक ऐसे यूज़र से आया था जिसने अपने browser का default font size बढ़ाकर 24px कर दिया था — और पाया कि मेरी "responsive" साइट ने इसे पूरी तरह नज़रअंदाज़ कर दिया — तब मुझे पता चला कि मैं कितना गलत था।

**आप font-size के लिए जो unit चुनते हैं, वह सिर्फ़ एक styling decision नहीं है। यह एक accessibility decision है।** कुछ units वह सम्मान करते हैं जो browser और यूज़र ने configure किया है। कुछ को इससे कोई फ़र्क ही नहीं पड़ता। कुछ स्क्रीन साइज़ में बहुत अच्छे से scale होते हैं। कुछ को सही तरीके से काम करने के लिए तीन media queries चाहिए। आइए इन सबको उस क्रम में देखते हैं, जिस क्रम में मैं असल में इन्हें इस्तेमाल करता हूँ।

## Absolute units: px और वो size keywords जिन्हें कोई इस्तेमाल नहीं करता

### Pixels — वही जिससे हर कोई शुरुआत करता है

`font-size: 16px` एक **absolute** length है। एक CSS pixel एक fixed reference unit है — यह parent element, viewport, या (यह सबसे ज़रूरी हिस्सा है) यूज़र की browser settings के आधार पर नहीं बदलता [1]।

```css
h1 { font-size: 32px; }
p  { font-size: 16px; }
```

यह predictable है, और यही वजह है कि यह लुभावना लगता है। जो आप design करते हैं, वही आपको मिलता है — आपके monitor पर, default zoom पर। समस्या तब सामने आती है जब किसी के पास आपका exact setup *नहीं* होता: कम दृष्टि वाला कोई यूज़र जिसने अपनी browser settings में "default font size" 16px से 24px कर दिया है, उसे... कुछ नहीं मिलता। `16px`, `16px` ही रहता है, क्योंकि px उस preference को सुनता ही नहीं [1]।

### Keyword units — `medium`, `x-large`, और इनके दोस्त

यह CSS का एक ऐसा कोना है जिसे ज़्यादातर developers ने कभी छुआ ही नहीं। Spec असल में **absolute-size keywords** define करता है: `xx-small`, `x-small`, `small`, `medium`, `large`, `x-large`, `xx-large`, और (हाल ही में) `xxx-large`। ये एक internal table से map होते हैं जिसे browser maintain करता है, और जो यूज़र के default font size (`medium`) के आसपास index होती है [2]।

इसके अलावा **relative-size keywords** भी हैं — `smaller` और `larger` — जो parent element के computed size से, आम तौर पर 1.2 से 1.5 के बीच के factor से, ऊपर या नीचे scale होते हैं [2]।

```css
small { font-size: smaller; }
.fine-print { font-size: x-small; }
```

सच कहूं तो, मैंने इन्हें असली codebases में लगभग कभी इस्तेमाल होते नहीं देखा। ये early web की एक निशानी हैं, `rem` के आने से पहले के समय की, जब "इसे यूज़र की preferences के हिसाब से size करो" कहने का कोई साफ़ तरीका नहीं था। इनका वजूद जानना फायदेमंद है, मुख्यतः इसलिए कि जब आप 2009 के किसी legacy stylesheet में इन्हें देखें, तो आप इन्हें पहचान सकें।

## वो relative units जो असल में किसी चीज़ का जवाब देते हैं

यहीं से यह दिलचस्प होता है — और यहीं असली misconceptions छिपे हैं।

### em — parent के font size के हिसाब से

`em` का मतलब है "*इस element* के computed value के font-size के हिसाब से, जिसका मतलब आम तौर पर parent के font-size से होता है" [3]। तो किसी child पर `font-size: 1.5em` का मतलब है "मेरे parent का font-size जो भी resolve हुआ है, उसका 1.5 गुना।"

सुनने में हानिरहित लगता है। यहीं यह tricky हो जाता है: अगर हर nested level `em` इस्तेमाल करता है, तो sizes **एक के ऊपर एक जुड़ती (compound)** चली जाती हैं।

```css
html    { font-size: 16px; }      /* root = 16px */
section { font-size: 1.25em; }    /* 1.25 × 16px = 20px */
article { font-size: 1.25em; }    /* 1.25 × 20px = 25px  ← compounding! */
p       { font-size: 1.25em; }    /* 1.25 × 25px = 31.25px */
```

वह `<p>` अब 31px से ज़्यादा पर render हो रहा है, जबकि आप शायद 20px के आसपास कुछ चाहते थे। यह कोई *जानबूझकर* नहीं करता — यह सिर्फ़ इस वजह से होता है कि nesting कैसे काम करती है, और यही वह सबसे common वजह है जिसकी वजह से लोग font-size के लिए `em` को पूरी तरह छोड़ देते हैं।

![em vs rem cascade](/images/posts/every-way-to-set-font-size-in-ui/em-vs-rem-cascade.svg)

इसके बावजूद, `em` बेकार नहीं है — यह उन चीज़ों के लिए वाकई बढ़िया है जिन्हें अपने ही element के font size के साथ scale *होना चाहिए*, जैसे किसी button पर `padding`, `line-height`, या `letter-spacing`। अगर button का text बड़ा हो जाता है, तो आप शायद चाहेंगे कि padding भी proportionally बढ़े। बस `em`-based font sizes को पाँच levels की nesting में chain मत कीजिए और फिर sanity की उम्मीद मत रखिए।

### rem — root के हिसाब से, और एक default recommendation के सबसे करीब

`rem` का मतलब है "root em"। यह हमेशा `<html>` element के `font-size` के हिसाब से होता है, चाहे element कितनी भी गहराई में nested हो [3]। पिछले example को फिर से लिखते हैं:

```css
html    { font-size: 16px; }    /* 1rem = 16px, always */
section { font-size: 1.25rem; } /* 20px */
article { font-size: 1.25rem; } /* 20px — no compounding */
p       { font-size: 1.25rem; } /* 20px */
```

हर `1.25rem` का मतलब 20px है, चाहे वह DOM में कहीं भी हो। **यही predictability वह वजह है जिसकी वजह से `rem`, font sizes, spacing, और ज़्यादातर layout dimensions के लिए de-facto recommendation बन गया है** [4]।

लेकिन `rem` के अहम होने की असली वजह predictability से आगे जाती है — यह यूज़र का सम्मान करने की बात है। अगर कोई अपने browser का default font size 16px के बजाय 20px कर देता है, तो आपकी साइट पर हर `rem`-based value automatically, proportionally scale हो जाती है, बिना कोई extra code लिखे [5]। `px` के साथ, उस यूज़र की preference को बस... नज़रअंदाज़ कर दिया जाता है।

### Percentages — em का शांत कज़िन

`font-size: 80%`, `em` जैसा ही काम करता है — यह parent के computed font-size के हिसाब से होता है, और nested elements में उसी तरह compound होता है [3]। आपको यह सबसे ज़्यादा `html { font-size: 62.5%; }` जैसी tricks में दिखेगा (ताकि mental math आसान हो जाए और `1rem = 10px` हो जाए), या उन पुराने stylesheets में जो `rem` को solid browser support मिलने से पहले के हैं।

### smaller और larger — भुला दिए गए relative keywords

पहले भी इसका ज़िक्र हुआ है, लेकिन यहाँ दोहराना ज़रूरी है: `smaller` और `larger` *relative-size keywords* हैं जो context के आधार पर, लगभग 1.2× से 1.5× तक, parent के computed size से font size को ऊपर या नीचे करते हैं [2]। `<small>` या `<sup>`-जैसे elements के लिए कभी-कभी उपयोगी हैं, लेकिन आज के component-based CSS में दुर्लभ हैं, जहाँ आप शायद design token का इस्तेमाल करेंगे।

## Viewport units — स्क्रीन के हिसाब से ही text को size करना

`vw` (viewport width), `vh` (viewport height), `vmin`, और `vmax`, चीज़ों को browser के viewport dimensions के हिसाब से size करते हैं। `1vw` = viewport की width का 1%। तो:

```css
h1 { font-size: 5vw; }
```

1000px-wide viewport पर, यह 50px का heading है। 1920px के viewport पर, यह 96px है। यह स्क्रीन साइज़ के साथ continuously scale होता है — किसी breakpoints की ज़रूरत नहीं।

सुनने में बढ़िया लगता है, है ना? **यहाँ पेंच यह है: सिर्फ़ viewport units, font-size के लिए खतरनाक हैं।** किसी छोटी phone स्क्रीन पर, `5vw` आपके body text को इतना छोटा कर सकता है कि वह पढ़ा ही न जा सके। किसी ultrawide monitor पर, यह किसी paragraph को 80px के text में फुला सकता है। और एक छिपी हुई समस्या भी है — सिर्फ़ `vw` में size किया गया text, कुछ setups में यूज़र की font-size *zoom* preference का सही जवाब नहीं देता, क्योंकि text-only zoom लगाने पर viewport dimensions बदलते नहीं हैं [6]।

तो सिर्फ़ viewport units, body text के लिए लगभग कभी सही चुनाव नहीं हैं। ये अगली चीज़ के लिए एक building block हैं।

## clamp() — वह function जो viewport units को असल में इस्तेमाल लायक बनाता है

`clamp(min, preferred, max)`, बिना किसी शक के, वह unit/function combo है जिसकी तरफ़ मैं अब किसी भी नए प्रोजेक्ट में सबसे पहले जाता हूँ। यह तीन values लेता है — एक minimum, एक preferred (अक्सर viewport-based) value, और एक maximum — और जो भी value आपको floor और ceiling के बीच रखे, उसे चुन लेता है [7]।

```css
h1 {
  font-size: clamp(2rem, 1.5rem + 3vw, 4rem);
}
```

इसे इस तरह पढ़ें: "2rem (32px) से नीचे कभी मत जाओ। 4rem (64px) से ऊपर कभी मत जाओ। बीच में, viewport width के आधार पर fluidly scale करो।" एक लाइन उस चीज़ की जगह ले लेती है जिसके लिए पहले चार या पाँच media queries लगती थीं [8]।

![clamp font size curve](/images/posts/every-way-to-set-font-size-in-ui/clamp-font-size-curve.svg)

कुछ practical नोट्स जो मैंने कई projects में `clamp()` इस्तेमाल करते हुए सीखे हैं:

- **min/max के लिए `rem` को preferred value के लिए `vw` के साथ combine करें।** इससे आपकी floor और ceiling, यूज़र की font-size preference से जुड़ी रहती हैं, जबकि बीच का हिस्सा fluidly scale होता रहता है [8]।
- `clamp()` एक tool है, कोई जादुई fix नहीं — अगर आपका minimum बहुत छोटा है, तो low-vision यूज़र्स अब भी इसे पढ़ नहीं पाएंगे, और अगर आपका maximum बहुत छोटा है, तो यह उन यूज़र्स की मदद नहीं करता जो किसी वजह से zoom in करते हैं [7]।
- `min()` और `max()` अलग-अलग भी मौजूद हैं, उन मामलों के लिए जब आपको सिर्फ़ एक bound की परवाह हो। `font-size: min(8vw, 3rem)`, किसी heading को 3rem पर cap कर देता है लेकिन छोटी स्क्रीन्स पर इसे छोटा होने देता है।

## ch, ex, और वो units जिन्हें text की ही परवाह है

दो अजीब-से units जिनके बारे में जानना ज़रूरी है:

- **`ch`** current font में "0" character की width पर आधारित है। इसका इस्तेमाल असल में font-size *के लिए* नहीं होता, लेकिन यह इसका perfect साथी है — `max-width: 66ch`, किसी paragraph को लगभग हर line में 50–75 characters पर रखता है, जिसे readability के लिए सबसे ज़्यादा माना जाने वाला sweet spot कहा जाता है [9]।
- **`ex`** font की x-height पर आधारित है (मोटे तौर पर lowercase "x" की height)। इस पर भरोसा करने लायक consistency से support मिलना दुर्लभ है, लेकिन कभी-कभी आपको यह typography-heavy designs में दिखेगा।

```css
article p {
  font-size: clamp(1rem, 0.95rem + 0.3vw, 1.125rem);
  line-height: 1.6;
  max-width: 66ch;
}
```

यह combo — fluid font size, generous line-height, और `ch`-based max-width — अब किसी भी long-form text block के लिए मूल रूप से मेरी पहली पसंद है। Line-height लगभग 1.5–1.6 आमतौर पर recommended baseline है, और 75 characters से लंबी lines के लिए इसे ज़्यादा (1.6–1.7) रखा जाता है [9]।

## Container query units — स्क्रीन के बजाय *component के* box के हिसाब से size करना

यह वाला नया है, और मैं मानता हूँ कि मैंने इसे पिछले साल या उसके आसपास ही इस्तेमाल करना शुरू किया। **Container query units (`cqw`, `cqh`, `cqi`, `cqb`, `cqmin`, `cqmax`) बिल्कुल viewport units जैसे काम करते हैं, सिवाय इसके कि ये पूरे browser viewport के बजाय, आपके द्वारा चुने गए एक *containing element* के हिसाब से होते हैं** [10]।

```css
.card {
  container-type: inline-size;
}

.card h2 {
  font-size: clamp(1rem, 4cqi, 1.5rem);
}
```

यह क्यों ज़रूरी है? क्योंकि वही `<h2>`, एक full-width hero section में *या* एक narrow sidebar widget में हो सकता है। Viewport units इस फ़र्क को नहीं समझ सकते — उन्हें सिर्फ़ browser window के बारे में पता होता है। Container query units उस heading को उसकी असली उपलब्ध जगह के हिसाब से size करने देते हैं, जो component-driven design systems के लिए बहुत बड़ी बात है [11]।

- `cqw` = query container की width का 1%
- `cqi` = container के *inline* size का 1% (writing-mode aware — आम तौर पर `cqw` के बजाय इसे prefer करें) [10]
- `cqb` = block size का 1%
- `cqmin` / `cqmax` = inline और block sizes में से जो छोटा/बड़ा हो

viewport units की तरह ही, इन्हें भी `clamp()` में wrap करें ताकि किसी tiny sidebar में squeeze किया गया component, 4px के text में न बदल जाए [10]। [CSS containment spec](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries) के ज़रिए evergreen browsers में browser support पहले से ही ठीक है, लेकिन फिर भी मैं उस पर test करने की सलाह दूँगा जो आपके analytics के मुताबिक आपके यूज़र्स असल में इस्तेमाल कर रहे हैं।

## rem बनाम px की लड़ाई — मेरी असली राय

मैंने इस पर *बहुत सारे* opinions पढ़े हैं, और आख़िर में मैं यहाँ पहुँचा हूँ।

**Browser zoom और "default font size" setting दो अलग-अलग चीज़ें हैं, और लोग अक्सर इन्हें मिला देते हैं** [6]:

| Mechanism | यह क्या करता है | `px` पर असर | `rem` पर असर |
|---|---|---|---|
| Browser zoom (Ctrl/Cmd + / -) | पूरे page को proportionally scale करता है — layout, images, सब कुछ | समान रूप से बड़ा होता है | समान रूप से बड़ा होता है |
| "Default font size" preference | `1rem` (और `medium` keyword) किस value में resolve होगा, उसे बदलता है | **कोई असर नहीं** | Proportionally scale होता है |

तो अगर कोई यूज़र पूरे page को 150% zoom करता है, तो `16px` वाला element और `1rem` वाला element दोनों 50% बड़े हो जाते हैं — यहाँ कोई फ़र्क नहीं है [6]। लेकिन अगर कोई यूज़र अपनी browser settings में जाकर default font size 16px से 24px कर देता है (एक ऐसी setting जिस पर कई low-vision यूज़र्स permanently, बिना कुछ zoom किए, निर्भर रहते हैं), तो `rem`-based sizes उस बदलाव के साथ scale होते हैं, जबकि `px`-based sizes बिल्कुल नहीं बदलते [4][5]।

असल में, यही पूरी दलील है। ऐसा नहीं है कि `px` "गलत" है — बात यह है कि **`px` चुपचाप आपके text को एक खास accessibility preference से बाहर कर देता है**, और ज़्यादातर developers को इस बात का अंदाज़ा ही नहीं होता कि यह preference मौजूद है, क्योंकि उन्हें इसका इस्तेमाल करने की कभी ज़रूरत ही नहीं पड़ी।

मेरा practical नियम, जो उन ज़्यादातर accessibility-focused writers की राय से मिलता है जिन पर मैं भरोसा करता हूँ:

- **font sizes, padding, margins, और text से जुड़ी हर चीज़ के लिए `rem` इस्तेमाल करें** — यह यूज़र की preferences का सम्मान करता है [4][5]।
- **उन चीज़ों के लिए `px` इस्तेमाल करें जिन्हें text scaling से बेपरवाह visually crisp रहना चाहिए** — 1px borders, box-shadow offsets, outline widths। अगर किसी ने अपना font size बढ़ा दिया और कोई 1px border अचानक 1.5px बन जाए, तो वह बस टूटा हुआ दिखेगा।
- `html { font-size: 16px; }` को hardcode करने के बजाय `html { font-size: 100%; }` सेट करें (या इसे बिल्कुल छुएं ही नहीं) — बाद वाला असल में यूज़र के browser default को *override* कर देता है, जो पूरी बात का मतलब ही खत्म कर देता है।

## 16px वाला gotcha जिसका डिज़ाइन से कोई लेना-देना नहीं

यह एक मज़ेदार वाला है जिसने मुझे एक mobile-first प्रोजेक्ट में परेशान किया। हमारे पास एक स्लीक, compact login form था — input fields को `14px` में styled किया गया था क्योंकि डिज़ाइन में tight, minimal लुक चाहिए था। Desktop पर, बिल्कुल सही। iPhones पर, जब भी कोई input field पर tap करता, **Safari पूरे पेज को zoomed-in view में खींच लेता**, जैसे वह "मदद" करने की कोशिश कर रहा हो।

पता चला कि यह iOS Safari का एक जानबूझकर किया गया accessibility behavior है: अगर किसी input field का *computed* font-size 16px से कम है, तो Safari मान लेता है कि टाइप करते समय इसे आराम से पढ़ना मुश्किल होगा, और जब वह field focus में आती है तो viewport को auto-zoom कर देता है [12][13]। यह बरसों से ऐसा ही है, और यह iOS-specific है — Android browsers ऐसा नहीं करते [12]।

Fix लगभग शर्मनाक रूप से simple था:

```css
input, textarea, select {
  font-size: 16px; /* या 1rem, यह मानते हुए कि root 16px है */
}
```

बस इतना ही। जैसे ही हर form field 16px या उससे बड़ा रेंडर होने लगा, auto-zoom पूरी तरह बंद हो गया। पेंच यह है कि यह threshold *computed, rendered* size को चेक करता है — तो अगर आप किसी वजह से किसी form पर `transform: scale()` लगा रहे हैं, तो इससे भी यह तय होता है कि zoom चालू होगा या नहीं [13]। यह उन चीज़ों में से एक है जिसका आपकी visual design preferences से कोई लेना-देना नहीं है, और सब कुछ एक platform quirk से जुड़ा है — और यह ठीक वैसा bug है जो किसी real device पर टेस्ट करने तक नज़र ही नहीं आता।

## Browser से आगे — दूसरे platforms इसे कैसे देखते हैं

अगर आप सिर्फ़ web के लिए नहीं बनाते, तो font-size units दूसरी जगहों पर थोड़े अलग दिखते हैं, लेकिन *असली tension* — fixed बनाम user-scalable — हर जगह एक जैसा है:

- **Android** में `dp` (density-independent pixels) और `sp` (scale-independent pixels) हैं। ये डिफ़ॉल्ट रूप से identical हैं, लेकिन जब यूज़र अपनी system font-size preference बदलता है तो `sp` scale होता है, जबकि `dp` नहीं होता [14][15]। Android की अपनी accessibility guidance इस बारे में साफ़ है: text sizes `sp` में होनी चाहिए, बस यही नियम है, वरना system-wide "make text bigger" सेटिंग आपकी स्क्रीन्स के लिए चुपचाप कुछ नहीं करती [14]।
- **iOS** Dynamic Type पर निर्भर करता है, जहाँ text styles (जैसे `.body` या `.headline`) semantic categories हैं जो यूज़र के चुने हुए text size के आधार पर साथ में scale होते हैं — यह hardcoded points की तुलना में, semantic class names के साथ `rem` इस्तेमाल करने की भावना के ज़्यादा करीब है।
- **Design systems और frameworks** आम तौर पर `rem` को ही default के रूप में शामिल करते हैं। उदाहरण के लिए, Tailwind CSS अपनी पूरी type scale `rem` में ship करता है, जिसमें `text-base`, `font-size: 1rem; line-height: 1.5rem` से मैप होता है, जो default root size पर 16px/24px के बराबर होता है [16]। अगर आपने कभी सोचा है कि Tailwind के spacing नंबर 16 के fractions जैसे क्यों दिखते हैं, तो यही इसकी वजह है।

हर platform पर pattern एक जैसा है: **एक absolute unit होता है (px, dp, pt) और एक scalable unit (rem, sp, Dynamic Type), और scalable वाला ही वह है जो यूज़र की मांग का सम्मान करता है।**

## अब मैं असल में क्या करता हूँ

कई प्रोजेक्ट्स में इस पर आगे-पीछे सोचने के बाद, यह वह सेटअप है जिस पर मैं डिफ़ॉल्ट रूप से जाता हूँ:

1. root font-size को छुएं नहीं (`100%` / browser default), इसे `16px` पर hardcode न करें।
2. base font sizes और spacing tokens को `rem` में रखें, और एक बार CSS custom properties के रूप में define करें — `--font-size-base: 1rem; --font-size-lg: 1.25rem;` — ताकि पूरा scale एक ही जगह से adjustable हो।
3. hero headings और उन सभी चीज़ों के लिए जिन्हें स्क्रीन साइज़ की एक बड़ी रेंज में scale होना है, `rem` bounds और `vw`-based middle के साथ `clamp()` इस्तेमाल करें।
4. उन components के लिए जो बहुत अलग-अलग layout contexts (cards, sidebars, widgets) में reuse होते हैं, `clamp()` में wrap किए गए container query units (`cqi`) इस्तेमाल करें।
5. readability के लिए body text को `max-width: 66ch` और `line-height: 1.5`–`1.6` के साथ pair करें।
6. सभी form inputs को कम से कम `1rem`/`16px` पर रखें, कोई अपवाद नहीं — इस एक लाइन ने मुझे iOS zoom bug से एक से ज़्यादा बार बचाया है।
7. raw `px` को borders, shadows, और अन्य पूरी तरह decorative details के लिए रिज़र्व रखें जिन्हें text scale होने पर हिलना नहीं चाहिए।

उस चीज़ के लिए यह बहुत सारे units हैं जो पहले बस "एक नंबर चुनो" हुआ करती थी। लेकिन एक बार जब आप देख लेते हैं कि कोई साइट किसी ऐसे व्यक्ति के लिए बेकार हो गई जिसने सिर्फ़ एक browser setting बदली थी जिसके होने का ज़्यादातर developers को पता ही नहीं है, तो "बस एक नंबर चुनो" काफ़ी नहीं लगता।

## स्रोत
1. [font-size - CSS: Cascading Style Sheets | MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/font-size)
2. [<relative-size> CSS type - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/relative-size)
3. [CSS Units गाइड - rem, em, px, vh, vw समझाया गया | Saeloun Blog](https://blog.saeloun.com/2024/07/22/css-units/)
4. [REM? PX? दोनों क्यों नहीं?](https://dbushell.com/2024/11/11/rem-or-px/)
5. [Accessibility: px या rem?](https://matklad.github.io/2022/11/05/accessibility-px-or-rem.html)
6. [Totally remdom, या Browsers टेक्स्ट को कैसे Zoom करते हैं - Manuel Matuzovic](https://www.matuzo.at/blog/2023/how-browsers-zoom-text)
7. [Viewport के आधार पर CSS clamp() से font-size को Linearly Scale करें | CSS-Tricks](https://css-tricks.com/linearly-scale-font-size-with-css-clamp-based-on-the-viewport/)
8. [CSS Clamp का उपयोग करके Modern Fluid Typography — Smashing Magazine](https://www.smashingmagazine.com/2022/01/modern-fluid-typography-css-clamp/)
9. [Readability के लिए Optimal Line Length: 50–75 Character Rule समझाया गया | UXPin](https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/)
10. [CSS Container Query Units](https://ishadeed.com/article/container-query-units/)
11. [CSS container queries - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries)
12. [16px या उससे बड़ा Text iOS Form Zoom को रोकता है | CSS-Tricks](https://css-tricks.com/16px-or-larger-text-prevents-ios-form-zoom/)
13. [Defensive CSS - iOS Safari पर Input zoom](https://defensivecss.dev/tip/input-zoom-safari/)
14. [Text Scaling - Android Accessibility सहायता](https://support.google.com/accessibility/android/answer/12159181?hl=en)
15. [Android UI Design में dp और sp](https://robotqa.com/blog/dp-and-sp-in-android-ui-design/)
16. [Font Size - Tailwind CSS](https://v3.tailwindcss.com/docs/font-size)