+++
title       = "React इंटरव्यू प्रश्न: शुरुआत से विशेषज्ञ स्तर तक"
description = "20+ React इंटरव्यू प्रश्नों में महारत हासिल करें — hooks, Fiber, React 19 की नई सुविधाएं और वरिष्ठ स्तर के आर्किटेक्चर पैटर्न।"
date        = "2026-05-30T17:26:46+05:30"
slug          = "react-interview-questions-beginner-to-expert"
tags          = ["React", "फ्रंटएंड इंटरव्यू", "JavaScript", "React 19", "वेब डेवलपमेंट"]
keywords      = ["React इंटरव्यू प्रश्न", "React hooks इंटरव्यू", "React 19 इंटरव्यू", "फ्रंटएंड डेवलपर इंटरव्यू", "एडवांस्ड React प्रश्न"]
canonical     = "/hi/posts/react-interview-questions-beginner-to-expert/"
feature_image = "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=1200"
+++

React फ्रंटएंड इकोसिस्टम में प्रमुख UI लाइब्रेरी बनी हुई है, और स्टार्टअप से लेकर FAANG कंपनियों तक के इंटरव्यूअर React-specific प्रश्नों से ज्ञान की गहराई मापते हैं [1]। यह गाइड सबसे अधिक पूछे जाने वाले प्रश्नों को कठिनाई के क्रम में प्रस्तुत करती है — बुनियादी प्रश्नों से लेकर विशेषज्ञ स्तर के आर्किटेक्चर और React 19 की आंतरिक कार्यप्रणाली तक — ताकि आप किसी भी फ्रंटएंड इंटरव्यू के लिए पूरी तरह तैयार हो सकें।

## शुरुआती स्तर: हर उम्मीदवार को पता होनी चाहिए ये मूल बातें

**1. React क्या है, और यह किस समस्या का समाधान करता है?**
React Meta द्वारा रखरखाव की जाने वाली एक JavaScript लाइब्रेरी है जो composable यूज़र इंटरफेस बनाने के लिए उपयोग की जाती है। यह UI को एप्लिकेशन state के साथ sync में रखने की समस्या हल करता है — बदलावों को ट्रैक करके केवल प्रभावित DOM हिस्सों को अपडेट करता है [2]।

**2. JSX क्या है?**
JSX एक syntax extension है जो आपको JavaScript के अंदर HTML जैसा markup लिखने देता है। Babel जैसे टूल्स build time पर JSX को `React.createElement()` calls में कम्पाइल कर देते हैं [2]।

**3. Props और State में क्या अंतर है?**
Props read-only inputs हैं जो parent component से child को पास किए जाते हैं; state component के अंदर internally manage होने वाला mutable data है। जब state बदलती है, React component और उसके subtree को फिर से render करता है [3]।

**4. Virtual DOM क्या है?**
असली browser DOM को सीधे छूने के बजाय, React पहले UI के एक lightweight in-memory representation पर बदलाव लागू करता है। फिर यह नए virtual tree को पिछले से compare करता है और केवल न्यूनतम real DOM mutations करता है [7]।

**5. Controlled और Uncontrolled Components में क्या अंतर है?**
*Controlled* component में, form element की values React state द्वारा `value` और `onChange` के ज़रिए नियंत्रित होती हैं। *Uncontrolled* component में, DOM खुद value संभालता है और आप इसे `ref` के ज़रिए पढ़ते हैं [3]।

## मध्यवर्ती स्तर: Hooks, Lists, और Side Effects

**6. React के मुख्य Hooks और उनका उद्देश्य बताएं।**
React Hooks — React 16.8 में पेश किए गए — ऐसे functions हैं जो functional components में state और lifecycle सुविधाएं देते हैं [1]:
- `useState` – सरल local state manage करें
- `useEffect` – data fetching या subscriptions जैसे side effects चलाएं
- `useContext` – wrapper component के बिना context value उपयोग करें
- `useRef` – re-renders किए बिना mutable value को renders के पार बनाए रखें
- `useReducer` – explicit action types के साथ complex state transitions संभालें [2]

