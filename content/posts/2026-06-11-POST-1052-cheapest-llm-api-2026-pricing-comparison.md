+++
title       = "Cheapest LLM API in 2026: Claude vs GPT vs AWS vs OCI"
description = "I compared per-token pricing for Claude, GPT, Gemini, DeepSeek, AWS Bedrock, Azure, Vertex AI and OCI to find the actual cheapest LLM API in 2026."
date        = "2026-06-11T13:00:50+05:30"
slug          = "cheapest-llm-api-2026-pricing-comparison"
tags          = ["LLM API pricing", "Claude", "OpenAI", "AWS Bedrock", "DeepSeek"]
keywords      = ["cheapest LLM API", "Claude API pricing 2026", "OpenAI API pricing", "Gemini API pricing", "AWS Bedrock pricing", "DeepSeek API pricing", "OCI generative AI pricing", "LLM API comparison"]
canonical     = "/posts/cheapest-llm-api-2026-pricing-comparison/"
feature_image = "/images/POST-1052-cheapest-llm-api-2026-pricing-comparison.svg"
+++

I spent a chunk of last weekend with about fifteen pricing pages open in different tabs, trying to figure out why a small side project's API bill quietly tripled in a month. Turns out the answer wasn't "the model got more expensive" — it was that I picked the wrong model for the job, on the wrong platform, without caching anything. So I went down the rabbit hole properly: every major LLM API, every cloud wrapper, and the budget options nobody talks about until their AWS bill shows up.

## Why "per million tokens" doesn't tell the whole story

Every provider quotes prices per million tokens, split into **input** and **output**. That split matters more than people realize — output tokens are almost always **3 to 5 times more expensive than input tokens** across every provider [1][5]. If your app generates long responses (summaries, code, reports), your bill is dominated by output pricing, not input. If you're mostly stuffing huge documents into context and getting short answers back, input pricing is what to optimize.

Here's the part that's genuinely confusing and almost nobody mentions: **the same text doesn't always cost the same number of tokens across models**. Anthropic quietly noted that Claude Opus 4.7 and later use a new tokenizer that "may use up to 35% more tokens for the same fixed text" compared to older Claude models [1]. So a model that looks 20% cheaper per token on paper could end up costing more per *task* once you account for tokenization differences. This is exactly the kind of gotcha that makes naive price comparisons misleading.

The two levers that actually move the needle on your bill:

- **Prompt caching** – reusing a system prompt, document, or conversation history. Anthropic charges just **10% of the base input price for cache hits** [1]. Google's Gemini caching can cut input costs by up to 90% too (cached Gemini 2.5 Flash input drops to $0.03/M from $0.30/M) [3].
- **Batch processing** – for anything that doesn't need a response in real time (classification, bulk summarization, data labeling), nearly every provider gives you a flat **50% discount** on both input and output tokens [1][2][3][5].

If you're not using at least one of these two, you're probably overpaying by a wide margin no matter which model you picked.

## The big three, head to head: Claude vs GPT vs Gemini

Let's start with the frontier labs everyone defaults to. Here's where things stood as of June 2026, per official pricing pages:

| Model | Input ($/M tokens) | Output ($/M tokens) | Batch (in/out) | Notes |
|---|---|---|---|---|
| Claude Opus 4.8 | $5.00 | $25.00 | $2.50 / $12.50 | Cache hit $0.50/M (90% off) [1] |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $1.50 / $7.50 | 1M context window included [1] |
| Claude Haiku 4.5 | $1.00 | $5.00 | $0.50 / $2.50 | Cheapest Claude, still very capable [1] |
| GPT-5.5 (flagship) | $5.00 | $30.00 | $2.50 / $15.00 | Cached input $0.50/M [2] |
| GPT-5.4 | $2.50 | $15.00 | ~50% off | Cached input $0.25/M [2] |
| GPT-5.4-mini | $0.75 | $4.50 | ~50% off | Cached input $0.075/M [2] |
| GPT-5.4-nano | $0.20 | $1.25 | ~50% off | Cached input $0.02/M [2] |
| GPT-4.1 nano | $0.10 | $0.40 | — | Cheapest OpenAI model overall [2][14] |
| Gemini 3.1 Pro | $2.00–$4.00 | $12.00–$18.00 | 50% off | Higher tier kicks in past 200k tokens [3] |
| Gemini 3.5 Flash | $1.50 | $9.00 | $0.75 / $4.50 | Newest Flash, May 2026 release [3] |
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | — | Generous free tier [3] |

