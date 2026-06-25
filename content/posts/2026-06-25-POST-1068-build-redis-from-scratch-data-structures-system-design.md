+++
title       = "Build Redis From Scratch: Data Structures & System Design"
description = "How Redis actually works under the hood — SDS strings, hash tables, skiplists, event loop, and the full system with code snippets and source links."
date        = "2026-06-25T11:33:38+05:30"
slug        = "build-redis-from-scratch-data-structures-system-design"
tags        = ["redis", "systems-design", "data-structures", "c-programming", "backend"]
keywords    = ["build redis from scratch", "redis internals", "redis data structures", "redis architecture", "redis source code"]
canonical   = "/posts/build-redis-from-scratch-data-structures-system-design/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200"
+++

Redis is one of those rare pieces of software where the source code is short enough to actually read and deep enough to teach you something new every time. I've spent a good amount of time going through the actual Redis source — and what strikes me every time is how deliberately every design choice was made. Nothing is accidental.

So let's actually design one from the ground up — not a toy, but an architecture that mirrors what Redis actually does. Data structures, event loop, protocol, expiry, persistence. All of it.

## The Big Picture First

Before a single line of C, it helps to understand what Redis *is*. Redis is a self-described "data structure store" — not a cache, not a database (well, it can be those too), but at its core, a server that lets you operate on named data structures over a network. It keeps everything in RAM and executes one command at a time on a **single thread**.

That last part always surprises people. A single thread. And yet Redis handles hundreds of thousands of operations per second. The trick is the event loop.

![redis architecture overview](/images/posts/build-redis-from-scratch-data-structures-system-design/redis-architecture-overview.svg)

## The Event Loop: One Thread, Many Connections

Redis wraps the OS-level I/O multiplexing APIs in a thin abstraction layer called `ae` (Async Events). At compile time it picks the best backend available:

```
Linux   → epoll
macOS   → kqueue
Others  → select (fallback)
```

