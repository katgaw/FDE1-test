"""Rendering model output in a Jupyter cell, including live streaming.

Strings are markdown. Streaming repaints the cell through an IPython display handle.

Tier 1: stdlib + IPython only.
"""

from __future__ import annotations

import time

# How often to repaint while streaming. Every token is far too chatty over SSH or a
# remote kernel and makes the cell feel laggy rather than fast.
_REPAINT_SECONDS = 0.08


def show(*parts: object) -> None:
    """Render one or more values as cell output.

    Strings are treated as markdown, so `show("**done**")` does what it looks like.
    """
    from IPython.display import Markdown, display

    for part in parts:
        display(Markdown(part) if isinstance(part, str) else part)


def _deltas(chunk) -> tuple[str, str]:
    """Pull (content, reasoning) out of one streamed chunk.

    Reasoning models expose their chain of thought as `delta.reasoning` (OpenAI
    style) or `delta.reasoning_content` (vLLM style). Providers that don't reason
    simply never populate either.
    """
    try:
        delta = chunk.choices[0].delta
    except (AttributeError, IndexError):
        return "", ""
    content = getattr(delta, "content", None) or ""
    reasoning = (
        getattr(delta, "reasoning", None)
        or getattr(delta, "reasoning_content", None)
        or ""
    )
    return content, reasoning


def _render(answer: str, reasoning: str, show_reasoning: bool) -> str:
    if reasoning and show_reasoning:
        quoted = "\n".join(
            f"> {line}" if line else ">" for line in reasoning.splitlines()
        )
        return f"{quoted}\n\n{answer}"
    return answer


def stream_md(stream, *, show_reasoning: bool = True) -> str:
    """Render a streaming completion live, and return the finished text.

    While the model thinks, its reasoning shows in a blockquote above the answer;
    that block is wiped when the stream ends, so the saved notebook keeps only the
    answer.

        reply = stream_md(completion(**cfg.kwargs(), messages=msgs, stream=True))
    """
    from IPython.display import Markdown, display

    answer, reasoning, last = "", "", 0.0
    handle = display(Markdown(""), display_id=True)

    for chunk in stream:
        content, thought = _deltas(chunk)
        answer += content
        reasoning += thought

        now = time.monotonic()
        if (content or thought) and now - last >= _REPAINT_SECONDS:
            handle.update(Markdown(_render(answer, reasoning, show_reasoning)))
            last = now

    handle.update(Markdown(answer))
    return answer


def stream_lc(prompt, llm, *, show_reasoning: bool = True) -> str:
    """Stream a LangChain prompt through the chat client, keeping reasoning visible.

    ChatOpenAI streaming drops the reasoning field, so a chain can sit blank while the
    model thinks. `prompt` is what a prompt chain returns from `build.invoke(...)`.
    """
    from helpers.llm_call import chat_stream

    messages = prompt.to_messages() if hasattr(prompt, "to_messages") else prompt
    payload = []
    for message in messages:
        role = getattr(message, "type", "user")
        role = {"human": "user", "ai": "assistant"}.get(role, role)
        payload.append({"role": role, "content": getattr(message, "content", message)})

    model = getattr(llm, "model_name", None) or getattr(llm, "model", None)
    temperature = getattr(llm, "temperature", None)
    extra = {"model": model} if model else {}
    if temperature is not None:
        extra["temperature"] = temperature
    return stream_md(chat_stream(payload, **extra), show_reasoning=show_reasoning)


def stream_chat(stream, *, show_reasoning: bool = True) -> dict:
    """Like `stream_md`, but also assembles streamed tool-call fragments.

    Returns `{"content": str, "tool_calls": [...]}` so an agent loop can act on the
    calls. Tool calls arrive in pieces across chunks — index, then name, then the
    arguments a few characters at a time — so they have to be stitched by index.
    """
    from IPython.display import Markdown, display

    answer, reasoning, last = "", "", 0.0
    calls: dict[int, dict] = {}
    handle = display(Markdown(""), display_id=True)

    for chunk in stream:
        content, thought = _deltas(chunk)
        answer += content
        reasoning += thought

        try:
            fragments = chunk.choices[0].delta.tool_calls or []
        except (AttributeError, IndexError):
            fragments = []

        for fragment in fragments:
            slot = calls.setdefault(
                fragment.index, {"id": None, "name": "", "arguments": ""}
            )
            if getattr(fragment, "id", None):
                slot["id"] = fragment.id
            function = getattr(fragment, "function", None)
            if function is not None:
                slot["name"] += getattr(function, "name", None) or ""
                slot["arguments"] += getattr(function, "arguments", None) or ""

        now = time.monotonic()
        if (content or thought) and now - last >= _REPAINT_SECONDS:
            handle.update(Markdown(_render(answer, reasoning, show_reasoning)))
            last = now

    handle.update(Markdown(answer))
    return {
        "content": answer,
        "tool_calls": [calls[i] for i in sorted(calls)],
    }