**7. Lists में `key` props क्यों ज़रूरी हैं?**
Arrays render करते समय, React renders के बीच elements को match करने के लिए `key` का उपयोग करता है। Stable, unique keys से React items को efficiently move, insert, और remove कर सकता है। इनके बिना React items को unnecessarily unmount और remount कर सकता है — उनकी internal state खो देता है [1]।

**8. `useEffect` dependency array कैसे काम करता है?**
Empty array `[]` effect को mount पर एक बार चलाता है। Variables list करने से यह तब re-run होता है जब वे values बदलती हैं। Array छोड़ने से यह हर render के बाद चलता है। सामान्य bugs में stale closures और missing dependencies शामिल हैं [4]।

**9. React Context कब उपयोग करना चाहिए?**
Context global, low-frequency data के लिए आदर्श है जैसे authentication status, locale, या theme। हालाँकि, अगर data बार-बार बदलता है — जैसे form inputs — तो हर consumer हर बदलाव पर re-render होता है, जो performance को नुकसान पहुंचा सकता है [1]। Contexts को update frequency के अनुसार split करें और ज़रूरत पड़ने पर provider values को memoize करें।

**10. Code Splitting क्या है, और इसे कैसे implement करते हैं?**
Code splitting initial bundle size को on-demand JavaScript loading से कम करती है। React में, `React.lazy` को dynamic `import()` के साथ उपयोग करें और component को `<Suspense fallback={…}>` में wrap करें [2]।

## एडवांस्ड स्तर: Performance, Reconciliation, और Fiber

**11. React का reconciliation algorithm कैसे काम करता है?**
Reconciliation वह प्रक्रिया है जिससे React state या props बदलने पर minimal DOM update calculate करता है। React एक नया virtual DOM tree बनाता है, उसे O(n) heuristic से पिछले से compare करता है (अलग-अलग types के elements अलग trees बनाते हैं), और फिर एक single synchronous pass में patch commit करता है [7]।

**12. React Fiber क्या है?**
React Fiber, React core algorithm का एक complete rewrite है जो incremental rendering को enable करने के लिए introduce किया गया। यह rendering को छोटे units of work में तोड़ता है, जिससे React in-progress renders को pause, prioritize, या abort कर सकता है — `startTransition`, `useDeferredValue`, और concurrent rendering model को शक्ति देता है [4]।

**13. `useMemo` बनाम `useCallback` — क्या अंतर है?**
`useMemo` एक computation के *result* को cache करता है; `useCallback` *function reference* को cache करता है। दोनों re-renders पर unnecessary काम से बचते हैं। हालाँकि, React 19 में React Compiler stable होने के साथ, अधिकांश components को अब इन्हें manually नहीं लिखना पड़ता — compiler build time पर auto-memoization inject करता है [1]। इन्हें तभी उपयोग करें जब profiling एक concrete bottleneck दिखाए [8]।

**14. Custom Hooks क्या हैं, और ये क्यों महत्वपूर्ण हैं?**
Custom hooks user-defined functions हैं जो `use` से शुरू होते हैं और component tree को बदले बिना components के बीच stateful logic extract और share करते हैं। सामान्य उदाहरणों में `useFetch`, `useDebounce`, और `useLocalStorage` शामिल हैं [3]।

**15. `useReducer` को `useState` पर कब प्राथमिकता दें?**
`useReducer` तब बेहतर होता है जब state के multiple sub-values हों या जब next state पिछले पर non-trivial तरीकों से निर्भर हो। यह transitions को explicit, auditable, और easily testable बनाता है — Redux जैसा ही pattern [5]।

**16. Render और Commit phases समझाएं।**
React का काम दो phases में बंटा है: *render phase* (reconciliation), जो interruptible है और pure functions चलाती है, और *commit phase*, जो resulting mutations को real DOM पर एक single synchronous pass में apply करती है। यह split ही concurrent mode को safe बनाती है — commit हमेशा atomic होता है [7]।

