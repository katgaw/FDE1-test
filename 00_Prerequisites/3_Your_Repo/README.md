# 3 · Your repo

You are going to work in **your own repository**, not in a copy of ours.

> **"How do I make changes to the repo I am reading right now?"**
>
> You don't. You create your own, pull this material into it, and push your work
> to yours. Your repository is then genuinely yours — private if you want it, on
> your own account, with your own history.

This is the same workflow you will use for the course itself, so it is worth
getting right once. Ten minutes.

---

## 0 · Before you start

You need a [GitHub account](https://github.com/signup) and a way to authenticate
to it. HTTPS works. SSH stops you retyping credentials all week; the key setup is
below if you want it.

### Tell Git who you are

Every commit is stamped with whatever this says, so set it before your first
commit rather than rewriting history later:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

Use the same address as your GitHub account, or your commits will not be
attributed to you.

<details>
<summary><strong>SSH key setup</strong> — open this if you still need a key</summary>

### Generate a key pair

```bash
ssh-keygen -t ed25519 -C "your-github-email@example.com"
```

- **Where to save it.** Press Enter. The default `~/.ssh/id_ed25519` is correct
  and every tool looks there.
- **Passphrase.** Set a real one. The private key is a credential that lives on
  disk; a passphrase is what makes a stolen laptop not also a stolen GitHub
  account.

> **`ed25519` not supported?** Some older enterprise tooling still wants RSA. Use
> `ssh-keygen -t rsa -b 4096 -C "your-email"` instead, which gives you
> `~/.ssh/id_rsa` and `~/.ssh/id_rsa.pub`.

You now have two files. `id_ed25519` is **private** — it never leaves the
machine and never goes in a repo. `id_ed25519.pub` is **public** and is the one
you hand to GitHub.

### Load it into the agent

So you type the passphrase once per session rather than once per push:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519        # macOS: add --apple-use-keychain to persist it
```

### Give the public half to GitHub

Copy it to your clipboard — the command depends on your OS:

| OS | Command |
| --- | --- |
| **macOS** | `pbcopy < ~/.ssh/id_ed25519.pub` |
| **Windows (WSL)** | `clip.exe < ~/.ssh/id_ed25519.pub` |
| **Linux** | `xclip -sel c < ~/.ssh/id_ed25519.pub` |

Then on GitHub: **Settings** → **SSH and GPG keys** → **New SSH key**. Give it a
name you will recognise in a year (`work-laptop` beats `key1`), paste into the
**Key** field, and click **Add SSH key**.

> Paste the contents of the `.pub` file and nothing else. It is one line starting
> `ssh-ed25519`. If you ever paste a key that does *not* end in `.pub`, treat it
> as compromised and generate a new pair.

### Confirm it works

```bash
ssh -T git@github.com
```

Say `yes` to the host authenticity prompt the first time. You should get:

```
Hi <your-username>! You've successfully authenticated, but GitHub does not provide shell access.
```

That second clause is not an error. Authentication is all we wanted.

> **SSH blocked at your firm?** Outbound port 22 is a common block, and `ssh -T`
> will hang or be refused. Use HTTPS addresses everywhere below instead —
> everything else is identical — and record the block. It is a real constraint.
> See [🧯 If it's blocked](#-if-its-blocked).

</details>

> **Model API keys are a separate thing** and come later, in
> [guide 4](../4_Your_Model/README.md). Nothing in this guide needs one.

---

## 1 · Create your own empty repo

On GitHub, create a **new, empty** repository.

| Setting | Value |
| --- | --- |
| **Name** | Something short you will not regret typing. `Hive1` is fine |
| **Visibility** | Your call. **Private is a perfectly good answer** if work-related material will end up in it |
| **Add a README** | **Deselect it.** You want a genuinely empty repo |
| **.gitignore / licence** | Add neither, for the same reason |

An empty repository is the point. Anything GitHub creates for you is something
you have to merge around in step 4.

---

## 2 · Clone your empty repo

Copy the SSH address from the green **Code** button, then:

```bash
git clone git@github.com:<YOUR_USERNAME>/Hive1.git
cd Hive1
```

> `warning: You appear to have cloned an empty repository` means you did it
> right.

---

## 3 · Add this repository as `upstream`

`origin` is yours, and you push to it. `upstream` is ours, and you only ever pull
from it.

```bash
git remote add upstream git@github.com:TowerBrook/Hive-Cohort-1-FDE-Training.git
git remote -v
```

You should see four lines — two for `origin`, two for `upstream`:

```
origin    git@github.com:<YOUR_USERNAME>/Hive1.git (fetch)
origin    git@github.com:<YOUR_USERNAME>/Hive1.git (push)
upstream  git@github.com:TowerBrook/Hive-Cohort-1-FDE-Training.git (fetch)
upstream  git@github.com:TowerBrook/Hive-Cohort-1-FDE-Training.git (push)
```

---

## 4 · Pull the material down

```bash
git pull upstream main --allow-unrelated-histories
```

`--allow-unrelated-histories` is needed exactly once, because your empty repo and
this one share no common commit. After this, a plain `git pull upstream main`
brings down anything new.

---

## 5 · Push it to your own remote

```bash
git push origin main
```

That is the loop, and it is the whole workflow:

```
  upstream (ours)  ──pull──►  your laptop  ──push──►  origin (yours)
```

You never push to `upstream`. You never pull from `origin` unless you are working
across two machines.

---

## 6 · Set up the environment

From the root of your repo:

```bash
make setup
```

That is `uv sync` — it reads `pyproject.toml` and builds the environment. One
command, and it is reproducible, which is why this uses `uv` rather than pip or
conda.

> **`make` not found on Windows?** You do not need it. Every `make` target is a
> one-line shortcut; run `uv sync` directly instead. The `Makefile` shows what
> each target actually does.

---

## 7 · Run the environment check

This is a Jupyter notebook.

```bash
uv run jupyter notebook 01_First_Steps/S1_Enterprise_Dev_Environment.ipynb
```

Run `make setup` first so the environment exists. `make nb` runs this same
command.

Work through Tasks 1 to 3. They need no model and no key:

| Task | What it tells you |
| --- | --- |
| **1** | What is actually installed, and at what version |
| **2** | **What your network allows** — six hosts, and who signed each certificate |
| **3** | Why configuration should fail at startup rather than forty minutes in |

**Task 2 is the one that matters.** Record what it shows you in
[`NETWORK.md`](../../NETWORK.md), then commit it to your own repo:

```bash
git add NETWORK.md
git commit -m "My network findings"
git push origin main
```

Task 4 makes one real model call, so come back to it after
[guide 4](../4_Your_Model/README.md).

---

## 🧯 If it's blocked

### `ssh -T git@github.com` hangs or is refused

Outbound port 22 is blocked. Use HTTPS addresses instead:

```bash
git clone https://github.com/<YOUR_USERNAME>/Hive1.git
git remote add upstream https://github.com/TowerBrook/Hive-Cohort-1-FDE-Training.git
```

You will be asked for a **personal access token** rather than a password —
GitHub stopped accepting passwords over HTTPS years ago. Generate one at
**Settings** → **Developer settings** →
[**Personal access tokens**](https://github.com/settings/tokens):

- **Classic** tokens are the simpler option. Give it a description, set an
  expiration — 90 days is a reasonable default — and tick the **`repo`** scope.
  That is all this course needs; do not grant scopes you do not use.
- Copy it when it is shown. **You cannot view it again**, only regenerate it.
- Paste it as the password at the Git prompt. To avoid pasting it on every push,
  cache it: `git config --global credential.helper manager` on Windows,
  `osxkeychain` on macOS, or `"cache --timeout=86400"` on Linux.

A token is a password. It does not go in a commit, a notebook, or a `.env` file
you might push.

> **If port 443 is also filtered**, you may be behind a proxy. Point Git at it
> with `git config --global http.proxy http://your-proxy:port`, and record that
> you needed to.

### `git@github.com: Permission denied (publickey)`

The network is fine; the key is not being offered or not recognised. In order:

```bash
ssh-add -l                       # is the key loaded in the agent at all?
ssh-add ~/.ssh/id_ed25519        # if not, load it
ssh -vT git@github.com           # verbose: shows which key files it tried
```

If the agent has the key and GitHub still refuses it, you pasted the wrong half
or the wrong key. Re-copy `~/.ssh/id_ed25519.pub` and compare it against the
fingerprint GitHub shows under **SSH and GPG keys**.

### `uv sync` or `uv run` fails with a certificate error

Same cause and same fix as in [guide 1](../1_Your_Machine/README.md) — set
`REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` to your firm's CA bundle. If PyPI itself
is blocked, set `UV_DEFAULT_INDEX` to your internal mirror.

### The notebook opens but a cell hangs

The network probe resolves DNS, and a system resolver that is being filtered can
take a while to give up. Let it finish — a slow answer is itself a result worth
recording.

### `cdn.jsdelivr.net` shows as blocked

Record it. A blocked CDN is **the single most common way a demo that worked on
your laptop dies on contact with a corporate network** — anything that loads
JavaScript at runtime stops working, and the page renders perfectly while doing
nothing.

### You cannot reach GitHub at all

Some firms block it outright, or allow only an internal mirror. Work from a
personal machine and record the block. "We cannot reach github.com" shapes how
anything you build gets delivered, and it is exactly the kind of thing worth
knowing before you promise anyone a delivery date.

---

## ➡️ Next

[**4 · Your model**](../4_Your_Model/README.md) — the key or endpoint that makes
the environment check's Task 4 answer.
