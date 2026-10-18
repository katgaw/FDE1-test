"""The single place where this repo talks to a model. Edit this file, not the notebooks.

Every notebook in modules 01-17 routes its model traffic through the functions below.
Routing is LiteLLM's job: the model id names the provider, so moving the whole repo to a
different one is a line in `.env` and no code change at all.

QUICK START
    Most people edit nothing in here. Fill in the repo-root `.env` and this works:

        OPENAI_API_KEY=...        # any non-empty string for an open self-hosted server
        OPENAI_BASE_URL=http://host:8000/v1
        LLM_MODEL=<chat-model-id>
        EMBED_BASE_URL=http://host:8080/v1
        EMBED_MODEL=<embedding-model-id>

    Run `python -m helpers.llm_call` to print what your environment resolves to.

CHOOSING A PROVIDER
    Prefix the model id with a LiteLLM route and that is the entire configuration -
    LiteLLM reads each provider's own credentials straight from the environment:

        LLM_MODEL=gpt-4o                              OpenAI, or any compatible server
        LLM_MODEL=anthropic/claude-sonnet-4-5         ANTHROPIC_API_KEY
        LLM_MODEL=azure/my-deployment                 AZURE_API_KEY, AZURE_API_BASE
                                                      (but see AZURE, below)
        LLM_MODEL=bedrock/anthropic.claude-...        the usual AWS credential chain
        LLM_MODEL=vertex_ai/gemini-2.5-pro            GOOGLE_APPLICATION_CREDENTIALS

    LiteLLM's provider docs list the variables for each. A bare model id is OpenAI, or
    an OpenAI-compatible server when OPENAI_BASE_URL is set.

    OPENAI_BASE_URL and OPENAI_API_KEY configure the OpenAI route and only that one. A
    route prefix hands the connection to LiteLLM, so those two are dropped rather than
    sent on to another provider, where an OpenAI key would override its own credential
    and fail with a 401. Azure is the exception, because it has a surface this repo can
    use end to end - see below.

AZURE, THE SHORT VERSION
    Azure OpenAI serves an OpenAI-compatible surface at `/openai/v1/` that needs no
    api-version, and every module in this repo can use it - the LangChain and Responses
    ones included. Point `.env` at your resource in whichever shape you have:

        OPENAI_API_KEY=<your Azure key>
        OPENAI_BASE_URL=https://<resource>.openai.azure.com
        LLM_MODEL=<your deployment name>        # a deployment, not a model family

    Any endpoint on an Azure host is rewritten onto `/openai/v1/`, so the resource root,
    the `/openai/deployments/<name>` data-plane path, and a URL already in v1 form all
    land in the same place. `AZURE_API_KEY` / `AZURE_OPENAI_ENDPOINT` are read as a
    fallback, and `LLM_MODEL=azure/<deployment>` is accepted and routed the same way.
    `AZURE_OPENAI_V1=false` opts out, back to LiteLLM's azure route - see `AZURE_V1`.

    Name the deployment after the model it serves. A deployment called `gpt-5-mini` gets
    reasoning budgets and constrained decoding; one called `prod-eastus-01` is a name
    nothing can read a capability out of, so both quietly degrade.

WHAT NOTEBOOKS CALL
    chat(messages) -> str                  one blocking turn
    chat_stream(messages)                  a stream for helpers.display.stream_md
    ask("question", system=...) -> str     single-prompt convenience
    structured(prompt, MySchema)           a validated Pydantic object back
    embed(texts) -> np.ndarray             L2-normalised embedding matrix

    Every function takes `role=` to choose a model: "chat" (default), "fast" (cheap and
    high-volume), "judge", "research", "writer", "app", "embed". Every role falls back to
    the chat model, so a one-model setup needs no extra configuration - see `ROLES`.

    Nothing here caps output tokens. Reasoning models spend tokens thinking before they
    answer and a cap truncates them mid-thought, so pass `max_tokens=` only if you mean it.

THE OPENAI-ONLY CORNERS
    Four things need an endpoint that speaks the OpenAI wire protocol, and raise a clear
    error on any other route:

        respond(), ask(effort=...)        the Responses API, reasoning budgets (02)
        langchain_chat/_embeddings        built on ChatOpenAI/OpenAIEmbeddings (03,05,07,13)
        openai_client()                   the raw SDK surface (02, 14)
        agents_sdk_model()                the OpenAI Agents SDK (12)

    OpenAI, Azure, and any OpenAI-compatible server are all fine here. To run them
    against something else, put an OpenAI-compatible gateway (a LiteLLM proxy, Bedrock
    Access Gateway) in front of it and set OPENAI_BASE_URL.

WHERE TO EDIT
    `resolve()` decides the model, endpoint, and credential for every call this repo
    makes. If your setup is stranger than a key and a base URL - a signed request, a
    gateway that mints short-lived tokens - override it in CUSTOM HOOKS at the bottom.
    Getting that one function right is enough.

NOT IN THIS FILE
    Behaviour built on top of these calls, all provider-independent:

        helpers/tools.py        tool specs and the tool-calling agent loop (06, 08, 11)
        helpers/judge.py        LLM-as-a-judge, and JSON extraction (04, 07, 08)
        helpers/guardrails.py   PII redaction and policy checks (12)

    Endpoints that are not LLM chat, and so keep their own configuration. If you move
    your models elsewhere, these still need a separate look:

        14_Voice_Agents/src/voice.py            STT_BASE, TTS_BASE, TTS_KEY - speech
        13_GraphRAG/msgraphrag/settings.yaml    GRAPHRAG_API_BASE and _KEY, read as YAML
                                                by a library in its own virtualenv
        10_Deep_Research, 11_Agent_Architecture TAVILY_API_KEY, WEB_SEARCH - search APIs
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, replace  # noqa: F401  (`replace` is for CUSTOM HOOKS)
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent

try:  # the explicit repo config wins over a stale shell value
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env", override=True)
    load_dotenv(override=False)
except ModuleNotFoundError:  # python-dotenv is optional; a pre-exported env still works
    pass


# A value still carrying an angle-bracket placeholder from .env.template, such as
# `<chat-model-id>` or `http://<your-llm-server>:8000/v1`, has not been filled in.
_PLACEHOLDER = re.compile(r"<[^>]+>")


def _env(*names: str) -> str | None:
    """First of `names` set to a real value.

    Copying `.env.template` and filling in only the lines you need is the documented
    workflow, so an untouched placeholder line has to read as unset. Otherwise a plain
    OpenAI user inherits the template's self-hosted `OPENAI_BASE_URL` and every call
    fails against a hostname that does not exist.
    """
    for n in names:
        v = (os.environ.get(n) or "").strip()
        if v and not _PLACEHOLDER.search(v):
            return v
    return None


DEFAULT_TIMEOUT = float(_env("LLM_TIMEOUT") or 600)
DEFAULT_MAX_RETRIES = int(_env("LLM_MAX_RETRIES") or 2)

# Used only when no model is configured at all, so a fresh clone with nothing but an
# OPENAI_API_KEY still runs. Against a custom endpoint there is nothing to guess - it
# serves whatever it was started with - so that case asks instead.
FALLBACK_CHAT_MODEL = "gpt-4o-mini"
FALLBACK_EMBED_MODEL = "text-embedding-3-small"

# LiteLLM route prefixes. A model id starting with one of these names its own provider,
# which is how `LLM_MODEL=vertex_ai/gemini-2.5-pro` works with no code change here.
LITELLM_ROUTES = frozenset(
    {
        "openai", "azure", "azure_ai", "anthropic", "bedrock", "vertex_ai", "gemini",
        "ollama", "hosted_vllm", "together_ai", "groq", "mistral", "cohere", "xai",
        "openrouter", "deepseek", "fireworks_ai", "cerebras", "sagemaker", "watsonx",
    }
)

# Hosts that serve Azure OpenAI. `cognitiveservices` is what newer resources get.
AZURE_HOSTS = (".openai.azure.com", ".cognitiveservices.azure.com")

# Azure OpenAI serves the OpenAI wire protocol at `/openai/v1/`, with no api-version and
# the deployment name in place of the model. That surface is the only Azure shape the
# section-5 functions can talk to, so by default any endpoint on an Azure host is
# rewritten onto it and `LLM_MODEL=azure/<deployment>` goes out as an ordinary
# OpenAI-compatible call. Set AZURE_OPENAI_V1=false for LiteLLM's azure route and the
# older api-version data plane instead, at the cost of modules 02, 03, 05, 07, 12-14.
AZURE_V1 = (_env("AZURE_OPENAI_V1") or "true").lower() not in ("0", "false", "no")


def _azure_v1(base: str | None) -> str | None:
    """An Azure OpenAI endpoint rewritten onto its `/openai/v1/` surface, else `None`.

    Accepts every shape Azure hands out - the bare resource host, the portal's resource
    root, the classic `/openai/deployments/<name>` data-plane path, a URL already in v1
    form - because which one someone pastes into `.env` should not decide whether half
    the repo works. `None` means "not an Azure host", so callers can tell that apart
    from "left alone".
    """
    if not base:
        return None
    parts = urlsplit(base if "://" in base else f"https://{base}")
    host = (parts.hostname or "").lower()
    if not host.endswith(AZURE_HOSTS):
        return None
    return f"{parts.scheme}://{parts.netloc}/openai/v1/"


# ======================================================================================
# 1. ROLES
# ======================================================================================
# The repo uses several models for different jobs. Each role names the environment
# variables it reads, in precedence order, and every role ends at the chat model so a
# single-model setup needs nothing extra. Add a role here and it is immediately
# available as `role="..."` on every function in this file.
ROLES: dict[str, dict[str, tuple[str, ...]]] = {
    # The main agent / assistant model.
    "chat": {
        "model": ("LLM_MODEL", "OPENAI_MODEL"),
        "base": ("OPENAI_BASE_URL", "LLM_API_BASE"),
        "key": ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"),
    },
    # Cheap and fast: synthetic data generation, knowledge-graph extraction, user
    # simulation. These make many calls, so a smaller model pays off.
    "fast": {
        "model": ("SDG_MODEL", "LLM_MODEL"),
        "base": ("RAGAS_BASE_URL", "OPENAI_BASE_URL"),
        "key": ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"),
    },
    # Evaluation. Deliberately separable from the model under test.
    "judge": {
        "model": ("JUDGE_MODEL", "RAGAS_MODEL", "SDG_MODEL", "LLM_MODEL"),
        "base": ("RAGAS_BASE_URL", "OPENAI_BASE_URL"),
        "key": ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"),
    },
    # Module 13's research graph: clarifying, briefing, planning, reflecting,
    # compressing. Many structured calls, so it is worth pointing somewhere cheap.
    "research": {
        "model": ("ODR_CHAT_MODEL", "LLM_MODEL"),
        "base": ("OPENAI_BASE_URL", "LLM_API_BASE"),
        "key": ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"),
    },
    # Long-form report writing (module 13's deep-research writer). Falls back through
    # the research model so setting ODR_CHAT_MODEL alone moves both.
    "writer": {
        "model": ("ODR_WRITER_MODEL", "ODR_CHAT_MODEL", "LLM_MODEL"),
        "base": ("OPENAI_BASE_URL", "LLM_API_BASE"),
        "key": ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"),
    },
    # The RAG application under test in module 07, kept separate from `chat` so the
    # pipeline and its judge can point at different servers.
    "app": {
        "model": ("RAGAS_MODEL", "LLM_MODEL"),
        "base": ("RAGAS_BASE_URL", "OPENAI_BASE_URL"),
        "key": ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"),
    },
    "embed": {
        "model": ("EMBED_MODEL",),
        "base": ("EMBED_BASE_URL", "OPENAI_BASE_URL"),
        "key": ("EMBED_API_KEY", "OPENAI_API_KEY"),
    },
}


@dataclass(frozen=True)
class Endpoint:
    """Everything needed to make one call. Frozen so it can be a cache key."""

    role: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES

    @property
    def provider(self) -> str:
        """The LiteLLM provider this model routes to. A bare model id means OpenAI."""
        head = self.model.split("/", 1)[0]
        return head if head in LITELLM_ROUTES else "openai"

    @property
    def route(self) -> str:
        """`model` as LiteLLM should see it.

        A bare id served from a custom `base_url` is prefixed `openai/`, which is how
        LiteLLM is told "this is an OpenAI-compatible server" rather than looking the
        name up in its model catalogue.
        """
        if self.model.split("/", 1)[0] in LITELLM_ROUTES:
            return self.model
        return f"openai/{self.model}" if self.base_url else self.model

    @property
    def sdk_model(self) -> str:
        """`model` as the OpenAI SDK should see it, with any route prefix stripped."""
        return self.model.split("/", 1)[1] if self.model.startswith("openai/") else self.model

    @property
    def is_openai_api(self) -> bool:
        """Whether the OpenAI SDK and LangChain's OpenAI classes can talk to this."""
        return self.provider == "openai"


