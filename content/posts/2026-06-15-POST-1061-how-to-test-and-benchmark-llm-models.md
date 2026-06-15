+++
title       = "How to Test an LLM: Benchmarks, Arenas, and Real Evals"
description = "Curious how engineers actually compare AI models? Here's how LLM benchmarks, arena leaderboards, and eval tools work, and why there's no single 'best' score."
date        = "2026-06-15T07:52:21+05:30"
slug          = "how-to-test-and-benchmark-llm-models"
tags          = ["AI", "LLM Benchmarks", "Machine Learning", "AI Tools"]
keywords      = ["LLM benchmarks", "how to test an LLM", "compare AI models", "MMLU GPQA benchmark", "Chatbot Arena LMArena", "LLM evaluation tools", "benchmark software for AI models"]
canonical     = "/posts/how-to-test-and-benchmark-llm-models/"
feature_image = "/images/POST-1061-how-to-test-and-benchmark-llm-models.svg"
+++

Every couple of weeks some AI lab drops a new model and immediately claims it's the smartest thing on the planet. Then another lab does the same thing a week later. If you've ever tried to figure out which one is *actually* better, you've probably stared at a wall of charts with names like MMLU, GPQA, and SWE-bench and felt your eyes glaze over. I went down this rabbit hole recently, and here's the short version: there's no single scoreboard. There are at least four completely different ways people measure "better," and once you know what each one is actually doing, the whole AI leaderboard circus starts to make a lot more sense.

## Why "Which LLM Is Best?" Doesn't Have One Answer

Here's the thing nobody tells you upfront: **"best" depends entirely on what you're using it for.**

A model that's brilliant at writing poetry might be mediocre at fixing a Python bug. A model that crushes math competitions might give you a clunky, over-formatted email. And a model that tops every chart might cost 10x more per request and respond noticeably slower than one that's "only" a few points behind.

So when people ask "is GPT better than Claude" or "is Gemini better than Llama," the honest answer is: **better at what, measured how, and compared on what budget?** That's not a cop-out — it's basically the entire reason the AI benchmarking industry exists. Roughly speaking, the ways people measure model quality fall into four buckets:

- **Standardized tests** — give the model a fixed set of questions with known right answers, like a school exam.
- **Human preference arenas** — show real people two anonymous responses and let them vote on which one is better.
- **LLM-as-a-judge** — use one AI model to grade another model's open-ended answers.
- **Real-world task benchmarks** — drop the model into something close to an actual job (fix this bug, complete this multi-step task) and see if it gets there.

Let's go through each one, because they each have a very different idea of what "smart" even means.

## Method 1: The Standardized Test Approach

This is the oldest and most familiar style — give the model a giant pile of questions, check the answers against a key, and report a percentage. It's basically the SAT for AI.

### Knowledge and Reasoning Tests

The granddaddy here is **MMLU** (Massive Multitask Language Understanding), a set of multiple-choice questions spanning 57 subjects from law to anatomy to abstract algebra. For years it was *the* number everyone quoted. The problem? Frontier models now score 90%+ on it, which means it's basically maxed out and can't tell good models apart from great ones anymore [2].

That's why labs moved on to harder versions:

- **MMLU-Pro** — same idea, but with 10 answer choices instead of 4 (much harder to guess your way to a good score) and questions designed to require actual reasoning, not just recall.
- **GPQA Diamond** — PhD-level questions in biology, chemistry, and physics, written so carefully that non-expert PhD holders only score around 34% on them. That low human baseline is what makes it a useful yardstick — if a model clears 80%+, it's doing something genuinely hard [2].
- **Humanity's Last Exam (HLE)** — 2,500 questions written by domain experts "at the boundary of human knowledge," covering everything from STEM to humanities. Human experts average around 90% on it, while frontier models without external tools land somewhere around 37-47% [7]. It exists specifically because everything else got too easy.

### Coding and Math Tests

