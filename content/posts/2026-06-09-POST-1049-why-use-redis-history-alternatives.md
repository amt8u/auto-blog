+++
title       = "Why Redis? History, Use Cases & Best Alternatives"
description = "What makes Redis so fast? From a 2009 Italian side project to industry standard — here's the real history, practical use cases, and honest alternatives in 2026."
date        = "2026-06-09T18:38:02+05:30"
slug          = "why-use-redis-history-alternatives"
tags          = ["redis", "databases", "caching", "backend", "system-design"]
keywords      = ["redis", "redis alternatives", "redis history", "in-memory database", "redis use cases", "valkey", "dragonfly", "memcached", "redis vs valkey"]
canonical     = "/posts/why-use-redis-history-alternatives/"
feature_image = "/images/posts/why-use-redis-history-alternatives/redis-cover.jpg"
+++

"Just cache it in Redis" — you've probably heard that in a code review, a system design interview, or a Stack Overflow comment. It's almost a reflex at this point. But why Redis specifically? Why not a regular database with a good index, or any other in-memory store? I dug into the history, the architecture, and the current landscape of alternatives, and the story is genuinely more interesting than the meme lets on.

## What Redis Actually Is

Let's clear something up first. **Redis is not just a cache.** That's the misconception that trips people up. Redis stands for **REmote DIctionary Server** [1], and it's an in-memory data structure store — meaning it holds data in RAM rather than on disk. That one decision explains most of what makes it fast.

But calling it a "key-value store" undersells it. Redis natively understands a rich set of data structures [1]:

- **Strings** — the basic type; also used as counters and binary blobs
- **Lists** — ordered, support duplicates; perfect for queues and activity feeds
- **Sets** — unique values with O(1) membership checks
- **Sorted Sets** — unique members with a numeric score for ordering; think real-time leaderboards
- **Hashes** — a mini hashmap within a key; store objects without serializing everything
- **Streams** — append-only event logs for processing
- **Bitmaps / HyperLogLogs** — space-efficient counting and probabilistic data
- **Geospatial indexes** — find nearby locations using coordinates

This is exactly why Redis dominates over Memcached for most modern use cases. Memcached is faster for raw string caching with very simple access patterns — and that's basically the only thing it does. The moment you need a sorted leaderboard, a pub/sub channel, or a rate-limiting counter, Memcached can't help you.

## The Origin Story

This is the part I wasn't expecting to be genuinely good.

Salvatore Sanfilippo — known online as *antirez* — is a Sicilian programmer who, in 2007, was building a real-time web analytics tool called LLOOGG [2]. The idea was clever: let website owners see their visitors' behaviour live, including which pages they visited and in what sequence. For context, **Google Analytics didn't ship real-time tracking until 2011**, so antirez was legitimately ahead of the curve [3].

The problem? MySQL couldn't handle it. Every page view needed to be written and queried quickly enough to display live data. Under real traffic, MySQL's disk I/O became the bottleneck. Sanfilippo's insight was to stop fighting disk altogether — he wrote a quick prototype in Tcl called LMDB (LLOOGG Memory Database) just to test the hypothesis [2]. It worked. So he rewrote it properly, in C.

That prototype became Redis. The first public release went out on **April 10, 2009** [1]. His friend David Welton posted it on Hacker News. The initial response was mostly silence — except for Ezra Zygmuntowicz, a well-known Ruby on Rails developer, who immediately saw what antirez had built and helped spread the word [2].

From there it moved fast. Here's the rough timeline:

1. **2010** — VMware hired Sanfilippo to work on Redis full-time [1]
2. **2012** — GitHub adopted it for activity feeds; Twitter used it for trending topics and timeline fanout [3]
3. **2013** — Pivotal took over sponsorship when VMware restructured
4. **2015** — Redis Labs (now Redis Inc.) became the primary commercial steward
5. **2020** — antirez stepped back from active development