def resolve(role: str = "chat", **overrides: Any) -> Endpoint:
    """Work out which model, endpoint, and credential a role should use.

    This is the seam. Every call in the repo passes through here, so overriding this
    function is enough to redirect all seventeen modules at once - see CUSTOM HOOKS.
    """
    if role not in ROLES:
        raise KeyError(f"Unknown role {role!r}. Known roles: {', '.join(ROLES)}")
    spec = ROLES[role]

    explicit_base = overrides.pop("base_url", None)
    explicit_key = overrides.pop("api_key", None)

    model = overrides.pop("model", None) or _env(*spec["model"])
    base = explicit_base or _env(*spec["base"])
    key = explicit_key or _env(*spec["key"])

    # Azure under its own variable names, as a fallback. Someone who configured Azure the
    # way Azure documents it - an endpoint and a key, no OPENAI_* anything - gets a
    # working repo without having to learn which names this file happens to read first.
    base = base or _env("AZURE_API_BASE", "AZURE_OPENAI_ENDPOINT")
    key = key or _env("AZURE_API_KEY", "AZURE_OPENAI_API_KEY")

    if AZURE_V1 and (azure_base := _azure_v1(base)):
        base = azure_base
        # On the v1 surface the deployment name is just the model, so the `azure/` route
        # prefix would send this to LiteLLM for no gain and cost the section-5 functions.
        if model and model.split("/", 1)[0] == "azure":
            model = model.split("/", 1)[1]

    if not model:
        if role == "embed":
            model = None if base else FALLBACK_EMBED_MODEL
            if not model:
                raise RuntimeError(
                    "No embedding model configured. Set EMBED_MODEL in your .env to the "
                    f"id your endpoint ({base}) serves."
                )
        else:
            model = FALLBACK_CHAT_MODEL

    ep = Endpoint(
        role=role,
        model=model,
        base_url=base,
        api_key=key,
        timeout=float(overrides.pop("timeout", DEFAULT_TIMEOUT)),
        max_retries=int(overrides.pop("max_retries", DEFAULT_MAX_RETRIES)),
    )

    # OPENAI_BASE_URL and OPENAI_API_KEY configure the OpenAI route, and only that one.
    # A model id carrying another route prefix means LiteLLM owns the connection and
    # reads that provider's own credential and endpoint from the environment
    # (AZURE_API_KEY/AZURE_API_BASE, the AWS chain, ANTHROPIC_API_KEY). Handing it an
    # inherited OpenAI key would override that and fail with a 401, so the inherited
    # values are dropped. Anything passed explicitly is the caller's business and stays,
    # which is what the CUSTOM HOOKS override relies on.
    if not ep.is_openai_api:
        ep = replace(ep, base_url=explicit_base, api_key=explicit_key)
    return ep


