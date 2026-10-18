# Shared ACME corpus

This folder is the shared ACME Analytics Corp corpus used by multiple demos. Demo 05 uses the full
folder for advanced retrieval experiments; Demo 07 reads selected Markdown files from it for simple
agent tools.

For Demo 05, this folder is also the **swap point** for the notebook. The bundled files are a
*default* corpus about a fictional consulting firm, engineered so each retrieval technique has
questions where it wins.

## To run on your own data

1. **Delete** the `acme_*` files in this folder (or move them aside).
2. **Drop in** your own documents. Supported formats:
   - `.pdf` — one retrievable *parent* per page
   - `.md` / `.markdown` — one parent per `##`-level (or any `#`-level) heading section
   - `.txt` — one parent per blank-line-separated block
   - `.csv` — one parent per row
3. **(Optional) Re-label** `../../05_Advanced_Retrieval_LangChain/data/eval_cases.jsonl` so each
   question points at the evidence ids that actually answer it. Run the **first two tasks** of the
   Demo 05 notebook — they print every parent id next to a snippet of its text, which is exactly what
   you paste into the label file.
   - Evidence ids are **stable parent ids** of the form `source_stem::kind+index`
     (e.g. `acme_glossary::s2`, `acme_quarterly_metrics::r9`). They do **not** change when you re-tune
     chunk size, so your labels survive chunking experiments.
4. If you leave Demo 05's `data/eval_cases.jsonl` empty or missing, the notebook still runs — it falls
   back to a **qualitative side-by-side** view (each retriever's top results) instead of scored metrics.

## The default ACME corpus at a glance

| File | Role in the retrieval comparison |
|------|----------------------------------|
| `acme_field_guide.md` | Plain "what is X" facts — the naive dense baseline should handle these |
| `acme_glossary.md` | Acronyms / codenames / SKUs (`ARP`, `Project NIGHTJAR`, `ACM-ENT-2024`) — BM25 wins |
| `acme_genai_practice.md` | Mixes exact tokens + semantics — hybrid (dense+BM25) wins |
| `acme_pricing_and_contracts.md` | Near-duplicate pricing tiers/clauses — reranking wins |
| `acme_security_compliance.md` | Breadth across many facets — multi-query expansion wins |
| `acme_delivery_playbook.md` | Long multi-step procedures — parent-child recovery wins |
| `acme_quarterly_metrics.csv` | Structured rows — exercises the CSV loader path |
