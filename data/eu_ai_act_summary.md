# EU AI Act — plain-language summary

A short, paste-into-a-prompt overview of the **EU Artificial Intelligence Act**
(Regulation (EU) 2024/1689) for the prompting and evaluation demos. For the full
legal text see `eu_ai_act.md`; for provenance and reuse terms see `SOURCE.md`.

## What it is

The AI Act is the first comprehensive, horizontal law regulating artificial
intelligence. It takes a **risk-based** approach: the more risk an AI system poses to
health, safety, or fundamental rights, the more obligations it carries. It entered into
force on **1 August 2024** and applies in phases through 2027. It binds providers,
deployers, importers, and distributors, and applies **extraterritorially** — it reaches
any system whose output is used in the EU, wherever the provider sits.

## The four risk tiers

- **Unacceptable risk — prohibited (Article 5).** A short list of banned practices,
  including manipulative or deceptive techniques that distort behaviour and cause harm,
  exploitation of vulnerabilities (age, disability, social/economic situation),
  social scoring by public authorities, untargeted scraping of facial images to build
  recognition databases, emotion recognition in the workplace and schools, and
  real-time remote biometric identification in public spaces (with narrow law-enforcement
  exceptions).
- **High risk (Annex III + safety components).** Permitted but heavily regulated. Covers
  AI used in biometrics, critical infrastructure, education, employment and worker
  management, access to essential public and private services, law enforcement, migration
  and border control, and the administration of justice. Providers must run a risk
  management system, ensure data governance and quality, keep technical documentation and
  logs, provide transparency and **human oversight**, and meet accuracy, robustness, and
  cybersecurity standards — then pass a conformity assessment and register the system.
- **Limited risk — transparency (Article 50).** Systems that interact with people or
  generate content must disclose it: chatbots must say they're AI, and synthetic or
  manipulated media (deepfakes) must be labelled.
- **Minimal risk.** Everything else — spam filters, recommendation features, AI in video
  games. No obligations; the vast majority of systems land here.

## General-purpose AI (GPAI) models

Providers of general-purpose models (the kind behind many downstream products) must
publish technical documentation, summarise training data, and respect copyright. Models
deemed to carry **systemic risk** (very capable, trained with extremely large compute)
face extra duties: model evaluations, adversarial testing, incident reporting, and
cybersecurity protections.

## Governance and penalties

Enforcement is shared between the new **European AI Office**, an AI Board, national
competent authorities, and notified bodies. Fines are tiered (Article 99):

- up to **€35 million or 7%** of total worldwide annual turnover — for prohibited practices;
- up to **€15 million or 3%** — for breaching most other obligations;
- up to **€7.5 million or 1%** — for supplying incorrect or misleading information.

Whichever figure is higher applies (a capped, lower figure applies to SMEs and start-ups).

## Timeline

- **2 February 2025** — the prohibitions take effect.
- **2 August 2025** — the GPAI model rules apply.
- **2 August 2026** — most high-risk obligations apply.
- **2 August 2027** — obligations for high-risk systems that are safety components of
  regulated products apply.

## What it does *not* do

It doesn't regulate AI used purely for military, defence, or national security; pure
scientific R&D before a system reaches the market; or AI used by individuals for purely
personal, non-professional activity. Free and open-source models are largely exempt unless
they're high-risk, prohibited, or general-purpose models with systemic risk.