def model_name(role: str = "chat") -> str:
    """The model id for a role, for printing or passing to something that wants a string."""
    return resolve(role).model


def require(*names: str) -> None:
    """Assert environment variables are set, with a copy-pasteable hint."""
    missing = [n for n in names if not _env(n)]
    if missing:
        raise RuntimeError(
            f"Missing in your .env: {', '.join(missing)}. "
            "Copy .env.template to .env at the repo root and fill it in."
        )


# ======================================================================================
# 2. THE LITELLM CALL
# ======================================================================================
def _litellm():
    """LiteLLM, configured and imported lazily.

    Lazily because it is a heavy import and `describe()` has to stay reachable on a
    half-configured machine to explain what is wrong.
    """
    try:
        import litellm
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on the active venv
        raise RuntimeError(
            "LiteLLM is missing. Run `uv sync` at the repo root, or `uv add litellm` "
            "inside this module's own virtualenv."
        ) from exc
    litellm.suppress_debug_info = True
    litellm.drop_params = True  # silently ignore params a given provider rejects
    os.environ.setdefault("LITELLM_LOG", "ERROR")
    return litellm


def _messages(messages: str | Sequence[dict], system: str | None = None) -> list[dict]:
    """Accept a bare string or a message list; optionally prepend a system turn."""
    if isinstance(messages, str):
        out = [{"role": "user", "content": messages}]
    else:
        out = [dict(m) for m in messages]
    if system:
        out = [{"role": "system", "content": system}] + out
    return out


