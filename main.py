"""
Multi-agent orchestrator: routes a user message through the agent pipeline
and emits Server-Sent Events so the UI can stream each agent's output live.
"""
import json
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from agents import intake_agent, research_agent, document_agent, advisor_agent

app = FastAPI(title="AI Legal Aid – Multi-Agent System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list[dict]          # [{role, content}, ...]
    mode: str = "full"            # "intake" | "research" | "document" | "full"


# ── SSE helpers ─────────────────────────────────────────────────────────────

def _event(agent: str, text: str, done: bool = False) -> str:
    return json.dumps({"agent": agent, "text": text, "done": done})


async def _run_pipeline(messages: list[dict]) -> AsyncGenerator[str, None]:
    """Full 4-agent pipeline with streaming events."""
    try:
        # ── INTAKE ──
        yield _event("intake", "", done=False)
        intake_reply = await intake_agent(messages)
        yield _event("intake", intake_reply, done=True)

        await asyncio.sleep(0.05)

        research_messages = messages + [
            {"role": "assistant", "content": intake_reply},
            {"role": "user",      "content": "Please analyse the legal issues in my situation above."},
        ]

        # ── RESEARCH ──
        yield _event("research", "", done=False)
        research_reply = await research_agent(research_messages)
        yield _event("research", research_reply, done=True)

        await asyncio.sleep(0.05)

        document_messages = research_messages + [
            {"role": "assistant", "content": research_reply},
            {"role": "user",      "content": "What documents do I need and can you provide a draft or template?"},
        ]

        # ── DOCUMENT ──
        yield _event("document", "", done=False)
        document_reply = await document_agent(document_messages)
        yield _event("document", document_reply, done=True)

        await asyncio.sleep(0.05)

        advisor_messages = document_messages + [
            {"role": "assistant", "content": document_reply},
            {
                "role": "user",
                "content": (
                    "Based on everything above – the intake, legal research, and documents – "
                    "please provide me with a complete, actionable legal aid plan."
                ),
            },
        ]

        # ── ADVISOR ──
        yield _event("advisor", "", done=False)
        advisor_reply = await advisor_agent(advisor_messages)
        yield _event("advisor", advisor_reply, done=True)

        yield _event("system", "Pipeline complete.", done=True)

    except Exception as exc:
        yield _event("system", f"ERROR: {exc}", done=True)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    async def generator():
        async for event_data in _run_pipeline(req.messages):
            yield {"data": event_data}
    return EventSourceResponse(generator())


@app.post("/api/chat/single")
async def chat_single(req: ChatRequest):
    """Run a single agent (for direct mode queries)."""
    agent_map = {
        "intake":   intake_agent,
        "research": research_agent,
        "document": document_agent,
        "advisor":  advisor_agent,
    }
    fn = agent_map.get(req.mode, advisor_agent)
    reply = await fn(req.messages)
    return {"agent": req.mode, "reply": reply}


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Serve static frontend ─────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
