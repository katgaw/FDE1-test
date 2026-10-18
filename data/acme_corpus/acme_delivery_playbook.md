# ACME Analytics Corp — Delivery Playbook

This playbook governs how ACME Analytics Corp delivers client engagements end to end. ACME is a management-and-data consulting firm founded in 2014 by Dr. Priya Ramanathan, headquartered in Chicago with offices in London, Singapore, and São Paulo. Every procedure below is mandatory for engagements that involve the ACME Retrieval Platform (`ARP`), our internal RAG product delivered through the Generative AI Practice (GAIP). Read each section in full: later steps depend on artifacts and approvals created in earlier steps.

## Engagement Kickoff Procedure

1. Confirm the signed Statement of Work (SOW) and verify the commercial model. ACME uses blended pricing: a fixed monthly retainer plus an outcome bonus tied to success metrics. The bonus cannot be invoiced until the metrics defined here are validated at closeout.
2. Build the stakeholder map. Identify the Executive Sponsor (signs off on go-live), the Data Owner (controls source-system access), and the Day-to-Day Lead (operational point of contact). Record each in the engagement workspace; the cutover approvals later in this playbook reference these exact roles.
3. Define success metrics jointly with the Executive Sponsor. Each metric must have a baseline, a target, and a measurement method. These are the figures the Outcome-Bonus Validation section will later test against, so they must be unambiguous and instrumented from day one.
4. Provision data access. The Data Owner grants ACME read access to the agreed source systems and signs the Data Processing Addendum. This access is the prerequisite for the Discovery & Data Assessment section — do not begin cataloguing until provisioning is confirmed in writing.
5. Schedule the kickoff workshop and publish the engagement charter summarizing roles, metrics, and access scope. The charter is the single source of truth referenced throughout delivery.

## Discovery & Data Assessment

1. Confirm that data access was provisioned in the Kickoff step. Discovery cannot start against systems ACME cannot read; if access is incomplete, escalate to the Data Owner before proceeding.
2. Catalogue every in-scope data source. For each, record system name, owner, refresh cadence, record volume, and sensitivity classification (Public, Internal, Confidential, Restricted). The classification drives the security controls applied in the ARP Deployment Runbook.
3. Profile data quality. Sample each source and document completeness, duplication, and known anomalies. Flag any source whose quality threatens a success metric defined at kickoff — these become risks in the engagement charter.
4. Map data lineage. Trace each field from origin to the point ARP will ingest it. Lineage is required input for the Solution Design Review; designs submitted without it are rejected.
5. Produce the Data Assessment Report and review it with the Data Owner and Day-to-Day Lead. Their written sign-off closes Discovery and unlocks Solution Design.

## Solution Design Review

1. Confirm the Data Assessment Report is signed off. The design must reference the catalogued sources and their sensitivity classifications; an unsigned assessment blocks this review.
2. Draft the solution architecture, covering ingestion, chunking strategy, retrieval configuration, and the embedding model selection for ARP.
3. Submit the design through the two-gate approval. Gate 1 is the GAIP Technical Lead, who validates architecture and ARP configuration. Gate 2 is the ACME Security Reviewer, who validates that controls match the highest sensitivity classification in scope. Both gates must pass before any build begins.
4. For engagements touching Restricted data, add a third approval from the ACME Data Protection Officer. This approval is a hard prerequisite for the production cutover described later.
5. Record all approvals in the engagement charter with names and dates. The Production Cutover & Go-Live section checks these records before authorizing the cutover window.

## ARP Deployment Runbook

1. Verify prerequisites: the Solution Design Review approvals (both gates, plus DPO if Restricted) are recorded, and the success metrics from Kickoff are instrumented in the target environment.
2. Provision the ARP environment in the client tenant. Apply the security controls dictated by the highest sensitivity classification from Discovery.
3. Stand up the ingestion pipeline using the lineage map. Load source data into the staging index, never directly into production at this stage.
4. Build the retrieval index in staging using the approved chunking and embedding configuration. Run the standard relevance test suite and record baseline retrieval scores.
5. Conduct User Acceptance Testing with the Day-to-Day Lead against the staging index. Capture sign-off; UAT approval is a prerequisite for the cutover.
6. Prepare the rollback plan. Snapshot the current production state (if any) and document the exact steps to restore it. No cutover may proceed without a tested rollback. Production promotion itself happens only in the Production Cutover & Go-Live window described next.