def _params(ep: Endpoint, **kw: Any) -> dict[str, Any]:
    """The LiteLLM arguments for one call: route, endpoint, credential, retries.

    `None` values are dropped, so a caller passing `temperature=None` means "whatever
    this server's default is" rather than sending a null.
    """
    params: dict[str, Any] = {
        "model": ep.route,
        "timeout": ep.timeout,
        "num_retries": ep.max_retries,
        **{k: v for k, v in kw.items() if v is not None},
    }
    if ep.base_url:
        params["api_base"] = ep.base_url
    if ep.api_key:
        # Omitted when unset so LiteLLM can read the provider's own credentials - an AWS
        # profile, an Azure key, a service account - from the environment itself.
        params["api_key"] = ep.api_key
    return params


def _text(resp) -> str:
    """The assistant text from an OpenAI-shaped response. LiteLLM matches this shape."""
    try:
        return (resp.choices[0].message.content or "").strip()
    except (AttributeError, IndexError, TypeError):
        return ""


def _parse_json(text: str):
    """Pulled in lazily: extraction lives in `helpers.judge`, which imports `chat` from
    here, so a module-level import would be circular."""
    from .judge import parse_json

    return parse_json(text)


# ======================================================================================
# 3. THE EVERYDAY CALLS
# ======================================================================================
def chat(
    messages: str | Sequence[dict],
    *,
    system: str | None = None,
    role: str = "chat",
    temperature: float | None = None,
    **kw: Any,
) -> str:
    """One blocking turn. Returns the assistant's text.

        chat("Summarise the EU AI Act in one line")
        chat(history, system="You are terse.", temperature=0)
        chat(prompt, role="judge")
    """
    return _text(chat_raw(messages, system=system, role=role, temperature=temperature, **kw))


