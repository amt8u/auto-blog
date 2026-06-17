+++
title       = "PowerShell क्यों है जब CMD पहले से था"
description = "CMD दशकों तक ठीक काम करता था — तो Microsoft ने PowerShell क्यों जोड़ा? और Windows में अब तीन अलग 'terminal' चीज़ें क्यों हैं? यही है असली कहानी।"
date        = "2026-06-17T18:33:01+05:30"
slug          = "why-powershell-when-cmd-exists"
tags          = ["powershell", "windows", "कमांड-लाइन", "devops", "sysadmin"]
keywords      = ["PowerShell क्यों मौजूद है", "PowerShell बनाम CMD", "Command Prompt बनाम PowerShell", "Windows टर्मिनल इतिहास", "PowerShell इतिहास"]
canonical     = "/hi/posts/why-powershell-when-cmd-exists/"
feature_image = "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=1200"
+++

आप Windows 11 खोलते हैं, Start menu पर राइट-क्लिक करते हैं, और देखते हैं: *Command Prompt*, *PowerShell*, *Windows Terminal*। तीन चीज़ें। आप बस एक झटपट command चलाना चाहते थे। अब आप अपने जीवन के फैसलों पर सवाल उठा रहे हैं।

यह उलझन वास्तविक है, और सच में, Microsoft ने इसे आसान नहीं बनाया। लेकिन PowerShell के अस्तित्व का एक वास्तविक अच्छा कारण है — और एक बार जब आप इसे समझ लेते हैं, तो पूरी तस्वीर स्पष्ट होने लगती है।

## CMD कभी सच में Shell नहीं था — यह एक अस्थायी समाधान था

