+++
title       = "CBSE Portal Hacks 2026: Risks, Impact & Government Fixes"
description = "CBSE's OSM portal was hacked in 2026, exposing answer sheets of 20 lakh students. Here's the full breakdown and what the government must do to fix it."
date        = "2026-06-01T10:24:49+05:30"
slug        = "cbse-portal-hacks-vulnerabilities-2026"
tags        = ["Cybersecurity", "CBSE", "Education", "Data Privacy", "India"]
keywords    = ["CBSE portal hack", "CBSE OSM vulnerability", "CBSE data breach 2026", "India education cybersecurity", "student data privacy India"]
canonical   = "/posts/cbse-portal-hacks-vulnerabilities-2026/"
+++

India's most trusted examination board, CBSE, was rocked by a sweeping cybersecurity scandal in May 2026 when a 19-year-old ethical hacker demonstrated live, unrestricted access to its On-Screen Marking (OSM) evaluation system — including shell access to production servers and free downloads of student answer sheets from an unsecured cloud bucket [1][2]. The breach put the personal and academic data of an estimated 20 lakh (2 million) Class 12 students at risk [5]. This article unpacks every layer of the hack, explains what it means for students and families, and maps out what the government must do to prevent a repeat.

## The 2026 CBSE OSM Breach: What Happened

On 22 May 2026, Nisarga Adhikary — a 19-year-old ethical hacker and Class 12 student — went public on social media with a detailed breakdown of critical security flaws inside CBSE's **OnMark portal**, the third-party system used by examiners to evaluate Class 12 answer sheets digitally [2][3]. What made his disclosures explosive was not just the vulnerabilities themselves, but the timeline: CBSE officials had previously denied that any such flaws existed, yet Adhikary demonstrated full **create, read, update, and delete (CRUD) access** along with **shell access to CBSE's live production servers** [1]. He also obtained **super-admin privileges** on another OnMark subdomain responsible for evaluation across multiple universities [1].

The portal is operated by a private vendor, **COEMPT Eduteck**, under contract with CBSE. Adhikary described the system's security posture as "insanely insecure" [4] — a characterization that even CBSE's own subsequent audit could not convincingly refute.

## Vulnerabilities Laid Bare

Adhikary identified at least **six high-severity vulnerabilities** across CBSE-linked systems [3]. The table below summarises the critical flaws uncovered:

| Vulnerability | Description | Risk Level |
|---|---|---|
| Hardcoded Master Password | A universal secret password embedded in publicly readable code, bypassing per-user authentication | Critical |
| OTP Exposed in Browser | One-time passwords sent to examiners visible in browser HTTP responses, making bypass trivial | High |
| Password Reset Without Verification | Any examiner's account password could be reset with no identity check | High |
| AWS S3 Bucket — No Auth Required | Answer sheets and question papers downloadable by anyone with the bucket URL | Critical |
| MD5 Password Hashing on SARAS Portal | Outdated, easily crackable hash algorithm used on CBSE's school affiliation system | High |
| Admin Password "123456" | An administrative portal linked to CBSE's ecosystem reportedly used this trivial password | Critical |

Sources: [3][4][8][14]

The Amazon Web Services (AWS) S3 storage bucket linked to the OnMark system allegedly allowed anyone to **browse and download scanned answer booklets and question papers from 2026 board examinations** without providing any credentials [4][15]. This is a classic *insecure cloud configuration* — one of the most common and most preventable causes of mass data exposure in modern IT.

![cbse attack flow](/images/posts/cbse-portal-hacks-vulnerabilities-2026/cbse-attack-flow.svg)

## Impact on Students: Who Gets Hurt?

The real-world consequences of these vulnerabilities fall squarely on millions of students:

- **Privacy violation**: Scanned answer booklets — containing handwriting, roll numbers, and school details — were allegedly accessible to anyone with a browser and a URL [15].
- **Risk of marks manipulation**: The ability to impersonate examiners and gain super-admin access theoretically allowed alteration of marks, though CBSE states no such tampering has been confirmed [1][14].
- **Financial fraud**: A separate malicious attack on the *re-evaluation portal* caused fee display amounts to fluctuate wildly between ₹1 and ₹68,000, overcharging approximately **50 students** [7].
- **Examination integrity compromised**: With 2026 question papers allegedly accessible in the AWS bucket, the fairness of the board exam itself came under a cloud [4].
- **Political uproar**: Congress leader Jairam Ramesh called it "a massive data leak that has put the privacy of 20 lakh students at risk," demanding government accountability [5][6].

## The COEMPT Eduteck Controversy