For code, **HumanEval** used to be the go-to — 164 small Python problems, each checked against unit tests. It's now sitting above 93% for top models, which again means it's basically saturated [2]. The action has shifted to **SWE-bench Verified**, which throws models at *real* GitHub issues from popular open-source repos and checks whether their patch actually makes the test suite pass. Top models are now clearing somewhere in the 80-89% range on the "Verified" set, while the much harder "Pro" variant — multi-file, multi-language, real architectural complexity — keeps scores down in the 55-65% range [6].

On math, **AIME** (American Invitational Mathematics Examination) problems have become the standard torture test for "reasoning" models. The gap here is wild: general-purpose models often score in the 7-35% range, while dedicated reasoning models hit 90-100% on the same problems [16]. That single benchmark is probably the clearest evidence that "reasoning mode" (the kind of model that thinks step-by-step before answering) is a genuinely different capability, not just marketing.

Here's a quick cheat sheet for what these tests actually measure:

| Benchmark | What It Tests | How It's Graded | Status in 2026 |
|---|---|---|---|
| MMLU | General knowledge, 57 subjects | Multiple-choice, auto-scored | Saturated (90%+) [2] |
| MMLU-Pro | Harder knowledge + reasoning | 10-option multiple-choice | Active, differentiating |
| GPQA Diamond | PhD-level science reasoning | Expert-written multiple-choice | Active, human baseline ~34% [2] |
| HumanEval | Basic Python code generation | Unit tests, pass@1 | Saturated (93%+) [2] |
| SWE-bench Verified | Real GitHub bug fixes, end-to-end | Automated test suite pass/fail | Active, ~80-89% top models [6] |
| AIME | Competition-level math | Exact numeric answer | Active for non-reasoning models [16] |
| Humanity's Last Exam | Expert questions across all fields | Exact/short answer match | Active, ~37-47% without tools [7] |
| ARC-AGI-2 | Novel visual pattern puzzles | Exact grid match | Largely unsolved |

The pattern you'll notice: **as soon as a benchmark gets "solved" (everyone scores 90%+), it stops being useful, and the field invents a harder one.** This has happened to at least four major benchmarks in the last two years. It's basically an arms race between test-makers and model-makers.

## Method 2: Skip the Test, Just Ask Humans

Standardized tests are great for measuring "did the model get the textbook answer right," but they're terrible at measuring "did the model give a *helpful, well-written, pleasant-to-read* answer." For that, the AI world built something that looks a lot more like a dating app than an exam.

The most famous example is **LMArena** (formerly known as Chatbot Arena, run by the LMSYS group, and rebranded again to just "Arena" in early 2026) [1]. Here's how it works:

1. You type a prompt — anything you want.
2. Two different models, picked at random, both answer your prompt.
3. Their names are hidden. You just see "Model A" and "Model B" side by side.
4. You vote for the one you think gave the better response.

Multiply that by millions of votes — the platform has racked up over 6 million of them — and you get an **Elo-style rating** for every model, the same statistical system used to rank chess players [1]. A model's rating goes up when it beats a higher-rated opponent and goes down when it loses to a lower-rated one, so the math automatically accounts for "strength of schedule."

There's a wrinkle, though. Early on, people noticed that some models were winning votes just by being *longer*, using more bullet points, or sprinkling in more emoji — basically winning on style rather than substance. So in 2024 the platform introduced **"style control,"** which tries to mathematically separate "what the model said" from "how it said it," and as of May 2025 this style-controlled score became the default ranking shown to visitors [1].

This arena approach is genuinely valuable because it captures things multiple-choice tests can't: tone, formatting, how a model handles ambiguous or poorly-phrased questions, whether it's annoyingly verbose, whether it refuses things it shouldn't. But it's also a popularity contest, and popularity contests can be gamed too — which brings us to the next method.

## Method 3: The Robot Judging the Robot

Here's where it gets a bit recursive: a huge amount of modern LLM evaluation is done by... other LLMs. This is called **LLM-as-a-judge**, and the idea is simple. You can't write a unit test for "was this email polite enough" or "did this summary capture the key points." So instead, you give a strong model (say, GPT-5 or Claude) the original question, the response you want to grade, and a rubric, and ask it to score the answer [10].

