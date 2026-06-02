+++
title       = "MCP Is Not Just an API Layer for AI"
description = "MCP feels like REST API calling for LLMs — but it's not. What Model Context Protocol actually is, why it's a protocol, and why Swagger doesn't replace it."
date        = "2026-06-02T20:47:54+05:30"
slug        = "what-is-mcp-model-context-protocol"
tags        = ["MCP", "AI", "API", "LLM", "Anthropic"]
keywords    = ["Model Context Protocol", "what is MCP", "MCP vs REST API", "MCP vs Swagger OpenAPI", "MCP explained"]
canonical   = "/posts/what-is-mcp-model-context-protocol/"
feature_image = "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200"
+++

Everyone calls MCP "just an API calling layer for AI". That framing is wrong — and it's exactly why the "we already have Swagger" objection keeps coming up. Both things need unpacking.

## What MCP Actually Is

MCP stands for Model Context Protocol. Anthropic announced it in November 2024 [1], and by December 2025 it was donated to the Linux Foundation under the Agentic AI Foundation, co-founded with Block and OpenAI [2]. That adoption speed alone is worth noting.

The one-liner: **MCP is a standard for how AI models discover and use external tools at runtime.**

It is built on JSON-RPC 2.0 [2]. Every message between an AI and its tools is a structured remote procedure call — not a REST endpoint, not a webhook. The wire format is always the same regardless of what the tool does or who built it.

An MCP server exposes exactly three kinds of things to a model [3]:

- **Tools** — callable functions. Think `get_weather(city)` or `create_github_issue(title, body)`.
- **Resources** — structured data the model can read. A file, a database row, a config object.
- **Prompts** — pre-baked templates that guide how the model should interact with the server.

The model can ask the server at runtime: *what can you do?* The server responds with a list of capabilities. The model picks from that list. This is called `ListToolsRequest` [4], and it's a core part of the protocol — not an optional feature someone bolted on.

## Why "Protocol" and Not Just "API"

An API is a surface — a set of endpoints or functions you call. A protocol is a contract about *how communication happens*, covering transport, message lifecycle, error format, capability negotiation, and session management.

HTTP is a protocol. REST is an architectural style layered on top. MCP is a protocol.

Here is specifically what MCP defines that earns it that label:

- **Transport layer** — three options: STDIO for local tools running as subprocesses, HTTP+SSE for remote tools, WebSocket for full-duplex interactivity [5].
- **Session lifecycle** — a handshake where client and server negotiate capabilities once, then maintain a stateful session. Every subsequent JSON-RPC call is faster because there's no renegotiation [5].
- **Capability negotiation** — the server declares what version it speaks, what primitives it exposes, what it supports. The client adapts.
- **Standardized error format** — same structure, always. No custom error schemas.

Compare this to a REST API. Each one invents its own auth scheme, its own pagination strategy, its own error codes, its own versioning. A developer reads the docs and writes adapter code. MCP mandates standard patterns for all of this [4].

The closest analogy is LSP — Language Server Protocol [2]. Your IDE doesn't need separate plugins for "how to talk to the Python language server" vs "how to talk to the TypeScript language server". LSP defines the conversation shape. Every language server speaks it. MCP does the same thing for AI tools.

![mcp architecture](/images/posts/what-is-mcp-model-context-protocol/mcp-architecture.svg)

Notice where OpenAPI sits in this picture — *inside* the MCP server, not competing with it.

## The "We Already Have Swagger" Objection

This is the most common pushback. The argument: OpenAPI already describes all my endpoints. An AI can read that spec and call the API. Why add MCP on top?

Fair question. Wrong conclusion.

**OpenAPI is a documentation format written for humans.** It describes your API so a developer can read it and write code against it. Descriptions assume human context. Auth patterns, pagination, error codes — however the team felt like doing them [6].

Put an LLM in front of a raw OpenAPI spec and several things break immediately:

- The GitHub API has over 600 endpoints [7]. Ask an LLM to pick the right one and it gets confused — too many choices, too much ambiguity in descriptions written for human developers.
- OpenAPI has no standardised runtime discovery. You hand the LLM a static spec file upfront. MCP's `ListToolsRequest` happens live, every session, with the server controlling exactly what it exposes.
- Every REST API uses custom auth, custom pagination, custom error shapes. Your LLM needs bespoke adapter code for each. MCP mandates standard patterns [4].
- Agents routinely misinterpret OpenAPI parameter constraints and invent fields that don't exist [6]. Descriptions written for developers are not the same as descriptions written for agent decision-making.

Here is the comparison laid flat:

| Aspect | OpenAPI / Swagger | MCP |
|---|---|---|
| Primary audience | Human developer | AI agent (LLM) |
| Discovery | Static spec file | Runtime `ListToolsRequest` |
| Session state | Stateless HTTP | Stateful session |
| Transport options | HTTP / REST | STDIO, HTTP+SSE, WebSocket |
| Auth pattern | Each API decides | Standardised in protocol |
| Descriptions written for | Developer reading docs | Agent making tool choices |
| Works across all tools uniformly? | No — bespoke adapters | Yes — single protocol |

They are not enemies. An MCP server can, and often does, wrap an existing REST API internally. Tools like FastMCP can auto-generate an MCP server straight from an OpenAPI spec [8]. The MCP server becomes a curated, agent-friendly façade on top of your existing API. You keep OpenAPI for developer-facing docs. You add MCP for agent-facing interaction.

## The N×M Problem

Before MCP, connecting AI assistants to external tools was an N×M problem [1]:

- **N** = number of AI models and assistants
- **M** = number of tools and data sources

Every combination needed its own integration. Claude's GitHub adapter wouldn't work with Cursor. The Cursor adapter wouldn't work with the next agent. Every team wrote glue code from scratch, separately.

MCP turns it into N+M. **Build one MCP server for GitHub — it works with any MCP client.** Claude, Cursor, Windsurf, any agent that speaks the protocol. This is the actual value proposition — not "it calls APIs" but "it's the universal connector shape so you write the adapter once."

## One Thing Worth Knowing

You can auto-generate an MCP server from an existing OpenAPI spec in a few minutes [8]. Sounds great. But every serious writeup on this warns the same thing: **prune aggressively afterward** [7]. A 600-endpoint GitHub MCP server is a disaster for an LLM. A 12-tool curated one works beautifully. The generation gets you started. The curation is the actual work.

Under the hood, MCP is JSON-RPC calls over a pipe or an HTTP stream — not magic. But the protocol is the point: the same conversation shape everywhere, with stateful sessions, runtime discovery, and standard error handling. That's what makes AI agents actually composable across tools and providers.

> End

## Sources
1. [Introducing the Model Context Protocol — Anthropic](https://www.anthropic.com/news/model-context-protocol)
2. [Model Context Protocol — Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)
3. [Model Context Protocol (MCP) an overview — Phil Schmid](https://www.philschmid.de/mcp-introduction)
4. [MCP vs APIs: What's the Real Difference? — freeCodeCamp](https://www.freecodecamp.org/news/mcp-vs-apis-whats-the-real-difference/)
5. [Architecture overview — Model Context Protocol](https://modelcontextprotocol.io/docs/learn/architecture)
6. [Exposing OpenAPI as MCP Tools — Christian Posta](https://blog.christianposta.com/semantics-matter-exposing-openapi-as-mcp-tools/)
7. [Auto-generating MCP Servers from OpenAPI Schemas: Yay or Nay? — Neon](https://neon.com/blog/autogenerating-mcp-servers-openai-schemas)
8. [From OpenAPI (Swagger) to MCP Servers — La Rebelion](https://rebelion.la/from-swagger-to-mcp)