शुरुआत से शुरू करते हैं। `cmd.exe` — Command Prompt — [दिसंबर 1987](https://en.wikipedia.org/wiki/Cmd.exe) में Windows NT के लॉन्च से मौजूद है [1]। इससे पहले, MS-DOS में COMMAND.COM काम संभालता था। तो हाँ, Windows में लगभग 40 साल से command-line interface है।

लेकिन यहाँ वह बात है जो लोग चूक जाते हैं: **CMD को power users या administrators के लिए डिज़ाइन नहीं किया गया था।** इसे पुराने DOS batch files को चलाए रखने और आपको बुनियादी काम करने देने के लिए बनाया गया था — एक फ़ाइल कॉपी करना, IP address जाँचना, एक program चलाना। बस इतना ही। इसकी जड़ें 1980s के एक single-user, single-tasking operating system में थीं, और वह बोझ कभी दूर नहीं हुआ।

[Windows command-line का विकास](https://devblogs.microsoft.com/commandline/windows-command-line-the-evolution-of-the-windows-command-line/) इस कहानी को अच्छी तरह बताता है — CMD हमेशा पीछे भागता रहा, कभी भी आधुनिक Windows systems की जटिलता के लिए सच में डिज़ाइन नहीं किया गया था [2]।

कुछ वास्तविक CMD सीमाएँ जो लोगों को पागल कर देती थीं:

- **अधिकतम command line string लंबाई: 8,191 characters।** लंबे file paths पास करने की कोशिश में उस सीमा को छूने पर cryptic failures मिलती थीं [3]।
- Objects के लिए कोई native support नहीं — सब कुछ plain text है, इसलिए आपको string gymnastics से output parse करना पड़ता था।
- `.bat` files में scripting capabilities वास्तव में भयानक हैं — conditional logic, loops, error handling — सब दर्दनाक।
- Registry, services, WMI, या Active Directory जैसे Windows internals तक शून्य built-in पहुँच।
- उल्लेखनीय tab completion नहीं। Syntax highlighting नहीं। कोई modern UX नहीं।

जब आप एक PC manage कर रहे हों, तो ये सीमाएँ परेशान करने वाली हैं। जब आप एक enterprise में **सैकड़ों या हज़ारों Windows machines** के लिए ज़िम्मेदार sysadmin हों? CMD के पास जो चाहिए वह पास भी नहीं आता [4]। बुनियादी bulk administration करने के लिए भी आपको VBScript से script करना होता या custom tools लिखने होते। यह एक गड़बड़ी थी।

## एक आदमी इससे थक गया — और उसने एक Manifesto लिखा

यहीं से कहानी दिलचस्प होती है।

1999 में, Jeffrey Snover नाम के एक developer Microsoft में शामिल हुए। उनके पास Unix background था और वे जानते थे कि एक असली shell क्या कर सकती है। उन्होंने Windows system administration को देखा और, उनके अपने स्वीकारोक्ति के अनुसार, भयभीत हो गए। Unix में `bash`, `grep`, `awk`, `sed` था — scale पर systems manage करने के लिए composable tools का पूरा ecosystem। Windows में... `.bat` files थीं।

Snover ने इस समस्या के बारे में कुछ साल सोचा। फिर, **8 अगस्त, 2002** को, उन्होंने वह लिखा जो [Monad Manifesto](https://learn.microsoft.com/en-us/powershell/scripting/developer/monad-manifesto?view=powershell-7.5) के नाम से जाना जाता है — एक 17-page document जो एक नए प्रकार के Windows shell के लिए उनके vision को रखता है [5]। उन्होंने project का नाम **Monad** रखा।

Manifesto आश्चर्यजनक रूप से पठनीय है। Snover का मूल तर्क यह था: Unix shells शक्तिशाली हैं क्योंकि वे *text* की pipelines के माध्यम से simple tools को compose करती हैं। लेकिन text नाज़ुक होता है — आपको इसे parse करना, split करना, columns गिनना होता है, और प्रार्थना करनी होती है कि output format कभी न बदले। क्या होगा अगर इसकी जगह आप *objects* pipe करें? Named properties के साथ structured data, raw strings नहीं?

वह विचार — **pipeline में objects, text नहीं** — वह एकमात्र सबसे बड़ी चीज़ है जो PowerShell को CMD (और सच में bash से भी) अलग करती है।

![powershell pipeline vs cmd](/images/posts/why-powershell-when-cmd-exists/powershell-pipeline-vs-cmd.svg)

Monad का नाम बदला गया और PowerShell 1.0 को आधिकारिक रूप से **नवंबर 2006** में जारी किया गया [6]। Manifesto से ship होने तक चार साल लगे।

## PowerShell वास्तव में क्या अलग करता है

ठीक है, पर्याप्त इतिहास — चलिए बात करते हैं *क्यों* यह व्यावहारिक रूप से महत्वपूर्ण है।

### Objects, Text नहीं

जब आप PowerShell में `Get-Process` चलाते हैं, तो आपको एक string नहीं मिलती। आपको `System.Diagnostics.Process` .NET objects का एक collection मिलता है — हर एक में `Name`, `Id`, `CPU`, `WorkingSet` जैसी properties होती हैं [7]। उनके *types* होते हैं। आप उन्हें filter कर सकते हैं, sort कर सकते हैं, compare कर सकते हैं, string parsing को कभी छुए बिना।

तुलना करें:

```powershell
# PowerShell — reads like English, rock solid
Get-Process | Where-Object WorkingSet -gt 100MB | Sort-Object CPU -Descending
```

```bat
REM CMD — parsing text by character position, good luck
tasklist /NH | sort /R /+65
```

CMD version output में character positions गिनता है। Windows version बदलें, column width बदले — यह चुपचाप टूट जाता है। PowerShell version? यह चाहे जो हो, ठीक काम करेगा।

### यह .NET पर बना है — जिसका मतलब है यह लगभग कुछ भी कर सकता है

PowerShell cmdlets .NET Framework (और बाद में .NET Core) पर बने हैं। इसका मतलब है आप अपने shell से सीधे .NET APIs call कर सकते हैं। Active Directory, Windows registry, Event Logs, COM objects, REST APIs, या WMI के साथ interact करना चाहते हैं? PowerShell में इन सभी के लिए native cmdlets हैं [4]।

CMD शाब्दिक रूप से external tools के बिना इनमें से कुछ भी नहीं कर सकता।

### Scale पर Remote Management

`Invoke-Command` आपको एक साथ 500 remote Windows machines पर PowerShell script चलाने देता है। यह अतिशयोक्ति नहीं है — enterprise sysadmins वास्तव में इसी के लिए इसका उपयोग करते हैं। CMD का कोई equivalent नहीं है। शून्य।

## और फिर Microsoft ने उलझन पैदा की

यहीं से चीज़ें बिगड़ती हैं।

PowerShell 1.0 से 5.1 तक — जिसे **Windows PowerShell** कहा जाता था — Windows-only था, पुराने .NET Framework पर बना था। फिर **अगस्त 2016** में, Microsoft ने कुछ ऐसा किया जिसकी किसी को उम्मीद नहीं थी: उन्होंने [PowerShell को open-source किया और Linux और macOS के लिए जारी किया](https://devblogs.microsoft.com/dotnet/powershell-is-now-open-source-and-cross-platform/) [8]। उन्होंने इसे .NET Core पर फिर से बनाया और नई चीज़ को **PowerShell Core 6.0**, अंततः बस **PowerShell 7** कहा।

तो अब हैं — और मैं मज़ाक नहीं कर रहा — **दो अलग PowerShells**:

| विशेषता | Windows PowerShell 5.1 | PowerShell 7.x |
|---|---|---|
| Executable | `powershell.exe` | `pwsh.exe` |
| आधारित | .NET Framework | .NET Core / .NET 5+ |
| Platform | केवल Windows | Windows, Linux, macOS |
| स्थिति | केवल Maintenance | सक्रिय विकास |
| Pre-installed | हाँ (Windows) | नहीं, अलग install |

Windows PowerShell 5.1 को [अब नई features नहीं मिल रही हैं](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/migrating-from-windows-powershell-51-to-powershell-7?view=powershell-7.6) — Microsoft केवल security bugs के लिए इसे patch करता है [9]। PowerShell 7 में सभी नई चीज़ें होती हैं। लेकिन Windows अभी भी 5.1 pre-installed के साथ आता है, और PowerShell 7 एक *अलग download* है।

तो अगर आप Windows के साथ आने वाला "PowerShell" खोलते हैं — वह पुराना वाला है। और कुछ modules जो 5.1 में काम करते हैं वे अभी 7 में काम नहीं करते। और इसके विपरीत भी। सच में, यहीं यह पेचीदा हो जाता है।

## और फिर Windows Terminal आया

**मई 2019 में Microsoft Build पर**, उन्होंने [Windows Terminal](https://devblogs.microsoft.com/commandline/introducing-windows-terminal/) की घोषणा की — एक बिल्कुल नया tabbed terminal application [10]। यह मई 2020 में stable हुआ।

लेकिन यहाँ बात यह है: **Windows Terminal एक shell नहीं है।** यह बस एक host app है — एक सुंदर wrapper जो CMD, PowerShell 5.1, PowerShell 7, WSL (Windows Subsystem for Linux), या SSH sessions चला सकता है — सभी tabs में, GPU-accelerated text rendering, themes, custom fonts, और split panes के साथ।

इसे इस तरह सोचें:

- **CMD** = एक shell (engine, interpreter)
- **PowerShell** = एक shell (अधिक शक्तिशाली engine)
- **Windows Terminal** = वह window जो उन shells को अंदर चलाती है

समस्या यह है कि जब आप Windows 11 पर Windows Terminal खोलते हैं, तो यह PowerShell पर default होता है। इसलिए बहुत से लोग सोचते हैं कि Windows Terminal *ही* PowerShell है। ऐसा नहीं है। यह बस PowerShell को default के रूप में धारण किए हुए है।

वह mental model जो Microsoft ने उम्मीद की कि लोग खुद समझेंगे:

```
Windows Terminal (the window)
├── PowerShell 7 tab    ← आधुनिक shell
├── Windows PowerShell 5.1 tab  ← पुरानी shell
├── Command Prompt tab  ← प्राचीन shell
└── Ubuntu (WSL) tab    ← Windows पर Linux shell
```

## तो CMD को ठीक क्यों नहीं किया?

उचित सवाल। Microsoft ने कुछ बिल्कुल नया बनाने की बजाय CMD को upgrade क्यों नहीं किया?

जवाब है **backwards compatibility** — वह चीज़ जो हर Windows निर्णय को सताती है। CMD का उपयोग शाब्दिक रूप से लाखों batch scripts द्वारा enterprises, अस्पतालों, बैंकों, सरकारी systems में किया जाता है। cmd.exe को छूएं, और कुछ महत्वपूर्ण टूट जाता है। [CMD engine जानबूझकर maintenance mode में है](https://www.theregister.com/2020/05/27/windows_cmd_maintenance_mode/) क्योंकि "हर बार जब कोई बदलाव किया जाता है, तो कुछ महत्वपूर्ण टूट जाता है" [11]।

एक strategic architectural कारण भी था: 2002 के आसपास, Microsoft COM (Component Object Model) programming से .NET Framework में जा रहा था। .NET पर एक नई shell बनाना पूरी तरह समझ में आता था। DOS-era interpreter पर .NET को retrofit करना एक nightmare होता।

इसलिए उन्होंने PowerShell को एक parallel track के रूप में बनाया — नए users इसे पाते हैं, पुराने systems CMD चलाते रहते हैं, अंततः CMD fade out होता है। सिद्धांत में। व्यवहार में, CMD 20 साल बाद भी वहाँ है, सबको उलझाते हुए।

## क्या आपको वास्तव में PowerShell सीखनी चाहिए?

अगर आप Windows पर एक developer या sysadmin हैं, तो जवाब है **हाँ, और विशेष रूप से PowerShell 7** — वह cross-platform वाला जिसे आप अलग से install करते हैं (`pwsh.exe`)। यह सक्रिय रूप से maintained है, Linux और Mac पर काम करता है, और यही वह है जिसमें Microsoft आगे निवेश कर रहा है [12]।

अगर आप बस झटपट एक बार के commands चला रहे हैं — एक file ढूंढना, network config जाँचना — CMD अभी भी उसके लिए ठीक काम करता है। कोई आपको नहीं रोक रहा।

असली जाल यह सोचना है कि ये tools परस्पर बदले जा सकते हैं। वे नहीं हैं। PowerShell loops, functions, error handling, classes, और remote execution के साथ एक proper scripting language है। CMD glorified batch files के साथ एक command runner है। 2026 में automation के लिए CMD का उपयोग करना raw CGI में एक web app लिखने जैसा है — तकनीकी रूप से संभव, व्यावहारिक रूप से दर्दनाक।

यहाँ एक मोटा guide है:

- **CMD का उपयोग करें जब**: आप legacy `.bat` scripts चला रहे हैं, एक झटपट `ipconfig` या `ping` कर रहे हैं, या locked-down enterprise environment में काम कर रहे हैं
- **Windows PowerShell 5.1 का उपयोग करें जब**: आपको ऐसे modules चाहिए जो अभी PS7 पर नहीं हैं, या आप ऐसी machine पर हैं जहाँ PS7 install करना option नहीं है
- **PowerShell 7 का उपयोग करें जब**: बाकी सब के लिए — automation, scripting, DevOps, cloud management, कुछ भी गंभीर
- **Windows Terminal का उपयोग करें जब**: आप उपरोक्त सभी को themes के साथ एक अच्छी tabbed window में चाहते हैं

## "Microsoft ने यह क्यों किया?" का असली जवाब

Microsoft ने इसे जानबूझकर उलझाऊ नहीं बनाया। उन्होंने एक वास्तविक रूप से अच्छा engineering निर्णय लिया (PowerShell administration के लिए CMD से वैध रूप से बेहतर है), लेकिन फिर वर्षों के naming decisions, backwards compatibility constraints, एक open-source pivot, दो parallel product lines, और एक नया terminal host app — सभी को बिना end users को mental model स्पष्ट रूप से समझाए — परत दर परत जोड़ते गए।

CMD बना रहा क्योंकि उसे *रहना था*। PowerShell बनाया गया क्योंकि CMD scale नहीं हो सकता था। Windows Terminal आया क्योंकि पुराना console host शर्मनाक रूप से पुराना था। और PowerShell 7, 5.1 के साथ-साथ मौजूद है क्योंकि cross-platform एक बड़ा architectural बदलाव था जिसे version bump handle नहीं कर सकता था।

इनमें से कोई भी *अतार्किक* नहीं है — यह बस दशकों के accumulated decisions हैं जिन्हें किसी ने regular लोगों के लिए एक simple picture में map करने की परवाह नहीं की। जो Microsoft के लिए बहुत, बहुत on-brand है।

> समाप्त

## स्रोत
1. [Cmd.exe — विकिपीडिया](https://en.wikipedia.org/wiki/Cmd.exe)
2. [Windows Command-Line: Windows Command-Line का विकास — Microsoft DevBlogs](https://devblogs.microsoft.com/commandline/windows-command-line-the-evolution-of-the-windows-command-line/)
3. [Command prompt line string सीमा — Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/command-line-string-limitation)
4. [2.1. CMD.exe की सीमाएँ — O'Reilly Professional Windows PowerShell](https://www.oreilly.com/library/view/professional-windows-powershell/9780471946939/9780471946939_limitations_of_cmd.exe.html)
5. [Monad Manifesto — Microsoft Learn](https://learn.microsoft.com/en-us/powershell/scripting/developer/monad-manifesto?view=powershell-7.5)
6. [Monad Manifesto – Windows PowerShell की उत्पत्ति — PowerShell Team Blog](https://devblogs.microsoft.com/powershell/monad-manifesto-the-origin-of-windows-powershell/)
7. [PowerShell Object Pipelines बनाम CMD Text Parsing — Windows News AI](https://windowsnews.ai/article/powershell-object-pipelines-vs-cmd-text-parsing-the-automation-edge-it-pros-cant-ignore.426263)
8. [PowerShell अब open-source और cross-platform है — .NET Blog](https://devblogs.microsoft.com/dotnet/powershell-is-now-open-source-and-cross-platform/)
9. [Windows PowerShell 5.1 से PowerShell 7 में Migration — Microsoft Learn](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/migrating-from-windows-powershell-51-to-powershell-7?view=powershell-7.6)
10. [Windows Terminal का परिचय — Windows Command Line Blog](https://devblogs.microsoft.com/commandline/introducing-windows-terminal/)
11. [CMD maintenance mode में है — The Register](https://www.theregister.com/2020/05/27/windows_cmd_maintenance_mode/)
12. [Windows PowerShell का कोई भविष्य नहीं — PowerShell Core में बदलें — 4sysops](https://4sysops.com/archives/no-future-for-windows-powershell-change-to-powershell-core/)