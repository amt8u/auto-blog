+++
title       = "UUID vs Sequential IDs: What, Why, and Which to Pick"
description = "UUIDs are 128-bit identifiers that solve real problems sequential IDs can't — distributed systems, security, and scale. Here's what you actually need to know."
date        = "2026-06-04T22:06:34+05:30"
slug        = "uuid-vs-sequential-ids-explained"
tags        = ["database", "uuid", "backend", "security", "distributed-systems"]
keywords    = ["UUID", "universally unique identifier", "UUID vs sequential ID", "UUIDv7", "database primary key", "IDOR prevention"]
canonical   = "/posts/uuid-vs-sequential-ids-explained/"
+++

You expose an API endpoint like `/api/orders/1042`. That integer tells anyone listening — a competitor, an attacker, a curious user — exactly how many orders you have. Change the number to 1041, you get the previous order. Change it to 1, you get the very first one. No auth bypass needed. The ID itself is the information leak.

That's the sequential ID problem in one paragraph. UUID exists to fix it — and a few other things that matter at scale.

## What Exactly is a UUID?

**UUID** stands for Universally Unique Identifier. It's a 128-bit number, represented as 32 hexadecimal characters split into five groups with hyphens [1]:

```
550e8400-e29b-41d4-a716-446655440000
```

The format is always `8-4-4-4-12` — that's the count of hex characters per group, 36 total including the four hyphens [2]. The 13th character encodes the version. The 17th character encodes the variant. So that UUID above — third group starts with `4`, meaning version 4 [3].

UUIDs need no central authority to generate. No database autoincrement sequence. No cross-server coordination. Any system, anywhere, can generate a UUID and be virtually certain nobody else generated the same one [1].

## UUID Versions — They're Not All the Same

Most articles list the versions without explaining why it actually matters for your database. It does.

| Version | How it's generated | Sortable? | Privacy |
|---|---|---|---|
| v1 | Timestamp + MAC address | ✅ Yes | ❌ Leaks MAC address |
| v3 | MD5 hash of namespace + name | ✅ Deterministic | N/A |
| v4 | Fully random (122 bits) | ❌ No | ✅ Good |
| v5 | SHA-1 hash of namespace + name | ✅ Deterministic | N/A |
| v7 | Unix timestamp + random bits | ✅ Yes | ✅ Good |

**v4 is what most people use today.** Random, simple, no privacy concerns. But it has a significant database performance problem that I'll get to [3].

**v7 is what you should be using for new projects.** Introduced in RFC 9562 (published May 2024), v7 combines a 48-bit Unix millisecond timestamp with 74 random bits [2]. You get time-ordering without leaking your MAC address.

![uuid format breakdown](/images/posts/uuid-vs-sequential-ids-explained/uuid-format-breakdown.svg)

## The Collision Question

"What if two systems generate the same UUID?"

Version 4 UUIDs have 122 bits of randomness. Total possible values: 2¹²⁸ ≈ 3.4×10³⁸. To produce a 50% chance of even one collision, you'd need to generate **2.71 quintillion** v4 UUIDs [4]. Generating 1 trillion UUIDs gives a collision probability of roughly 10⁻¹⁵ [4]. That's a one in a quadrillion chance.

You're not worrying about this.

## The Real Problem with Sequential IDs

Sequential IDs — `SERIAL` or `AUTO_INCREMENT` — are simple and fast. For a small app on a single server, they're perfectly fine. The problems show up in two specific areas.

### Security: Enumeration and IDOR

Predictable IDs make **Insecure Direct Object Reference (IDOR)** attacks trivially easy [5]. IDOR is in the OWASP Top 10 — it's one of the most commonly exploited vulnerability classes for a reason [6].

With sequential IDs, if I know my user ID is 4821, I can try 4820, 4819, 4818... and access other users' data if your authorization checks are weak or missing at all. With UUIDs, guessing `a47c3f2e-91bb-4d2e-b3f0-c6e88d3f0a1c` next is computationally infeasible.

