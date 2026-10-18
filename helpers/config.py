"""What a notebook needs to know about where it is and which model to call.

Tier 1: stdlib + python-dotenv only. Nothing here may import litellm, numpy, or
anything else heavy — every notebook imports this, including the ones running in a
minimal sandbox.

This module is also a thin compatibility layer over `helpers.llm_call`, which is the
single place the repo decides which model to call and how to reach it. The names below
are kept so notebooks that have not been migrated yet keep working unchanged:

    import sys; sys.path.insert(0, "..")        # put the repo root on the path
    from helpers.config import LLM_MODEL, LLM_BASE, KEY, DATA, require

New code should skip this module and call `helpers.llm_call` directly, which works
across OpenAI, Azure, Bedrock, and Anthropic rather than assuming one OpenAI-compatible
endpoint:

    from helpers.llm_call import chat, embed, langchain_chat

Because these are resolved through `llm_call`, pointing `LLM_MODEL` at another provider
(say `azure/my-deployment`) also redirects every un-migrated notebook that reads
`LLM_BASE` / `LLM_MODEL` from here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from . import llm_call
from .llm_call import ROOT, require  # noqa: F401  (re-exported for existing callers)

DATA = ROOT / "data"                 # shared corpus: eu_ai_act.md + eu_ai_act_summary.md

@dataclass(frozen=True)
class Config:
    """Paths and model settings, resolved once per notebook."""

    root: Path          # repo root — the directory holding pyproject.toml
    data: Path          # our instructional corpus
    use_case: Path      # the student's own work, when a project defines one

    llm_model: str
    api_base: str | None
    embed_model: str
    embed_api_base: str | None

    def kwargs(self) -> dict:
        """LiteLLM kwargs for this config. Spread into completion(**cfg.kwargs())."""
        out = {"model": self.llm_model}
        if self.api_base:
            out["api_base"] = self.api_base
        return out

    @property
    def has_injection_endpoint(self) -> bool:
        """True when the shared chat model from `.env` is configured.

        Prompt-injection cells use the same endpoint as every other notebook
        (`LLM_MODEL` via `nb.bootstrap()`), not a separate local model.
        """
        return bool(self.llm_model)

    @property
    def injection_model(self) -> str:
        return self.llm_model

    @property
    def injection_api_base(self) -> str | None:
        return self.api_base

    def injection_kwargs(self) -> dict:
        """LiteLLM kwargs for attack cells. Same chat endpoint as `kwargs()`."""
        return self.kwargs()

    def embed_kwargs(self) -> dict:
        """LiteLLM kwargs for embeddings.

        Separate from `kwargs()` because the embedding endpoint is often a
        different host from the chat one — a firm may serve embeddings locally
        while chat goes through a gateway, or the reverse.
        """
        out = {"model": self.embed_model}
        if self.embed_api_base:
            out["api_base"] = self.embed_api_base
        return out

    def __str__(self) -> str:
        where = f" @ {self.api_base}" if self.api_base else ""
        return f"{self.llm_model}{where}"


def from_env(root: Path) -> Config:
    return Config(
        root=root,
        data=root / "data",
        use_case=root / "use_case",
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        api_base=os.getenv("LLM_API_BASE"),
        embed_model=os.getenv("EMBED_MODEL", "text-embedding-3-small"),
        # Falls back to the chat endpoint, which is right for hosted providers
        # and for most single-gateway setups.
        embed_api_base=os.getenv("EMBED_API_BASE") or os.getenv("LLM_API_BASE"),
    )


def _field(role: str, attr: str):
    """One resolved endpoint field, or None if that role is not configured.

    Import of this module must never fail on a half-configured environment - the
    notebooks import it before they get a chance to print a helpful message.
    """
    try:
        return getattr(llm_call.resolve(role), attr)
    except (RuntimeError, KeyError):
        return None


# Any non-empty key works against the open self-hosted servers; on Azure and Bedrock the
# credential comes from that provider's own variables instead.
KEY = _field("chat", "api_key") or "EMPTY"

# Chat LLM (Demos 03-04)
LLM_MODEL = _field("chat", "model")
LLM_BASE = _field("chat", "base_url")

# Embeddings for modules that use an OpenAI-compatible embedding service
EMBED_MODEL = _field("embed", "model")
EMBED_BASE = _field("embed", "base_url")

# Chat LLM for Demo 07's RAGAS work (separate so it can pick its own model)
RAGAS_MODEL = _field("app", "model")
RAGAS_BASE = _field("app", "base_url")

# Optional remote Qdrant URL for legacy/shared RAG modules; Module 08 uses Chroma directly
QDRANT_URL = os.environ.get("VECTOR_STORE")

# Web search (optional)
WEB_SEARCH = os.environ.get("WEB_SEARCH")

# Cohere reranking (Demo 05). COHERE_BASE_URL is optional; set it for Azure AI
# Cohere deployments that expose a dedicated endpoint.
COHERE_BASE = os.environ.get("COHERE_BASE_URL") or os.environ.get("COHERE_URL")

