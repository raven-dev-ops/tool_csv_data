# Statement of Work – MamboLite (Phase 1)

## Project: MamboLite Single CSV Contact Formatter (Phase 1)

### Purpose
Provide a simple, reliable tool that standardizes a single exported contacts CSV into a clean, well-defined schema with basic name parsing, phone/email normalization, optional email-based deduplication, and (optionally) emailing the result.

### Scope (Included)
- CLI formatter and a Tkinter GUI wrapper
- Editable lookups
- Sample CSV
- Documentation
- Basic SMTP sending of the final CSV

### Out of Scope (Phase 1)
- Multi-file merging
- Fuzzy duplicate detection beyond exact email
- Excel M1–M4 tabs
- Windows .exe packaging
- Integrations with Google/LinkedIn/CRM APIs

These can be scheduled in later phases.

### Deliverables
1) `mambo_lite.py` (core CLI)
2) `mambo_lite_gui.py` (GUI)
3) `lookups/` with starter files
4) `samples/sample_contacts.csv`
5) `README.md`
6) `docs/SOW.md` (source for PDF)
7) `scripts/export_kanban.py` + `scripts/project_plan.yml` (GitHub Project export)

### Acceptance Criteria
- Running the CLI or GUI on provided sample produces a formatted CSV conforming to the documented schema
- Email send works when valid SMTP config is supplied
- Clear logs with no garbled characters on Windows
- Lookup edits are respected without code changes

### Assumptions
- CSV exports are parseable with common encodings (UTF-8/CP1252/Latin-1)
- Python 3.9+ available; `pandas` install permitted
- Client provides SMTP credentials if email is used

### Change Management
Additional features and adjustments beyond this scope are billed hourly and can be added incrementally without blocking Phase 1 usage.

### Intellectual Property
All project-specific source code and lookup files are delivered to the client.

