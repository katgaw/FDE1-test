# Evals / LLM-as-a-Judge — From Scratch

## 🏗️ Build | 🚢 Ship | 📤 Share

### 🏗️ Build

Build four judges for an EU AI Act assistant, validate their output, and find the answers where their scores disagree.

### 🚢 Ship

Run the same harness against your group project and keep an auditable JSONL record of the answers, scores, rationales, and model versions.

### 📤 Share

Bring one disagreement case. Explain what each judge measured and which evidence you used to decide whether the answer passed.

## Student mission brief

Your team has eight plausible-looking answers. Your job is to determine which are correct, useful, clear, and supported by the source—and to avoid treating one model score as ground truth.

This module is intentionally framework-free: students can see the prompts, validation, scores, and failure modes directly.

> **Why this matters to you as an Towerbrook consultant:** A client needs to know what a score supports, how it was produced, and which outputs still require review. This notebook produces that audit trail instead of presenting a dashboard number without its underlying evidence.

## What students build

- An assistant that answers eight questions from a supplied EU AI Act summary
- An accuracy judge for factual questions with reviewed answers
- Rubric-based quality and clarity judges for open-ended answers
- A groundedness judge that checks every response against the source
- Strict validation and retry handling for judge output
- A repeatability check that runs the same evaluation three times
- An auditable JSONL artifact containing responses, scores, rationales, and model names
- A heatmap and disagreement table for choosing which cases to inspect

The central distinction is simple: a response can be correct, useful, clear, or grounded. Those properties overlap, but they are not the same measurement.

## Setup

From the repository root:

```bash
cp .env.template .env
uv sync
uv run jupyter lab
```

Then open `04_Evals_LLM_as_Judge/Evals_LLM_as_Judge.ipynb`.

Configure one of these routes in `.env`:

- an Anthropic API key;
- an OpenAI API key; or
- an OpenAI-compatible endpoint with `OPENAI_BASE_URL` and `LLM_MODEL`.

`LLM_MODEL` selects the assistant under test. `JUDGE_MODEL` is optional; when omitted, the same model writes and judges the answers. That is convenient for the exercise but should be treated as a limitation, not independent validation.

## Dataset

`data/seed_questions.jsonl` contains eight reviewed questions:

| Type | Count | Evaluation evidence |
|---|---:|---|
| Factual | 4 | Reviewed reference answer, rubric, and source text |
| Explanatory | 2 | Rubric and source text |
| Advisory | 2 | Rubric and source text |

The notebook reads `../data/eu_ai_act_summary.md` as the source available to the assistant.

## Output

Running the notebook writes `data/judge_scores.jsonl`. Each row includes:

- the question, reference, and assistant response;
- assistant and judge model names; and
- every applicable score with its rationale.

The file is generated evidence, not a replacement for the reviewed seed dataset.

## What to inspect

Start with the rows that have the largest spread between applicable judges. Read the response and rationales, then decide whether the difference came from:

- a problem in the answer;
- judges measuring different properties;
- an ambiguous rubric; or
- ordinary model variation.

For factual fields that can be checked exactly—dates, article numbers, percentages, and monetary amounts—prefer programmatic checks over an LLM judge.

## Exercise handoff

Run the harness against outputs from your group project. Bring one disagreement case and explain which evidence you trusted when deciding whether the response passed.
