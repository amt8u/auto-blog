+++
title       = "TLS Termination Explained (and Is SSL Really Transport Layer?)"
description = "What TLS termination actually does, why load balancers decrypt your traffic, and whether SSL/TLS genuinely belongs to the transport layer. A practical, no-fluff guide."
date        = "2026-06-07T16:16:06+05:30"
slug          = "tls-termination-explained"
tags          = ["networking", "security", "tls", "load-balancing"]
keywords      = ["TLS termination", "SSL termination", "is SSL transport layer", "TLS passthrough", "load balancer TLS", "mTLS"]
canonical     = "/posts/tls-termination-explained/"
feature_image = "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?auto=format&fit=crop&w=1600&q=80"
+++

Two questions get mashed together constantly: "what is TLS termination" and "is SSL a transport layer thing?" People assume the answer to the second is obviously yes — it's literally called *Transport* Layer Security, right? Well. That naming has fooled a lot of smart people, and the confusion bleeds straight into how folks reason about termination. So let me untangle both, because once the layer question clicks, termination stops feeling like magic.

## The short answer to the layer question

Here's the blunt version: **TLS does not run at the transport layer, even though its name says "Transport."** It runs *on top of* the transport layer.

When your browser talks to a server over HTTPS, the actual transport is still TCP. That's layer 4. TCP handles ports, sequencing, retransmission, the reliable byte-stream stuff. TLS sits above that, wraps the bytes in encryption, and hands the plaintext up to whatever application protocol you're using (HTTP, SMTP, IMAP, gRPC, whatever). The official spec, [RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446), describes TLS 1.3 as a protocol that "allows client/server applications to communicate over the Internet in a way that is designed to prevent eavesdropping, tampering, and message forgery" — and it explicitly assumes a reliable transport like TCP underneath it [1].

So why the "Transport" in the name? Honestly, it's mostly a historical accident of branding. The protocol began life as **SSL (Secure Sockets Layer)**, built by Netscape in the mid-90s. When the IETF took it over and standardized it in 1999, they renamed it Transport Layer Security — partly to avoid the Netscape trademark baggage, partly because it secures data *in transit* [2]. The name describes intent, not its position in the OSI stack.

### Where it actually fits in the OSI model

If you try to slot TLS neatly into the seven-layer OSI model, you'll struggle, and that's not your fault. As the [Wikipedia entry on TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security) and plenty of network engineers put it, TLS just doesn't fit cleanly [3]. The most common honest description:

- It runs **above** the transport layer (layer 4 / TCP).
- It sits **below** the application layer (layer 7 / HTTP).
- In OSI terms, the functions it performs — encryption, session establishment — map roughly onto the **presentation (6)** and **session (5)** layers.

In the TCP/IP model (the one that actually matches the real internet), there's no separate presentation or session layer, so people often lazily file TLS under "transport" or "application" depending on their mood. Neither is precisely right. The most defensible thing you can say: **TLS is a session/presentation-layer security protocol that depends on a transport-layer protocol to do its job** [4].

Why does this matter for termination? Because TLS being a distinct layer that wraps TCP is *exactly* what lets a load balancer peel it off, deal with it, and pass the inner traffic onward. If encryption were baked into TCP itself, you couldn't cleanly separate the two. The layering is the whole reason termination exists as a concept.

![tls layer stack](/images/posts/tls-termination-explained/tls-layer-stack.svg)

## So what is TLS termination?

**TLS termination is the point where the encrypted connection ends and the traffic gets decrypted.** That's it. The word "terminate" just means "this is where the TLS tunnel stops."

In a simple world, that point is your application server. Client opens an HTTPS connection straight to your app, the app holds the certificate and private key, it decrypts the request, processes it, encrypts the response. End to end, single hop.

But almost nobody runs it that way at scale. Instead, you put something in front — a load balancer, a reverse proxy like Nginx or HAProxy, an API gateway, a CDN edge node. That front device does the TLS handshake, decrypts the traffic, and forwards the now-plaintext request to your backend servers, usually over plain HTTP on a trusted internal network [5]. The "termination" has moved from your app to the edge. This is also called **SSL offloading**, because you're offloading the cryptographic work off your backends.

