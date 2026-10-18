# Prompt Engineering Patterns — From Scratch

## 🏗️ Build | 🚢 Ship | 📤 Share

### 🏗️ Build
A thin helper layer on top of OpenAI's Responses API, plus seven prompt patterns — each demonstrated on a consulting-flavored task with a weak→strong comparison where it matters.

### 🚢 Ship
Apply two or three of these patterns to your group project's real prompts. Keep the before/after so you can explain the improvement to a client.

### 📤 Share
Which pattern moved your task the most, and why do you think that was?

---

## Student mission brief

Your client does not need a clever prompt. They need a reliable behavior they can reuse. Your job is to learn the prompt patterns that make model outputs clearer, more structured, easier to compare, and easier to improve.

Plain English first: prompt engineering is not magic wording. It is task design: role, examples, context, output shape, critique, and cost control.

---

## What this is

A from-scratch tour of prompt engineering: no prompt-management platform, no agent framework, just the OpenAI SDK and seven patterns that work. You'll see *why* each pattern helps by watching the weak version fail first, and you'll end with a reasoning-budget readout that puts a number on the cost/quality tradeoff.

> **Why this matters to you as an Towerbrook consultant:** Prompting is the cheapest and fastest lever you have before fine-tuning or new infrastructure. Every AI solution you deliver depends on prompts that were *engineered* — not guessed. This notebook is the smallest version of that, and the larger tools (prompt-management platforms, agent loops, automated evals) are the same ideas scaled up.

---

## Prerequisites

- Python 3.11+ and an `OPENAI_API_KEY` in the repo-root `.env`
- A recent `openai` SDK — this demo uses the **Responses API**, which requires `openai>=1.60` (the pin in `pyproject.toml` has been updated; run `uv sync` if you haven't already)
- Familiarity with the chat message format (`system` / `user` / `assistant`)

---

## Setup

```bash
cp ../.env.template ../.env   # add your OPENAI_API_KEY
uv sync                        # or: pip install -e ..
uv run jupyter lab            # then open Prompt_Engineering_Patterns.ipynb
```

---

## The patterns

| # | Pattern | What it does | When to use |
|---|---------|--------------|-------------|
| 1 | **Personas** | `instructions` steers tone, voice, and style | Any client-facing AI feature; brand/audience consistency |
| 2 | **Few-shot** | Role-message examples teach a task-specific convention | Novel labels, classification schemes, or output formats the model can't infer from language alone |
| 3 | **Chain of thought + reasoning budget** | Explicit thinking step; `effort` controls depth vs. cost | Multi-step reasoning, math, logic, decision problems |
| 4 | **Structured outputs** | Pydantic schema guarantees the response shape | Any downstream code that parses the model's reply |
| 5 | **Manually retrieved context** | Paste a document into `instructions` | Client-specific data, internal docs, knowledge that postdates the model's training cutoff |
| 6 | **Self-refine** | Two-call loop: draft → critique → revised | Deliverables where quality criteria are explicit (length, evidence, tone) |
| 7 | **Meta-prompting** | Ask the model to write or improve a prompt | Recurring tasks; rapid prompt drafting; generating prompt variants for A/B testing |

---

## Data files

- `../data/eu_ai_act_summary.md` — shared EU AI Act summary used for the grounded-context examples (tracked)
