"""The stateless Think-Act-Observe loop (the control flow the agent owns).

The loop — not the model — owns termination, via a hard MAX_STEPS cap. The model
routes to tools; tools (the data plane) return compact JSON; the model narrates.
Each call to `answer()` is a blank slate: no memory across questions.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from backend import config
from backend.tools import TOOL_SCHEMAS, dispatch

SYSTEM_PROMPT = (Path(__file__).resolve().parent / "prompt.md").read_text()


@dataclass
class AgentResult:
    answer: str
    trace: list[dict] = field(default_factory=list)  # [{tool, args, observation}]
    steps: int = 0
    stopped: str = "answered"


def answer(question: str, router=None, max_steps: int | None = None) -> AgentResult:
    if router is None:
        from backend.router import Router

        router = Router()
    max_steps = max_steps or config.MAX_STEPS

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace: list[dict] = []

    for step in range(1, max_steps + 1):
        msg = router.chat(messages, TOOL_SCHEMAS).choices[0].message
        calls = getattr(msg, "tool_calls", None)

        if not calls:
            return AgentResult(answer=msg.content or "", trace=trace, steps=step)

        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {
                            "name": c.function.name,
                            "arguments": c.function.arguments,
                        },
                    }
                    for c in calls
                ],
            }
        )
        for c in calls:
            try:
                args = json.loads(c.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            observation = dispatch(c.function.name, args)
            trace.append({"tool": c.function.name, "args": args, "observation": observation})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": c.id,
                    "content": json.dumps(observation),
                }
            )

    return AgentResult(
        answer="I couldn't finish within the step limit.",
        trace=trace,
        steps=max_steps,
        stopped="max_steps",
    )