Here's a concrete picture. A user hits `https://yourshop.com`. The request lands on your load balancer. The load balancer:

1. Completes the TLS handshake with the browser.
2. Validates and presents the certificate.
3. Decrypts the incoming bytes into a normal HTTP request.
4. Forwards that request to one of your backend app servers (`http://10.0.1.42:8080`).
5. Takes the backend's plain HTTP response, re-encrypts it, sends it back to the browser.

The browser thinks it had a secure conversation with `yourshop.com` — and it did, all the way to the load balancer. Your backend never touched a single byte of encryption.

## Why bother terminating at the edge?

Why introduce this extra step at all? A few genuinely good reasons:

- **It saves your backends from crypto work.** TLS handshakes and bulk encryption cost CPU. Pushing all of it onto dedicated load balancers (often with hardware acceleration) frees your application servers to actually run application logic [6].
- **Certificate management gets sane.** Instead of copying certs and private keys to fifty app servers and renewing all of them, you manage one cert in one place. Tools like AWS Certificate Manager will even auto-renew and rotate without downtime [7].
- **You unlock layer-7 features.** Once the traffic is decrypted, the proxy can read it. That means path-based routing, header rewrites, sticky sessions, request-level metrics, response compression, caching, and Web Application Firewall (WAF) inspection. None of that is possible while the bytes are still encrypted [8].
- **Scaling is easier.** Spin up a new backend instance and it just needs to speak plain HTTP. No TLS config, no cert provisioning per node.

That last point about layer-7 features is the one people underrate. A load balancer cannot route based on the URL path — say, sending `/api/*` to one pool and `/images/*` to another — if it can't see the URL. And it can't see the URL while the request is encrypted. **Visibility requires decryption.** This single fact drives most architectural decisions around TLS.

## The three models: termination, passthrough, re-encryption

TLS termination isn't a single thing — it's one of three patterns, and picking the wrong one causes real pain. Here's how they stack up.

| Model | Where TLS decrypts | Backend hop | L7 features? | End-to-end encrypted? |
|---|---|---|---|---|
| **Termination (offloading)** | At the proxy | Plain HTTP | Yes | No |
| **Passthrough** | At the backend only | Still encrypted | No | Yes |
| **Re-encryption (bridging)** | At the proxy, then again | New TLS session | Yes | Yes |

### Termination / offloading

The default we just described. Decrypt at the edge, plain HTTP to the backend. Maximum features, simplest backends. The catch: traffic between your load balancer and your app servers travels **unencrypted**. On a locked-down private VPC that's often acceptable. On a shared or untrusted network, it's a liability — SSL offloading can leave that internal hop open to man-in-the-middle snooping if someone gets inside your network [8].

### Passthrough

The proxy doesn't decrypt anything. It forwards the encrypted stream byte-for-byte to the backend, which holds the certificate and terminates TLS itself. Clever proxies still route intelligently by peeking at the unencrypted **SNI** (Server Name Indication) field in the ClientHello — that tells them which hostname the client wants without decrypting the payload [9].

The upside is real security: encryption is unbroken from client all the way to the backend, decryption happens only at the destination. The downside is you lose *everything* at layer 7 — no path routing, no header manipulation, no WAF, no cookie-based sticky sessions. You're basically a dumb TCP pipe. Passthrough makes sense when backends already manage their own certs, or when compliance demands the proxy never sees plaintext.

### Re-encryption / TLS bridging

The "have your cake and eat it" option. The proxy terminates the client's TLS, decrypts, does whatever layer-7 magic it needs, then opens a **brand new TLS connection** to the backend and re-encrypts before forwarding [10]. Red Hat's OpenShift docs describe this "re-encrypt" route type exactly: TLS terminates at the router, then the router establishes fresh encryption to the pod [10].