## विशेषज्ञ स्तर: React 19, Server Components, और Architecture

**17. React Compiler क्या है?**
React Compiler एक build-time tool है जो React 19 के साथ stably ship हुआ है और component tree में automatically memoization logic inject करता है। यह बिना नए code में manual `useMemo`, `useCallback`, या `React.memo` calls के hand-optimized performance देता है [1]।

**18. React Server Components (RSC) क्या हैं?**
Server Components exclusively server पर render होते हैं और browser को कभी ship नहीं होते। ये directly databases और file systems access कर सकते हैं और Client Components के साथ seamlessly compose होते हैं। 2026 में किसी भी Next.js role के लिए, Server Component और Client Component में अंतर न जान पाना effectively disqualifying है [5]।

**19. `useActionState` समझाएं।**
`useActionState` एक action function और initial state accept करता है, `[state, dispatchAction, isPending]` return करता है। Action dispatch करने से `isPending` `true` होती है, function चलता है, और resolution पर state उसके return value से replace हो जाती है — जो पहले data, loading, और error के लिए तीन अलग `useState` calls की ज़रूरत थी [6]।

**20. `useOptimistic` क्या है?**
`useOptimistic` async action in-flight रहते state का एक optimistic version तुरंत render करता है, फिर action settle होने पर automatically real state पर वापस आ जाता है। यह likes, chat messages, या list reorders के लिए आदर्श है जहाँ network round-trip sluggish लगती है [6]।

**21. Large-scale React application को कैसे architect करते हैं?**
Senior प्रश्न syntax recall की बजाय architectural judgment probe करते हैं। मुख्य considerations में शामिल हैं: complexity के अनुपात में state management strategy चुनना (local state → Context → Zustand/Redux Toolkit), data-heavy server-rendered views के लिए RSC का लाभ उठाना, route-level code splitting लागू करना, memoization के लिए React Compiler पर भरोसा करना, और UI components और business logic के बीच clean separation enforce करना [5]।

**22. React में performance optimization कैसे करते हैं?**
Performance पहले एक measurement discipline है। `React.memo` या `react-window` जैसी virtualization libraries की ओर जाने से पहले React Profiler और bundle analysis tools से शुरुआत करें। Time to Interactive (TTI) benchmark करें ताकि पता चले किसी बदलाव ने वास्तव में असर किया या नहीं [9]।

## स्रोत
1. [Ex-interviewers के 100+ React इंटरव्यू प्रश्न (2026) – GreatFrontEnd](https://www.greatfrontend.com/blog/100-react-interview-questions-straight-from-ex-interviewers)
2. [70+ React इंटरव्यू प्रश्न और उत्तर (2026) – InterviewBit](https://www.interviewbit.com/react-interview-questions/)
3. [React इंटरव्यू प्रश्न और उत्तर (2026) – Toptal](https://www.toptal.com/react/interview-questions)
4. [25 React इंटरव्यू प्रश्न 2026 – DEV Community](https://dev.to/aindrila_bhattacharjee_0f/25-react-interview-questions-2026-with-answers-hooks-react-19-concurrent-mode-48en)
5. [50+ Senior React Architect इंटरव्यू प्रश्न (2026) – Hirecta](https://hirecta.com/interviews/react-senior-level-interview-questions)
6. [React 19 इंटरव्यू प्रश्न – CodifyNext](https://www.codifynext.com/all/react-19-interview-questions)
7. [Virtual DOM से परे: React का Fiber Architecture – Medium](https://medium.com/@usama.aslam.dev/beyond-the-virtual-dom-understanding-reacts-fiber-architecture-and-reconciliation-process-e3e41af99396)
8. [Advanced ReactJS इंटरव्यू प्रश्न 2026 – InterviewKickstart](https://interviewkickstart.com/blogs/interview-questions/advanced-reactjs-interview-questions)
9. [React Coding इंटरव्यू प्रश्न 2026 – Playcode Blog](https://playcode.io/blog/react-coding-interview-questions-2026)