def chat_stream(
    messages: str | Sequence[dict],
    *,
    system: str | None = None,
    role: str = "chat",
    temperature: float | None = None,
    **kw: Any,
):
    """The same call, streamed. Returns the raw chunk iterator.

    Hand it straight to the repo's renderers, which print as tokens arrive and return
    the finished text:

        from helpers.display import stream_md
        answer = stream_md(chat_stream("Explain Article 99"))
    """
    return chat_raw(messages, system=system, role=role, temperature=temperature, stream=True, **kw)


def chat_raw(
    messages: str | Sequence[dict],
    *,
    system: str | None = None,
    role: str = "chat",
    **kw: Any,
):
    """The full response object, for when you need usage, logprobs, or finish_reason."""
    ep = resolve(role, model=kw.pop("model", None))
    return _litellm().completion(**_params(ep, messages=_messages(messages, system), **kw))


def supports_reasoning_effort(model: str) -> bool:
    """True for gpt-5+ / o-series style models that accept Responses `reasoning.effort`."""
    m = (model or "").split("/")[-1].lower()
    return bool(re.match(r"(o[1-9]|gpt-5)", m) or "reasoning" in m)


def ask(
    prompt: str,
    *,
    instructions: str | None = None,
    system: str | None = None,
    effort: str | None = None,
    role: str = "chat",
    **kw: Any,
) -> str:
    """Single-prompt convenience with optional reasoning effort.

    `effort` ("low" / "medium" / "high") is passed through the Responses API where the
    provider supports it, and ignored where it does not, so module 02's reasoning demos
    degrade to an ordinary call against a self-hosted server instead of erroring.
    """
    guidance = instructions or system
    if effort and resolve(role, model=kw.get("model")).is_openai_api:
        try:
            resp = respond(prompt, instructions=guidance, effort=effort, role=role, **kw)
            return (getattr(resp, "output_text", "") or "").strip()
        except Exception:  # no Responses API on this server; fall through to chat
            pass
    return chat(prompt, system=guidance, role=role, **kw)