And LLOOGG, the analytics tool that sparked everything? It ran on Redis until it was shut down in 2014 — handling over **two billion page views**, running at 350–400 commands per second, on a virtual machine that cost $150 a month [2]. A side project built to fix one developer's database problem ended up powering one of the most widely deployed infrastructure components on the planet.

## Why It's So Fast

Three architectural decisions make Redis what it is.

### Everything lives in RAM

This is obvious once you say it out loud, but it's worth stating clearly. Accessing RAM is **roughly 100,000x faster than a spinning disk and about 10x faster than an SSD for random reads** [4]. Disk-based databases manage buffer pools, page caches, and I/O queues. Redis skips all of that. You ask for a key, it's already in memory, done.

### Single-threaded event loop

This surprises people. Doesn't single-threaded mean slower? Not for Redis — because Redis isn't CPU-bound, it's I/O-bound. The single-threaded model eliminates **lock contention entirely**: no mutexes, no race conditions, no synchronization overhead between threads. Commands execute atomically and sequentially [4]. The event loop handles thousands of concurrent connections via non-blocking I/O (using `epoll` internally), so the single thread never blocks waiting for a slow client [11]. Since Redis 6.0, optional threaded I/O can offload network reads and writes to multiple threads — but the command execution itself stays single-threaded. It's a cleaner design than it looks.

### Efficient protocol and data structures