## Production Cutover & Go-Live

1. Run the pre-cutover checklist. Confirm: UAT sign-off from the Deployment Runbook is recorded; the rollback plan is tested; all Solution Design approvals (Gate 1, Gate 2, and DPO where Restricted) are present in the charter.
2. Obtain cutover authorization. The Executive Sponsor named in the Kickoff stakeholder map must approve the cutover window in writing. Without this approval the cutover is blocked, regardless of technical readiness.
3. Execute the cutover within the agreed maintenance window. Promote the validated staging index to production, repoint client traffic to ARP, and freeze further configuration changes.
4. Run post-cutover validation. Re-run the relevance test suite against production and confirm scores match the staging baseline from the Runbook. Confirm the success-metric instrumentation is emitting data.
5. If validation fails, invoke the rollback plan immediately and notify the Executive Sponsor. If validation passes, declare go-live and start the outcome-bonus measurement clock referenced in the next section.

## Outcome-Bonus Validation

OBV is the final commercial validation workflow used after go-live measurement closes. The workflow gathers production measurements, compares each success metric with its baseline and target, reviews external adjustment factors, obtains Executive Sponsor agreement, and authorizes the outcome-bonus invoice only after attainment has been validated.

1. Confirm go-live was declared and the measurement clock started at cutover. The bonus measurement period runs from go-live to engagement closeout.
2. Retrieve the success metrics defined at Kickoff, including their baselines, targets, and measurement methods. Only these pre-agreed metrics count toward the bonus; metrics introduced later are excluded.
3. Collect production measurements over the full measurement period using the instrumentation validated at cutover. Do not rely on staging or spot-check figures.
4. Compute attainment per metric against target. Document any external factors that affected results and adjust only where the SOW explicitly allows.
5. Review results jointly with the Executive Sponsor and obtain written agreement on attainment. This agreement is the trigger that authorizes the outcome-bonus invoice; finance will not process the bonus without it.

## Incident Response During Delivery

1. Detect and classify. On any production ARP issue, classify severity: Sev1 (service down or data exposure), Sev2 (degraded retrieval quality), Sev3 (minor or cosmetic). Sensitivity classifications from Discovery determine whether an incident is also a data-protection event.
2. Notify per severity. Sev1 requires immediate notification to the Executive Sponsor and the ACME Security Reviewer; Sev2 notifies the Day-to-Day Lead within the business day.
3. Contain. For data-exposure incidents, isolate the affected index and, if cutover has occurred, prepare to invoke the rollback plan from the Deployment Runbook.
4. Remediate and verify. Apply the fix, then re-run the relevance and validation tests used at cutover to confirm the system is healthy.
5. Conduct a blameless post-incident review within five business days and log corrective actions in the engagement charter. Unresolved Sev1 actions block engagement closeout.

## Engagement Closeout & Handover

1. Confirm prerequisites: Outcome-Bonus Validation is signed by the Executive Sponsor, and no open Sev1 incident actions remain from the Incident Response section.
2. Transfer ownership. Hand the ARP environment, ingestion pipeline, and runbooks to the client or to ACME managed services per the SOW.
3. Deliver the closeout package: final architecture as built, the signed metric attainment, the data catalogue and lineage from Discovery, and all approval records from the charter.
4. Run a knowledge-transfer session with the Day-to-Day Lead and the client operations team, walking through the Deployment Runbook and rollback procedure.
5. Decommission ACME access provisioned at Kickoff, archive the engagement workspace, and trigger the final retainer and validated outcome-bonus invoices. Closeout is complete only when access is revoked and both invoices are issued.
