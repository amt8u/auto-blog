+++
title       = "Git: Why It Won, and What It Gets Wrong"
description = "Git has 94% developer market share and its rivals are mostly dead. Here's why it won, what happened to SVN and Mercurial, and what Git genuinely gets wrong."
date        = "2026-06-03T22:29:55+05:30"
slug          = "git-why-it-won-and-what-it-gets-wrong"
tags          = ["git", "version-control", "developer-tools"]
keywords      = ["git version control", "why git is popular", "git vs SVN", "git disadvantages", "git history", "git vs mercurial"]
canonical     = "/posts/git-why-it-won-and-what-it-gets-wrong/"
feature_image = "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?auto=format&fit=crop&w=1200"
+++

Ninety-four percent of developers use Git [6]. The remaining six percent are mostly in specialized industries — game studios, large finance companies — and even they are slowly migrating. Every other version control system has either died, is in hospice, or survives only in a corner niche. That's a strange outcome for software one person wrote in about two weeks.

## The BitKeeper Incident That Started All of This

Git didn't appear because someone sat down and thought "let me design the perfect version control system." It appeared because someone yanked a free license away.

The Linux kernel — one of the most complex collaborative software projects ever built — was using BitKeeper, a proprietary distributed VCS, for free. In 2005, BitKeeper's owner revoked that free license after a dispute with the open-source community [2]. Linus Torvalds couldn't fall back to the existing alternatives. CVS and SVN were too slow and too centralized for Linux's scale. Mercurial was being developed in parallel but wasn't ready.

So Torvalds went offline for roughly ten days and wrote Git from scratch [2].

That's the origin story. Necessity, not inspiration. Anger, actually.

## What Git Actually Is

**Git is a distributed version control system.** That one word — distributed — is what separates it from everything that came before it.

In older systems like CVS and SVN, there's one central server. Every developer connects to it to commit, to view history, to do anything meaningful [3]. If that server goes down, you're stuck. If you're on a flight, you're stuck. If the network is slow, you already know how that goes.

With Git, **every developer has a complete copy of the entire repository** — full history, all branches, every single commit — locally on their machine [3]. You commit locally. You branch locally. You diff locally. The network only gets involved when you want to share changes with others.

This sounds like a minor architectural choice. It's not. It changes how you think about development entirely.

A few things Git genuinely gets right technically:

- **Branching is cheap.** In SVN, branching copies the entire directory — slow and expensive. In Git, a branch is just a pointer to a commit, so creating or deleting one is essentially free [5].
- **Merging actually works.** Git tracks the exact ancestors of every commit, so when two branches diverge it knows what changed relative to the common base. SVN's merging was famously painful [5].
- **SHA-1 content hashing.** Every file, commit, and tree is identified by a cryptographic hash of its content [1]. You cannot silently corrupt data — Git will detect it.
- **Speed by design.** Most operations — log, diff, commit, branch switch — are local and therefore fast. Git was built for a project the size of the Linux kernel from day one [2].

![centralized vs distributed vcs](/images/posts/git-why-it-won-and-what-it-gets-wrong/centralized-vs-distributed-vcs.svg)

## Why SVN, Mercurial, CVS, and Perforce Lost

**CVS** — built in the 1980s — doesn't even support atomic commits [6]. If your commit crashes halfway through, the repository is left in a broken inconsistent state. It also has no real rename support. CVS wasn't so much beaten by Git as it was already dying before Git existed.

**SVN** fixed most of CVS's problems and was genuinely dominant for a while. But it's centralized, branching is expensive, and offline work is severely limited [6]. As development teams shifted to distributed models — open-source contributors across continents, multiple independent microservice teams, remote-first orgs — SVN's assumptions started to hurt. By 2025, SVN is mostly found in legacy enterprise codebases that nobody wants to touch [6].

**Mercurial** is the most interesting story and the one that should make Git fans at least a little humble. Mercurial launched the same year as Git, also in response to the BitKeeper incident [2]. It's arguably easier to use, and has a more consistent CLI. But Bitbucket dropped Mercurial support in 2020, which was effectively a death sentence [6]. Without a major hosting platform, Mercurial had no network effect. Today it sits at roughly 2% market share [6].

**Perforce** (Helix Core) is the only serious alternative still alive — but only in specific verticals: game development, finance, regulated enterprise. It handles large binary files better than Git and has centralized access controls that some enterprises require. It's expensive, proprietary, and not going anywhere fast.

| System | Architecture | Branching | Offline Work | Market Share 2025 |
|---|---|---|---|---|
| **Git** | Distributed | Cheap, instant | Full | ~94% |
| SVN | Centralized | Expensive | Very limited | ~5% |
| Mercurial | Distributed | Good | Full | ~2% |
| CVS | Centralized | Painful | None | Essentially dead |
| Perforce | Centralized | Moderate | Limited | Niche (games/enterprise) |