This is incredibly useful because it scales — you can grade thousands of open-ended responses overnight instead of paying humans to read them all. It's the backbone of most custom evaluation pipelines companies build for their own products.

But, honestly, this is where it gets tricky. Research has documented a whole zoo of biases in LLM judges [10]:

- **Verbosity bias** — judges tend to prefer longer answers, even when a shorter one is actually clearer.
- **Position bias** — in side-by-side comparisons, the judge can favor whichever answer is shown first (or second).
- **Self-enhancement bias** — a model judging responses sometimes favors answers that "sound like itself."
- **Reproducibility issues** — ask the same judge to grade the same answer twice, and you might get different scores, especially on fine-grained numeric scales rather than simple pass/fail calls.

None of this makes LLM-as-a-judge useless — it just means you shouldn't treat a single judge's score as gospel. The smart move (and what most serious eval setups do) is to combine it with hard, verifiable checks wherever possible, and to spot-check the judge's reasoning with actual humans periodically.

## The Big Catch: Benchmarks Get Gamed

Okay, here's the part that honestly bugs me the most about this whole space. **Benchmarks are public.** The questions, and often the answers, are sitting on GitHub, in academic papers, on Reddit threads, in textbooks scraped for training data. So what happens when a model is trained on data that happens to include the test it's later evaluated on?

This is called **data contamination**, and it's a bigger deal than it sounds. Researchers have found that some models show accuracy gaps of up to 8 percentage points between "clean" versions of a benchmark and versions where the questions have been seen before [5]. Even weirder: just **shuffling the order of multiple-choice answers** on MMLU can swing a model's accuracy by up to 13 percentage points [5]. Think about what that actually means — the model isn't reasoning about the content nearly as much as we'd like to believe. It's partly pattern-matching against memorized question formats.

It gets worse with indirect contamination too. One analysis found that roughly 42% of papers it reviewed may have inadvertently leaked benchmark data into GPT-3.5 and GPT-4 through API calls during evaluation — totaling something like 4.7 million benchmark samples across 263 different benchmarks [5]. Nobody did this maliciously; it's just a side effect of how everyone evaluates models by... calling the API of the model being evaluated, on data that sometimes ends up feeding back into future training.

This is part of why Hugging Face eventually retired its original **Open LLM Leaderboard** — built on the open-source [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) [3] — and rebuilt it around harder, less-gameable tasks [4]. It's also why a project like **LiveBench** exists: it releases a fresh batch of questions every single month, sourced from recent arXiv papers, news articles, and even movie synopses, specifically so there's no way the questions could have leaked into training data yet [9]. Even with that protection, top models still score below 70% on it [9] — which tells you something about how much headroom is actually left versus how much of the "90%+" scores elsewhere are inflated by familiarity.

## Method 4: Real-World Task Benchmarks

If standardized tests are like exams, this category is more like an apprenticeship — drop the model into something resembling an actual job and see how far it gets.

**SWE-bench** (mentioned earlier) is the flagship example for coding: real GitHub issues, real codebases, and the model has to read the code, figure out a fix, write a patch, and pass the existing test suite [6]. No multiple choice, no shortcuts — either the tests pass or they don't.

A newer and frankly more interesting angle comes from **METR**, a nonprofit that measures how long a task an AI agent can complete on its own. They call it the **"time horizon"** — specifically, the task duration (measured in how long it would take a skilled human) at which a model succeeds 50% of the time, or 80% of the time [8]. The wild part is the trend: this time horizon has been doubling roughly every seven months for the last several years [8]. Extrapolate that line and you get a pretty stark prediction about how much "real work" AI agents will be able to handle autonomously within a decade. Whether or not that trend holds exactly, it's a genuinely different way to think about capability — not "did it get the right answer" but "how long of a leash can you give it before it gets lost."

