+++
title       = "Can You Still Call an API RESTful Without Every Rule?"
description = "Most APIs labeled REST break Roy Fielding's rules. So can you still call yours RESTful? Here's what the constraints actually require and what's fine to skip."
date        = "2026-06-08T00:03:37+05:30"
slug          = "can-i-call-my-api-restful"
tags          = ["rest", "api-design", "http", "web-development"]
keywords      = ["restful api", "rest constraints", "richardson maturity model", "hateoas", "rest vs http api"]
canonical     = "/posts/can-i-call-my-api-restful/"
feature_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=80"
+++

Everyone slaps "RESTful" on their API. Open any docs page, scroll the marketing copy, and there it is — "our clean, RESTful API." But here's the uncomfortable bit: by the strict definition, almost none of them actually are. So the question you're really asking is whether the word still means anything if you break some of the rules. Honestly, that's where it gets tricky.

Short answer first, because I hate articles that bury it: **yes, you can still call it RESTful in everyday conversation, but no, it isn't a REST API by Roy Fielding's original definition unless it's hypertext-driven.** Both of those things are true at the same time, and the gap between them is the whole story.

## What "REST" actually means (and who decided)

REST isn't a protocol. It's not a spec you download. It's an architectural style described by Roy Fielding in his 2000 PhD dissertation, where he was basically reverse-engineering the principles that made the web itself scale [1]. That's an important framing — REST came *after* the web worked, as an explanation of *why* it worked.

Fielding defined six constraints. Hit all of them and you've got a RESTful system; skip the wrong one and, by his definition, you don't [2][3]:

- **Client–server** — separate the UI concerns from the data storage concerns so each can evolve on its own.
- **Stateless** — every request carries everything the server needs. The server keeps nothing about your previous request lying around.
- **Cacheable** — responses must say whether they can be cached, so clients and intermediaries can reuse them.
- **Uniform interface** — the big one, and the one everyone half-implements. More on this below.
- **Layered system** — a client can't tell whether it's talking to the real server or a proxy/load balancer/gateway in front of it.
- **Code on demand** — optional. The server can ship executable code (think JavaScript) to extend the client. This is the only constraint Fielding marked optional.

Notice that last word: *optional*. Code on demand is the only one you're explicitly allowed to drop. Everything else, in the strict reading, is mandatory. So when people ask "can I skip a rule and still be RESTful," the honest answer is the rules already have a built-in opt-out for exactly one of them, and it's not the one you wanted to skip.

## The uniform interface is where APIs quietly fall apart

The uniform interface itself breaks into four sub-constraints, and this is where the "RESTful" label gets shaky [3]:

1. **Identification of resources** — each thing has a URI, like `/users/123`.
2. **Manipulation through representations** — you hold a representation (JSON, XML) and that's enough to modify or delete the resource.
3. **Self-descriptive messages** — each message carries enough info to process it (media types, status codes, headers).
4. **HATEOAS** — Hypermedia As The Engine Of Application State. The server's responses include links telling the client what it can do next.

Most APIs nail the first three. They have nice `/users/123` URLs, they speak JSON, they set content types and status codes. And then they completely ignore number four. That's not a small omission — it's the one Fielding cared about most.

## The line in the sand: "REST APIs must be hypertext-driven"

In 2008, eight years after the dissertation, Fielding got fed up enough to write a blog post with a title that doesn't leave much room for debate: ["REST APIs must be hypertext-driven"](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven) [1]. His exact words:

> "If the engine of application state (and hence the API) is not being driven by hypertext, then it cannot be RESTful and cannot be a REST API."

That's blunt. He was reacting to a flood of APIs calling themselves REST while actually being RPC-style calls dressed in HTTP clothing [11]. His point: a true REST client should start at one entry URL and *discover* everything else by following links the server hands it — exactly like you browse a website without memorising every URL on it. The data format and link relations tell the client what's possible, not some out-of-band documentation you read on a wiki.

Think about how you use a normal website. You don't memorise that the checkout page lives at `/cart/checkout/step-3`. You click a button that's on the page. The page *tells you* what you can do next. That's hypertext driving the application state. Fielding's argument is that a REST API should work the same way for machines [1].

By that standard, here's the gut punch: the Twitter and Facebook APIs everyone learned "REST" from don't use hypermedia at all [8]. Neither do most of the APIs in your daily work. In practice, most so-called REST APIs implement statelessness and a uniform interface but ignore HATEOAS entirely [7][8].

## So is your API RESTful? Meet the Richardson Maturity Model

