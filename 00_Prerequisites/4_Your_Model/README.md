# 4 · Your model

**There is no shared class server.** You bring either an API key from a provider,
or an endpoint you can reach — your firm's internal gateway, a server you run, or
a model on your own laptop.

That is deliberate, and it is not us being unhelpful. It is the actual situation
you will be in at work. An application that treats its provider as *configuration*
survives being moved; one that hardcodes a vendor SDK gets rewritten.
Everything in this course routes through [LiteLLM](https://docs.litellm.ai/), so
switching providers is one line and no code changes.

> Plenty of you cannot reach `api.openai.com` from a work machine at all.
> **Finding that out now is much better than finding it out under deadline.**

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
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4.1-mini
```

Anthropic, or Azure OpenAI — which is the common one inside large firms:

```bash
# ANTHROPIC_API_KEY=sk-ant-...
# LLM_MODEL=anthropic/claude-sonnet-5

# AZURE_API_KEY=...
# AZURE_API_BASE=https://your-resource.openai.azure.com
# AZURE_API_VERSION=2024-10-21
# LLM_MODEL=azure/your-deployment-name
```

**Budget.** A few dollars covers the whole course on a small model. Nothing here
requires a frontier model, and `gpt-4.1-mini` is the default for that reason.

### Option 2 — an endpoint you can reach

Anything OpenAI-compatible: your firm's internal gateway, vLLM, LM Studio,
llama.cpp, or a colleague's server. Prefix the model with `openai/` so LiteLLM
uses the OpenAI-compatible path, and set the base URL.

```bash
OPENAI_API_KEY=EMPTY
LLM_MODEL=openai/your-model-name
LLM_API_BASE=http://your-server:8000/v1
```

**If your firm has an internal gateway, use it.** It is the most realistic setup
in this course, it is usually already approved, and it means your coursework runs
where your real work would.

### Option 3 — a model on your own laptop

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

## 🧯 If it's blocked

### `api.openai.com` is unreachable

Expected on plenty of corporate networks. Record the policy and continue — we'll
need it later. The environment check measures exactly which hosts you can reach
and produces a table to put in front of an infrastructure team.

In order of preference:

1. **Ask whether your firm has an internal LLM gateway.** Most large firms now
   do, and it is Option 2 above. This is the best outcome — it is approved,
   it is realistic, and it is the answer your infrastructure team wants anyway.
2. **Azure OpenAI**, if your firm is a Microsoft shop. Frequently allowed where
   `api.openai.com` is not, because it is inside the tenant.
3. **Ollama on your own machine** (Option 3). No network needed at all.

### TLS certificate errors when calling the API

Your firm is intercepting TLS. Set the CA bundle variables from
[guide 1](../1_Your_Machine/README.md) — `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE`
— and they will apply here too.

### It worked yesterday and stopped today

Check your credit balance before you debug anything else. A `401` with an
otherwise-correct key is almost always an exhausted balance or a rotated key.

### You have no key and no gateway and cannot install Ollama

Do [Getting to Concreteness](../../01_Product_Engineering/challenge/getting_to_concreteness/README.md)
while you sort it out. It needs no model, no tooling, and no network, and it is
the input to every other week. Then come back.

---

## ✅ Ready

Go back to the [checklist](../README.md#-you-are-ready-when) and confirm every
box. Then start
[Getting to Concreteness](../../01_Product_Engineering/challenge/getting_to_concreteness/README.md)
— about forty minutes, and it is the deliverable everything else is built on.
