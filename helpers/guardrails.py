"""Input and output guardrails: scrub PII, and check text against a policy.

Used by module 12. Provider-independent — the LLM-backed checks go through
`helpers.llm_call`, so configure your endpoint there.

    from helpers.guardrails import redact_pii, make_guardrail, check_guardrails

    safe = redact_pii(user_input)          # -> Redaction(text=..., found={...})
    scope = make_guardrail("scope", "Text must be about ACME company business.")
    if not scope(safe.text):              # a tripped guardrail is falsy
        ...
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .llm_call import chat
from .judge import parse_json

PII_PATTERNS = {
    "email": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    "phone": r"\b(?:\+?\d{1,2}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
    "account": r"\b(?:acct|account)[\s#:-]*\d{6,}\b",
    "aws_key": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "api_key": r"\b(?:sk|pk)-[A-Za-z0-9_-]{16,}\b",
}


@dataclass
class Redaction:
    """The result of scrubbing a string: what to send on, and what was removed."""

    text: str
    found: dict[str, list[str]]

    @property
    def clean(self) -> bool:
        return not self.found

    def __str__(self) -> str:
        return self.text


def redact_pii(text: str, patterns: dict[str, str] | None = None) -> Redaction:
    """Replace PII with `[REDACTED_KIND]` placeholders before the text reaches a model.

    Regexes catch the obvious shapes and cost nothing. For production, run Presidio or
    an equivalent NER-based scrubber - names and addresses have no regex.
    """
    found: dict[str, list[str]] = {}
    out = text
    for kind, pattern in (patterns or PII_PATTERNS).items():
        hits = re.findall(pattern, out)
        if hits:
            found[kind] = [h if isinstance(h, str) else "".join(h) for h in hits]
            out = re.sub(pattern, f"[REDACTED_{kind.upper()}]", out)
    return Redaction(text=out, found=found)


@dataclass
class Verdict:
    """A guardrail decision. Falsy when the guardrail trips, so `if not verdict:` reads well."""

    allowed: bool
    reason: str = ""
    guardrail: str = ""

    def __bool__(self) -> bool:
        return self.allowed


GUARDRAIL_SYSTEM = (
    "You are a strict policy checker. Judge only whether the text violates the stated "
    'policy. Reply with a JSON object: {"violation": <true|false>, '
    '"reason": "<one short sentence>"}.'
)


def make_guardrail(name: str, policy: str, *, role: str = "fast", patterns: Sequence[str] = ()):
    """Build `guard(text) -> Verdict` from a policy in plain English.

    Regex `patterns` are checked first and short-circuit the model call, which keeps the
    obvious jailbreak attempts free. Anything subtler goes to the model. Uses the "fast"
    role because guardrails run on every request.

        scope = make_guardrail("scope", "Text must be about ACME company business.",
                               patterns=[r"ignore (all )?previous instructions"])
    """
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]

    def guard(text: str) -> Verdict:
        for rx in compiled:
            if rx.search(text or ""):
                return Verdict(False, f"matched blocked pattern {rx.pattern!r}", name)
        reply = chat(
            f"Policy: {policy}\n\nText:\n{text}",
            system=GUARDRAIL_SYSTEM,
            role=role,
            temperature=0.0,
        )
        parsed = parse_json(reply) or {}
        violated = bool(parsed.get("violation"))
        return Verdict(not violated, str(parsed.get("reason", "")), name)

    guard.name = name
    return guard


def check_guardrails(text: str, guards: Iterable[Callable[[str], Verdict]]) -> Verdict:
    """Run guardrails in order and return the first failure, else an allowing verdict."""
    for guard in guards:
        verdict = guard(text)
        if not verdict.allowed:
            return verdict
    return Verdict(True)


__all__ = ["redact_pii", "Redaction", "PII_PATTERNS", "make_guardrail",
           "check_guardrails", "Verdict", "GUARDRAIL_SYSTEM"]
