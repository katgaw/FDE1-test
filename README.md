<div align="center">
  <p>
    <img
      src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
      style="vertical-align: middle;"
      height="100"
      alt="AI Makerspace logo"
    />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <img
      src="https://www.towerbrook.com/wp-content/uploads/2025/05/TOWERBROOK-LOGO-PMS280C.svg"
      style="vertical-align: middle;"
      height="45"
      alt="TowerBrook logo"
    />
  </p>

  <h1>The Hive FDE Training</h1>

  <p><strong>🧰 Get your machine ready.</strong></p>
</div>

> 🎯 **Engage with your own company as a world-class AI Forward-Deployed
> Engineer.** Not a sample dataset, not a demo use case — the actual problem you
> have at the actual place you work.

---

## Two tasks

| # | Deliverable | What it is | Time |
| --- | --- | --- | --- |
| 1 | [**Set up your machine**](./00_Prerequisites/README.md) |Four guides: your machine, Claude Code, your repo, your model | 45-90 minutes |
| 2 | [**First Steps**](./01_First_Steps/S1_Enterprise_Dev_Environment.ipynb) | A notebook to test your environement and identify limitations | 40 minutes |


---

## Why this exists

Two things go wrong at the start of work like this, and both are avoidable.

**People start with nothing installed.** Then the first real session is spent
installing things instead of building, and the interesting question — *what does
my employer's network actually let me do?* — never gets asked.

**People start with a vague idea.** Project ideas will be assigned directly from leadership to ensure high quality ideas.

---

## Start here

Set up **your own repository** and pull this material into it — you do not fork,
and you do not push to ours. [Guide 3](./00_Prerequisites/3_Your_Repo/README.md)
walks through it, and it is the same workflow you will use throughout the course:

```
  upstream (ours)  ──pull──►  your laptop  ──push──►  origin (yours)
```

Once you have it locally:

```bash
./00_Prerequisites/scripts/setup_check.sh        # macOS / Linux / WSL
```
```powershell
.\00_Prerequisites\scripts\setup_check.ps1       # Windows PowerShell
```

It reports what is missing and names the guide that fixes it. It never installs
anything.

---

## The environment check

The setup script tells you *what* is missing. The notebook tells you what your
**network** does to you, which is the part nobody documents:

```bash
uv run jupyter notebook 01_First_Steps/S1_Enterprise_Dev_Environment.ipynb
```

Run `make setup` first. The notebook probes six hosts —
PyPI, OpenAI, jsDelivr, Hugging Face, Docker Hub, GitHub — and reports **who
signed each certificate**.

On a managed laptop that column often names your own employer rather than a
public CA. That is TLS interception, stated as a fact rather than a suspicion,
and it is the single most useful thing to put in front of an infrastructure team
because it is measured rather than assumed.

---

## 🔑 You bring the model

There is no shared server. Bring **either** an API key from a provider (OpenAI,
Anthropic, Azure) **or** an endpoint you can reach — your firm's internal
gateway, a server you run, or a model on your own laptop.

[`.env.template`](./.env.template) has a worked example of each. Everything
routes through LiteLLM, so switching between them is one line and no code
changes.

This is deliberate. Plenty of you cannot reach `api.openai.com` from a work
machine at all, and finding that out now is much better than finding it out
under deadline.

---

## 🧑‍🤝‍🧑 Your team

- [Dr. Greg Loughnane](https://www.linkedin.com/in/gregloughnane/), Owner/CEO @ AI Makerspace
- [Dr. Katerina Gawthorpe](https://www.linkedin.com/in/chris-brousseau/), Instructor @ AI Makerspace
- [Jacob Kilpatrick](https://www.linkedin.com/in/jacobkilpatrickai/), Course Operations Lead @ AI Makerspace

Questions? Reach out to `jacob@aimakerspace.io`.

Keep building, shipping, and sharing 🏗️🚢🚀
