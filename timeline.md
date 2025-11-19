# MamboLite Timeline & Milestones

This document turns the Phase 1 project plan into a simple, checkbox-style milestone tracker.  
For full issue text and acceptance criteria, see `MamboLite/scripts/project_plan.yml`.

## Milestone overview

| Milestone | Target date  | Summary                               |
|----------:|--------------|---------------------------------------|
| M1        | 2025-11-07   | Baseline CLI formatter                |
| M2        | 2025-11-12   | GUI + email sending                   |
| M3        | 2025-11-14   | Docs, packaging, and Kanban export    |
| M4        | 2025-11-18   | UAT, acceptance, and handover         |

## M1: Baseline + CLI (2025-11-07)

- [ ] Select baseline and stabilize code  
  - Single-source CSV flow, clean logging, encoding fallbacks.
- [ ] Add header alias mapping via lookups  
  - Alias -> target mapping from `lookups/column_map_lookup.csv`.
- [ ] Implement name parsing and normalization  
  - Prefix/suffix handling, compound last names, phone/email normalization.
- [ ] CLI flags and output schema  
  - `--input`, `--output`, `--lookups`, `--source`, `--no-dedupe`; fixed output column order.

## M2: GUI + Email (2025-11-12)

- [ ] Tkinter GUI wrapper  
  - Input/output pickers, lookups folder, dedupe toggle, email toggle.
- [ ] SMTP send of result  
  - JSON SMTP config, TLS/SSL support, clear error messages.
- [ ] Outlook (MAPI) email option  
  - pywin32 integration, Outlook prerequisites, graceful failure when unavailable.

## M3: Docs + Packaging (2025-11-14)

- [ ] Seed lookups and sample CSV  
  - Prefixes/suffixes/compound names and a representative sample CSV.
- [ ] Documentation and README  
  - GUI/CLI usage, output schema, acceptance notes.
- [ ] Troubleshooting & FAQ  
  - Encoding, SMTP, Outlook, file permissions, and other common issues.
- [ ] Windows packaging (.exe)  
  - PyInstaller builds for CLI and GUI; bundled lookups and SMTP template.
- [ ] Packaging validation on clean Windows  
  - Smoke tests on a clean VM with no dev tools.
- [ ] Security & privacy notes  
  - Credential handling, no data retention, privacy assumptions.
- [ ] Publish Kanban to GitHub Project  
  - Run exporter, verify columns/issues, avoid duplicates.

## M4: Acceptance & Handover (2025-11-18)

- [ ] UAT: Acceptance & Handover  
  - Run 3–5 real CSVs, validate correctness, verify email sending, deliverables (EXEs, README, SOW).
- [ ] Release notes & CHANGELOG  
  - v1.1 entry, feature summary, known limitations.