This category also includes things like **ARC-AGI-2**, a set of abstract visual puzzles designed to test whether a model can generalize to genuinely novel patterns rather than recalling something similar from training — and it remains stubbornly difficult for even the best models.

## Okay, But Is There a "3DMark" for LLMs?

This is the question I was most curious about myself, since I've spent plenty of time running [3DMark](https://benchmarks.ul.com/3dmark) [17] and Cinebench on PC builds. With GPUs, you run one app, get one number, and that number is directly comparable across reviews, forums, and years of hardware. Is there an equivalent for LLMs?

Sort of — but it's split across a few tools rather than one app, and the analogy maps out like this:

| GPU/PC World | What It Does | LLM World Equivalent | What It Does |
|---|---|---|---|
| 3DMark | Synthetic graphics workload, one comparable score | MMLU / GPQA / AIME | Synthetic question sets, one accuracy score [2] |
| Cinebench | Real rendering workload on CPU/GPU | SWE-bench / agentic evals | Real coding tasks, graded by execution [6] |
| MLPerf (hardware) | Vendor-neutral standard across chipmakers | MLPerf Inference (LLM track) | Vendor-neutral latency/throughput on real models like Llama 3.1 405B and GPT-OSS 120B [14] |
| Forum/community rankings | Crowd-sourced real-owner reports | LMArena | Crowd-sourced blind human votes, Elo-style [1] |
| Price-to-performance charts | Cost vs FPS | Artificial Analysis | Cost vs "Intelligence Index" vs tokens/sec, tracking 350+ models [15] |

The closest thing to an actual industry-standard tool is **MLPerf**, run by the nonprofit MLCommons — the same body that's done hardware benchmarking for years. Their inference suite now includes dedicated LLM workloads (Llama 3.1 405B, Llama 2 70B, and as of the v6.0 release, an open-weight GPT-OSS 120B benchmark for math, science, and coding), measuring things like time-to-first-token and tokens-per-second under standardized conditions across different hardware vendors [14]. That's genuinely apples-to-apples in the way 3DMark is.

For *model quality* comparisons rather than hardware, the closest thing to a one-stop dashboard is **Artificial Analysis**, which tracks over 350 models simultaneously across an "Intelligence Index" (a composite of multiple benchmarks), speed in tokens per second, and cost per million tokens — updated hourly [15]. It's not a single downloadable app like 3DMark, but it serves the same function: one place to see the trade-off curve.

The honest answer to "is there a 3DMark for LLMs" is: **not exactly one tool, but a layered stack of them**, each operating at a different level of realism and cost:

![llm evaluation stack](/images/posts/how-to-test-and-benchmark-llm-models/llm-evaluation-stack.svg)

The further up that stack you go, the more realistic the test gets — but also the more expensive, slower, and harder to compare across models it becomes. No single layer tells the whole story, which is exactly why every model release comes with about six different charts instead of one.

## Tools You Can Run Yourself

Here's something I didn't realize until I started poking around: you don't need to be an AI lab to run these evaluations yourself. There's a decent ecosystem of open tools for exactly this:

- **[lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)** by EleutherAI — the actual backend behind Hugging Face's leaderboards, used by NVIDIA, Cohere, and others. It runs a model against dozens of standardized benchmarks (MMLU, GSM8K, BBH, and more) and spits out comparable numbers [3].
- **[HELM](https://crfm.stanford.edu/helm/)** from Stanford's Center for Research on Foundation Models — goes beyond raw accuracy to measure things like bias, toxicity, and efficiency across a unified set of models and benchmarks, with a public leaderboard for comparing results [13].
- **[Promptfoo](https://www.promptfoo.dev/docs/intro/)** — an open-source, YAML-configured tool for testing and comparing prompts/models side by side, including LLM-as-a-judge style grading. Used by hundreds of thousands of developers, and particularly strong for security/red-teaming style tests [11].
- **[DeepEval](https://deepeval.com/)** — a Python-native framework with 50+ pre-built metrics for chatbots, RAG pipelines, and agents, designed to plug straight into your existing `pytest` suite [12].

The practical pattern most teams land on: run the big public benchmarks to get a general sense of where a model stands, then build a small custom eval set (even just 20-50 examples) that looks like *your* actual use case, and run every candidate model against that. That second part is the bit the public leaderboards can never do for you.

## So How Should You Actually Pick a Model?

After all this, here's where I've landed. **No single benchmark, leaderboard, or arena score should be the deciding factor** — they're all measuring slightly different things, and several of them are partially saturated or contaminated anyway.

What actually works, in rough order:

1. **Use the big leaderboards (Artificial Analysis, LMArena) to shortlist 2-3 candidates** for your price/speed/quality range — not to pick a single "winner."
2. **Check the specific benchmark that matches your use case.** If you're building a coding tool, SWE-bench numbers matter way more than MMLU. If you're building a customer-support bot, arena-style human preference scores probably matter more than AIME scores.
3. **Build a tiny eval set from your own real prompts** — even 20 examples from actual user queries beats 10,000 generic benchmark questions for predicting how a model will perform *for you*.
4. **Run that eval set every time** a new model version drops, before switching. Models get updated silently, and "better on the leaderboard" doesn't always mean "better for your prompt."
5. **Still do some good old vibe testing** — just don't *only* do that. Researchers have started studying "vibe-testing" seriously precisely because it captures real things (tone, formatting quirks, how a model handles your weird edge cases) that formal benchmarks miss [15].

The GPU benchmark comparison turns out to be more useful than I expected, actually — just not in the "one number to rule them all" sense. It's useful in the sense that **serious hardware reviewers never trust a single 3DMark score either**. They run synthetic benchmarks, real game benchmarks, thermal tests, and power draw measurements, then form a judgment across all of it. LLM evaluation is heading the same direction — just a few years behind, and with the added headache that the "hardware" keeps getting silently swapped out from under you.

## Sources

1. [Arena (AI platform) - Wikipedia](https://en.wikipedia.org/wiki/Arena_(AI_platform))
2. [AI Benchmarks 2026: Compare 300+ LLM Benchmarks & Tests - llm-stats.com](https://llm-stats.com/benchmarks)
3. [lm-evaluation-harness - EleutherAI (GitHub)](https://github.com/EleutherAI/lm-evaluation-harness)
4. [What's going on with the Open LLM Leaderboard? - Hugging Face](https://huggingface.co/blog/open-llm-leaderboard-mmlu)
5. [Towards Contamination Resistant Benchmarks - arXiv](https://arxiv.org/pdf/2505.08389)
6. [Top 7 Benchmarks That Actually Matter for Agentic Reasoning in LLMs - MarkTechPost](https://www.marktechpost.com/2026/04/26/top-7-benchmarks-that-actually-matter-for-agentic-reasoning-in-large-language-models/)
7. [Humanity's Last Exam - Wikipedia](https://en.wikipedia.org/wiki/Humanity%27s_Last_Exam)
8. [Measuring AI Ability to Complete Long Tasks - METR](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
9. [LiveBench: A Challenging, Contamination-Free LLM Benchmark - GitHub](https://github.com/livebench/livebench)
10. [LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods - arXiv](https://arxiv.org/pdf/2412.05579)
11. [Promptfoo Documentation](https://www.promptfoo.dev/docs/intro/)
12. [DeepEval - The LLM Evaluation Framework](https://deepeval.com/)
13. [HELM - Holistic Evaluation of Language Models - Stanford CRFM](https://crfm.stanford.edu/helm/)
14. [MLCommons Releases New MLPerf Inference v6.0 Benchmark Results](https://mlcommons.org/2026/04/mlperf-inference-v6-0-results/)
15. [LLM Leaderboard - Artificial Analysis](https://artificialanalysis.ai/models)
16. [AIME 2025 Benchmark: An Analysis of AI Math Reasoning - IntuitionLabs](https://intuitionlabs.ai/articles/aime-2025-ai-benchmark-explained)
17. [3DMark Benchmark - UL Solutions](https://benchmarks.ul.com/3dmark)