A few things jump out here. **Anthropic's pricing is the most transparent of the three** — one table, no asterisks about "short vs long context tiers." Google's Gemini 3.1 Pro, by contrast, doubles its price once you cross 200k tokens of context [3], which is easy to miss if you're testing with small prompts and then ship something that processes whole PDFs.

Also worth knowing: Anthropic just had its biggest price cut in company history. Opus went from **$15/$75 per million tokens (Opus 4.1) down to $5/$25 (from Opus 4.5 onward)** — a 67% reduction [4]. That's the kind of thing that can make a six-month-old cost analysis completely wrong, which is honestly half the reason these comparisons age so fast.

If you're picking purely on output-token cost for similar "smart but not flagship" tiers, **Claude Haiku 4.5 at $1/$5 and GPT-5.4-nano at $0.20/$1.25 sit near the bottom of the big-three lineup** [1][2], with Gemini 2.5 Flash-Lite even cheaper at $0.10/$0.40 [3] — though Flash-Lite trades off some reasoning quality for that price.

## Does going through AWS, Azure, GCP, or OCI actually save money?

This is the question I really wanted answered, because a lot of companies route everything through their existing cloud billing for procurement reasons. Short answer: **going through a cloud provider rarely makes things cheaper, and sometimes adds a real markup.**

### AWS Bedrock

Bedrock hosts Claude, Llama, Mistral, and Amazon's own Nova models. The Claude pricing on Bedrock matches Anthropic's direct pricing exactly — Opus 4.6 at $5/$25, Sonnet 4.6 at $3/$15, Haiku 4.5 at $1/$5 [5]. So no markup there... unless you turn on **cross-region inference** for better availability, which adds a flat **10% surcharge across the board** (Sonnet input goes from $3.00 to $3.30, output from $15.00 to $16.50) [5].

Where Bedrock gets genuinely interesting is **Amazon's own Nova models**, which are dramatically cheaper than anything from Anthropic, OpenAI, or Google:

- Nova Pro: $0.80 / $3.20 per million tokens
- Nova Lite: $0.06 / $0.24
- Nova Micro: $0.035 / $0.14 [5]

Nova Micro at $0.035 input is genuinely one of the cheapest "real" hosted models around — though it's also the least capable of the bunch, so test it on your actual task before committing.

### Azure OpenAI Service

Azure gives you the same models as OpenAI's direct API, but the economics shift. The headline numbers can look *cheaper* — Azure's GPT-5 listing shows $1.25/$10 versus OpenAI's direct GPT-5.4 at $2.50/$15 [6][2] — but that's comparing different model generations, and Azure layers on **support plans ($100–$1,000+/month)**, networking, and infra costs that typically add **20-40% on top of listed token rates** in production [6]. If you need **provisioned throughput units (PTUs)** for guaranteed latency, that's a separate ~$2,448/month commitment that only pays off at serious scale [6].

### GCP Vertex AI

Vertex AI is literally "Gemini, but with enterprise wrapping" — VPC Service Controls, customer-managed encryption keys, regional residency. The token pricing matches the Gemini Developer API, but if you need the **Priority tier** for tighter latency SLAs, expect to pay roughly **80% more than Standard tier** [3]. For most projects that don't need the compliance extras, hitting the Gemini API directly through [Google AI Studio](https://ai.google.dev/gemini-api/docs/pricing) is simpler and identically priced.

### Oracle Cloud Infrastructure (OCI)

OCI's Generative AI service is the odd one out — it bills **per character rather than per token** for most models, and hosts a narrower set: Cohere's Command family and Meta's Llama models [7]. The pricing range Oracle publishes runs from **$0.075 per million tokens on the cheap end up to $10.68 on the premium end** [7]. Honestly, I couldn't pull exact per-model rate cards off Oracle's pricing page (it kept blocking automated fetches), so if OCI is on your shortlist, budget time to run their [cost estimator](https://www.oracle.com/artificial-intelligence/enterprise-ai/cost-estimator/) directly rather than trusting third-party summaries — the per-character billing model makes naive token-based comparisons unreliable.

