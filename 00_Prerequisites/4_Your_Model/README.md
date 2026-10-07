# 4 · Your model

---

## Two different keys, and they are not the same

This trips people up in the first hour, so it is worth being explicit.

| Where | What reads it | Set up in |
| --- | --- | --- |
| `.env` at the **repo root** | Every notebook, via `helpers.nb.bootstrap()` | Here |
| `ANTHROPIC_API_KEY` in your **shell environment** | **Claude Code**, the agent | [Guide 2](../2_Claude_Code/README.md) |

They are unrelated. The first is your *application's* model call; the second is
how the agent authenticates. Setting one does not set the other, and a key that
works for Claude Code will not make the notebook run.

> Applications often carry their own `.env` as well, so they stay self-contained
> things you could hand to someone. Same values, separate file.

---

## Set it up

From the repository root:

```bash
cp .env.template .env      # copy .env.template .env    on Windows
```

Open `.env` and pick **one** option.

### Option 1 — a hosted provider, with your own key

The default, and the fastest to get working. LiteLLM picks the provider from the
model string.

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=anthropic/claude-sonnet-5
```

OpenAI, or Azure — which is the common one inside large firms:

```bash
# OPENAI_API_KEY=sk-...
# LLM_MODEL=gpt-4.1-mini

# AZURE_API_KEY=...
# AZURE_API_BASE=https://your-resource.openai.azure.com
# AZURE_API_VERSION=2024-10-21
# LLM_MODEL=azure/your-deployment-name
```


### Option 2 — a model on your own laptop

No key, no network, nothing leaves the machine.

```bash
LLM_MODEL=ollama/llama3.2
LLM_API_BASE=http://localhost:11434
```

Install [Ollama](https://ollama.com/download), then:

```bash
ollama pull llama3.2
ollama serve
```

Slower, and worth doing at least once. Being able to run a model with no network
at all is a genuinely different capability.

---

## Check it works

```bash
uv run jupyter notebook 01_First_Steps/S1_Enterprise_Dev_Environment.ipynb
```

The setup cell prints `✅ model: <whatever you configured>`. **Task 4 sends one
real message** when you run that cell. If it streams an answer back, you are
done.

Then try the activity under it: change `LLM_MODEL` in `.env` to a different
provider and re-run the same cell. It works unchanged — that property is the
whole reason this course routes everything through LiteLLM.

---

## ✅ Ready

Go back to the [checklist](../README.md#-you-are-ready-when) and confirm every
box. Then start
[Getting to Concreteness](../../01_Product_Engineering/challenge/getting_to_concreteness/README.md)
— about forty minutes, and it is the deliverable everything else is built on.
