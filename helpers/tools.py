"""Tool calling: build tool specs, take one tool turn, or run the whole agent loop.

Used by the agentic modules (06, 08, 11). Nothing here knows or cares which provider
you are on — it goes through `helpers.llm_call`, so configure your endpoint there and
this works unchanged.

    from helpers.tools import tool_schema, run_tools

    TOOLS = [tool_schema("get_article", "Return a numbered Article of the EU AI Act.",
                         {"number": {"type": "integer"}}, ["number"])]

    result = run_tools("What are the fines?", TOOLS, {"get_article": get_article})
    result["answer"]   # the final text
    result["steps"]    # every tool call and its result - the trajectory to evaluate
"""
from __future__ import annotations

import json
from typing import Any, Callable, Iterable, Sequence

from .llm_call import chat_raw, chat_stream


def tool_schema(
    name: str,
    description: str,
    properties: dict[str, Any] | None = None,
    required: Sequence[str] | None = None,
) -> dict:
    """Build one OpenAI function-calling tool spec.

        tool_schema("get_article", "Return a numbered Article of the EU AI Act.",
                    {"number": {"type": "integer"}}, ["number"])

    `required` defaults to every property, which is what you almost always want: an
    optional argument the model can silently omit is a common source of tool bugs.
    """
    props = properties or {}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": list(required if required is not None else props),
            },
        },
    }


def tools_from_mcp(discovered: Iterable[Any]) -> list[dict]:
    """Convert MCP `list_tools()` results into function-calling specs (module 11)."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema or {"type": "object", "properties": {}},
            },
        }
        for t in discovered
    ]


def chat_tools(
    messages: str | Sequence[dict],
    tools: Sequence[dict] | None = None,
    *,
    system: str | None = None,
    role: str = "chat",
    temperature: float | None = 0,
    tool_choice: str = "auto",
    stream: bool = False,
    **kw: Any,
) -> dict:
    """One turn that may ask for tool calls.

    Returns `{"content": str, "tool_calls": [{"id", "name", "arguments"}], "raw": msg}`
    with `arguments` already JSON-decoded. Normalising that shape here is what lets
    modules 06, 08, and 11 share one agent loop across every provider.
    """
    if tools:
        kw["tools"] = list(tools)
        kw["tool_choice"] = tool_choice

    if stream:
        from .display import stream_chat  # prints as it goes, returns the assembled message

        return stream_chat(chat_stream(messages, system=system, role=role,
                                       temperature=temperature, **kw))

    msg = chat_raw(messages, system=system, role=role,
                   temperature=temperature, **kw).choices[0].message
    calls = []
    for call in getattr(msg, "tool_calls", None) or []:
        raw = call.function.arguments
        try:
            args = json.loads(raw) if isinstance(raw, str) else (raw or {})
        except json.JSONDecodeError:
            args = {}
        calls.append({"id": call.id, "name": call.function.name, "arguments": args})
    return {"content": msg.content or "", "tool_calls": calls, "raw": msg}


def run_tools(
    messages: str | Sequence[dict],
    tools: Sequence[dict],
    funcs: dict[str, Callable[..., Any]],
    *,
    system: str | None = None,
    role: str = "chat",
    temperature: float | None = 0,
    max_turns: int = 8,
    on_step: Callable[[dict], None] | None = None,
    **kw: Any,
) -> dict:
    """The tool-calling agent loop: call the model, run what it asks for, repeat.

    `funcs` maps tool name to the Python callable that implements it. Returns
    `{"answer", "messages", "steps", "turns"}`; `steps` records each tool call and its
    result, which is the trajectory module 08 evaluates.
    """
    from .llm_call import _messages  # same normalisation the plain calls use

    history = _messages(messages, system)
    steps: list[dict] = []

    for turn in range(max_turns):
        reply = chat_tools(history, tools, role=role, temperature=temperature, **kw)
        if not reply["tool_calls"]:
            history.append({"role": "assistant", "content": reply["content"]})
            return {
                "answer": reply["content"].strip(),
                "messages": history,
                "steps": steps,
                "turns": turn + 1,
            }

        history.append(
            {
                "role": "assistant",
                "content": reply["content"],
                "tool_calls": [
                    {
                        "id": c["id"],
                        "type": "function",
                        "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])},
                    }
                    for c in reply["tool_calls"]
                ],
            }
        )

        for call in reply["tool_calls"]:
            fn = funcs.get(call["name"])
            try:
                result = fn(**call["arguments"]) if fn else f"No such tool: {call['name']}"
            except Exception as exc:  # a tool crash is information, not a dead end
                result = f"Tool error: {type(exc).__name__}: {exc}"
            step = {"tool": call["name"], "arguments": call["arguments"], "result": str(result)}
            steps.append(step)
            if on_step:
                on_step(step)
            history.append({"role": "tool", "tool_call_id": call["id"], "content": str(result)})

    return {
        "answer": "<hit the turn limit without a final answer>",
        "messages": history,
        "steps": steps,
        "turns": max_turns,
    }


__all__ = ["tool_schema", "tools_from_mcp", "chat_tools", "run_tools"]
