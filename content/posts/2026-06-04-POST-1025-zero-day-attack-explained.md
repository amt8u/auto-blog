+++
title       = "Zero Day Attacks: What They Are and When They Expire"
description = "Zero day attacks exploit vulnerabilities vendors don't know about yet. Learn what makes them different—and when exactly they stop being zero days."
date        = "2026-06-04T12:29:07+05:30"
slug        = "zero-day-attack-explained"
tags        = ["cybersecurity", "zero-day", "vulnerability", "hacking"]
keywords    = ["zero day attack", "zero day vulnerability", "n-day vulnerability", "zero day exploit", "cybersecurity"]
canonical   = "/posts/zero-day-attack-explained/"
feature_image = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200&q=80"
+++

I've seen "zero day" used in breach headlines, movie trailers, and vendor marketing emails. Almost always it means "scary hack." That's not wrong exactly — but it misses the precise thing that makes a zero-day structurally different from every other attack. That precision actually matters when you're trying to understand your risk.

## Three Terms That Are Not the Same

I see these used interchangeably constantly. They're not.

- **Zero-day vulnerability**: a security flaw in software the vendor doesn't know exists. No patch, no CVE, no warning. [1]
- **Zero-day exploit**: the specific code or technique an attacker builds to take advantage of that flaw. [1]
- **Zero-day attack**: the actual real-world use of that exploit against a live target. [1]

The vulnerability is the hole. The exploit is the key that fits it. The attack is someone walking through the door.

You can have a vulnerability that no attacker has found yet. You can have an exploit that's been written but not deployed. These carry very different risk levels and require different responses. Most articles never make this distinction, which is frustrating, because it's the whole point.

## Where the "Zero" Actually Comes From

The name is from the vendor's perspective. **Zero days means the vendor has had zero days to prepare a fix.** [2]

Normal vulnerability discovery works like this: researcher finds bug → reports it to vendor → vendor patches → users update. Zero-days skip steps one through three entirely. By the time anyone at the company knows the flaw exists, it's already being exploited in the wild.

That's the structural difference. Not "it's a really bad bug." It's a bug where **the defender has had no time to respond whatsoever** before the attack begins [2]. The asymmetry is total — the attacker has all the information, the defender has none.

## The Lifecycle: From Bug to Patch

A zero-day doesn't appear from nowhere. It follows a path [4]:

1. **Introduction** — a developer ships a bug. Buffer overflow, authentication bypass, improper input validation. It sits dormant in the codebase.
2. **Discovery** — someone finds it. An attacker, a security researcher, an intelligence agency.
3. **Exploitation** — if the discoverer is malicious (or sells to someone who is), an exploit is built and deployed before the vendor knows the flaw exists. This is the zero-day window.
4. **Disclosure** — the vulnerability becomes public. Either someone catches the attack in progress, a researcher independently finds it, or the vendor gets notified through responsible disclosure.
5. **Patch release** — vendor ships a fix. This is the exact moment the zero-day stops being a zero-day.
6. **Patch adoption** — organisations actually deploy the fix. This can take months.

![zero day lifecycle](/images/posts/zero-day-attack-explained/zero-day-lifecycle.svg)

The average window from bug introduction to widespread patch adoption is **312 days** [4]. That's a long time for something to be silently exploited.

## When Exactly Does a Zero Day Stop Being a Zero Day?

Precisely: **the moment the vendor ships a patch and a CVE identifier is published** [3].

After that, it's called an **n-day vulnerability** — where "n" is the number of days since the patch dropped. A week later, still an n-day. A year later, still an n-day. The clock counts up, not down.

The threat doesn't go away when the patch lands. Organisations take an average of 60 to 150 days to actually deploy security updates across their environments [4]. Attackers keep exploiting the same flaw — now with full public documentation of exactly how it works, because CVE details are public. That's sometimes worse than the original zero-day phase. The exploit gets democratised.

## Zero-Day vs N-Day: The Real Difference

| | Zero-Day | N-Day |
|---|---|---|
| Patch exists? | No | Yes |
| Vendor aware? | No | Yes |
| CVE published? | No | Yes |
| Who uses it? | Nation-states, APT groups | Anyone with a PoC script |
| Cost of exploit | Millions of dollars | Near zero |
| Can defender patch? | No | Yes — but often doesn't |

The zero-day is scarce, expensive, and typically used surgically [6]. The n-day is a commodity. Once a CVE drops and a proof-of-concept appears on GitHub, script kiddies can run the exploit within 24 hours [6]. The economics are completely different.

