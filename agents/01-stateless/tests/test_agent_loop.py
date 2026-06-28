"""Loop control-flow tests using a stub router — no live LLM, no network.

Verifies the loop dispatches tool calls, records a trace, terminates on the
model's final message, and is bounded by MAX_STEPS (the loop owns termination).
"""
import json
from types import SimpleNamespace as NS

from backend import agent


def _resp(content=None, tool_calls=None):
    return NS(choices=[NS(message=NS(content=content, tool_calls=tool_calls))])


def _call(cid, name, args):
    return NS(id=cid, function=NS(name=name, arguments=json.dumps(args)))


class StubRouter:
    """Returns scripted responses in order; records the messages it was given."""

    def __init__(self, script):
        self._script = list(script)
        self.seen = []

    def chat(self, messages, tools):
        self.seen.append(messages)
        return self._script.pop(0)


def test_loop_dispatches_tool_then_answers():
    script = [
        _resp(tool_calls=[_call("c1", "compute_stat",
                                {"race": "full", "year": 2026, "metric": "count"})]),
        _resp(content="There were 2,102 finishers in the 2026 full marathon."),
    ]
    res = agent.answer("How many ran the 2026 marathon?", router=StubRouter(script))

    assert res.stopped == "answered"
    assert len(res.trace) == 1
    assert res.trace[0]["tool"] == "compute_stat"
    assert res.trace[0]["observation"]["n"] == 2102
    assert "2,102" in res.answer


def test_loop_is_bounded_by_max_steps():
    class LoopForever:
        def chat(self, messages, tools):
            return _resp(tool_calls=[_call("c", "list_columns", {})])

    res = agent.answer("anything", router=LoopForever(), max_steps=3)
    assert res.stopped == "max_steps"
    assert res.steps == 3


def test_final_answer_without_tools_terminates_immediately():
    res = agent.answer("hi", router=StubRouter([_resp(content="Hello.")]))
    assert res.stopped == "answered"
    assert res.trace == []
    assert res.answer == "Hello."