def respond(
    prompt: str | Sequence[dict],
    *,
    instructions: str | None = None,
    effort: str | None = None,
    role: str = "chat",
    **kw: Any,
):
    """A raw Responses API call, returning the SDK `Response` object.

    OpenAI-compatible endpoints only. Prefer `ask()` or `chat()`, which work everywhere.
    `effort` is sent only when the model looks like it supports reasoning budgets; if the
    API still rejects it, we retry once without `reasoning` so demos keep running on
    gpt-4o-mini and similar chat models.
    """
    ep = resolve(role, model=kw.pop("model", None))
    client = openai_client(role, model=ep.model)
    params: dict[str, Any] = {"model": ep.sdk_model, "input": prompt}
    if instructions is not None:
        params["instructions"] = instructions
    use_effort = effort is not None and supports_reasoning_effort(ep.model)
    if use_effort:
        params["reasoning"] = {"effort": effort}
    try:
        return client.responses.create(**params, **kw)
    except Exception as exc:  # noqa: BLE001 - provider SDKs raise several error types
        msg = str(exc).lower()
        if use_effort and "reasoning.effort" in msg and "unsupported" in msg:
            params.pop("reasoning", None)
            return client.responses.create(**params, **kw)
        raise


def structured(
    prompt: str | Sequence[dict],
    schema: type,
    *,
    instructions: str | None = None,
    role: str = "chat",
    **kw: Any,
):
    """Return a validated instance of a Pydantic model.

    Asks for constrained decoding where LiteLLM knows the model supports it, and falls
    back to putting the schema in the prompt, so the same call works on OpenAI, Azure,
    and a bare vLLM server that implements neither.
    """
    ep = resolve(role, model=kw.pop("model", None))
    messages = _messages(prompt, instructions)
    litellm = _litellm()

    try:
        native = bool(litellm.supports_response_schema(ep.route))
    except Exception:  # a self-hosted id LiteLLM has never heard of
        native = False
    if native:
        try:
            resp = litellm.completion(**_params(ep, messages=messages, response_format=schema), **kw)
            return schema.model_validate_json(_text(resp))
        except Exception:
            pass  # fall through and ask for the schema in words

    spec = json.dumps(schema.model_json_schema(), indent=2)
    text = chat(
        messages + [{"role": "user", "content": f"Reply with JSON matching this schema:\n{spec}"}],
        role=role,
        **kw,
    )
    payload = _parse_json(text)
    if payload is None:
        raise ValueError(f"Model did not return JSON for {schema.__name__}: {text[:200]}")
    return schema.model_validate(payload)


def chat_json(prompt: str | Sequence[dict], *, system: str | None = None, role: str = "chat", **kw):
    """One turn whose reply is parsed as JSON. Returns `None` if nothing parsed."""
    return _parse_json(chat(prompt, system=system, role=role, **kw))