| Cloud platform | Markup vs. direct API | Best reason to use it |
|---|---|---|
| AWS Bedrock | None for Claude (0% to +10% for cross-region) | Already deep in AWS billing/IAM; want Nova's ultra-low pricing |
| Azure OpenAI | ~20-40% effective (support, infra, PTUs) | Enterprise compliance, Microsoft ecosystem lock-in |
| GCP Vertex AI | 0% (Standard) / +80% (Priority) | Need data residency / VPC controls with Gemini |
| OCI Generative AI | Hard to compare (per-character billing) | Already on Oracle Cloud Universal Credits |

The pattern is consistent: **cloud platforms are about compliance, procurement, and existing infrastructure — not about saving money on tokens.** If your only goal is the lowest possible bill, go direct to the model provider's API.

## The actual cheapest options nobody talks about

If you want the real budget tier, the frontier labs aren't even in the conversation anymore. The price floor is set by **open-weight models running on specialized inference providers**, and one Chinese lab in particular.

**DeepSeek** is the standout. DeepSeek V4 Flash costs **$0.14 per million input tokens (cache miss) and $0.28 output** — and if your prompt structure hits the cache, that input cost drops to **$0.0028 per million tokens**, a 50x reduction [8]. DeepSeek reduced cache-hit pricing to one-tenth of its launch price back in April 2026 [8], and context caching is enabled by default — if your requests share a common prefix (like a system prompt), you get the discount automatically without any extra setup. For high-volume, repetitive workloads (think: classifying thousands of similar support tickets with the same instructions), this is close to free.

Then there's the **open-weight + specialized hardware** combo:

- **Groq** runs Llama, Mixtral, Gemma, and DeepSeek-distilled models on custom LPU chips at 500+ tokens/second. Llama 3.1 8B Instant costs just **$0.05 input / $0.08 output per million tokens** [10] — and it's *fast*, which matters if your app is latency-sensitive.
- **Cerebras** pushes inference even faster (1,800-2,600 tokens/sec on their wafer-scale chips), with pricing from **$0.10/M for Llama 3.1 8B up to $2.30/M for GLM-4.7**, plus a free tier of 1 million tokens per day [9].
- **Mistral's Ministral 3B** is about as cheap as it gets for a "real" hosted model: **$0.04 input / $0.04 output per million tokens** — effectively 8 cents round-trip [8]. Mistral Small 3 sits at $0.10/$0.30, and even their flagship Mistral Large 2 is $2/$6, undercutting both Claude Sonnet and GPT-5.4 [8].

To put the spread in perspective — and this genuinely surprised me when I plotted it out — the gap between the cheapest and most expensive "frontier-ish" models is well over 300x on output tokens alone:

![output token cost comparison](/images/posts/cheapest-llm-api-2026-pricing-comparison/output-token-cost-comparison.svg)

There's also **OpenRouter**, which doesn't host models itself but acts as a single API in front of dozens of providers. Their free tier gives you **20 requests/minute and 50-1,000 requests/day across 28+ free models**, including DeepSeek R1, Llama 3.3 70B, and Qwen3 Coder 480B [12]. It's a great way to test which model fits your task before committing to a paid tier with any single provider — and the [free models collection](https://openrouter.ai/collections/free-models) is updated as new open-weight releases land.

## What's actually free (and usable)?

"Free tier" claims are usually marketing fluff, but a few of these are legitimately useful for prototyping or low-volume production:

- **Google Gemini API** — the most generous of the majors. Free tier offers **1,500 requests per day on Gemini Flash models**, no credit card, no expiry [13]. Both Gemini 2.5 Flash and Flash-Lite show "unlimited tokens" on the free tier (subject to rate limits) [3].
- **Groq** — published limits of **30 requests/minute, 1,000 requests/day, and 100K tokens/day** on Llama 3.3 70B [13]. Combine that with their LPU speed and it's a solid free option for anything latency-sensitive.
- **Cerebras** — 1 million tokens per day, free, on some of the fastest inference hardware available [9].
- **OpenRouter** — 20 RPM / up to 1,000 RPD across two dozen-plus open models, no card required [12].
- **OpenAI** — gives new accounts about **$5 in credit that expires three months after activation**, but you need a credit card on file from day one [13]. Not really a "free tier" in the same sense.
- **Anthropic** — small trial credits for new accounts, plus a separate program giving qualifying open-source maintainers **6 months of Claude Max access** (a $1,200 value, 10,000 spots) [13].

