# MamboLite Roadmap

This roadmap outlines the next phases beyond Phase 1 to grow from a single-CSV formatter to a robust, multi-source contact processing tool.

## Phase 2 - Multi-File + Fuzzy Dedupe + Excel

- Multi-file intake (merge by source) and per-source mapping profiles
- Dedupe tiers: exact email, domain+name, fuzzy name+company (threshold)
- Excel export with M1-M4 tabs + summary (per source), dedupe report
- Deliverables: CLI flags (`--inputs`, `--profile`, `--xlsx`), thresholds config, XLSX output
- Effort: ~2 weeks

## Phase 3 - Web Dashboard & API Connectors

- Secure web app where users create accounts, manage settings, and connect sources
- OAuth connectors to collate contacts without manual CSV export (e.g., Google People, Microsoft Graph, HubSpot)
- Background sync jobs, dedupe into unified schema, and run the formatter pipeline server-side
- Deliverables: dashboard (auth, settings), connectors, sync jobs, unified output export/download
- Effort: ~3-5 weeks

## Phase 4 - Business Card OCR & Scanning App

- OCR pipeline to transcribe business cards to contact cards and store to the user's account
- Web app capture (camera) and/or mobile app capture; image cleanup and field extraction
- Map extracted fields to unified schema and dedupe into existing contacts
- Deliverables: OCR engine integration (Tesseract/Cloud), capture UI, extraction/validation, contact creation
- Effort: ~2-4 weeks

## Phase 5 - Data Quality & Enrichment

- Address normalization (state/country codes), phone parsing by region
- Name quality rules (initials, particles, suffix order), configurable scoring
- Email domain heuristics (catch-all, disposable, malformed)
- Deliverables: `quality.yaml`, quality tiers + flags in CSV/XLSX (and dashboard views)
- Effort: ~1-2 weeks

## Phase 6 - Integrations (Pick-and-Choose)

- Sources: Google Contacts API, Outlook/Exchange CSV variants, LinkedIn CSV enhancements
- Destinations: CRM CSV packs (HubSpot/Salesforce), S3 upload, email templates
- Deliverables: one importer + one destination, end-to-end sample
- Effort: ~1-3 weeks per integration

## Phase 7 - Advanced Matching & Learning

- Probabilistic entity resolution (name/email/company/domain features)
- Confidence scores and "review CSV" for accept/reject of merges
- Deliverables: configurable thresholds; learned lookup expansions with review step
- Effort: ~2-3 weeks

## Phase 8 - Packaging & Ops

- Windows installer (MSI), optional code signing, auto-update
- Logging to files, optional anonymized telemetry toggle
- Deliverables: installer, signed binaries (if cert provided), update channel
- Effort: ~1-2 weeks

## Security & Compliance

- Secrets: credentials reside only in local JSON; rotation documented
- PII: no external calls by default; enrichment opt-in
- Logs: configurable redaction, no data retention beyond local artifacts

## Project Tracking

- GitHub Project (classic) milestones:
  - M5: Integrations, M6: Advanced Matching, M7: Packaging & Ops
- Each phase: 6-10 issues with clear acceptance checklists and sample fixtures