# ======================================================================================
# 4. EMBEDDINGS
# ======================================================================================
def embed(
    texts: str | Sequence[str],
    *,
    role: str = "embed",
    batch: int = 64,
    normalize: bool = True,
    **overrides: Any,
):
    """Embed one string or many. Returns an `(n, d)` array, L2-normalised by default.

    Normalised vectors make a dot product a cosine similarity, which is what the RAG
    and memory modules assume.
    """
    import numpy as np

    single = isinstance(texts, str)
    items = [texts] if single else list(texts)
    if not items:
        return np.zeros((0, 0), dtype="float32")

    ep = resolve(role, **overrides)
    litellm = _litellm()
    vectors: list[list[float]] = []
    for i in range(0, len(items), batch):
        resp = litellm.embedding(**_params(ep, input=items[i : i + batch]))
        vectors.extend(d["embedding"] for d in resp["data"])

    arr = np.asarray(vectors, dtype="float32")
    if normalize:
        arr /= np.clip(np.linalg.norm(arr, axis=1, keepdims=True), 1e-12, None)
    return arr[0] if single else arr


# ======================================================================================
# 5. THE OPENAI-ONLY SURFACE
# ======================================================================================
# A few modules want the OpenAI SDK itself, or a LangChain class built on it. Those need
# an endpoint that speaks the OpenAI wire protocol; everything else above does not.
_clients: dict[tuple, Any] = {}


def _require_openai_api(ep: Endpoint, what: str) -> None:
    if ep.is_openai_api:
        return
    raise RuntimeError(
        f"{what} needs an OpenAI-compatible endpoint, but model {ep.model!r} routes to "
        f"{ep.provider!r}. Use chat() / chat_stream() / structured() / embed(), which go "
        "through LiteLLM and work on any provider, or put an OpenAI-compatible gateway "
        "(a LiteLLM proxy, Bedrock Access Gateway) in front of it and set OPENAI_BASE_URL."
    )


def openai_client(role: str = "chat", *, is_async: bool = False, **overrides: Any):
    """A cached `OpenAI` / `AsyncOpenAI` client.

    Modules 02 and 14 demonstrate the raw API surface - the Responses API,
    `chat.completions.create` - so they need a real client rather than `chat()`.
    """
    ep = resolve(role, **overrides)
    _require_openai_api(ep, "The OpenAI SDK")

    cache_key = (ep, is_async)
    if cache_key not in _clients:
        from openai import AsyncOpenAI, OpenAI

        cls = AsyncOpenAI if is_async else OpenAI
        _clients[cache_key] = cls(
            base_url=ep.base_url,
            api_key=ep.api_key or "EMPTY",
            timeout=ep.timeout,
            max_retries=ep.max_retries,
        )
    return _clients[cache_key]


def async_openai_client(role: str = "chat", **overrides: Any):
    """A cached `AsyncOpenAI` client. Used by modules 12 and 14."""
    return openai_client(role, is_async=True, **overrides)


def langchain_chat(role: str = "chat", *, temperature: float | None = None, **overrides: Any):
    """A LangChain chat model. Modules 03, 05, 07, and 13 pipe this into LCEL chains.

    Always `ChatOpenAI`, pointed at the resolved endpoint. Those modules lean on
    `.bind_tools()` and `.with_structured_output()`, which LangChain's generic LiteLLM
    wrapper does not implement as completely - so for a provider that is not
    OpenAI-compatible, front it with a LiteLLM proxy rather than swapping the class.
    """
    ep = resolve(role, **overrides)
    _require_openai_api(ep, "langchain_chat()")

    from langchain_openai import ChatOpenAI

    kwargs: dict[str, Any] = {
        "model": ep.sdk_model,
        "api_key": ep.api_key or "EMPTY",
        "timeout": ep.timeout,
        "max_retries": ep.max_retries,
    }
    if ep.base_url:
        kwargs["base_url"] = ep.base_url
    if temperature is not None:
        kwargs["temperature"] = temperature
    return ChatOpenAI(**kwargs)


def langchain_embeddings(role: str = "embed", **overrides: Any):
    """LangChain embeddings for the vector-store modules (05, 07).

    `check_embedding_ctx_length=False` is deliberate: it stops LangChain from splitting
    and re-averaging long inputs with a tokenizer it guessed, which self-hosted
    embedding servers handle themselves.
    """
    ep = resolve(role, **overrides)
    _require_openai_api(ep, "langchain_embeddings()")

    from langchain_openai import OpenAIEmbeddings

    kwargs: dict[str, Any] = {
        "model": ep.sdk_model,
        "api_key": ep.api_key or "EMPTY",
        "check_embedding_ctx_length": False,
    }
    if ep.base_url:
        kwargs["base_url"] = ep.base_url
    return OpenAIEmbeddings(**kwargs)


