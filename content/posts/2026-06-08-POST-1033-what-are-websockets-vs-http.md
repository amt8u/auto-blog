+++
title       = "What Are WebSockets and How Do They Differ From HTTP?"
description = "WebSockets explained in plain terms — how the handshake works, why they beat polling for real-time apps, and yes, they really are a protocol (RFC 6455)."
date        = "2026-06-08T10:04:50+05:30"
slug          = "what-are-websockets-vs-http"
tags          = ["websockets", "http", "networking", "web-development"]
keywords      = ["what are websockets", "websocket vs http", "websocket protocol", "real-time communication", "RFC 6455"]
canonical     = "/posts/what-are-websockets-vs-http/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=80"
+++

I kept hearing "use WebSockets for real-time stuff" without anyone explaining what actually happens on the wire. So I went and read the RFC, poked at a few servers, and figured I'd write down what I found — including the part that confused me the most: whether WebSocket is a protocol of its own or just some clever trick on top of HTTP.

## So what is a WebSocket?

A **WebSocket is a persistent, full-duplex communication channel between a browser (or any client) and a server, opened over a single TCP connection** [1]. Full-duplex means both sides can send messages whenever they want — not just in response to a request. That's the part that breaks the usual mental model of the web.

Compare that to how you've probably been thinking about web traffic your whole career:

- Client sends a request.
- Server sends back a response.
- Connection (logically) closes or sits idle until the next request.

With WebSockets, once the connection is open, either side can push data at any moment — no request needed first. The server can message you the instant something happens, instead of waiting for you to ask "anything new?" [2].

## Are WebSockets a protocol? Yes — and it's a real standard

This is the bit I was genuinely unsure about. **WebSocket is not a JavaScript trick or a library feature — it's a standardized protocol, defined in RFC 6455 by the IETF in 2011** [1][3]. It has its own URI schemes too: `ws://` for plain WebSocket traffic (default port 80) and `wss://` for WebSocket over TLS (default port 443, the encrypted version you should actually use in production) [1].

In terms of where it sits in the stack: **both HTTP and WebSocket are application-layer (Layer 7) protocols that run on top of TCP (Layer 4)** [4]. So WebSocket isn't replacing TCP or competing with HTTP at a fundamental level — it's a sibling protocol to HTTP that happens to *start* its life by speaking HTTP.

> "The WebSocket Protocol enables two-way communication between a client running untrusted code in a controlled environment to a remote host that has opted-in to communications from that code." — RFC 6455 [3]

That "opted-in" phrasing matters — a server has to explicitly agree to switch protocols. Which brings us to the handshake.

## The handshake: how an HTTP request turns into a WebSocket

This is the cleverest part of the design, and honestly the reason WebSockets work as well as they do across the existing internet. Instead of inventing a brand-new connection mechanism that firewalls, proxies and corporate networks would all need to learn about, **WebSocket bootstraps itself through an ordinary HTTP request using the `Upgrade` header** [5][6].

Here's the actual sequence:

1. The client sends a normal-looking HTTP `GET` request, but with extra headers: `Upgrade: websocket`, `Connection: Upgrade`, and a randomly generated `Sec-WebSocket-Key` [1][6].
2. The server, if it supports WebSockets, responds with `HTTP/1.1 101 Switching Protocols`, echoing `Upgrade: websocket` and `Connection: Upgrade`, plus a `Sec-WebSocket-Accept` header [6].
3. That `Sec-WebSocket-Accept` value isn't arbitrary — the server takes the client's key, appends a fixed "magic" GUID (`258EAFA5-E914-47DA-95CA-C5AB0DC85B11`), runs it through SHA-1, and base64-encodes the result. This proves the server actually understood the WebSocket request rather than some random server just echoing headers back [6].
4. From this point on, the same underlying TCP socket stops speaking HTTP entirely and starts exchanging WebSocket **frames** — a lightweight binary framing format with as little as 2-6 bytes of overhead per message, supporting text frames, binary frames, and control frames (ping/pong/close) [2][1].

![websocket handshake](/images/posts/what-are-websockets-vs-http/websocket-handshake.svg)

Once that handshake is done, the connection is no longer "an HTTP connection that happens to do something special." It has fully become a WebSocket connection — same TCP pipe, completely different protocol running over it.

## WebSocket vs HTTP — the actual differences

Here's where it gets interesting, because the two protocols solve fundamentally different problems even though one bootstraps the other.