## Stuxnet: What Burning Four Zero Days at Once Tells You

Stuxnet was discovered in 2010. Widely attributed to the US and Israel, it was designed to sabotage Iran's nuclear programme — specifically the centrifuges used to enrich uranium [7].

It used **four separate zero-day vulnerabilities simultaneously**, all targeting Windows, to spread across air-gapped networks and send malicious commands to Siemens industrial controllers that physically destroyed the centrifuges [7].

Four zero-days in a single piece of malware was almost unheard of. Zero-days are expensive. You don't burn four of them unless you have near-unlimited resources and an extremely high-value target. When researchers found Stuxnet, the number of zero-days used was itself evidence that this was a state-level operation. Normal malware can't afford that.

## Pegasus: Zero-Click Means You Did Nothing Wrong

NSO Group's Pegasus spyware went further than most people realise. It used iOS zero-day exploits — specifically **zero-click** exploits [8]. Zero-click means the victim doesn't tap a link, doesn't open an attachment, doesn't do anything at all.

You receive an iMessage. Your phone is compromised. You never knew it happened.

iOS zero-click exploits reportedly sell for close to **$10 million on the gray market** [9]. Governments are the primary buyers [9]. The economics explain why most high-quality zero-days don't end up in ransomware campaigns targeting hospitals — they're too valuable, and too finite. Once used, a zero-day can be detected and patched.

## The Disclosure Problem

There's genuine tension in the security community about how long vendors should get to fix something before details go public.

Google's Project Zero uses a **90+30 day policy**: 90 days for the vendor to ship a patch, then 30 days for users to install it, then details go public regardless of whether the vendor is ready [10].

The logic: disclosure deadlines force vendors to act. Without them, vendors can delay fixes for years while users stay exposed.

The counter-argument: once technical details are public, every attacker in the world has a tutorial. For n-day exploitation, a published PoC is the starting gun.

I'm not sure either approach fully solves the problem. Pegasus exploited iOS flaws faster than Apple could patch them. The journalists and activists whose phones were compromised weren't protected by any disclosure timeline.

## Defending Against Something You Can't See Coming

Signature-based detection doesn't work against unknown vulnerabilities. You can't match a pattern that doesn't exist yet.

Realistic defences have to be behavioural:

- **Behavioural monitoring** — detect unusual process activity, lateral movement, and anomalous privilege escalation instead of known malware signatures
- **Least-privilege architecture** — limit what an attacker can access even after getting in
- **Network segmentation** — contain the blast radius when something does get exploited
- **Web Application Firewalls** — block anomalous request patterns before they reach the application layer
- **Aggressive patch deployment** — the moment a zero-day becomes an n-day, you have a fix available. Not deploying it fast just means becoming an easy n-day target with a published attack manual

In 2024 alone, 75 zero-day vulnerabilities were exploited in the wild [5]. Microsoft had 26, Google had 11, Ivanti had 7, Apple had 5 [5]. Every single one eventually became a patched CVE — and every organisation that delayed applying that patch kept the door open long after it needed to be closed.

The zero-day window ends when the patch ships. The n-day problem starts immediately after.

> End

## Sources
1. [What is a Zero Day Attack? — Fortinet](https://www.fortinet.com/resources/cyberglossary/zero-day-attack)
2. [Zero-day vulnerability — Wikipedia](https://en.wikipedia.org/wiki/Zero-day_vulnerability)
3. [One-day, n-day, and zero-day vulnerabilities explained — Field Effect](https://fieldeffect.com/blog/1-day-0-day-vulnerabilities-explained)
4. [The Zero Day Vulnerability Lifecycle & 5 Defensive Measures — Oligo Security](https://www.oligo.security/academy/the-zero-day-vulnerability-lifecycle-5-defensive-measures)
5. [Hello 0-Days, My Old Friend: A 2024 Zero-Day Exploitation Analysis — Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/2024-zero-day-trends)
6. [Zero-Day vs One-Day Attack: Key Differences Explained — Secure.com](https://www.secure.com/blog/infrastructure-security/zero-day-vs-one-day-attack)
7. [Stuxnet — Wikipedia](https://en.wikipedia.org/wiki/Stuxnet)
8. [Pegasus (spyware) — Wikipedia](https://en.wikipedia.org/wiki/Pegasus_(spyware))
9. [What is a zero-day exploit and why are they dangerous? — Proton VPN](https://protonvpn.com/blog/zero-day-exploit)
10. [Vulnerability Disclosure Policy — Google Project Zero](https://projectzero.google/vulnerability-disclosure-policy.html)