If you're just prototyping, **the strongest free stack right now is Gemini for general capability, Groq for speed-sensitive calls, and OpenRouter for trying out whatever new open model just dropped** [13].

## So what would I actually use?

Here's how I'd map this onto real decisions, based on everything above:

| Your situation | What I'd pick | Why |
|---|---|---|
| Prototyping / hobby project | Gemini free tier or OpenRouter free models | Zero cost, decent quality, no card needed |
| High-volume, repetitive tasks (classification, bulk summarization) | DeepSeek V4 Flash with caching | Cache hits at $0.0028/M are basically a rounding error [8] |
| Latency-critical chat/agents | Groq (Llama 3.1 8B) or Cerebras | LPU/wafer-scale speed at near-zero cost [9][10] |
| Production app needing strong reasoning, cost-conscious | Claude Haiku 4.5 or GPT-5.4-mini with prompt caching | Good quality-to-cost ratio, mature tooling [1][2] |
| Best-in-class quality, cost secondary | Claude Opus 4.8 or GPT-5.5 | Use Batch API for non-realtime parts of the pipeline [1][2] |
| Already deep in AWS and need Claude | Bedrock, but watch the cross-region 10% surcharge | Same pricing as direct, plus AWS billing/IAM integration [5] |
| Enterprise compliance requirements | Azure OpenAI or Vertex AI Standard tier | Pay the markup for VPC controls, residency, support SLAs [6][3] |

To make this concrete: Anthropic's own worked example shows processing **10,000 support tickets through Claude Haiku 4.5 costs about $37** at standard rates — and that drops further with caching [1]. At roughly Rs 88 to the dollar, that's about **Rs 3,250 for 10,000 conversations** — genuinely hard to beat for a production support bot.

The honest takeaway after all this digging: **DeepSeek and the open-weight providers (Groq, Cerebras, Together AI) have become the price floor that the big labs are forced to compete against** [10][14]. Anthropic's 67% Opus price cut and OpenAI's proliferation of nano/mini variants aren't happening in a vacuum — they're a direct response to models that cost pennies and are "good enough" for an enormous chunk of real workloads. Whether "good enough" is actually good enough for *your* task is something no pricing page can tell you. You have to test it.

## Sources
1. [Claude API Pricing - Anthropic Docs](https://platform.claude.com/docs/en/about-claude/pricing)
2. [OpenAI API Pricing](https://developers.openai.com/api/docs/pricing)
3. [Gemini Developer API Pricing](https://ai.google.dev/gemini-api/docs/pricing)
4. [Anthropic Claude API Pricing In 2026 - CloudZero](https://www.cloudzero.com/blog/claude-api-pricing/)
5. [Amazon Bedrock Pricing - AWS](https://aws.amazon.com/bedrock/pricing/)
6. [Azure OpenAI Service - Pricing | Microsoft Azure](https://azure.microsoft.com/en-us/pricing/details/azure-openai/)
7. [OCI Generative AI Pricing - Oracle](https://www.oracle.com/artificial-intelligence/generative-ai/generative-ai-service/pricing/)
8. [Models & Pricing - DeepSeek API Docs](https://api-docs.deepseek.com/quick_start/pricing)
9. [Cerebras Pricing](https://www.cerebras.ai/pricing)
10. [Groq API Pricing - AI Pricing Guru](https://www.aipricing.guru/groq-pricing/)
11. [Mistral AI Pricing](https://mistral.ai/pricing/)
12. [Free AI Models on OpenRouter](https://openrouter.ai/collections/free-models)
13. [Free LLM APIs in 2026: Every Provider With Free Tier Tested - TokenMix](https://tokenmix.ai/blog/free-llm-api)
14. [LLM API Pricing Comparison In 2026 - CloudZero](https://www.cloudzero.com/blog/llm-api-pricing-comparison/)