| Aspect | HTTP | WebSocket |
|---|---|---|
| Communication model | Request–response, client always initiates [2] | Full-duplex — either side sends anytime [1][2] |
| Connection lifetime | Short-lived; opened and closed per exchange (or pooled/reused) [2] | Persistent; stays open after the handshake until explicitly closed [2] |
| Per-message overhead | Hundreds of bytes of headers on every request/response [2] | As little as 2–6 bytes of frame overhead [2] |
| Statefulness | Stateless by design — each request stands alone | Stateful — the server keeps the connection (and often session context) alive [4] |
| Server-initiated push | Not natively possible; client must ask | Native — server can push the moment data is ready [2] |
| URI scheme | `http://`, `https://` | `ws://`, `wss://` [1] |
| Underlying transport | TCP (Layer 4), itself Layer 7 | Also TCP (Layer 4), also Layer 7 [4] |

**The big one is "who's allowed to start talking."** In HTTP, the server can never just message you — it has to wait to be asked. That's why apps that need live updates over plain HTTP resort to workarounds like polling (asking "anything new?" every few seconds) or long-polling (asking and having the server hold the request open until something happens). Both work, but **they waste bandwidth on empty responses and add latency proportional to your polling interval** [7].

WebSockets remove that constraint entirely. Once the handshake completes, the server can shove a message down the pipe the instant something happens — no polling, no waiting, no wasted "nothing new" round trips [7].

## When you'd actually reach for WebSockets

I'll be honest — for most CRUD apps and dashboards that refresh every few seconds, plain HTTP with polling or long-polling is simpler to run and good enough [7]. WebSockets earn their complexity when the *frequency* and *direction* of updates make request-response awkward:

- **Chat applications** — messages from any participant need to reach everyone else in near real time, and the standard approach here is WebSockets for good reason [7].
- **Multiplayer gaming** — game state often needs to sync 20–60 times per second; nothing else gets close to the per-frame efficiency of a persistent socket [7].
- **Collaborative editing** — every keystroke needs to propagate with minimal delay (think Google Docs-style tools).
- **Financial trading / live price feeds** — sub-100ms updates with the ability to submit orders on the same connection [7].
- **Live notifications and dashboards** that genuinely need second-by-second pushes rather than periodic refreshes.

If your "real-time" requirement is actually "update every 30 seconds is fine," don't reach for WebSockets just because it sounds modern. **The trade-off is real** — WebSockets need you to manage connection state, reconnection logic, and scaling thousands of long-lived sockets, which is a meaningfully different operational burden than stateless HTTP servers behind a load balancer [7].

## A quick note on encryption

Just like HTTP has HTTPS, **WebSocket has `wss://`, which runs the WebSocket protocol over TLS** [1]. There's no good reason to ship `ws://` in production — use `wss://` the same way you'd refuse to ship a login form over plain `http://`. The handshake still starts as an HTTPS request before upgrading, so you get the same certificate-based trust model you're already used to.

## Wrapping up

WebSocket isn't a hack bolted onto HTTP — it's its own IETF-standardized protocol (RFC 6455) that simply *uses* HTTP's `Upgrade` mechanism as a polite way to ask "can we switch to something better suited for this conversation?" [1][3][6]. Once the server says yes with a `101 Switching Protocols`, you're no longer in HTTP-land at all — you're exchanging lightweight frames over a connection that stays open and lets both sides talk whenever they need to [6][2].

Whether you actually need that is a different question than whether it sounds cool. For most things, you don't. For chat, games, and live collaborative tools, you very much do.

## Sources
1. [WebSocket Protocol: RFC 6455 Handshake, Frames & More — WebSocket.org](https://websocket.org/guides/websocket-protocol/)
2. [WebSockets vs HTTP: Key Differences Explained — Postman Blog](https://blog.postman.com/websockets-vs-http-key-differences-explained/)
3. [RFC 6455 — The WebSocket Protocol (RFC Editor)](https://www.rfc-editor.org/rfc/rfc6455.html)
4. [What is a WebSocket? — IP With Ease](https://ipwithease.com/what-is-a-websocket/)
5. [Protocol upgrade mechanism — HTTP — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Protocol_upgrade_mechanism)
6. [Writing WebSocket servers — Web APIs — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers)
7. [Long Polling vs WebSockets: Choosing the Right Transport for Real-Time Feeds — GetStream](https://getstream.io/blog/long-polling-vs-websockets/)