I want to be direct about something here: **UUIDs are not a substitute for proper authorization checks.** If your app has IDOR vulnerabilities, fixing them at the authorization layer is the primary fix. UUIDs just raise the floor significantly [5].

Sequential IDs also leak business intelligence you probably don't want leaking. A competitor scraping `/api/invoices/1` in January and `/api/invoices/8500` in December now knows your invoice volume for the year. That's a real thing that happens.

### Distributed Systems: The Single-Node Problem

**Sequential IDs require centralized generation.** Reliably autoincrementing an integer works on one node at a time [7].

The moment you have multiple database replicas writing simultaneously, data sharding across regions, microservices generating records independently, or offline-capable mobile clients — sequential IDs become a coordination nightmare. Two nodes generating the next integer will collide without a central coordinator.

UUIDs need no coordinator. Each service, each region, each device can generate IDs independently and merge data later without conflicts [1]. That's architecturally significant.

## Where UUID Actually Falls Short

UUIDs are not strictly better in every situation. Let me be honest about the trade-offs.

- **Storage cost** — 16 bytes per UUID vs 4–8 bytes for an integer. On a table with hundreds of millions of rows and multiple foreign key references, this adds up [7].
- **Human-readability** — `42` is easier to say on a support call than `550e8400-e29b-41d4-a716-446655440000`. Sequential IDs win here, always.
- **Index performance with v4** — this is the one that bites people in production.

When you use UUID v4 as a primary key, every insert lands at a **random position in the B-tree index**. The database has to constantly rebalance. Pages fragment. Cache locality suffers. On high write volumes with v4 UUIDs, index performance degrades noticeably compared to sequential integers [7][8].

## v7 Fixes the Performance Problem

This is why v7 matters. The millisecond timestamp prefix means v7 UUIDs are time-ordered. Inserts are mostly sequential — the index grows in one direction, fragmentation stays low, cache behavior is good [2][8].

If you're currently using v4 UUIDs as primary keys on high-write tables, migrating to v7 is worth considering. UUID libraries in most languages and platforms have added v7 support since RFC 9562 landed [2].

You get:

- The distributed generation advantage of UUIDs
- The security benefits (non-guessable)
- Index performance close to sequential integers
- No MAC address leakage (unlike v1)

## When Sequential IDs Are Still Fine

For a lot of applications, sequential IDs are the right call.

- Internal tools never exposed externally
- Reference/lookup tables (status codes, categories) where the ID is never user-facing
- Systems guaranteed to run on a single database node with no plans to shard

The mistake isn't using sequential IDs — it's using them everywhere by default without thinking about it. Exposing `/api/users/1` publicly in 2026 and not having thought about what that leaks is just careless.

> End

## Sources
1. [Universally unique identifier — Wikipedia](https://en.wikipedia.org/wiki/Universally_unique_identifier)
2. [RFC 9562: Universally Unique IDentifiers (UUIDs) — RFC Editor](https://www.rfc-editor.org/rfc/rfc9562.html)
3. [UUID Versions Explained — UUIDTools.com](https://www.uuidtools.com/uuid-versions-explained)
4. [UUID Collision Probability: Can Two UUIDs Ever Be the Same? — SecureBin](https://securebin.ai/blog/uuid-collision-probability/)
5. [Replace Sequential IDs With UUIDs to Prevent IDOR Vulnerabilities or Scraping — HackerNoon](https://hackernoon.com/replace-sequential-ids-in-your-models-with-uuids-to-prevent-idor-vulnerabilities-or-scraping)
6. [Insecure Direct Object Reference (IDOR) — OWASP Foundation](https://owasp.org/www-community/attacks/insecure_direct_object_reference)
7. [UUID vs. Sequential ID as Primary Key — Baeldung](https://www.baeldung.com/uuid-vs-sequential-id-as-primary-key)
8. [Goodbye to Sequential Integers, Hello UUIDv7! — Buildkite](https://buildkite.com/resources/blog/goodbye-integers-hello-uuids/)