Leonard Richardson came up with a model that Martin Fowler [popularised](https://martinfowler.com/articles/richardsonMaturityModel.html), and it's the most useful tool for answering your question because it stops treating "RESTful" as a yes/no and turns it into a ladder [4][5]. There are four levels, 0 through 3 [13].

| Level | Name | What it uses | What it's missing |
|-------|------|--------------|-------------------|
| 0 | The Swamp of POX | Single URI, single verb (usually POST) | Everything. This is RPC/SOAP-style. |
| 1 | Resources | Multiple URIs, one per resource | HTTP verbs still misused |
| 2 | HTTP Verbs | URIs + proper GET/POST/PUT/DELETE + status codes | HATEOAS |
| 3 | Hypermedia | Everything above + HATEOAS links | Nothing — this is "full" REST |

Here's the reality check that should make you feel better: the vast majority of APIs that proudly call themselves RESTful are sitting at **Level 2** [6][8]. They've got clean resource URLs, they use the right HTTP methods, they return sensible status codes. They just don't embed navigational links. And Level 2 is genuinely good engineering — it's a perfectly sane place to be.

Fowler himself is careful here. He notes the model is a helpful way to *think* about the elements of REST, not a strict definition of when you're allowed to use the word [4]. Fielding, on the other hand, would say only Level 3 earns the name. Both views exist in the wild, and that tension is exactly why your question doesn't have a clean answer.

![rest maturity ladder](/images/posts/can-i-call-my-api-restful/rest-maturity-ladder.svg)

## HTTP API vs REST API — they're not the same thing

This trips up a lot of people, so let me state it plainly. **All REST APIs run over HTTP, but not every HTTP API is a REST API** [10]. The web API category is huge — anything you can call over HTTP qualifies. REST is a specific architectural style *inside* that category with those six constraints [8].

When your API is structured around resources, uses verbs correctly, and returns JSON, but doesn't do hypermedia, what you actually have is an **HTTP API that follows REST conventions** [10]. Some people call it "REST-like," some call it "pragmatic REST," and some just keep calling it RESTful because that's the word everyone understands [9]. None of those are wrong in casual use. They're just more honest about where you sit on the ladder.

Ben Morris has a [solid piece on pragmatic REST](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/) arguing that dropping hypermedia is a deliberate, reasonable trade-off for most teams, not a failure [9]. I'm inclined to agree, and I'll get into why.

## Why almost nobody does full HATEOAS

If Level 3 is the "real" REST, why does basically the entire industry stop at Level 2? A few honest reasons:

- **Clients don't actually navigate dynamically.** The dream of HATEOAS is a generic client that discovers the API at runtime by following links. In reality, your frontend team hardcodes the endpoints they need against a known contract. The links sit there unused.
- **It's more work for unclear payoff.** Embedding `_links` everywhere, picking a hypermedia format like HAL, keeping relation types consistent — that's real effort [8]. If no consumer uses the links to drive behaviour, you've added weight for nothing.
- **Documentation and tooling won.** OpenAPI/Swagger gives clients discoverability through a spec file instead of through runtime links. It's not what Fielding had in mind, but it solved the practical problem people had.
- **The big players never did it.** When the most-copied APIs on earth skip hypermedia [8], that becomes the de facto standard regardless of what the dissertation says.

There's a real counterpoint though, and I don't want to be unfair to it. APIs *do* exist at Level 3, and some big ones lean that way — GitHub's API famously embeds URLs to related resources right in its responses so you can follow them rather than constructing URLs yourself. When you genuinely have many independent clients you don't control, or a long-lived API where you want to move resources around without breaking everyone, hypermedia earns its keep. The decoupling Fielding talked about isn't academic — it's how the server keeps the freedom to change URLs without a coordinated client redeploy [1][12]. Most internal APIs just never need that freedom badly enough to pay for it.

## A concrete look: same endpoint, three levels

Let me make this less abstract. Say you're fetching an order. Here's roughly what each maturity level looks like.

**Level 0 — the swamp.** One endpoint, POST everything, verbs live in the body:

```
POST /api
{ "action": "getOrder", "id": 42 }
```

**Level 2 — where most "RESTful" APIs live.** Real resource URL, real verb, real status code:

```
GET /orders/42

200 OK
{ "id": 42, "status": "shipped", "customerId": 7 }
```

**Level 3 — hypertext-driven.** Same data, but the response tells the client what it can do next:

```
GET /orders/42

200 OK
{
  "id": 42,
  "status": "shipped",
  "_links": {
    "self":     { "href": "/orders/42" },
    "customer": { "href": "/customers/7" },
    "cancel":   { "href": "/orders/42/cancel" }
  }
}
```

See the difference? At Level 3, a client doesn't need to *know* that cancelling lives at `/orders/42/cancel`. The server told it. And crucially, if the order is already shipped, the server can just *omit* the `cancel` link — now the available actions are driven by state, which is the literal meaning of "hypermedia as the engine of application state" [1][8]. That's the genuinely clever part people miss. It's not about decorating responses with links. It's about the server controlling what's possible next.

## So what should you actually call your API?

Here's my opinionated take after years of building these things.

- **If it's Level 2, calling it "RESTful" in casual writing is fine.** Everyone understands what you mean, and fighting the entire industry's usage is a losing battle. The word has drifted, and that's okay.
- **If you want to be technically precise, say "REST-like" or "HTTP API following REST conventions."** Pedants on Hacker News will still argue, but you'll be correct [7].
- **Reserve "REST API" with a straight face for Level 3.** If someone's being strict and asks "is it a *REST* API," and you don't do hypermedia, the honest answer is "no, it's REST-like" [1][7].

The thing I'd push back on hardest is *pretending* the rules don't exist. Plenty of teams call something RESTful without knowing there's a HATEOAS constraint they're skipping. Skipping it on purpose is a fine engineering decision. Skipping it because you never knew it existed is just ignorance with good marketing.

## The rules you really shouldn't break

Not all constraints are equal, and this is where I'll be direct about what actually matters for a working API versus what's safe to drop.

- **Statelessness — don't break this.** The moment your server starts remembering client state between requests, you lose horizontal scaling, you lose the layered-system benefits, and you've genuinely left REST behind in a way that hurts you operationally [2][12]. This one has teeth.
- **Proper use of HTTP verbs and status codes — don't break this either.** A GET that mutates data is a real bug waiting to happen, because caches and crawlers assume GET is safe. This is Level 1-to-2 stuff and it's table stakes.
- **Cacheability — respect it.** Setting proper cache headers is low effort and it's one of the things that made the web scale. Ignoring it is leaving performance on the floor [3].
- **HATEOAS — fine to skip, knowingly.** This is the one almost everyone drops, and for most APIs that's a defensible trade-off [9]. Just don't claim full REST while you do.

Notice the pattern? The constraints that protect *operational* properties — statelessness, caching, correct verbs — are the ones you actually feel pain from breaking. The constraint that's purely about *evolvability and discoverability* — HATEOAS — is the one you can usually live without. That's not a coincidence. It's why the industry settled where it did.

## Where this leaves you

The word "RESTful" stopped being a binary a long time ago. Fielding has a strict definition that says hypertext or bust [1], and a good chunk of the developer world quietly ignores it because Level 2 solves their problems just fine [7][8]. Neither side is lying — they're using the same word for two different bars.

So can you still call your API RESTful if it doesn't follow all the rules? In practice, yes, and you'll be in the overwhelming majority. Just know which rule you're skipping, know that a purist would call you out, and know that the one you're probably skipping — HATEOAS — is the exact one Roy Fielding said you can't skip. Whether that bothers you depends entirely on whether you're writing for a strict architecture review or shipping software people actually use.

I know which side I'm usually on. But I at least know what I'm skipping.

> End

## Sources
1. [REST APIs must be hypertext-driven — Roy T. Fielding](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven)
2. [The Six Constraints — REST API Tutorial](https://www.restapitutorial.com/introduction/restconstraints)
3. [REST Architectural Constraints — restfulapi.net](https://restfulapi.net/rest-architectural-constraints/)
4. [Richardson Maturity Model — Martin Fowler](https://martinfowler.com/articles/richardsonMaturityModel.html)
5. [Richardson Maturity Model — restfulapi.net](https://restfulapi.net/richardson-maturity-model/)
6. [Know how RESTful your API is: An Overview of the Richardson Maturity Model — Red Hat Developer](https://developers.redhat.com/blog/2017/09/13/know-how-restful-your-api-is-an-overview-of-the-richardson-maturity-model)
7. [Most RESTful APIs aren't really RESTful — Florian Krämer](https://florian-kraemer.net/software-architecture/2025/07/07/Most-RESTful-APIs-are-not-really-RESTful.html)
8. [When Is an API Truly REST vs REST-Like? — Nordic APIs](https://nordicapis.com/when-is-an-api-truly-rest-vs-rest-like/)
9. [Pragmatic REST: APIs without hypermedia and HATEOAS — Ben Morris](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/)
10. [REST over HTTP, or why your HTTP API isn't RESTful — Christophe Maillard](https://medium.com/@sp00m/rest-over-http-or-why-your-http-api-isnt-restful-94fd92a0e6d4)
11. [REST APIs Must be Hypertext-driven — Stefan Tilkov, INNOQ](https://www.innoq.com/blog/st/2008/10/rest-apis-must-be-hypertext-driven/)
12. [REST — Wikipedia](https://en.wikipedia.org/wiki/REST)
13. [Richardson Maturity Model — Wikipedia](https://en.wikipedia.org/wiki/Richardson_Maturity_Model)
14. [Roy Fielding on Versioning, Hypermedia, and REST — InfoQ](https://www.infoq.com/articles/roy-fielding-on-versioning/)