def agents_sdk_model(role: str = "chat", *, use_responses: bool | None = None, **overrides: Any) -> str:
    """Point the OpenAI Agents SDK at the configured endpoint (module 12).

    Installs our async client as the SDK default, disables tracing (it would otherwise
    phone home to OpenAI even against a local server), and returns the model name to
    pass as `Agent(model=...)`.

        acme_agent = Agent(name="...", model=agents_sdk_model(), tools=[...])
    """
    from agents import set_default_openai_api, set_default_openai_client, set_tracing_disabled

    ep = resolve(role, **overrides)
    set_default_openai_client(async_openai_client(role, **overrides), use_for_tracing=False)
    # The Responses API is an OpenAI feature; self-hosted servers need chat completions.
    responses = use_responses if use_responses is not None else not ep.base_url
    set_default_openai_api("responses" if responses else "chat_completions")
    set_tracing_disabled(True)
    return ep.sdk_model


# ======================================================================================
# 6. CUSTOM HOOKS
# ======================================================================================
# If your infrastructure does not fit a key and a base URL - a gateway that mints
# short-lived tokens, a signed request, a per-team routing rule - override `resolve()`
# here rather than touching the notebooks. Everything in this file, and therefore
# everything in modules 01-17, goes through it.
#
#     _stock_resolve = resolve
#
#     def resolve(role="chat", **overrides):
#         ep = _stock_resolve(role, **overrides)
#         return replace(ep, api_key=my_gateway_token(), base_url="https://gw.corp/v1")
#
# `replace` is imported at the top of this file for exactly that. To swap in a client the
# OpenAI SDK cannot build at all, override `openai_client()` the same way.


# ======================================================================================
# 7. DIAGNOSTICS
# ======================================================================================
def describe() -> str:
    """Show what your environment resolves to, per role. Run this first when something breaks."""
    lines = [
        f"{'role':<9} {'model':<32} {'litellm route':<34} endpoint",
        f"{'-' * 9} {'-' * 32} {'-' * 34} {'-' * 36}",
    ]
    for role in ROLES:
        try:
            ep = resolve(role)
            key = "set" if ep.api_key else "unset (provider env)"
            lines.append(
                f"{role:<9} {ep.model:<32} {ep.route:<34} "
                f"{ep.base_url or '<provider default>'} [key: {key}]"
            )
        except RuntimeError as exc:
            lines.append(f"{role:<9} {'-- not configured --':<32} {exc}")
    return "\n".join(lines)


def check_connection(role: str = "chat") -> bool:
    """Make one real call and report whether it worked."""
    try:
        reply = chat("Reply with the single word: ok", role=role, temperature=0.0)
    except Exception as exc:
        print(f"[{role}] FAILED  {type(exc).__name__}: {exc}")
        return False
    print(f"[{role}] ok  {resolve(role).model} -> {reply[:60]!r}")
    return True


def __getattr__(name: str):
    """Late-bound convenience constants, so `from helpers.llm_call import MODEL` works.

    Resolved on access rather than at import so that importing this file never fails on
    a half-configured environment - `describe()` needs to be reachable to explain why.
    """
    if name in ("MODEL", "LLM_MODEL"):
        return model_name("chat")
    if name == "EMBED_MODEL":
        return model_name("embed")
    if name == "JUDGE_MODEL":
        return model_name("judge")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # configuration
    "ROLES", "LITELLM_ROUTES", "Endpoint", "resolve", "model_name", "require",
    # everyday calls
    "chat", "chat_stream", "chat_raw", "ask", "respond", "structured", "chat_json",
    "supports_reasoning_effort",
    # embeddings
    "embed",
    # the OpenAI-only surface
    "openai_client", "async_openai_client", "langchain_chat", "langchain_embeddings",
    "agents_sdk_model",
    # diagnostics
    "describe", "check_connection",
]


if __name__ == "__main__":
    print(describe())
    print()
    check_connection("chat")
