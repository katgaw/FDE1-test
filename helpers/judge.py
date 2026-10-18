"""The LLM-as-a-judge you build from scratch in Demo 04, packaged so later demos can
reuse it without rebuilding it. Same idea: one LLM call, JSON in, a score + rationale out.

    from helpers.judge import make_judge
    relevance = make_judge("relevance",
        "Question: {question}\\nAnswer: {response}\\n\\nScore how well the answer "
        "addresses the question, 0-10.")
    relevance({"question": q, "response": a})   # -> {"judge", "score", "rationale"}

Also home to the JSON extraction the judges depend on (`parse_json`,
`parse_judge_json`), since pulling a clean object out of a chatty model reply is the
part that actually breaks in practice.

Provider-independent: the model call goes through `helpers.llm_call`, so point that at
your endpoint and this follows.
"""
from __future__ import annotations

import json

from .llm_call import chat


def _json_blocks(text: str) -> list[str]:
    """Every balanced `{...}` substring, ignoring braces inside string literals.

    Models wrap JSON in prose, fences, and reasoning. Scanning for balanced braces
    survives all of that, and skipping quoted regions means a `{` in the rationale text
    does not throw off the depth count.
    """
    blocks, depth, start, in_str, esc = [], 0, None, False, False
    for i, ch in enumerate(text or ""):
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = in_str
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(text[start : i + 1])
                start = None
    return blocks


def parse_json(text: str):
    """The first balanced `{...}` block that parses as JSON, else `None`."""
    for blob in _json_blocks(text or ""):
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            continue
    return None


def parse_judge_json(content: str) -> dict:
    """The last JSON block containing a "score", so a trailing correction wins."""
    for blob in reversed(_json_blocks(content or "")):
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "score" in obj:
            return obj
    return {"score": None, "rationale": f"<unparseable: {(content or '')[:80]}>"}


JUDGE_SYSTEM = (
    "You are a careful evaluator. Always reply with a JSON object: "
    '{"score": <integer 0-10>, "rationale": "<one short sentence>"}.'
)


def make_judge(
    name: str,
    template: str,
    *,
    needs_reference: bool = False,
    role: str = "judge",
    scale: tuple[int, int] = (0, 10),
):
    """Turn a prompt template into `judge(row) -> {judge, score, rationale}`.

    The template may use `{question}`, `{response}`, and `{reference}`. Substitution is
    by literal replacement rather than `str.format`, so a template that embeds JSON or
    set notation does not blow up on its own braces.
    """

    def judge(row: dict) -> dict:
        if needs_reference and not row.get("reference"):
            return {"judge": name, "score": None, "rationale": "<no reference>"}
        prompt = (
            template.replace("{question}", str(row.get("question", "")))
            .replace("{response}", str(row.get("response", "")))
            .replace("{reference}", str(row.get("reference") or ""))
        )
        system = JUDGE_SYSTEM if scale == (0, 10) else (
            "You are a careful evaluator. Always reply with a JSON object: "
            f'{{"score": <integer {scale[0]}-{scale[1]}>, "rationale": "<one short sentence>"}}.'
        )
        parsed = parse_judge_json(chat(prompt, system=system, role=role, temperature=0.0))
        return {"judge": name, "score": parsed.get("score"), "rationale": parsed.get("rationale", "")}

    judge.name = name
    return judge


__all__ = ["make_judge", "parse_judge_json", "parse_json", "JUDGE_SYSTEM"]
