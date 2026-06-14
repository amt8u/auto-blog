+++
title       = "How OpenAI and Anthropic Actually Train Their Models"
description = "A look inside how frontier labs like OpenAI and Anthropic train AI models — the GPU clusters, the pipeline stages, the costs, and how long it really takes."
date        = "2026-06-14T21:01:45+05:30"
slug          = "how-openai-anthropic-train-models"
tags          = ["ai", "llm", "machine-learning", "gpu", "infrastructure"]
keywords      = ["how AI models are trained", "OpenAI training hardware", "Anthropic Claude training", "GPU cluster LLM", "LLM training pipeline", "how long to train an AI model"]
canonical     = "/posts/how-openai-anthropic-train-models/"
feature_image = "https://images.unsplash.com/photo-1591405351990-4726e331f141?q=80&w=1600&auto=format&fit=crop"
+++

Everyone talks about ChatGPT and Claude like they just appeared one day. You type something, you get an answer, magic. But have you ever stopped to ask what it actually takes to *make* one of these things? Not the chat interface — the model itself. The thing that took months, hundreds of millions of dollars, and enough electricity to power a small town.

I've been curious about this for a while, partly because the numbers are genuinely hard to believe until you sit with them. So I went digging through what's actually known — the leaked architecture details, the hardware announcements, the data center buildouts. Some of it is public, some of it is well-sourced speculation, and some of it the labs keep deliberately vague. Let me walk you through what we actually know.

## The short version: it's three big stages, not one

When people say a model was "trained," they usually picture one giant computation. That's wrong. Modern frontier models go through a [multi-stage pipeline](https://mlops.community/blog/pretraining-breaking-down-the-modern-llm-training-pipeline) that OpenAI more or less formalized with InstructGPT back in 2022 [1]. The three stages are:

1. **Pretraining** — feed the model trillions of words and have it learn to predict the next token. This is the expensive part, the one that eats the GPU clusters for months.
2. **Supervised fine-tuning (SFT)** — show it curated examples of good question-and-answer behavior so it learns to actually be helpful instead of just autocompleting.
3. **Reinforcement learning from human feedback (RLHF)** — humans rank model responses, a separate "reward model" learns those preferences, and the main model gets nudged toward answers people prefer [1].

That last stage is the secret sauce that turns a raw text predictor into something that feels like it's talking *to* you. Anthropic adds its own twist here with a method called [Constitutional AI](https://www.anthropic.com/news/challenges-in-red-teaming-ai-systems), where the model critiques itself against a written set of principles instead of relying purely on human labels.

![training pipeline](/images/posts/how-openai-anthropic-train-models/training-pipeline.svg)

Honestly, this is where most explanations stop and where it gets interesting. So let's go deeper on each piece.

## Before anything trains: the data problem

You can't train a frontier model without data, and the scale here is the first thing that breaks your brain. GPT-3 was trained on roughly 300 billion tokens. By the time you get to Meta's Llama 3, that number is **over 15 trillion tokens** [2]. GPT-4 reportedly sat around 13 trillion [3]. A token is roughly a sub-word chunk — "running" might be one token, or it might split into "run" and "ning" depending on the tokenizer.

