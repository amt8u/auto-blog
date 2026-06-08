+++
title       = "Why Not Just Use One WebSocket Per Page Instead of HTTP?"
description = "WebSockets are stateful and persistent, so why don't we replace hundreds of HTTP calls with one socket per page load? Here's the honest trade-off."
date        = "2026-06-08T13:36:02+05:30"
slug          = "websocket-vs-http-one-socket-per-page"
tags          = ["websockets", "http", "web-development", "system-design"]
keywords      = ["websocket vs http", "stateful websocket", "why not use websocket for everything", "websocket scalability", "REST vs websocket", "http requests vs websocket connection"]
canonical     = "/posts/websocket-vs-http-one-socket-per-page/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=80"
feature_image = "/images/POST-1044-websocket-vs-http-one-socket-per-page.svg"
+++

I get why this question keeps coming up. A WebSocket stays open, remembers who you are, and lets the server push data to you without you asking for it again and again. So why are we still firing off a hundred separate HTTP requests for a single page load when we could just open one persistent pipe and be done with it? Honestly, the question sounds smarter than most people give it credit for — and the answer is not "because HTTP is better." It's a lot more nuanced than that.

## Wait, isn't a stateful connection obviously more efficient?

On paper, yes. Once a [WebSocket connection](https://blog.postman.com/how-do-websockets-work/) is established through that initial HTTP "upgrade" handshake, both the client and server can send data to each other at any time, with very little framing overhead per message [1]. No repeating headers, no cookies riding along on every request, no re-establishing who-you-are on every single exchange. After the handshake, WebSocket data frames carry minimal protocol overhead compared to HTTP, where every request and response drags along headers like cookies, user-agent strings, and cache-control directives [2].

So the instinct makes sense: **if the connection already knows who I am and stays open, why re-introduce myself a hundred times per page?**

Here's the catch though — the thing that makes WebSockets good at real-time communication (statefulness) is the *exact same thing* that makes them expensive to run at scale. It's not a free lunch. It's a trade you're making, and most of the time, for a regular web page, that trade doesn't pay off.

## The hidden cost of "the server remembers you"

When you make a regular HTTP request, [REST APIs are stateless — the server doesn't track client details between requests](https://ably.com/topic/websocket-vs-rest), which makes it trivial to add more servers and spread the load around [3]. Any server in your fleet can answer any request because nobody is "remembering" anything about you between calls.

A WebSocket flips that completely. The server has to keep track of every single connection — who's connected, what state they're in, what they've subscribed to — for as long as that socket lives. That's not free:

- Each open WebSocket connection eats up roughly **2–10 KB of memory** just sitting there idle, and that adds up fast once you're talking about hundreds of thousands of users [4].
- Every connection also claims a **file descriptor** on the server, and operating systems have hard limits on how many of those you can have open at once [4].
- The server burns CPU just keeping connections alive — sending heartbeats, handling reconnects, processing whatever trickles through [5].

Now multiply that by "one socket per page load." If your site gets a few thousand concurrent visitors, you've suddenly got a few thousand long-lived, memory-hungry, stateful connections that your servers have to babysit — for pages that, realistically, just needed to fetch some JSON and render it once.

### The load balancer headache nobody mentions

Here's where it gets genuinely annoying for backend teams. Because a WebSocket is stateful, the server holding that connection is the *only* server that knows what's going on with that client. That means **WebSocket connections require session affinity (aka "sticky sessions") in load-balanced environments** [4]. Once a client connects to server B, every future interaction for that client has to keep going to server B — your load balancer can't just shrug and route it wherever's free.

That sounds manageable until you actually run it in production:

- When server B crashes, **every single client pinned to it loses its session state at once** [6].
- Rebalancing load across your fleet becomes much harder because connections can't just be freely shuffled around [6].
- Rolling deployments turn into a disruptive event, since draining a server for an update means forcibly disconnecting every sticky client attached to it [6].

The "fix" for this is to externalize session state into something like Redis so any server can pick up any client [6] — which is absolutely doable, but notice what just happened: you went from "no shared state needed" (HTTP) to "now I need a distributed state store to make my stateful protocol behave statelessly." That's a lot of extra moving parts to build a page that, with HTTP, would've just worked out of the box.

![websocket vs http tradeoff](/images/posts/websocket-vs-http-one-socket-per-page/websocket-vs-http-tradeoff.svg)

## "But HTTP wastes so many connections!" — not really, anymore

This is the part of the argument that I think trips people up the most, because it's stuck in a 2009 understanding of HTTP. Yes, browsers historically capped you at **6 concurrent connections per domain** under HTTP/1.1 [9], and yes, that did mean a chatty page could feel like it was queuing requests behind each other.

But two things changed that picture a lot:

1. **HTTP/1.1 keep-alive.** The "Connection: keep-alive" mechanism lets the browser reuse the same TCP connection for multiple requests instead of opening a fresh one each time [8], which already cuts out a huge chunk of the "overhead" people imagine HTTP has.
2. **HTTP/2 multiplexing.** With HTTP/2, the browser opens a *single* TCP connection per domain and runs multiple request/response "streams" over it concurrently [9]. That essentially erases the old per-domain bottleneck — you get most of the efficiency people love about WebSockets (one connection, many exchanges) without giving up statelessness.

Here's a side-by-side that makes the real trade-offs a lot clearer:

| Aspect | HTTP/1.1 (keep-alive) | HTTP/2 | WebSocket |
|---|---|---|---|
| Connections per page | Up to 6 per domain [9] | 1 per domain (multiplexed) [9] | 1 (persistent) |
| Server has to "remember" you | No | No | Yes — for the connection's lifetime [3] |
| Can be cached by CDNs/proxies | Yes [12] | Yes [12] | No — there's nothing to cache, it's a live stream |
| Server can push without being asked | No (request must come first) | No | Yes, at any time [2] |
| Works behind strict corporate firewalls | Yes (port 443 is always open) | Yes | Often blocked or needs fallback [15] |
| Scaling model | Stateless — any server, anywhere | Stateless — any server, anywhere | Needs sticky sessions or shared state [4][6] |

Looking at that table, the question kind of answers itself: HTTP/2 already solved the "too many connections" problem **without** asking you to give up statelessness. You get to keep caching, easy horizontal scaling, and firewall-friendliness — and you only reach for a WebSocket when you need its one genuinely unique superpower: the server pushing data to you when *it* decides something happened, not when you ask.

## You'd lose caching — and that's a much bigger deal than it sounds

This is the one I think gets underrated the most. **Using WebSockets for everything means you can't cache anything**, and that quietly drives your server costs way up [3]. Think about what a normal page load actually involves — your CSS, your images, your API responses for things that rarely change, your user avatar, your product listings. A huge chunk of that is identical for thousands of users and barely changes minute to minute.

With plain HTTP, [CDNs and reverse proxies sit in front of your servers and cache all of that](https://www.imperva.com/learn/performance/cdn-caching/), serving repeat requests straight from the edge without your origin server breaking a sweat [12]. That's a structural advantage baked into the stateless request/response model — *because* nobody's remembering anything, any cache, anywhere, can serve the answer.

A WebSocket is a live, two-way stream. There's no "response" to cache — there's just an ongoing conversation that's unique to that one connection. The moment you push everything through sockets, you've thrown away one of the cheapest, most battle-tested performance tools the web has: the humble HTTP cache.

## Then there's the random corporate firewall that just says no

Ever built something that worked perfectly on your home Wi-Fi and then completely fell apart the moment someone tried it from their office network? WebSockets run into this constantly. **Most web proxies and restrictive corporate firewalls will straight-up block WebSocket connections**, often because they're configured to only allow plain HTTP traffic on ports 80 and 443 through a transparent proxy [15][16].

Even when the port is right, **the single most common cause of WebSocket failures in production is that reverse proxies need to be explicitly configured to forward the HTTP "Upgrade" handshake** that kicks off a WebSocket connection [15]. If that config is missing — and it very often is, because not every ops team thinks to add it — your socket just won't connect, and now you're stuck writing fallback logic (long-polling, retry loops, the works) just so your app degrades gracefully.

Plain HTTP doesn't have this problem. It *is* the thing every proxy, firewall, and corporate network on Earth is built to expect and allow. That's not a small advantage — that's "your app actually works for the accountant on the hotel Wi-Fi" levels of advantage.

## So how do the big real-time apps actually do it?

This is the part that I find genuinely instructive, because companies like Slack and Discord *do* lean heavily on persistent connections — but notice they don't replace HTTP with sockets. They run both, side by side, each doing what it's good at.

- **Discord's Gateway** is a persistent WebSocket connection that pushes real-time events — a channel got renamed, a role was created, someone went online. But [Discord is explicit that in most cases, regular operations on its resources should go through the regular HTTP API, not the Gateway](https://docs.discord.com/developers/events/gateway), because gateway connections are simply more complex to open, maintain, and recover from disconnects [13].
- **Slack's Socket Mode** is similar — apps use a WebSocket to *receive* live events, but [Slack explicitly recommends still using the standard Web API (plain HTTPS) to send responses back](https://docs.slack.dev/apis/events-api/comparing-http-socket-mode/) [14]. One channel for "tell me what just happened," another for "here's what I want to do about it."

Notice the pattern? **The persistent connection is reserved for the one thing HTTP genuinely can't do well: the server pushing data to you on its own schedule.** Everything else — logging in, fetching your message history, updating your profile, searching — still rides on plain old stateless HTTP requests, because that's the model that caches well, scales horizontally without drama, and survives a corporate firewall.

## So when *does* "one socket per page" actually make sense?

I don't want to make it sound like WebSockets are some kind of mistake — they're not. They're the right call when:

1. **The server needs to push data without being asked** — live chat, multiplayer game state, stock tickers, collaborative editing where every keystroke from one person needs to reach everyone else within milliseconds [3].
2. **Update frequency is high enough that polling would be wasteful** — if you'd otherwise be hammering an endpoint every second "just in case," a socket is clearly the more honest design.
3. **Latency actually matters to the experience** — a half-second delay in a typing indicator is fine; a half-second delay in a competitive multiplayer game is not.

But for a typical page load — fetching a product page, a dashboard, a list of orders, a user's profile — none of those conditions really apply. You're asking for something once, getting an answer, and moving on. That's *exactly* the shape HTTP was built for, and exactly the shape that benefits from caching, statelessness, and not needing your ops team to configure sticky sessions and shared Redis state just to keep things working.

## My honest take

If I had to boil this down: **the "stateful" part of WebSockets isn't a bonus feature you get for free — it's the bill you pay for the ability to receive pushes.** It's a great deal when you actually need pushes. It's a bad deal when you don't, because you end up carrying all the costs (memory per connection, sticky sessions, firewall fragility, zero caching) for a feature you're not using.

HTTP/2's multiplexing already gave us most of the "single efficient pipe" benefit people associate with sockets, minus the operational headache [9]. So the real answer to "why not one socket per page" isn't "because HTTP is good and sockets are bad" — it's that **the two protocols are optimized for opposite problems**, and reaching for the stateful one by default just swaps a problem you don't have (too many requests) for several you definitely will have (memory pressure, sticky sessions, cache invalidation, and a very confused ops engineer at 2 AM).

## Sources
1. [How Do WebSockets Work? — Postman Blog](https://blog.postman.com/how-do-websockets-work/)
2. [WebSocket vs HTTP: When to Use Each Protocol — WebSocket.org](https://websocket.org/comparisons/http/)
3. [WebSocket vs REST: Key differences and which to use — Ably](https://ably.com/topic/websocket-vs-rest)
4. [WebSocket Connection Limits: The Real Bottlenecks — WebSocket.org](https://websocket.org/guides/connection-limits/)
5. [WebSockets at Scale: Architecture for Millions of Connections — WebSocket.org](https://websocket.org/guides/websockets-at-scale/)
6. [How to scale WebSockets for high-concurrency systems — Ably](https://ably.com/topic/the-challenge-of-scaling-websockets)
7. [How to Scale WebSocket Connections — OneUptime](https://oneuptime.com/blog/post/2026-01-26-websocket-scaling/view)
8. [Connection management in HTTP/1.x — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Connection_management_in_HTTP_1.x)
9. [Chrome's 6 TCP connections limit — HTTP/1.1](https://medium.com/@hnasr/chromes-6-tcp-connections-limit-c199fe550af6)
10. [WebSocket Handshake: HTTP Upgrade at Protocol Level — WebSocket.org](https://websocket.org/reference/handshake/)
11. [RFC 6455 — The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
12. [Web (HTTP/S) Cache and Caching Proxy — Imperva CDN Guide](https://www.imperva.com/learn/performance/cdn-caching/)
13. [Gateway Documentation — Discord Developers](https://docs.discord.com/developers/events/gateway)
14. [Comparing HTTP & Socket Mode — Slack Developer Docs](https://docs.slack.dev/apis/events-api/comparing-http-socket-mode/)
15. [How to Fix 'Connection Refused' WebSocket Errors — OneUptime](https://oneuptime.com/blog/post/2026-01-24-websocket-connection-refused-errors/view)
16. [Getting through firewalls — RTC Quickstart Guide](https://rtcquickstart.org/guide/multi/optimal-connectivity-firewalls.html)