# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Course material for "The Hive FDE Training": numbered, notebook-driven modules (`00_Prerequisites` guides, `01_First_Steps`, `02_Prompt_Engineering`, `03_Evals_LLM_as_Judge`, ...) that share one Python helper package, `helpers/`, and one corpus under `data/`. There is no application, test suite, or linter config; the deliverables are Jupyter notebooks and READMEs.

## Commands

Python 3.12 only (`requires-python >=3.12,<3.13`), managed with `uv`.

```bash
make setup    # uv sync
make check    # bash 00_Prerequisites/scripts/setup_check.sh (read-only; never installs anything). Windows: setup_check.ps1
make nb       # uv run jupyter notebook 01_First_Steps/S1_Enterprise_Dev_Environment.ipynb
python -m helpers.llm_call   # print which model/endpoint the current .env resolves to
```

Configuration: copy `.env.template` to `.env` (gitignored). The user supplies their own model, either a provider key, an OpenAI-compatible endpoint (`LLM_API_BASE`), or a local Ollama model. `LLM_MODEL` and `EMBED_MODEL` select the models.

## Architecture

- **`helpers/llm_call.py` is the single place the repo talks to a model.** It routes through LiteLLM, where the model id prefix (`anthropic/`, `azure/`, `bedrock/`, `ollama/`, ...) picks the provider, so switching providers is an `.env` change, not a code change. It exposes `chat`, `embed`, and `langchain_chat`. New code should call it directly rather than hardcoding a vendor SDK.
- **`helpers/config.py`** is a backward-compat layer over `llm_call` (`LLM_MODEL`, `LLM_BASE`, `KEY`, `DATA`, `require`) for notebooks not yet migrated. Don't add new logic here.
- **`helpers/nb.py`**: every notebook starts with `bootstrap()`, which walks up from the cwd to find the repo root (a directory with both `pyproject.toml` and `helpers/`), loads `.env`, and returns a `Config`. This keeps notebooks working regardless of where Jupyter was launched.
- **Dependency tiers.** `config.py` and `nb.py` are "Tier 1" (stdlib + python-dotenv only), and `preflight.py` is stdlib-only. They must not import litellm, numpy, or other heavy packages, because they run in minimal sandboxes and before installs succeed. `preflight.py` is deliberately built on hard wall-clock deadlines (DNS can hang on locked-down corporate networks), so keep that property when editing.
- Other helpers are per-module utilities: `guardrails.py` (PII redaction and policy checks, module 12), `judge.py` (LLM-as-judge, module 03), `rag.py`/`vectorstore.py` (RAG demos), `tools.py`, `display.py`/`ui.py`.
- **Data:** `data/` holds the shared EU AI Act corpus and `acme_corpus/` (fictional company docs); `03_Evals_LLM_as_Judge/data/` holds JSONL eval sets.

## Conventions worth knowing

- Notebooks are committed, so keep outputs and `.ipynb_checkpoints` noise out of diffs where possible.
- Dependency pins in `pyproject.toml` carry platform markers (for example Intel macOS torch/numpy/onnxruntime limits). Preserve these when bumping versions.
