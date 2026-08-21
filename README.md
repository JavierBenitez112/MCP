# MCP Server — Wholesale distributor chatbot (CC3067 Redes, Proyecto 1)

Terminal host that talks to multiple MCP servers over hand-written
JSON-RPC 2.0 (no MCP SDK) and exposes their tools to Claude through the
Messages API. Full plan: `plan-maestro-proyecto1-mcp.md`.

**Status: Fase 1 done** — conversational host with a `tool_use`/`tool_result`
loop and JSONL logging. No real MCP server is wired in yet (Fase 2); a local
`demo__get_time` tool exists only to exercise the loop end to end.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set ANTHROPIC_API_KEY
```

## Run

```bash
python -m host.main
```

Try: "¿qué hora es?" — it should trigger the `demo__get_time` tool and you'll
see the call recorded in `logs/session.jsonl`.

## Project layout

```
host/            conversational core (Messages API loop, tool registry, JSONL logger)
mcp_clients/     transport layers — transport_stdio.py (Fase 2), transport_http.py (Fase 4)
distribuidora/   distributor MCP server — tools.py + SQLite backend (Fase 3, blocked on
                 the use case being confirmed with the professor)
docs/            protocol-notes.md, server-spec.md
logs/            JSONL interaction logs (gitignored)
```

## AI use disclosure

This project's scaffolding and Fase 1 host were built with Claude Code
assistance, per UVG's academic integrity policy. [Expand with specifics as
the project progresses.]