The [RESP (Redis Serialization Protocol)](https://redis.io/docs/latest/develop/data-types/sorted-sets/) is minimal and fast to parse. No SQL planner, no JOIN resolution, no optimizer overhead. And the data structures aren't generic implementations — sorted sets, for example, are implemented using a skip list + hash table combination simultaneously, giving O(log N) inserts with O(1) score lookups [5].

The result: a standard Redis instance handles **over 100,000 operations per second** with median latency around **0.167 milliseconds** for GET/SET operations [4]. With pipelining — batching multiple commands into one network round trip — you can push past a million ops/sec on the same hardware.

![redis caching flow](/images/posts/why-use-redis-history-alternatives/redis-caching-flow.svg)

## What People Actually Use Redis For

### Caching (the obvious one)

You've got a Postgres query that takes 180ms on every request. You cache the result in Redis with a 60-second TTL. Now 95% of reads hit RAM and return in under 1ms. This is the dominant use case — and the reason Redis is effectively default infrastructure at any company with real traffic [11].

GitHub used this for their activity feeds early on. Instead of reconstructing a user's timeline from database joins on every page load, they stored pre-computed timelines in Redis and updated them on write events [3].

### Session management

Think about what a session holds: user ID, auth token, maybe a cart ID. It's small, it's read on almost every authenticated request, and it needs to be fast. Redis fits perfectly — you set a key with a TTL and it auto-expires when the session should end. No cron job to clean up stale sessions, no garbage in your main database. Instagram stored hundreds of millions of these pairs in Redis at their scale [3].

### Rate limiting

"How many API calls has this IP made in the last 60 seconds?" Redis answers this with a single atomic `INCR` + `EXPIRE`. No transactions, no locking, no race conditions. Twitter used this pattern to enforce API rate limits across their entire platform [3]. It's probably the most elegant implementation of a leaky bucket pattern I've seen — and it's three lines of code.

### Real-time leaderboards

This is where [sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/) earn their keep. `ZADD leaderboard 9500 "player:88"` adds a score. `ZRANGE leaderboard 0 9 WITHSCORES REV` returns the top 10 instantly, no re-sorting needed, O(log N) inserts [5]. This is how mobile games handle millions of concurrent score updates without choking a relational database. It just works.

### Pub/Sub messaging

Redis has a built-in [publish/subscribe messaging system](https://www.geeksforgeeks.org/system-design/redis-publish-subscribe/) — publishers send to named channels, subscribers receive in real time [9]. It's not meant to replace Kafka for durable, replayed event streams (Redis Pub/Sub doesn't persist messages), but for lightweight real-time notifications — "new chat message", "price update", "follow event" — it works beautifully and adds zero infrastructure overhead.

### Vector search and AI workloads

More recently, Redis has leaned hard into AI use cases. Redis can store vector embeddings alongside regular data, making it useful for [semantic caching of LLM responses](https://redis.io/blog/in-memory-databases-the-foundation-of-real-time-ai-and-analytics/) and retrieval-augmented generation (RAG) pipelines [4]. If you've been building anything with LangChain, LangGraph, or mem0, you've likely already seen Redis pop up as a memory backend. The new Vector Sets type in Redis 8.0 was written by antirez himself specifically for this use case [13].

## The License Drama (It Actually Matters)

This part is relevant if you're making an architecture decision today. Honestly, this got messy.

In **March 2024**, Redis Inc. changed the project's license from the permissive **BSD 3-Clause** to a dual **RSALv2 / SSPLv1** model [6]. Neither is OSI-approved open source. The SSPLv1 was originally created by MongoDB to target cloud providers — it essentially says: if you offer this as a managed service, you must also open-source your entire platform.

The target was obvious. AWS ElastiCache was generating hundreds of millions in revenue from Redis while Redis Inc. struggled with a ~1% conversion rate from free to paid users [6]. The frustration is completely understandable. The execution was a disaster.

The community backlash was immediate. Linux distributions (openSUSE, Fedora) began dropping Redis from their repos. Within weeks, former Redis maintainers forked the last BSD-licensed version and launched **Valkey** under the Linux Foundation in April 2024, backed by AWS, Google Cloud, Oracle, Alibaba, and Ericsson [7].

Then antirez himself — who had stepped back from the project in 2020 — rejoined Redis Inc. in November 2024. He pushed hard for a course correction. On May 1, 2025, Redis 8.0 launched under a **tri-license: RSALv2, SSPLv1, or AGPLv3** [13]. The AGPLv3 is OSI-approved open source — a genuine step back toward the community. [Antirez wrote about it openly](https://antirez.com/news/151): "I'm happy that Redis is open source software again."

Did the reversal fix the damage? Not really. Valkey had already achieved critical mass by then [14].

## The Alternatives

### Valkey

The most significant fork in recent open-source history. Valkey is Redis 7.2.4 under the Linux Foundation — fully protocol-compatible, drop-in replacement for almost every use case [7]. AWS migrated ElastiCache to it. [Google Cloud Memorystore supports it](https://aws.amazon.com/elasticache/what-is-valkey/). Aiven migrated 15,000 servers between May and August 2024.

Valkey 8.1 reportedly runs ~8% more ops/sec than Redis OSS, cuts P99 latency by 22%, and uses 20% less memory [7]. For most teams, this is the safest migration path — change the package name, swap the image, done.

### Dragonfly

A ground-up rewrite in C++, not a Redis fork. Dragonfly uses modern concurrency primitives — fibers, SIMD, shared-nothing architecture — to utilise all CPU cores efficiently [8]. The claimed throughput is 25x better than Redis on the same hardware, with meaningfully lower memory footprint per dataset.

The caveat: it's ~95-98% Redis-compatible. There are edge-case gaps in administrative commands [8]. For new projects with extreme throughput requirements, it's worth a benchmark run. For migrating existing setups, test your specific command usage before committing.

### KeyDB

Multi-threaded Redis. Same protocol, same commands, but it runs on all your cores. Acquired by Snap, which brought proper engineering resources to it [8]. The FLASH feature (tiered storage to SSD) is genuinely interesting for datasets that don't fully fit in RAM. If multi-threading on familiar Redis semantics is what you want, KeyDB is a proven option.

### Memcached

The elder statesman. Memcached predates Redis and is still genuinely fast for pure string caching with minimal operational overhead [10]. No persistence, no sorted sets, no Lua scripting, no pub/sub — just fast key-value storage. If all you need is "cache this database result for 60 seconds" and nothing more, Memcached's simplicity is a feature. But for any use case beyond basic string caching, Redis (or Valkey) gives you substantially more at similar latency.

| | Redis 8.0 | Valkey 8.1 | Dragonfly | KeyDB | Memcached |
|---|---|---|---|---|---|
| **License** | RSALv2/SSPL/AGPL | BSD 3-Clause | BSL 1.1 | BSD 3-Clause | BSD |
| **Persistence** | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Sorted Sets** | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Pub/Sub** | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Multi-threaded cmd exec** | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Redis protocol compat** | Native | Native | ~95–98% | Native | ✗ |
| **Cloud managed** | Redis Cloud | AWS / GCP / Aiven | Self-hosted mostly | Self-hosted | AWS / GCP |

## Which One Should You Pick?

Not a single answer, but some honest shortcuts:

- **Already on Redis, it's working** — upgrading to Redis 8.0 under AGPLv3 is fine. The AGPLv3 only affects you if you're wrapping Redis in a managed service and selling it.
- **Starting fresh, AWS or GCP** — use Valkey via ElastiCache or Memorystore. Same protocol, cleaner licensing, 20% cheaper on AWS [7].
- **Extreme throughput requirements and new project** — benchmark Dragonfly seriously.
- **Simple caching only** — Memcached is not a wrong answer if you truly don't need the extras.
- **Need multi-threading on Redis protocol** — KeyDB.

The weird footnote to all of this: LLOOGG — the analytics tool that started everything — was shut down over a decade ago. The side project antirez built to fix one developer's MySQL performance problem now runs inside nearly every serious tech stack on the planet. He stepped away in 2020, came back in 2024, watched a fork become the default on major cloud providers inside twelve months, and then helped push Redis back toward open source.

You genuinely can't plan for that arc.

> End

## Sources
1. [Redis - Wikipedia](https://en.wikipedia.org/wiki/Redis)
2. [Story: Redis and its creator antirez — Brachiosoft Blog](https://blog.brachiosoft.com/en/posts/redis/)
3. [History of Redis: From Side Project to Industry Standard — OneUptime](https://oneuptime.com/blog/post/2026-03-31-redis-history-side-project-to-industry-standard/view)
4. [Complete Guide to Redis in 2026 — DragonflyDB](https://www.dragonflydb.io/guides/complete-guide-to-redis-architecture-use-cases-and-more)
5. [Redis sorted sets | Docs — redis.io](https://redis.io/docs/latest/develop/data-types/sorted-sets/)
6. [Redis tightens its license terms, pleasing no one — The Register](https://www.theregister.com/2024/03/22/redis_changes_license/)
7. [Valkey Turns One: How the Community Fork Left Redis in the Dust — Momento](https://www.gomomento.com/blog/valkey-turns-one-how-the-community-fork-left-redis-in-the-dust/)
8. [8 Best Redis Alternatives — DragonflyDB](https://www.dragonflydb.io/guides/best-redis-alternatives-top-oss-and-managed-solutions)
9. [Complete Guide to Redis Publish Subscribe — GeeksforGeeks](https://www.geeksforgeeks.org/system-design/redis-publish-subscribe/)
10. [The Good and the Bad of Redis In-Memory Database — AltexSoft](https://www.altexsoft.com/blog/redis-pros-and-cons/)
11. [What is Redis Explained? — IBM](https://www.ibm.com/think/topics/redis)
12. [Redis Switches to SSPLv1: Restrictive License Sparks Fork — InfoQ](https://www.infoq.com/news/2024/03/redis-license-open-source/)
13. [Redis is open source again — antirez.com](https://antirez.com/news/151)
14. [Redis Returns to Open Source under AGPL License: Is It Too Late? — InfoQ](https://www.infoq.com/news/2025/05/redis-agpl-license/)
15. [Redis is now available under the AGPLv3 open source license — redis.io](https://redis.io/blog/agplv3/)
16. [Understanding Redis Threading — DEV Community](https://dev.to/ricky512227/understanding-redis-threading-what-i-learned-the-hard-way-paf)