Where does all this text come from? The backbone is [Common Crawl](https://developer.nvidia.com/blog/curating-trillion-token-datasets-introducing-nemo-data-curator/), an open archive of web pages that releases fresh snapshots every month, measured in petabytes [2]. But here's the thing nobody tells you: **raw web data is garbage, and most of the work is cleaning it.** Teams build elaborate filtering pipelines that do:

- **Language identification** — keep the languages you actually want
- **Boilerplate removal** — strip nav menus, cookie banners, ads
- **Quality scoring** — toss low-quality or spammy pages
- **Deduplication** — remove repeated content so the model doesn't over-memorize
- **Safety filtering** — drop the genuinely nasty stuff [2]

That deduplication step is sneakily one of the biggest bottlenecks. At trillion-token scale you can't just compare every document to every other document — that's computationally insane. So teams use tricks like [MinHash LSH](https://zilliz.com/blog/data-deduplication-at-trillion-scale-solve-the-biggest-bottleneck-of-llm-training) and Jaccard similarity to find near-duplicates approximately rather than exactly [4]. Then everything gets converted to UTF-8 bytes and run through Byte Pair Encoding to become the token IDs the model actually sees [2].

This stage is unglamorous and it takes serious engineering, but skip it and your billion-dollar training run learns from clickbait and comment-section sludge. Garbage in, garbage out — except the garbage costs $100 million to process.

## Pretraining: where the GPUs go to work

Now the expensive part. In pretraining, the model is shown a chunk of text and asked, over and over, billions of times: *what's the next token?* It guesses, it's wrong, the error gets pushed back through the network, the weights nudge slightly. Repeat that across trillions of tokens and the thing slowly learns grammar, facts, reasoning patterns, coding — all of it emerging from one stupidly simple objective.

The catch is that "billions of times across trillions of tokens" demands a frankly absurd amount of compute. Let's talk hardware, because this is the part the user actually asked about.

### What GPT-4 ran on

According to the [widely-cited leaked details](https://newsletter.semianalysis.com/p/gpt-4-architecture-infrastructure) (OpenAI never officially confirmed these), GPT-4 was trained on roughly **25,000 NVIDIA A100 GPUs over about 90–100 days** [3][5]. The model itself is reportedly around 1.8 trillion parameters using a *Mixture-of-Experts* design — 16 experts of about 111B parameters each, where only a couple activate per token instead of the whole network [5]. The raw compute came to roughly 2 × 10²⁵ FLOPs, and the training run alone cost an estimated **$63 million** [3].

### What GPT-5 reportedly runs on

Jump forward and the hardware generation flips to NVIDIA's Hopper chips. Reports peg GPT-5 training on around **50,000 H100 GPUs**, totaling roughly 144 million GPU-hours, with an estimated cost north of **$600 million** [6]. NVIDIA itself has stated GPT-5 was trained on H100 and H200 GPUs [7]. The H200 is the upgrade that gave OpenAI more breathing room: 141 GB of memory at 4.8 TB/s bandwidth, versus the H100's 80 GB [8].

### What Anthropic runs on

Here's where it gets genuinely different. Anthropic leans heavily on Amazon — not NVIDIA — through [Project Rainier](https://www.aboutamazon.com/news/aws/aws-project-rainier-ai-trainium-chips-compute-cluster), one of the largest AI compute clusters on Earth, built on AWS's custom **Trainium2** silicon. Rainier came online in 2025 with nearly **half a million Trainium2 chips**, and AWS says Claude was expected to be running on more than **1 million Trainium2 chips** by the end of that year [9]. That's more than five times the compute Anthropic used for its previous models [9].

The architecture stitches these chips together with UltraServers — four servers of 16 Trainium2 chips each — connected internally over high-speed NeuronLinks and across clusters via Elastic Fabric Adapter networking [9]. And they're not stopping: Anthropic committed to spending [over $100 billion on AWS](https://www.aboutamazon.com/news/company-news/amazon-invests-additional-5-billion-anthropic-ai) and securing up to 5 gigawatts of capacity across Trainium2, Trainium3, and beyond [10]. They've also signed a separate deal with Google and Broadcom for more custom chips [11]. When you hear "compute is the new oil," this is what it looks like in practice.

### The GPU generations, side by side

| Chip | Architecture | Memory | Bandwidth | Notable |
|---|---|---|---|---|
| A100 | Ampere | 40/80 GB | ~2 TB/s | Trained GPT-4 (reportedly) [5] |
| H100 | Hopper | 80 GB | 3.35 TB/s | The workhorse of 2023–24 [8] |
| H200 | Hopper | 141 GB | 4.89 TB/s | Memory upgrade, same die [8] |
| B200 | Blackwell | 180 GB | 8 TB/s | ~4x H100 training throughput, FP4 [12] |
| Trainium2 | AWS custom | — | NeuronLink fabric | Anthropic's Project Rainier [9] |

The jump from H100 to Blackwell's B200 matters a lot. The B200 brings NVLink 5.0 at 1.8 TB/s per GPU (double the H100) and new FP4 precision tensor cores that deliver roughly **4x the training throughput** on transformer models [12]. When you're paying by the GPU-hour across tens of thousands of chips, a 4x speedup isn't a nice-to-have — it's the difference between a three-month run and a three-week one.

## Wiring 100,000 GPUs together is its own nightmare

Here's a thing that surprised me: buying the GPUs is almost the easy part. Getting 100,000 of them to act like one computer is where the real engineering pain lives.

A single [100,000 H100 cluster](https://newsletter.semianalysis.com/p/100000-h100-clusters-power-network) needs around **150 megawatts** of data center capacity and burns through roughly 1.59 terawatt-hours of electricity a year — about $124 million in power costs alone at standard rates [13]. The servers themselves run around $4 billion [13]. That's before you've trained anything.

Then there's networking. Every GPU has to constantly share its slice of the model with every other GPU, so the interconnect — InfiniBand or high-speed Ethernet — becomes the bottleneck. xAI's [Colossus supercomputer](https://www.tomshardware.com/tech-industry/artificial-intelligence/xai-colossus-supercomputer-with-100k-h100-gpus-comes-online-musk-lays-out-plans-to-double-gpu-count-to-200k-with-50k-h100-and-50k-h200) is the wild example here. They built it with 100,000 H100s in **122 days**, then doubled it to 200,000 GPUs in another 92 days [14]. Their building block is a Supermicro liquid-cooled rack of 64 H100s, arranged in groups of 8 racks (512 GPUs) as mini-clusters [15]. Unusually, they skipped InfiniBand entirely and used NVIDIA's Spectrum-X Ethernet fabric [14]. By late 2025 Colossus reportedly held 150,000 H100s, 50,000 H200s, and 30,000 GB200s [14].

And at this scale, **failures aren't an edge case — they're constant.** With tens of thousands of GPUs running flat out for months, individual chips, cables, and nodes die regularly. That's why labs lean so hard on *checkpointing*: periodically saving the entire model state so that when (not if) something fails, you restart from the last checkpoint instead of from zero [13]. Lose a week of a $600M run because you didn't checkpoint and, well, you're going to have a bad quarter.

![cluster cost](/images/posts/how-openai-anthropic-train-models/cluster-cost.svg)

## So how long does it really take, start to finish?

This is the question that I think most people get wrong, because they assume "training time" equals "the whole timeline." It doesn't. Let me break it into the phases that actually consume calendar time.

### The pretraining run itself

The headline compute run — the GPU-melting part — is on the order of **2 to 4 months** for a frontier model. GPT-4's was reportedly about 100 days on 25,000 A100s [5]. That's the number you usually see quoted. But it's also the *smallest* slice of the real timeline.

### Everything around it

According to the GPT-4 leaks, the actual training took around 3 months, with roughly **6 additional months of safety testing** layered on top before release [16]. So the compute is a third of the picture, at most.

Here's a rough end-to-end breakdown for a frontier model, based on what's publicly known:

| Phase | Roughly how long | What's happening |
|---|---|---|
| Data collection & curation | Months (often overlapping) | Crawling, filtering, dedup, tokenizing trillions of tokens [2] |
| Architecture & small-scale experiments | Weeks to months | Testing designs at small scale before committing |
| Main pretraining run | 2–4 months | The big GPU cluster job [5] |
| SFT + RLHF | Weeks to a couple of months | Teaching helpfulness and preferences [1] |
| Safety testing & red teaming | Months (~6 for GPT-4) | Stress-testing for harm before release [16] |
| Total, idea to launch | Often ~9–18 months | — |

That safety phase isn't a rubber stamp. Anthropic's red teaming, for instance, requires subject-matter and LLM experts to spend [100+ hours per domain](https://www.anthropic.com/news/frontier-threats-red-teaming-for-ai-safety) probing the model for dangerous capabilities [17]. Before shipping Claude 3, their Trust & Safety team red-teamed for both text and image risks and brought in external testers [17]. Models from both Anthropic and OpenAI have also gone through pre-deployment testing with the US and UK AI Safety Institutes [17]. So when a lab says a model is "done training," there's often half a year of poking, prodding, and patching still ahead.

And honestly, even after launch it's never really finished. There are continued fine-tuning passes, the vision components (GPT-4's image abilities were reportedly trained on *another* 2 trillion tokens after the text pretraining) [5], and the endless cycle of evaluation and iteration.

## Why does any of this cost so much?

Let me put the dollars in one place, because the scale is the whole story:

- **GPT-4 training run:** ~$63 million [3]
- **GPT-5 training run:** estimated $600M+ [6]
- **A single 100K-GPU cluster:** ~$4 billion in hardware, ~$124M/year in power [13]
- **Anthropic's AWS commitment:** $100+ billion over a decade [10]

The reason is almost embarrassingly simple. It's **compute**. You're renting (or buying) tens of thousands of the most in-demand chips on the planet, running them at full tilt for months, in data centers that draw as much power as a city. Every one of those GPU-hours costs money, every watt costs money, and every failed run that has to restart costs money. Stack that up across the full pipeline and the hundreds of millions stops looking crazy and starts looking inevitable.

There's also a quieter cost most coverage ignores: the people. Data engineers building curation pipelines, researchers running small-scale experiments to de-risk the big run, human annotators ranking thousands of responses for RLHF, red teamers spending hundred-hour stretches trying to break the thing. The chips get the headlines, but a frontier model is as much a logistics and human-coordination feat as a hardware one.

## What this means if you're not a trillion-dollar lab

You're probably not going to pretrain a 1.8-trillion-parameter model in your garage, and that's kind of the point. The barrier to building a *frontier* model from scratch is now measured in billions of dollars and gigawatts of power — which is exactly why only a handful of organizations on Earth do it.

But here's the more useful takeaway. Almost everything interesting *you* might build sits on top of that work — through an [API](https://www.anthropic.com/), through fine-tuning a smaller open model, through retrieval and prompting. The trillion-token pretraining run is the part you rent, not the part you redo. The labs spent the $600 million so you can spend a few dollars per million tokens.

What I find genuinely wild is how much of this is still half-secret. OpenAI never officially confirmed GPT-4's architecture — most of what we "know" comes from leaks and well-sourced analysis [5]. Anthropic publishes a lot about safety methods but stays quiet on exact model sizes. So if you read this whole thing wanting a precise, confirmed spec sheet, I have to be honest: nobody outside those buildings has one. What we've got is leaks, hardware announcements, and the labs telling us how much money and silicon they're throwing at the problem — and even *that* is enough to make your head spin.

## Sources

1. [Pretraining: Breaking Down the Modern LLM Training Pipeline — MLOps Community](https://mlops.community/blog/pretraining-breaking-down-the-modern-llm-training-pipeline)
2. [Curating Trillion-Token Datasets — NVIDIA Technical Blog](https://developer.nvidia.com/blog/curating-trillion-token-datasets-introducing-nemo-data-curator/)
3. [GPT-4 architecture, datasets, costs and more leaked — The Decoder](https://the-decoder.com/gpt-4-architecture-datasets-costs-and-more-leaked/)
4. [Data Deduplication at Trillion Scale — Zilliz Blog](https://zilliz.com/blog/data-deduplication-at-trillion-scale-solve-the-biggest-bottleneck-of-llm-training)
5. [GPT-4 Architecture, Infrastructure, Training Dataset, Costs — SemiAnalysis](https://newsletter.semianalysis.com/p/gpt-4-architecture-infrastructure)
6. [How Many GPUs to Train GPT-5 — CometAPI](https://www.cometapi.com/how-many-gpus-to-train-gpt-5/)
7. [OpenAI's GPT-5 was trained on NVIDIA H100 and H200 GPUs — NVIDIA Data Center](https://www.facebook.com/NVIDIADataCenter/posts/-openais-gpt-5-was-trained-on-nvidia-h100-and-h200s-gpus-and-served-on-systems-l/1349113753888089/)
8. [NVIDIA H200 GPU: Specs, VRAM, Price — RunPod](https://www.runpod.io/articles/guides/nvidia-h200-gpu)
9. [AWS activates Project Rainier — About Amazon](https://www.aboutamazon.com/news/aws/aws-project-rainier-ai-trainium-chips-compute-cluster)
10. [Amazon announces additional $5B Anthropic investment — About Amazon](https://www.aboutamazon.com/news/company-news/amazon-invests-additional-5-billion-anthropic-ai)
11. [Anthropic expands partnership with Google and Broadcom — Anthropic](https://www.anthropic.com/news/google-broadcom-partnership-compute)
12. [NVIDIA B200 vs H100 — Clarifai](https://www.clarifai.com/blog/nvidia-b200-vs-h100)
13. [100,000 H100 Clusters: Power, Network, Reliability — SemiAnalysis](https://newsletter.semianalysis.com/p/100000-h100-clusters-power-network)
14. [xAI Colossus supercomputer with 100K H100 GPUs comes online — Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/xai-colossus-supercomputer-with-100k-h100-gpus-comes-online-musk-lays-out-plans-to-double-gpu-count-to-200k-with-50k-h100-and-50k-h200)
15. [Inside the 100K GPU xAI Colossus Cluster — ServeTheHome](https://www.servethehome.com/inside-100000-nvidia-gpu-xai-colossus-cluster-supermicro-helped-build-for-elon-musk/)
16. [GPT-4 Details Revealed — Patrick McGuinness](https://patmcguinness.substack.com/p/gpt-4-details-revealed)
17. [Frontier Threats Red Teaming for AI Safety — Anthropic](https://www.anthropic.com/news/frontier-threats-red-teaming-for-ai-safety)