## GitHub Made the Win Permanent

Git won on technical merit. GitHub made it irreversible.

GitHub launched in 2007, just two years after Git [1]. It gave Git a social layer — pull requests, forks, code review, issue tracking. Open-source projects moved there. Companies followed. Then the entire ecosystem followed. CI/CD tools assumed GitHub. Hiring pipelines referenced GitHub profiles. Package registries linked to GitHub repos.

By the time Bitbucket and GitLab tried to compete, GitHub had network effects that were essentially unassailable. Mercurial being technically comparable didn't matter once GitHub existed. **The platform ate the tool.**

The 2025 Stack Overflow Developer Survey shows GitHub as the dominant collaboration platform at 81% usage among developers [11].

## What's Actually Bad About Git

Here's the part most tutorials skip, or cover with a one-line "Git has a steep learning curve" and move on.

**The CLI is a disaster of inconsistency.** `git checkout` used to handle both switching branches *and* discarding file changes — two completely unrelated operations, one command. They eventually had to split it into `git switch` and `git restore` [9]. Error messages are often cryptic. "Detached HEAD state" confuses people who've been using Git for years. The mental model required to understand rebase vs merge vs cherry-pick is genuinely nontrivial.

**Binary files are a genuine architectural mismatch.** Git stores the full content of every version of every file. Text files compress and delta-encode beautifully. A 100MB Photoshop file or a game asset does not [9]. Large binary-heavy repos balloon in size quickly. This is the actual reason game studios stick with Perforce — not preference, but a fundamental mismatch between Git's design and their data. Git LFS exists as a workaround, but it adds operational complexity and doesn't fully solve the problem.

**Monorepos break down at scale.** Companies running massive codebases with millions of files find that Git degrades badly. A single `git pull` on a 9GB repo can take six minutes [9]. Microsoft had to build their own virtual filesystem layer (VFS for Git, now Scalar) just to make Windows source development viable in Git. That's not a ringing endorsement of scalability.

**The "distributed" architecture collapsed into centralized in practice.** Git was designed peer-to-peer. In reality, every team pushes to GitHub, which has had 48 major outages in the past 12 months — roughly one significant disruption per week, with 257 total incidents between May 2025 and April 2026 [10]. The distributed design provides no real-world resilience when everyone's workflow is blocked by one service being down.

**AI-generated code is straining Git's assumptions hard.** GitHub saw 206% year-over-year growth in AI-generated projects in 2025 [10], and AI agents commit at a volume and frequency that humans never did. Git's merge conflict model, pull request workflow, and history semantics were designed for humans reading and writing code at human pace. The Register reported in May 2026 that "Git is unprepared for the AI coding tsunami" [8] — and looking at how Git currently handles this volume of automated commits, that assessment is hard to argue with.

Git won because it was the right tool at the right time, attached to the right project, and then locked in by the right platform. It's still the right tool for most things most of the time. It's also a 20-year-old design built for problems that have now shifted considerably.

> End

## Sources
1. [Git — Wikipedia](https://en.wikipedia.org/wiki/Git)
2. [The History of Git: The Road to Domination — Welcome to the Jungle](https://www.welcometothejungle.com/en/articles/btc-history-git)
3. [About Version Control — Git SCM](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
4. [What Is Version Control — Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/what-is-version-control)
5. [Git vs. Other Version Control Systems — GeeksforGeeks](https://www.geeksforgeeks.org/git/git-vs-other-version-control-systems-why-git-stands-out/)
6. [Version Control Systems Popularity in 2025 — RhodeCode](https://rhodecode.com/blog/156/version-control-systems-popularity-in-2025)
7. [Beyond Git: The Other Version Control Systems Developers Use — Stack Overflow Blog](https://stackoverflow.blog/2023/01/09/beyond-git-the-other-version-control-systems-developers-use/)
8. [Git Is Unprepared for the AI Coding Tsunami — The Register](https://www.theregister.com/devops/2026/05/15/git-is-unprepared-for-the-ai-coding-tsunami/5241480)
9. [Why Git Is Quietly Falling Behind in 2026 — Medium](https://medium.com/@kakamber07/why-git-is-quietly-failing-and-what-developers-dont-want-to-admit-yet-57dcb5242a07)
10. [GitHub Outages 2025–2026: Reliability Analysis — IncidentHub Blog](https://blog.incidenthub.cloud/github-reliability-outage-history-2025-2026)
11. [2025 Stack Overflow Developer Survey](https://survey.stackoverflow.co/2025/)