You get inspection *and* an encrypted internal hop. The cost is double the crypto work and a bit more config (now you manage certs in two places). For regulated workloads — healthcare data under HIPAA, card data under PCI-DSS — this is frequently the right answer, because those frameworks expect encryption in transit across untrusted segments, not just at the front door [11].

![tls termination models](/images/posts/tls-termination-explained/tls-termination-models.svg)

## What actually happens when TLS "terminates"

To terminate TLS you have to complete the handshake, so it's worth knowing what that involves. People picture it as one magic step, but it's a negotiated dance between client and server. Here's the TLS 1.3 flow, roughly [1]:

1. **ClientHello** — the browser says hi, lists the cipher suites and TLS versions it supports, and (in 1.3) already throws in its key-share guess to save a round trip.
2. **ServerHello** — the server picks a cipher suite, sends its key share, and starts encrypting almost immediately.
3. **Certificate + verification** — the server proves its identity with its certificate; the client checks it against trusted Certificate Authorities.
4. **Finished** — both sides confirm they've derived the same session keys, and from here everything is encrypted with fast symmetric crypto.

TLS 1.3 is a big deal here because it slashed the handshake from two round trips down to one, and even supports **0-RTT** resumption for returning clients [1]. If you've ever wondered why modern HTTPS sites feel snappier than they did years ago, the leaner handshake is a chunk of the reason. There's a gorgeous byte-by-byte walkthrough at [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/) if you want to see every field on the wire [12].

Once the handshake finishes, TLS doesn't send raw bytes — it chops the conversation into **records**. Each record has a content type: handshake (22), application data (23), or alert (21) [3]. A neat privacy trick in TLS 1.3: the real content type gets hidden inside the encrypted payload, and the outer header always claims it's "application data." So a network observer can't even tell handshake messages apart from your actual traffic [3]. The thing doing termination has to understand all of this record machinery — which is precisely why it's non-trivial work you'd want to centralize.

## A word on SSL vs TLS, since the terms are a mess

You'll see "SSL termination" and "TLS termination" used interchangeably everywhere, including in AWS and Nginx docs. Technically that's wrong, and it's the same naming confusion from the top of this article.

