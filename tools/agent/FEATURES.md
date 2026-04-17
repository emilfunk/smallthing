# Features

Tracks planned, in-progress, and completed features for the biotech AI agent built on pi-mono.

**Status legend**: `[ ]` planned · `[~]` in progress · `[x]` done

---

## Domain Specialization

Skills and context that make this agent useful for biotech business developers.

- [ ] **PubMed search skill** — query PubMed/NCBI for literature, return structured summaries
- [ ] **ChEMBL skill** — search compounds, targets, and bioactivity data
- [ ] **Benchling ELN skill** — read/write entries, results, and sequences via Benchling API
- [ ] **LIMS integration skill** — query sample status and run data from common LIMS platforms
- [ ] **FHIR patient data skill** — read HL7 FHIR resources (observations, conditions, medications)
- [ ] **Data format tools** — CLI helpers for FASTQ, VCF, DICOM, SDF/MOL parsing and summarization
- [ ] **Regulatory prompt library** — curated `.pi/prompts/` for FDA 21 CFR Part 11, IND/NDA sections, SOP drafting, audit response templates
- [ ] **CRO portal skill** — pull study status and data packages from common CRO web portals

---

## Security & Compliance

Requirements for commercial biotech deployment.

- [ ] **Private model routing** — route proprietary sequences and patient data to self-hosted vLLM; non-sensitive tasks to cloud providers. Configured via `models.json` routing rules
- [ ] **Audit trail** — tamper-evident, structured log of every agent action (tool call, file edit, model response). Hook into `event-bus.ts`; emit to WORM store (e.g. S3 Object Lock)
- [ ] **SSO/OIDC authentication** — require identity before session start; inject user identity into audit log. Wired at `src/cli.ts` entrypoint
- [ ] **Data-at-rest encryption** — encrypt session transcripts and `.pi/` state at rest
- [ ] **Secret scanning** — CI check to block commits containing API keys, OAuth credentials, or patient identifiers (upstream pi-mono had hardcoded Google OAuth creds; already redacted)
- [ ] **Role-based tool access** — restrict which skills/tools a given user role can invoke (e.g. lab scientist vs. regulatory writer vs. admin)
- [ ] **Network egress controls** — allowlist of approved external endpoints the agent may call; deny-by-default for everything else

---

## UX & Deployment

Reducing friction for non-engineer biotech users.

- [ ] **Single install script** — `npm install && pi auth && pi`; no manual config required
- [ ] **Web UI mode** — replace TUI with `packages/web-ui` for users who prefer a browser interface
- [ ] **Slack bot mode** — deploy via `packages/mom` so researchers can query the agent from Slack without leaving their workflow
- [ ] **Docker image** — pre-packaged image with vLLM pod, skills, and default biotech model; ready for VPC deployment
- [ ] **Onboarding wizard** — first-run flow that sets LLM provider, API keys, and org-level config

---

## Commercial

Licensing, pricing, and distribution.

- [ ] **License audit** — verify all pi-mono and skill dependencies are MIT/Apache-2 compatible with commercial use
- [ ] **Usage metering** — token-level consumption tracking per user/team via the model routing layer; basis for consumption-based pricing
- [ ] **Seat license enforcement** — per-researcher seat licensing with org-level admin portal
- [ ] **Tiered prompt library** — free tier ships basic skills; paid tier unlocks validated regulatory prompt packs and premium integrations
- [ ] **Support SLA tooling** — session export and diagnostic bundle for customer support escalations
