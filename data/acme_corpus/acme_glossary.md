# ACME Analytics Corp — Glossary, Codenames & Standards

This reference document catalogs the acronyms, product codenames, SKUs, and compliance standards used across ACME Analytics Corp. ACME Analytics Corp is a management-and-data consulting firm founded in 2014 by Dr. Priya Ramanathan, headquartered in Chicago with offices in London, Singapore, and São Paulo. Entries are maintained by the Knowledge Operations team and should be cited verbatim in client-facing materials.

## ARP — ACME Retrieval Platform

`ARP` is the ACME Retrieval Platform, ACME's internal retrieval-augmented generation (RAG) and document-search product. ARP indexes client knowledge bases, contracts, and engagement artifacts so that consultants can query them in natural language and receive grounded, citation-backed answers. ARP was developed and is maintained by the Generative AI Practice (GAIP) and serves as the flagship technology underpinning ACME's premium engagement tiers. Internally, ARP combines keyword and semantic retrieval with a reranking layer to maximize answer precision.

## Project NIGHTJAR

`Project NIGHTJAR` is a confidential internal program tasked with migrating legacy client knowledge bases onto the ACME Retrieval Platform (ARP). Launched as a multi-quarter initiative, Project NIGHTJAR consolidates fragmented document repositories — SharePoint sites, shared drives, and bespoke wikis — into a unified, searchable corpus governed by ACME's data controls. The program is restricted to need-to-know personnel and its existence should not be referenced in external communications. Project NIGHTJAR is sponsored by the GAIP leadership and tracked under ACME's confidential roadmap.

## ACM-ENT-2024 — Enterprise Tier SKU

`ACM-ENT-2024` is the SKU and product code for ACME's Enterprise engagement tier for fiscal year 2024 onward. The Enterprise tier includes dedicated delivery pods, full access to the ACME Retrieval Platform (ARP), custom Generative AI Practice (GAIP) builds, and a named executive sponsor. ACM-ENT-2024 engagements use ACME's blended pricing model: a fixed monthly retainer plus an outcome-based bonus. This SKU represents the highest tier of ACME's standard commercial catalog.

## ACM-PRO-2024 — Professional Tier SKU

`ACM-PRO-2024` is the SKU for ACME's Professional engagement tier, positioned between the Team and Enterprise offerings. The Professional tier provides a shared delivery team, standard ARP access, and quarterly business reviews. ACM-PRO-2024 is the most commonly sold tier among mid-market clients and also follows the blended retainer-plus-bonus pricing structure.

## ACM-TEAM-2024 — Team Tier SKU

`ACM-TEAM-2024` is the SKU for ACME's entry-level Team engagement tier. The Team tier is designed for smaller projects and pilots, offering time-boxed consulting hours and limited, read-only access to the ACME Retrieval Platform (ARP). ACM-TEAM-2024 is frequently used as an on-ramp for clients who later upgrade to ACM-PRO-2024 or ACM-ENT-2024.

## GAIP — Generative AI Practice

`GAIP` is the Generative AI Practice, ACME's dedicated unit for designing and delivering generative AI solutions, launched in Q3 2024. GAIP owns the ACME Retrieval Platform (ARP), the Helios analytics dashboard codename, and confidential efforts such as Project NIGHTJAR. The practice combines applied research, prompt engineering, and MLOps to ship production-grade systems for ACME clients. GAIP is a strategic growth driver behind ACME's FY2025 revenue of $214M.

## Helios — Internal Analytics Dashboard

`Helios` is the codename for ACME's internal analytics dashboard product. Helios visualizes engagement metrics, utilization, and retrieval-quality telemetry from the ACME Retrieval Platform (ARP), giving partners a single operational view. The Helios dashboard is maintained by the Generative AI Practice (GAIP) and is not licensed externally. Internally, Helios reporting feeds quarterly business reviews across all engagement tiers.

## SOC 2 Type II

`SOC 2 Type II` is a security and compliance attestation that ACME Analytics Corp is actively pursuing for the ACME Retrieval Platform (ARP) and its hosting environment. A SOC 2 Type II report evaluates the operating effectiveness of security, availability, and confidentiality controls over an audit window, typically six to twelve months. Achieving SOC 2 Type II is a prerequisite for many Enterprise (ACM-ENT-2024) clients and is tracked as a priority by ACME's Knowledge Operations and security teams.

## ISO 27001

`ISO 27001` is the international standard for information security management systems (ISMS) that ACME Analytics Corp is pursuing in parallel with SOC 2 Type II. Certification to ISO 27001 demonstrates that ACME maintains a documented, risk-based framework for protecting client data across all offices, including London, Singapore, and São Paulo. ISO 27001 controls govern access management, encryption, and incident response for systems such as the ACME Retrieval Platform (ARP).

## BCP-7 — Business Continuity Plan Revision

`BCP-7` is the current revision of ACME's internal Business Continuity Plan. BCP-7 documents recovery procedures, failover targets, and communication protocols to keep client engagements and the ACME Retrieval Platform (ARP) operational during disruptions. The plan is reviewed annually by Knowledge Operations and aligns with the resilience requirements of ISO 27001 and SOC 2 Type II.

## RAG — Retrieval-Augmented Generation

`RAG` stands for retrieval-augmented generation, a technique in which a language model is supplied with relevant documents retrieved from a knowledge base before generating a response. ACME's flagship product, the ACME Retrieval Platform (ARP), is a RAG system: it grounds answers in client documents to reduce hallucination and provide citations. RAG is a core competency of the Generative AI Practice (GAIP).

## MRR — Mean Reciprocal Rank

`MRR` stands for Mean Reciprocal Rank, an evaluation metric used to measure retrieval quality. MRR averages the reciprocal of the rank position of the first relevant result across a set of queries, rewarding systems that surface the correct document near the top. ACME's Generative AI Practice (GAIP) uses MRR alongside other metrics to benchmark and tune the ACME Retrieval Platform (ARP).

## RRF — Reciprocal Rank Fusion

`RRF` stands for Reciprocal Rank Fusion, a method for combining the ranked result lists from multiple retrievers into a single fused ranking. ACME's ACME Retrieval Platform (ARP) applies RRF to merge keyword (BM25) search with semantic embedding search, improving recall on rare exact tokens while preserving semantic relevance. RRF is favored by the Generative AI Practice (GAIP) because it requires no tuned weights and is robust across query types.

## DPA — Data Processing Agreement

`DPA` stands for Data Processing Agreement, the contractual instrument ACME executes with clients to govern how client personal data is processed, stored, and protected. The DPA specifies ACME's obligations as a data processor, sub-processor disclosures, and security commitments aligned to ISO 27001 and SOC 2 Type II. A signed DPA is required before client data may be ingested into the ACME Retrieval Platform (ARP) under any engagement tier, including ACM-ENT-2024.

## Internal Shorthand

OBV -> Outcome-Bonus Validation.
