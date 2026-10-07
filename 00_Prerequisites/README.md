<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Prerequisites</h1>
  <p><strong>🧰 Get your machine ready</strong></p>
</div>

---

## 🎯 What you'll be able to do

Finish with a working environment: the tooling installed, Claude Code
authenticated, your own repository set up, and a model you can actually reach.

> **Do this first.** The environment check *verifies* your machine and probes
> what your network allows. If nothing is installed yet, there is nothing to
> verify.
>
> Budget **45–90 minutes**. It is longer on a managed corporate laptop, and the
> long pole is almost always approvals, not installation — which is exactly why
> you want to start early.

---

## 🔗 Quicklinks

| # | Guide | What it gets you |
| --- | --- | --- |
| 1 | [**Your machine**](./1_Your_Machine/README.md) | Docker, VS Code, Git, Python 3.12+, uv |
| 2 | [**Claude Code**](./2_Claude_Code/README.md) | Installed, authenticated, and you know how to drive it |
| 3 | [**Your repo**](./3_Your_Repo/README.md) | Your own remote, this material pulled into it, and the environment check running |
| 4 | [**Your model**](./4_Your_Model/README.md) | An API key or an endpoint, and a `.env` that works |

When you think you are done:

```bash
./00_Prerequisites/scripts/setup_check.sh        # macOS / Linux / WSL
```
```powershell
.\00_Prerequisites\scripts\setup_check.ps1       # Windows PowerShell
```

---

## 🛣️ Pick your path

The two situations are genuinely different, and most of the course material
assumes the first one. If you are on the second, this module is where you get the
attention the rest of the course does not give you.

<table>
  <tr>
    <td width="180"><strong>🏢 Managed work laptop</strong></td>
    <td>
      Someone else decides what you can install and what you can reach. There is
      a proxy you did not configure and a certificate authority you did not
      install. <strong>Expect to need approvals, and start asking now.</strong>
      Every blocker you hit is material — the environment check turns it into
      evidence, and evidence is what a deployment plan gets built from.
    </td>
  </tr>
  <tr>
    <td><strong>💻 Your own machine</strong></td>
    <td>
      Nothing is in your way, and the install is genuinely quick. Your risk is
      the opposite one: you will sail through setup and then find that half of
      the environment check is about restrictions you do not have.
      <strong>Read <a href="#-if-you-are-on-a-personal-machine">the note below</a></strong>
      so you know what to do with that time.
    </td>
  </tr>
</table>

Doing both is the strongest option, and it is not as silly as it sounds — the
[environment check](../01_First_Steps/S1_Enterprise_Dev_Environment.ipynb)
suggests it as an advanced exercise. The *difference* between the two machines is your firm's security posture, stated
precisely, which is a far better opening with an infrastructure team than a list
of questions.

---

## 🧯 When something is blocked

**A block is a policy, not a fault. Record the policy and continue — we'll need
it later.**

That is the single most important idea in this module. An engineer who says
*"it doesn't work"* is stuck. An engineer who says *"outbound TLS to
`huggingface.co` is intercepted by a certificate signed by our own CA, so we need
an internal model registry, and here is who owns that decision"* is doing the job.

Each guide has a **🧯 If it's blocked** section with two things: how to actually
work around it, and what to record in [`NETWORK.md`](../NETWORK.md). Do both.

> Do not put real hostnames, internal URLs, or company data in a file you will
> push to a repository. Describe the *shape* — "an internal PyPI mirror",
> not its address.

---

## 💻 If you are on a personal machine

Nothing here is a waste of your time, but the emphasis shifts.

- **Setup will take you 20 minutes, not 90.** Use the rest to get further into
  [Getting to Concreteness](../01_Product_Engineering/challenge/getting_to_concreteness/README.md),
  which is the other half of this challenge and the harder half.
- **You still need an ecosystem story.** Most of you will eventually deploy
  something inside a firm that *does* have these restrictions. The probe will
  tell you "open network, nothing here will bite you" — that is a valid result,
  and the exercise becomes imagining the constrained case rather than measuring
  it.
- **The remediation sections are still worth reading.** Certificate interception
  and blocked registries are the two things most likely to break your first real
  client engagement, and reading them once now is cheaper than meeting them
  under deadline.

---

## ✅ You are ready when

- [ ] `docker --version`, `git --version`, `python --version`, and `uv --version` all print something
- [ ] `claude --version` prints a version, and `claude doctor` is happy
- [ ] You created your own repo, pulled this material into it, and pushed
- [ ] The environment-check notebook opens, and Tasks 1–3 run
- [ ] Task 4 makes one real model call and gets an answer back
- [ ] Anything that was blocked is written down in [`NETWORK.md`](../NETWORK.md)

The last box counts. It is the only thing here that survives the week, and it is
the part nobody else can produce for you.

---

## 🆘 Still stuck

Post in the Maven Community with: your OS, the exact command you ran, and the
exact error text. "It doesn't work" cannot be debugged; a traceback can.

If you are blocked on an approval that will take days, say so — start the
material anyway. Every guide here notes what you can do without the thing that
is blocked.
