+++
title       = "HATEOAS: What It Is and Why Almost No One Uses It"
description = "HATEOAS is the H in REST that everyone skips. Here's what it actually is, why nobody implements it, and when your API earns the name 'REST'."
date        = "2026-07-05T19:47:46+05:30"
slug          = "hateoas-rest-api-why-nobody-implements-it"
tags          = ["rest", "api-design", "hateoas", "web-development"]
keywords      = ["HATEOAS", "REST API", "hypermedia", "Richardson Maturity Model", "what makes an API RESTful"]
canonical     = "/posts/hateoas-rest-api-why-nobody-implements-it/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=1600&auto=format&fit=crop"
+++

Everyone is building "REST APIs" nowadays. You have got endpoints, you return JSON, you use `GET` and `POST` and `DELETE`, you send back `404` when something is missing. Congratulations, you have a REST API. Right?

Well, according to the person who literally coined the term REST, probably not. And the piece you are missing is a scary-looking acronym called **HATEOAS** — the one part of REST that almost nobody implements and most people can't even spell. I have been writing APIs for more than 8 years and honestly, for the longest time I treated HATEOAS as academic trivia. So let me untangle it: what it is, why the industry collectively ignores it, and the more interesting question — when you actually earn the right to call your thing a REST API.

## What HATEOAS actually stands for

HATEOAS is **Hypermedia As The Engine Of Application State**. Ugly acronym, simple-ish idea.

The core claim is this: a client should be able to interact with your API using nothing but the links your server hands back in its responses. Each response doesn't just carry data — it carries the data *plus* links telling the client what it can do next [1]. The client shows up knowing one entry URL and a media type, and from there the server drives the whole conversation by offering choices.

Think about how you use a website. You don't memorize URLs. You land on a homepage, you see links and buttons, you click them, the next page shows you the next set of links. You never had to read documentation that said "to view your cart, issue a GET to `/cart/items?userId=...`". The page *told you* where to go. That's hypermedia as the engine of application state — the current page (state) is driven by the links (hypermedia) it contains [1].

HATEOAS says your JSON API should work the same way. A machine client, not a human, but same principle: **the server tells the client what's possible next, the client doesn't hardcode it.**

Here's what a plain response looks like versus a HATEOAS one.

Plain, the way 95% of us write it:

```json
{
  "id": 12,
  "status": "PENDING",
  "total": 4999
}
```

The same thing with hypermedia controls:

```json
{
  "id": 12,
  "status": "PENDING",
  "total": 4999,
  "_links": {
    "self":   { "href": "/orders/12" },
    "pay":    { "href": "/orders/12/payment", "method": "POST" },
    "cancel": { "href": "/orders/12/cancel",  "method": "POST" }
  }
}
```

See the difference? The second one is telling the client "hey, this order is pending, so you can either pay for it or cancel it." If the order were already shipped, the server just wouldn't include those links — no `cancel` link means you can't cancel, and the client doesn't need business logic to figure that out. That's the pitch. It's genuinely elegant.

## Where this idea comes from (and why it matters)

This isn't some blog-invented best practice. It comes straight from **Roy Fielding's 2000 doctoral dissertation**, the document that defined REST in the first place. REST has six constraints — client-server, stateless, cacheable, layered system, code-on-demand (optional), and the big one, **uniform interface** [5].

The uniform interface itself breaks into four sub-constraints: identification of resources (URIs), manipulation through representations, self-descriptive messages, and — you guessed it — **hypermedia as the engine of application state** [5]. So HATEOAS isn't a nice-to-have bolted onto REST. In Fielding's model it's one of the load-bearing walls.

And Fielding got tired enough of people ignoring it that in 2008 he wrote a famously grumpy blog post titled ["REST APIs must be hypertext-driven"](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven). The money quote:

> "If the engine of application state (and hence the API) is not being driven by hypertext, then it cannot be RESTful and cannot be a REST API." [2]

He goes further:

> "A REST API should be entered with no prior knowledge beyond the initial URI and set of standardized media types... From that point on, all application state transitions must be driven by client selection of server-provided choices that are present in the received representations." [2]

Read that carefully. By Fielding's own definition, the thing you built — the one where the client has a hardcoded list of endpoints copied from your Swagger docs — is **not a REST API**. It might be a perfectly good HTTP API. It's just not REST in the strict sense. This is the misconception at the heart of the whole topic: **"REST" as the industry uses it is not the REST Fielding defined.** The htmx folks have a whole [essay on how REST came to mean the opposite of REST](https://htmx.org/essays/how-did-rest-come-to-mean-the-opposite-of-rest/), and they are not wrong.

## The Richardson Maturity Model — a ladder for how RESTful you are

Before we bash HATEOAS, it helps to see where it sits. Leonard Richardson proposed a maturity model in 2008, later popularized by [Martin Fowler](https://martinfowler.com/articles/richardsonMaturityModel.html), that grades your API on three axes: URIs, HTTP verbs, and hypermedia controls [3][4]. It gives you four levels.

| Level | Name | What you use | Reality |
|-------|------|--------------|---------|
| 0 | The Swamp of POX | One URI, one verb (usually POST) | SOAP, XML-RPC. Tunneling everything through a single endpoint |
| 1 | Resources | Many URIs, still one verb | Each thing has its own address, but everything is POST |
| 2 | HTTP Verbs | URIs + proper GET/POST/PUT/DELETE + status codes | **This is where 90% of "REST APIs" actually live** |
| 3 | HATEOAS | Everything above + hypermedia links | The "pinnacle." Rarely reached |

Fowler is careful to say these levels are a nice way to think about the ingredients of REST, not a strict scoring you must max out [4]. But the picture is clear: what everybody calls "REST" is really **Level 2** — sensible URLs, correct verbs, meaningful status codes [3]. Level 3, the hypermedia layer, is the one that gets skipped.

![richardson maturity ladder](/images/posts/hateoas-rest-api-why-nobody-implements-it/richardson-maturity-ladder.svg)

## So why does almost nobody implement it?

This is the part I actually find interesting, because HATEOAS looks great on a slide and then quietly dies the moment you try to ship it. There are real reasons, not just laziness. Let me go through the honest ones.

### 1. The clients that would benefit don't exist

The whole promise of HATEOAS rests on a **generic client** — some smart consumer that shows up, reads links, and navigates your API without being pre-programmed for it. That client is basically mythical outside of the web browser [6].

In the real world your API is consumed by a React frontend, an iOS app, and three backend services — all of which were written by the same team, in the same sprint, tightly coupled to your specific API [6]. They are not generic. They already *know* your endpoints because your teammate wrote them last Tuesday. Handing a hardcoded React app a `_links.pay` field doesn't make it magically flexible; the developer still hardcodes `order._links.pay.href` instead of `/orders/${id}/payment`. You added ceremony, not freedom.

### 2. The promised benefit — "evolve your URLs freely" — mostly doesn't materialize

The headline sales pitch is: with HATEOAS you can move your endpoints around and clients just follow the new links, no coordination needed. Sounds beautiful.

In practice it falls apart. As Ben Morris [points out in his pragmatic-REST piece](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/), if you change your endpoints, you still don't get obedient clients following links to the new location — because real clients hardcoded the URLs anyway, or depend on the *link relation names* (`rel: "pay"`) which now become the contract you can't change [7]. You just moved the coupling from URLs to relation names. Congratulations. The decoupling was theoretical.

### 3. No standard format, and everyone does it differently

Say you buy the vision and want to add hypermedia. Cool — in what format? Here's the mess:

- **HAL** — simple, `_links` and `_embedded`, the most popular, created by Mike Kelly in 2011 [8].
- **Siren** — adds explicit `actions` describing methods and expected fields, good for workflows [8].
- **JSON:API** — its own whole spec with `links` and `relationships`, decent tooling [8].
- **JSON-LD / Hydra**, **Collection+JSON**, and a few others.

There is [no de facto winner](https://zuplo.com/learning-center/a-deep-dive-into-alternative-data-formats-for-apis-hal-siren-and-json-ld). Every one of these formats is somebody's opinion, and picking one means betting on tooling and hoping the next developer knows it [8]. Andreas Reiser argues in ["Why HATEOAS is useless"](https://medium.com/@andreasreiser94/why-hateoas-is-useless-and-what-that-means-for-rest-a65194471bc8) that even with a format agreed, you still can't communicate the *meaning* of the data through links, so a truly generic client remains impossible. That's the deep problem — links tell you *where*, not *what it means*.

### 4. It bloats responses and adds complexity

Every response now carries a pile of link boilerplate. Your `GET /orders` that returns 50 orders now returns 50 orders each wrapped in `_links` objects with 3-5 links apiece. The payload balloons, and someone has to write and test the logic that decides which links to include based on state. It's real work for a benefit your clients aren't set up to use [6].

### 5. The tooling and docs won the war instead

Here's the pragmatic truth. HATEOAS was supposed to make APIs self-describing so you wouldn't need out-of-band documentation. But then **OpenAPI/Swagger** showed up and gave us machine-readable docs, code generators, interactive explorers, and mock servers. GraphQL went further — it's [natively discoverable through its schema](https://blog.postman.com/graphql-vs-rest/), so a client can introspect the whole API without any hypermedia at all [10]. Discoverability got solved by other means, and those means had great tooling. HATEOAS never got that ecosystem [6].

## But wait — some big players DO use it

I don't want to be unfair. HATEOAS isn't vaporware. Several serious APIs use it, at least partially:

- **PayPal** returns a `links` array on payment responses, each with `href`, `rel`, and `method`, so you construct the payment flow by following `self`, `refund`, `parent_payment` and friends [9]. This one actually makes sense — payment flows are stateful multi-step processes where "what can I do next" genuinely changes.
- **GitHub's API** is littered with `*_url` fields — fetch a repo and you get `issues_url`, `pulls_url`, `commits_url` pointing you onward [11]. It's not a strict HAL format, but the spirit is there.
- **AWS AppStream, Visa, and Stormpath** have used hypermedia too, and Spring even ships [Spring HATEOAS](https://github.com/spring-guides/gs-rest-hateoas) to make it easier in Java land.

Notice the pattern? HATEOAS earns its keep in **workflow-heavy, stateful domains** — payments, provisioning, multi-step approvals — where "the available actions depend on current state" is a genuinely hard problem worth encoding in the response. For a plain CRUD-over-a-database API, it's mostly ceremony. That's the nuance people miss when they either dismiss it entirely or evangelize it blindly.

![hateoas flow](/images/posts/hateoas-rest-api-why-nobody-implements-it/hateoas-flow.svg)

## So when can I actually call my API a "REST API"?

This is the question you actually came for, so let me give you a straight answer and then the honest answer.

**The strict answer (Fielding's):** you can call it a REST API only when it hits Level 3 — resources with URIs, proper use of HTTP verbs and status codes, self-descriptive messages, *and* hypermedia driving state transitions [2][5]. No hypermedia, no REST. Full stop. By this bar, GitHub is close, PayPal's payment flow qualifies, and your typical microservice does not.

**The honest, industry answer:** the word "REST" has drifted. When a job posting or a teammate says "REST API," they mean an HTTP API that:

- **Uses resource-based URLs** — `/orders/12`, not `/getOrder?id=12`.
- **Uses HTTP verbs correctly** — `GET` reads, `POST` creates, `PUT`/`PATCH` updates, `DELETE` removes.
- **Uses HTTP status codes meaningfully** — `200`, `201`, `404`, `400`, `500` mean what they should.
- **Is stateless** — each request carries everything the server needs; no server-side session leaning.
- **Returns a consistent representation** — usually JSON, with sane structure.

That's Richardson **Level 2**, and that's what the entire industry has agreed to call "REST" [3][4]. Fielding would grumble, and he'd be technically correct, but this ship sailed a long time ago. Stefan Tilkov's classic ["REST APIs must be hypertext-driven"](https://www.innoq.com/blog/st/2008/10/rest-apis-must-be-hypertext-driven/) commentary and a decade of practice landed on a comfortable compromise: most people say **"RESTful"** for Level 2 and reserve **"hypermedia API"** or "HATEOAS-compliant" for the real Level 3 thing.

My personal take after years of shipping these: don't stress about the purity badge. **Aim for a clean Level 2 and you have built something 99% of consumers will happily call REST.** Add hypermedia selectively where the domain is genuinely stateful and a link like `refund` or `cancel` carries real business meaning. Don't sprinkle `_links` everywhere just to appease a dissertation from 2000. That's cargo-cult engineering.

## A quick reality check on the whole debate

Here's the thing that took me a while to accept. The reason HATEOAS "failed" in practice isn't that it's a bad idea — it's that it solved a problem most people don't have. It was designed for a web-scale world of long-lived, independently-evolving, generic clients following links the way browsers follow anchor tags. Most of us are building a frontend and a backend that ship together, version together, and die together. For that world, tight coupling is fine and hypermedia is overhead.

And where the original vision *was* right — the browser and the HTML web — HATEOAS is wildly successful. You just don't call it HATEOAS. You call it "the web." The htmx project makes exactly [this argument](https://htmx.org/essays/hateoas/): HTML *is* the working hypermedia format, and JSON APIs abandoned hypermedia the moment they became the plumbing between machine components rather than something a human navigates.

So next time someone asks whether your API is "properly RESTful," you have got two honest answers ready. Technically? Probably not, and here's the exact reason why. Practically? It's Level 2, it's clean, it's what everyone means by REST, and adding HATEOAS wouldn't buy your React app a single thing. Both answers are true at once, and knowing which one to give in the room is the actual skill.

## Sources

1. [How to Build HATEOAS Driven REST APIs — restfulapi.net](https://restfulapi.net/hateoas/)
2. [REST APIs must be hypertext-driven — Roy T. Fielding](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven)
3. [Richardson Maturity Model — restfulapi.net](https://restfulapi.net/richardson-maturity-model/)
4. [Richardson Maturity Model — Martin Fowler](https://martinfowler.com/articles/richardsonMaturityModel.html)
5. [Fielding Dissertation, Chapter 5: Representational State Transfer](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
6. [Do People Really Use HATEOAS in REST APIs? — Pradeesh Kumar](https://pradeesh-kumar.medium.com/do-people-really-use-hateoas-in-rest-apis-an-honest-industry-take-8eb29cbd2c99)
7. [Pragmatic REST: APIs without hypermedia and HATEOAS — Ben Morris](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/)
8. [A Deep Dive into Alternative Data Formats for APIs: HAL, Siren, and JSON-LD — Zuplo](https://zuplo.com/learning-center/a-deep-dive-into-alternative-data-formats-for-apis-hal-siren-and-json-ld)
9. [API responses (HATEOAS links) — PayPal Developer Docs](https://developer.paypal.com/docs/api/reference/api-responses/#hateoas-links)
10. [GraphQL vs REST — Postman Blog](https://blog.postman.com/graphql-vs-rest/)
11. [Using HATEOAS with REST APIs — 3ap Engineering Blog](https://engineering.3ap.ch/post/using-hateoas-with-rest/)
12. [REST APIs Must be Hypertext-driven — Stefan Tilkov, INNOQ](https://www.innoq.com/blog/st/2008/10/rest-apis-must-be-hypertext-driven/)
13. [HATEOAS essay — htmx.org](https://htmx.org/essays/hateoas/)
14. [How Did REST Come To Mean The Opposite of REST? — htmx.org](https://htmx.org/essays/how-did-rest-come-to-mean-the-opposite-of-rest/)
15. [Why HATEOAS is useless and what that means for REST — Andreas Reiser](https://medium.com/@andreasreiser94/why-hateoas-is-useless-and-what-that-means-for-rest-a65194471bc8)