At the centre of the storm is **COEMPT Eduteck**, the private IT vendor operating CBSE's OSM platform [17]. Critics allege that successive Requests for Proposal (RFPs) were modified across multiple tender rounds in ways that may have altered eligibility criteria to the vendor's benefit [17]. Key red flags include:

- The requirement for **robotic scanning machines** — a critical physical security safeguard — was reportedly removed in the third RFP [6].
- Scanned images showed signs of being captured via **mobile phone cameras** rather than certified secure scanners, raising physical data-handling concerns [6].
- Congress formally demanded a probe into the tendering process and the vendor's conduct [17].

CBSE has maintained that identified vulnerabilities "have been contained," attributing some hacking demonstrations to a testing environment rather than live production systems — a claim disputed by cybersecurity researchers [3][10].

## Fake DigiLocker: A Shadow Threat

Compounding the crisis, the Ministry of Electronics and Information Technology (**MeitY**) issued a public warning about a **counterfeit DigiLocker website** operating in the shadows of the CBSE controversy [9]. The fraudulent portal:

- Mimics the official government DigiLocker interface in look and feel.
- Claims to provide DigiLocker and CISCE services to students.
- Is engineered to harvest student credentials and personal information.

Students and parents rushing to verify board results are prime phishing targets. MeitY urges users to access DigiLocker **only** via [digilocker.gov.in](https://digilocker.gov.in) and to report suspect sites through CERT-In's official channels [9].

## Government Response So Far

The government's immediate response has been energetic, though its long-term follow-through remains to be seen:

- **IIT Task Force Deployed**: CBSE brought in cybersecurity experts from **IIT Madras** and **IIT Kanpur**, alongside government agency professionals, to audit OnMark and shore up remaining vulnerabilities [11].
- **Vulnerability Containment Declared**: CBSE stated all "identifiable vulnerabilities" have been contained, with additional sweeps still ongoing [10].
- **DigiLocker Pivot Announced**: The Ministry of Education confirmed that from the next academic year, CBSE Class 12 answer sheets will move to **DigiLocker**, reducing dependence on third-party vendor portals entirely [16].
- **National Cybersecurity Strategy 2026 Launched**: This umbrella policy framework mandates coordination among CERT-In, state police cyber cells, and private sector stakeholders for faster detection and response across critical sectors [13].
- **CERT-In Scale-Up**: In 2024–25, CERT-In handled over **29.44 lakh cyber incidents**, issued 1,530 alerts, 390 vulnerability advisories, and conducted over **9,700 security audits** across government and critical infrastructure [12].

## What More Must Be Done: A Policy Roadmap

Reactive patching is not a strategy. Here is what systemic reform must look like:

### Mandatory Vendor Security Standards

- Any EdTech vendor handling government education data must pass a **CERT-In-approved third-party security audit** before contracts are signed and renewed annually.
- Security requirements in government RFPs must be **non-negotiable, version-locked clauses** — not items that can be quietly diluted across tender revisions.
- Formal **bug bounty programmes** should be established for all government education portals, giving ethical hackers like Adhikary a safe, legally protected, and financially rewarded disclosure channel.

### Cloud Configuration Governance

- All government-linked cloud storage (AWS S3, Azure Blob, GCP) must undergo **automated misconfiguration scanning** — a standard already mandated in the EU, USA, and Australia.
- The **Digital Personal Data Protection (DPDP) Act 2023** must be enforced with meaningful penalties: vendors who expose student data through negligence should face financial liability, not just advisory notices.

### A Dedicated Edu-CERT

- India should establish a **sectoral Education CERT** (Edu-CERT) modelled on the financial sector's CERT-Fin, with authority to independently audit, respond to, and penalise vendors operating education infrastructure in real time — without waiting for student complaints to reach newspapers.

### Cybersecurity Talent Pipeline

- The National Cybersecurity Strategy 2026 targets training **5 lakh cybersecurity professionals** over five years [13]; a dedicated portion must be channelled specifically into edtech security and government portal auditing.
- Cybersecurity must be added to school and college curricula so the next generation of administrators and developers builds security-first thinking from the ground up.

### Student and Parent Awareness

- Annual **digital literacy campaigns** should educate students, parents, and school administrators on verifying official URLs, identifying phishing portals, and reporting data anomalies through official channels [9].
- CBSE should publish a **clear public incident-response protocol** so students know what to do the moment a breach is suspected.

The CBSE crisis is ultimately a symptom of a systemic gap: India's rapid digital expansion in public services has not consistently been matched by equivalent investment in security architecture. As examination results, identities, and academic records become ever-more tightly bound to digital systems, the stakes only grow higher — and the window for meaningful structural reform is right now, before the next breach makes headlines.

## Sources

1. [CBSE Online Marking Portal Hacked After Officials Denied Security Flaws — MediaNama](https://www.medianama.com/2026/05/223-cbse-hacked-cybersecurity-researcher-demonstrates-access-official-denials/)
2. [How a 19-year-old student hacked CBSE's OSM portal, exposed vulnerabilities — The Print](https://theprint.in/feature/19-student-hacked-cbses-osm-portal-vulnerabilities/2942305/)
3. [CBSE admits vulnerabilities in OnMark portal after teen hacker alleges answer sheet leak — Careers360](https://news.careers360.com/cbse-onmark-portal-security-vulnerability-nisarga-adhikary-answer-sheets-question-papers-data-exposure-cybersecurity)
4. ['Insanely insecure': Ethical hacker alleges CBSE answer sheets were publicly accessible — BusinessToday](https://www.businesstoday.in/education/story/insanely-insecure-ethical-hacker-alleges-cbse-answer-sheets-question-papers-were-publicly-accessible-534141-2026-05-31)
5. [CBSE Class 12 data leak: 20 lakh students' privacy at risk, says Cong — Asianet Newsable](https://newsable.asianetnews.com/india/cbse-class-12-data-leak-20-lakh-students-privacy-at-risk-says-cong-articleshow-z9w4sgl)
6. [Massive data leak that has put privacy of 20 lakh students at risk: Congress slams government — ANI News](https://aninews.in/news/national/politics/massive-data-leak-that-has-put-privacy-of-20-lakh-students-at-risk-congress-slams-government-over-post-result-problems-faced-by-cbse-students20260531200124/)
7. [CBSE Portal Faces Malicious Attack Affecting Approximately 50 Students — The Chenab Times](https://thechenabtimes.com/2026/05/30/india-cbse-portal-faces-malicious-attack-affecting-approximately-50-students/)
8. ['Password was 123456': Student alleges fresh security lapses in CBSE-linked systems — BusinessToday](https://www.businesstoday.in/education/story/password-was-123456-student-alleges-fresh-security-lapses-in-cbse-linked-systems-534150-2026-05-31)
9. [Govt warns students about fake DigiLocker website amid CBSE OSM row — Digit](https://www.digit.in/news/general/govt-warns-students-about-fake-digilocker-website-amid-cbse-osm-row-how-to-stay-safe)
10. [CBSE says OSM portal 'vulnerabilities contained', deploys IIT teams for cybersecurity review — India TV News](https://www.indiatvnews.com/education/news/cbse-says-osm-portal-vulnerabilities-contained-deploys-iit-teams-for-cybersecurity-review-2026-05-31-1043112)
11. [CBSE Deploys IIT Madras and IIT Kanpur Experts After Security Concerns Over OnMark Portal — Swarajya Mag](https://swarajyamag.com/amp/story/news-brief/cbse-deploys-iit-madras-and-iit-kanpur-experts-after-security-concerns-over-onmark-portal)
12. [Government Strengthens Cybersecurity Across Critical Sectors; Over 9,700 CERT-In Audits Conducted in 2024–25 — PIB](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2148943)
13. [India Launches National Cybersecurity Strategy 2026 — Education Post](https://educationpost.in/news/education/current-affairs/science-and-technology/india-launches-national-cybersecurity-strategy-2026)
14. [CBSE OSM Controversy Explained: Board Admits Security Gaps After Portal Was Hacked — Gulf News](https://gulfnews.com/uae/education/cbses-osm-controversy-explained-why-the-board-admits-security-gaps-after-portal-was-hacked-1.500558632)
15. [CBSE Answer Sheet Leak Row: Students Allege AWS Data Breach, Poor Scanning and Evaluation Errors — OneIndia](https://www.oneindia.com/india/cbse-answer-sheet-leak-row-students-allege-aws-data-breach-poor-scanning-and-evaluation-errors-014-8104317.html)
16. [From next year, CBSE Class 12 answer sheets to be available on DigiLocker — Careers360](https://news.careers360.com/cbse-class-12th-result-2026-answer-sheet-digilocker-gov-in-next-year-osm-portal-coempt-eduteck-education-ministry-results-news)
17. [Congress raises alarm over alleged CBSE answer sheet leak, questions evaluation contractor — The Statesman](https://www.thestatesman.com/india/congress-raises-alarm-over-alleged-cbse-answer-sheet-leak-questions-evaluation-contractor-1503600350.html/amp)