**SSL is dead.** All versions of SSL are deprecated and insecure. The IETF officially killed SSL 3.0 in June 2015, largely thanks to the [POODLE attack](https://en.wikipedia.org/wiki/Transport_Layer_Security) discovered by Google researchers in 2014 — an exploit that let an attacker downgrade a connection to SSL 3.0 and decrypt session cookies one byte at a time [13]. TLS replaced it with stronger ciphers, better authentication, and fixes for exactly those padding and renegotiation holes [13].

So why does everyone still say "SSL"? Pure legacy. The term got burned into the industry's brain during the 90s and early 2000s, certificate vendors still sell "SSL certificates," and people search for "SSL" far more than "TLS" [14]. When someone says "SSL termination" in 2026, they almost certainly mean TLS termination — the protocol underneath is TLS 1.2 or 1.3. Don't let the vocabulary trip you up, but do make sure your actual config disables SSL and old TLS versions. The history of these versions, if you're curious, is laid out nicely by [The SSL Store](https://www.thesslstore.com/blog/ssl-and-tls-versions-celebrating-30-years-of-history/) [15].

## The security trade-off you can't ignore

Here's where I'll get opinionated. Plain TLS termination — decrypt at the edge, plaintext to the backend — is fine *until it isn't*. The risk is the internal hop. Anyone with a foothold inside your network, a misconfigured security group, or a compromised neighbouring service can potentially read traffic that you assumed was protected because the user saw a padlock.

For a lot of internal-only, well-segmented setups, that risk is acceptable and the simplicity wins. But the moment you're handling regulated data, rethink it:

- **HIPAA** expects electronic protected health information to stay encrypted across untrusted networks, not just on the public hop [11].
- **PCI-DSS** and similar frameworks push for strong encryption end to end for cardholder data [11].
- **Zero-trust architectures** assume the internal network is hostile by default, which rules out plaintext backend hops entirely.

That's where **mutual TLS (mTLS)** enters. Regular TLS authenticates only the server to the client. mTLS adds a second check: the client also presents a certificate, so both sides cryptographically prove who they are [16]. In a microservices mesh, mTLS between services means a rogue pod can't just start talking to your payment service — it doesn't have a valid cert. Your load balancer can terminate inbound mTLS from clients and separately establish mTLS to the backends [11]. Google Cloud, Istio, and most service meshes bake this in now [16].

The practical rule I'd give: **decide where your trust boundary is, then put your termination point at that boundary.** If the edge is your boundary, terminate there. If you don't trust your own network, re-encrypt or use mTLS so the protected zone extends all the way to the app.

## Putting it together

If you only remember a few things:

- **SSL/TLS isn't a transport-layer protocol** despite the name. It rides on top of TCP (the real transport) and behaves like a session/presentation layer wrapper. That layering is what makes termination possible at all.
- **TLS termination is just the spot where encryption ends and decryption happens** — usually pushed to a load balancer or proxy to save backend CPU, centralize certs, and unlock layer-7 routing and inspection.
- **There are three flavors:** terminate (plaintext backend), passthrough (encrypted backend, no L7), and re-encrypt (encrypted backend *with* L7). Pick based on whether you trust your internal network.
- **"SSL" is a dead protocol** but a live word. When people say SSL termination they mean TLS.

The next time someone confidently tells you SSL is "a transport layer thing," you can gently point out that the name is marketing, not architecture — and that understanding the difference is exactly what lets you reason clearly about where to terminate.

## Sources
1. [RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3](https://datatracker.ietf.org/doc/html/rfc8446)
2. [SSL Deprecation: Why TLS took over internet security — Sectigo](https://www.sectigo.com/resource-library/ssl-deprecation-understanding-the-evolution-of-security-protocols)
3. [Transport Layer Security — Wikipedia](https://en.wikipedia.org/wiki/Transport_Layer_Security)
4. [Transport Layer Security — which layer of OSI model? — Medium](https://medium.com/@kush123/transport-layer-security-which-layer-of-osi-model-3bd9546c67c5)
5. [What is SSL/TLS termination? — HAProxy](https://www.haproxy.com/glossary/what-is-ssl-tls-termination)
6. [New – TLS Termination for Network Load Balancers — AWS](https://aws.amazon.com/blogs/aws/new-tls-termination-for-network-load-balancers/)
7. [Understanding TLS Termination with Load Balancers in AWS — Cloudericks](https://cloudericks.com/blog/understanding-tls-termination-with-load-balancers-in-aws/)
8. [TLS Termination Models: Passthrough vs Termination vs Bridging — DEV Community](https://dev.to/sharonkynu/tls-termination-models-ssl-passthrough-vs-ssl-termination-offloading-vs-ssl-bridging-39ck)
9. [Understanding Nginx: TLS Termination vs. TLS Passthrough — Medium](https://medium.com/@navneetskahlon/understanding-nginx-tls-termination-vs-tls-passthrough-0654fd67880f)
10. [3 ways to encrypt communications with Red Hat OpenShift](https://www.redhat.com/en/blog/encryption-secure-routes-openshift)
11. [Is TLS Enough for HIPAA? — HIPAA Vault](https://www.hipaavault.com/resources/is-tls-enough-for-hipaa/)
12. [The Illustrated TLS 1.3 Connection: Every Byte Explained](https://tls13.xargs.org/)
13. [SSL vs TLS: What's the Difference — Authgear](https://www.authgear.com/post/ssl-vs-tls/)
14. [Is SSL Deprecated? Transition from SSL to TLS — SSL Dragon](https://www.ssldragon.com/blog/is-ssl-deprecated/)
15. [SSL and TLS Versions: Celebrating 30 Years of History — The SSL Store](https://www.thesslstore.com/blog/ssl-and-tls-versions-celebrating-30-years-of-history/)
16. [Mutual TLS overview — Google Cloud Load Balancing](https://docs.cloud.google.com/load-balancing/docs/mtls)