The actual source is in [`src/ae.c`](https://github.com/redis/redis/blob/unstable/src/ae.c). The idea is simple: instead of spawning a thread per client, Redis registers all client sockets with `epoll_wait()` (or equivalent) and blocks until *something* happens. The kernel wakes Redis up, Redis reads the command, executes it, writes back a response — then polls again. No context switches, no locks, no condition variables.

The core loop in C looks roughly like this:

```c
void aeMain(aeEventLoop *eventLoop) {
    eventLoop->stop = 0;
    while (!eventLoop->stop) {
        aeProcessEvents(eventLoop,
            AE_ALL_EVENTS |
            AE_CALL_BEFORE_SLEEP |
            AE_CALL_AFTER_SLEEP);
    }
}
```

Every tick of that loop does three things:
1. Poll all registered file descriptors via epoll/kqueue
2. Fire I/O callbacks (read from client, write response back)
3. Fire time callbacks (key expiry cycles, background saves)

The reason this works at scale is that Redis commands execute in *microseconds*. The CPU never sits idle waiting for I/O — it's always either doing useful work or parked in the kernel waiting for the next event.

> Redis 6.0 introduced multi-threaded I/O for *reading and writing* to sockets, but actual command execution still happens on a single thread. The core invariant is preserved [6].

## RESP: The Protocol That's Almost Embarrassingly Simple

Every Redis client speaks [RESP — the Redis Serialization Protocol](https://github.com/redis/redis-specifications/blob/master/protocol/RESP3.md). It's text-based, line-oriented, and you can read a raw packet with netcat and understand it immediately. Here's what `SET foo bar` looks like on the wire:

```
*3\r\n
$3\r\n
SET\r\n
$3\r\n
foo\r\n
$3\r\n
bar\r\n
```

That's a RESP array (`*3`) containing three bulk strings (`$3`). The single-character type prefix tells you what follows:

| Prefix | Type          | Example          |
|--------|---------------|------------------|
| `+`    | Simple string | `+OK\r\n`        |
| `-`    | Error         | `-ERR unknown\r\n` |
| `:`    | Integer       | `:42\r\n`        |
| `$`    | Bulk string   | `$3\r\nfoo\r\n`  |
| `*`    | Array         | `*2\r\n...`      |

Parsing this in C is maybe 60 lines. The simplicity is intentional — RESP makes it trivial to debug with raw netcat, easy to implement clients in any language, and parseable with zero external dependencies.

## SDS: Because C Strings Are a Trap

Here's the first real design decision: Redis doesn't use C's native null-terminated `char*` strings. It uses **SDS — Simple Dynamic Strings**, defined in [`src/sds.h`](https://github.com/redis/redis/blob/unstable/src/sds.h).

Why? Because C strings are terrible for a database:
- `strlen()` is O(n) — unacceptable when called millions of times per second
- They can't store binary data (a null byte terminates the string)
- Appending requires a manual `realloc` on every call

SDS solves all three. Here's the core structure (simplified to the most common variant):

```c
struct __attribute__ ((__packed__)) sdshdr64 {
    uint64_t len;        /* used bytes in buf */
    uint64_t alloc;      /* total allocated, excluding header */
    unsigned char flags; /* which sdshdr type? */
    char buf[];          /* actual string bytes */
};
```

The trick: the `buf` pointer is what gets returned to calling code, making it **compatible with any standard C string function**. But because the header is stored just *before* `buf`, you subtract `sizeof(struct sdshdr)` to get the length in O(1) [3].

The memory pre-allocation strategy prevents realloc churn:
- New length **< 1MB** → allocate 2× new length
- New length **≥ 1MB** → allocate new length + 1MB (linear growth)

And when you shrink a string, SDS doesn't immediately free the memory — the `alloc` field stays large, `len` drops, and a future append reuses the slack. Classic lazy shrinking.

There are actually *five* SDS header types (`sdshdr5` through `sdshdr64`) to minimise header overhead. A 10-character string doesn't need a 64-bit length field — it gets `sdshdr8` with a one-byte length counter.

## The Hash Table (dict.c): Two Tables and the Rehashing Trick

Redis's hash table is in [`src/dict.c`](https://github.com/redis/redis/blob/unstable/src/dict.c) and it's worth reading in full. The outer struct:

```c
typedef struct dict {
    dictType *type;
    dictEntry **ht_table[2];  /* TWO hash tables */
    long long ht_used[2];
    long rehashidx;           /* -1 = no rehash in progress */
    int16_t pauserehash;
} dict;
```

Notice the two hash tables. **That's the key to Redis's approach to resizing.**

**The problem with naive rehashing:** when a hash table grows past its load factor, you allocate a bigger table and migrate all keys. Migrating millions of keys is O(N) — that blocks the event loop for a noticeable pause. Unacceptable in a latency-sensitive system.

**The solution: incremental rehashing [2].** When resizing kicks in:

1. A second, larger table (`ht_table[1]`) is allocated
2. `rehashidx` is set to 0 (first bucket to migrate)
3. Every subsequent dict operation migrates a small batch of buckets from `ht_table[0]` to `ht_table[1]`, advancing `rehashidx`
4. Reads check *both* tables during the transition
5. New keys go into `ht_table[1]` only
6. When `ht_table[0]` is empty, swap and reset

The cost gets distributed across normal operations. Each command pays a tiny incremental tax instead of one enormous bill.

Collision resolution is **chaining** — each bucket holds a linked list of entries:

```c
typedef struct dictEntry {
    void *key;
    union {
        void *val;
        uint64_t u64;
        int64_t  s64;
        double   d;
    } v;
    struct dictEntry *next;   /* next in chain */
    void *metadata[];
} dictEntry;
```

The `union` for the value is a neat optimisation — small integers and doubles are stored directly in the entry struct without an extra heap allocation.

## The Object System: redisObject Wraps Everything

Every key and value in Redis is wrapped in a `redisObject` (typedefed `robj`). From [`src/server.h`](https://github.com/redis/redis/blob/unstable/src/server.h):

```c
typedef struct redisObject {
    unsigned type:4;       /* OBJ_STRING, OBJ_LIST, OBJ_SET, ... */
    unsigned encoding:4;   /* OBJ_ENCODING_HT, OBJ_ENCODING_SKIPLIST, ... */
    unsigned lru:LRU_BITS; /* LRU clock or LFU counter */
    int refcount;
    void *ptr;             /* actual data */
} robj;
```

Four bits for type, four bits for encoding — they fit in a single byte together. The `ptr` points to the actual data structure, but *which* structure depends on `encoding`, not `type`. This is how Redis achieves its dual-encoding magic:

| Type       | Small (listpack / intset)      | Large encoding            |
|------------|-------------------------------|---------------------------|
| String     | INT or EMBSTR (≤ 44 bytes)    | Raw SDS                   |
| List       | LISTPACK (≤ 128 elements)     | QUICKLIST                 |
| Hash       | LISTPACK (≤ 128 fields)       | HT (dict)                 |
| Set        | LISTPACK or INTSET            | HT (dict)                 |
| Sorted Set | LISTPACK (≤ 128 members)      | SKIPLIST + HT             |

A Redis hash with 50 small fields uses a flat listpack — no hash table at all, just a contiguous array. The moment you push past the threshold, Redis transparently converts it to a `dict`. The client never sees this transition [7].

The `refcount` enables **shared objects**. Redis preallocates integers 0–9999 as permanent shared `robj` instances. If a value is the integer `42`, multiple keys can point to the same object without duplicating memory.

## Lists: The Quicklist

Redis lists are a [quicklist](https://github.com/redis/redis/blob/unstable/src/quicklist.h) — a doubly-linked list where each *node* is a small listpack (compact array) of multiple elements.

```c
typedef struct quicklist {
    quicklistNode *head;
    quicklistNode *tail;
    unsigned long count;   /* total entries across all nodes */
    unsigned long len;     /* number of quicklistNode */
} quicklist;

typedef struct quicklistNode {
    struct quicklistNode *prev;
    struct quicklistNode *next;
    unsigned char *entry; /* listpack bytes */
    size_t sz;
    unsigned int count : 16;
    unsigned int encoding : 2; /* RAW=1, LZF=2 */
} quicklistNode;
```

Pure listpack: memory-efficient and cache-friendly but slow to grow — appending to a large listpack shifts data [9]. Pure linked list: O(1) head/tail ops but wastes memory on pointers. Quicklist gives you both.

Middle nodes can even be LZF-compressed, which is great for queue patterns where only head and tail are ever touched.

## Sorted Sets: Skiplist + Hash Table — Two Data Structures at Once

This is honestly my favourite design in all of Redis. Sorted sets need to support two wildly different access patterns simultaneously:

- "What is the score of member X?" → O(1) lookup by name
- "Get all members with scores between 10 and 50, in order" → O(log N) range scan

No single data structure handles both optimally. So Redis uses two — at the same time [5]:

- A **dict** (hash table) for O(1) member → score lookups
- A **skiplist** for O(log N) ordered range operations

The SDS string for each member is *shared* between both structures as a pointer — no duplication. The skiplist is defined in [`src/t_zset.c`](https://github.com/redis/redis/blob/unstable/src/t_zset.c):

```c
typedef struct zskiplistNode {
    sds ele;                       /* the member string */
    double score;
    struct zskiplistNode *backward;
    struct zskiplistLevel {
        struct zskiplistNode *forward;
        unsigned long span; /* nodes skipped to reach forward */
    } level[];                     /* variable-length */
} zskiplistNode;

typedef struct zskiplist {
    struct zskiplistNode *header, *tail;
    unsigned long length;
    int level;
} zskiplist;
```

The `span` field is a Redis-specific addition to the classic skip list algorithm — it counts how many nodes you skip when following a forward pointer at each level. This lets Redis calculate the *rank* of any element in O(log N) without a separate rank tree [4].

Level assignment is probabilistic: every new node gets level 1. With probability 0.25 it also gets level 2, with probability 0.25² it gets level 3, up to a cap of 64. This gives O(log N) expected search time without tree rotations or rebalancing logic.

## Key Expiry: Two Strategies, One Memory Leak Risk

When you run `SET foo bar EX 60`, Redis doesn't start a timer. It records the absolute UNIX expiry timestamp (in milliseconds) in a separate dict called `db->expires`. The key in `db->dict`, the expiry in `db->expires`. Two parallel dicts.

**Two strategies run together to clean up expired keys:**

### Lazy Expiry (Passive)

Every time a client reads a key, Redis checks `db->expires` first. If expired — delete it, return nil. Simple, cheap, correct. But here's the hole: if a key is *never accessed after it expires*, it stays in memory indefinitely. That's a real memory leak for set-and-forget patterns.

### Active Expiry (Background Sampling)

Redis runs an expiry cycle `hz` times per second (default: 10, meaning every 100ms). Each cycle [8]:

```c
/* Simplified from expire.c */
void activeExpireCycle(int type) {
    do {
        num     = ACTIVE_EXPIRE_CYCLE_LOOKUPS_PER_LOOP; /* 20 */
        expired = 0;

        while (num--) {
            de = dictGetRandomKey(db->expires);
            if (!de) break;
            if (activeExpireCycleTryExpire(db, de, now))
                expired++;
        }
        /* repeat if > 25% of sample was expired */
    } while (expired > ACTIVE_EXPIRE_CYCLE_LOOKUPS_PER_LOOP / 4);
}
```

Sample 20 random keys. Delete the expired ones. If more than 25% of the sample was stale, repeat — because a high stale ratio implies many more stale keys still lurk. This terminates quickly in healthy databases but adapts under expiry storms.

One important replication behaviour: **replicas do not independently delete expired keys**. They wait for `DEL` commands propagated from the primary. Since Redis 3.2, a replica refuses to serve an expired key to a client even before the `DEL` arrives — but the memory isn't freed until the primary says so.

## Persistence: Snapshots and the Write Log

Redis lives in RAM. Surviving a restart requires one (or both) of two mechanisms:

### RDB — Point-in-Time Snapshots

`BGSAVE` forks the process. The **child** writes a compact binary `.rdb` file of the entire dataset. The **parent** keeps serving requests. Copy-on-write semantics give the child a frozen view of memory — pages the parent modifies get duplicated by the kernel, not by Redis code.

Restart is fast: deserialise the RDB. Downside: anything written between the last snapshot and the crash is lost [1].

```c
/* From rdb.c — the high-level flow */
int rdbSaveBackground(char *filename, rdbSaveInfo *rsi) {
    if ((childpid = fork()) == 0) {
        /* Child process */
        rdbSave(filename, rsi);
        _exit(exitcode);
    }
    /* Parent continues serving clients */
}
```

### AOF — Append-Only File

Every write command is appended to a log file *after* it executes. On restart, replay the log from the beginning. Durability is configurable:

| `appendfsync` | Behaviour                  | Durability          |
|---------------|----------------------------|---------------------|
| `always`      | fsync after every command  | Highest (slowest)   |
| `everysec`    | fsync once per second      | ≤1s loss (default)  |
| `no`          | OS decides                 | Fastest (least safe)|

AOF files grow forever, so Redis rewrites them periodically — fork a child, write the minimal command set to represent current state, atomically replace the old file. Since Redis 7.0, the AOF is split into base + incremental files (multi-part AOF) for more efficient rewriting [10].

**Hybrid mode** (Redis 4.0+): the AOF file begins with an RDB snapshot, followed by incremental AOF commands. Fast restarts from the embedded RDB snapshot, minimal data loss from the AOF tail.

## Putting It All Together: The GET Command Walk-Through

When you send `GET foo` to Redis, here's the full chain from socket bytes to response:

1. `epoll_wait()` returns — the client fd has data
2. `readQueryFromClient()` reads bytes into `client->querybuf` (an SDS)
3. `processInputBuffer()` parses RESP → fills `client->argv[]`
4. `processCommand()` looks up `"GET"` in `server.commands` (a dict)
5. `getCommand()` calls `lookupKeyRead(db, key)` → probes `db->dict`
6. Checks `db->expires` for TTL — delete and return nil if expired
7. Dereferences `robj->ptr` depending on `robj->encoding` to get the value
8. Serialises result as a RESP bulk string into `client->buf`
9. `writeToClient()` flushes the buffer back over the socket

The entire round-trip for a cache hit on a simple string — microseconds. That's before any threading or cluster tricks.

## Where to Start If You're Building One

I'd sequence the implementation like this:

1. **RESP parser + TCP server** — accept raw connections, parse commands, respond `+OK`. Use `epoll` from day one, not threads per connection.
2. **SDS** — implement the header trick and pre-allocation before anything touches strings.
3. **dict with incremental rehashing** — hardest part. Budget time for it.
4. **redisObject wrapper** — type + encoding fields so you can swap internals transparently later.
5. **SET / GET / DEL / EXPIRE** — the core four on string keys.
6. **Lazy expiry** — add `db->expires` and check it on every read.
7. **Lists and sorted sets** — quicklist and skiplist come after the core is solid.
8. **RDB persistence** — `fork()` + binary serialisation. Use the real system call, not a thread.
9. **Active expiry cycle** — background sampling loop via `ae` time events.

The [Build Your Own Redis with C/C++](https://build-your-own.org/redis/) book is the most structured guide I've found for actually implementing this step by step. The real Redis source — specifically the annotated [`src/dict.c`](https://github.com/redis/redis/blob/unstable/src/dict.c), [`src/sds.c`](https://github.com/redis/redis/blob/unstable/src/sds.c), and [`src/t_zset.c`](https://github.com/redis/redis/blob/unstable/src/t_zset.c) — is the ground truth.

The real learning isn't in getting `SET`/`GET` to respond correctly. It's in making the hash table *not block* under a write storm during rehashing, and making expiry *not leak memory* for keys that are never accessed. Those edge cases are exactly where every design decision Redis made starts making sense.

> End

## Sources

1. [Redis Persistence | Docs](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
2. [Analyzing Redis Source Code: Hash Tables, Chained Hashing, and Incremental Rehashing](https://www.linjiangxiong.com/2024/09/11/analyzing-redis-source-code-hash/index.html)
3. [Redis SDS — String Internals | Docs](https://redis.io/docs/latest/operate/oss_and_stack/reference/internals/internals-sds/)
4. [Redis Sorted Sets — Under the Hood](https://jothipn.github.io/2023/04/07/redis-sorted-set.html)
5. [redis/src/t_zset.c at unstable · redis/redis](https://github.com/redis/redis/blob/unstable/src/t_zset.c)
6. [The Engineering Wisdom Behind Redis's Single-Threaded Design](https://riferrei.com/the-engineering-wisdom-behind-rediss-single-threaded-design/)
7. [Redis Deep Dive Part 2 — The Building Blocks](https://thuva4.com/blog/part-2-the-building-blocks/)
8. [How Redis Expires Keys — A Deep Dive into How TTL Works Internally](https://www.pankajtanwar.in/blog/how-redis-expires-keys-a-deep-dive-into-how-ttl-works-internally-in-redis)
9. [Redis Quicklist — From a More Civilized Age](https://matt.sh/redis-quicklist)
10. [Redis Persistence Explained: AOF & RDB](https://dev.to/leapcell/redis-persistence-explained-aof-rdb-1i23)
11. [GitHub — redis/redis (official source)](https://github.com/redis/redis)
12. [Build Your Own Redis with C/C++](https://build-your-own.org/redis/)
13. [GitHub — antirez/sds: Simple Dynamic Strings library for C](https://github.com/antirez/sds)
14. [redis/src/quicklist.h at unstable · redis/redis](https://github.com/redis/redis/blob/unstable/src/quicklist.h)
15. [RESP3 Protocol Specification](https://github.com/redis/redis-specifications/blob/master/protocol/RESP3.md)