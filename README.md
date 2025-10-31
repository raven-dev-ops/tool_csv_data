# MamboLite - single-CSV contact formatter

**Phase 1 goal:** non-technical users can take one CSV (Gmail, iPhone, LinkedIn, etc.), click to format, and get a standard, clean CSV. Optional: email the result.

## Project layout

```
MamboLite/
- mambo_lite.py             # CLI formatter (core logic)
- mambo_lite_gui.py         # Tiny Tk GUI wrapper (browse -> run -> get CSV)
- lookups/
  - column_map_lookup.csv   # Header alias -> target column mapping
  - prefixes.csv            # Name prefixes (Dr, Mr, etc.)
  - suffixes.csv            # Name suffixes (Jr, PhD, etc.)
  - compound_names.csv      # Particles for compound last names (de, de la, van, etc.)
- samples/
  - sample_contacts.csv     # Quick sample to validate output
- smtp.json.example         # Template for email sending
- scripts/
  - export_kanban.py        # Exports timeline/tasks to a GitHub Project (classic)
  - project_plan.yml        # Milestones, columns, and tasks definition
- docs/
  - SOW.md                  # Statement of Work (source for PDF)
```

## Run the GUI (recommended for non-technical users)

1. Ensure Python 3.9+ is installed.
2. Install dependencies:
   ```bash
   pip install -r MamboLite/requirements.txt
   ```
3. Launch:
   ```bash
   python MamboLite/mambo_lite_gui.py
   ```
4. In the window:
   - Choose `Input CSV`.
   - (Optional) adjust `Lookups` folder (defaults to `./MamboLite/lookups`).
   - Choose `Output CSV` path.
   - Keep `Deduplicate by email` on (recommended).
   - (Optional) tick `Send result via email`, choose `SMTP` or `Outlook`.
     - For `SMTP`, provide `recipient` and `SMTP JSON`.
     - For `Outlook` (Windows), provide `recipient` only (requires Outlook + pywin32).
   - Click `Run`.

## Run the CLI

```bash
python MamboLite/mambo_lite.py --input path/to/contacts.csv --source "Gmail"
# Optional:
# --output out/formatted.csv --lookups MamboLite/lookups --no-dedupe \
# --email you@domain.com --email-method outlook
# --email you@domain.com --email-method smtp --smtp MamboLite/smtp.json.example
```

### Output schema (column order)

```
source, full_name, prefix, first_name, middle_name, last_name, suffix,
email, email_2, phone_mobile, phone_work, phone_home, company, title,
street, street2, city, state, postal_code, country, website,
linkedin_profile, notes
```

## About the lookup files

You can edit the files in `MamboLite/lookups/` to teach MamboLite how to map unusual headers and parse names for your sources. For example, add column name aliases to `column_map_lookup.csv` to catch vendor-specific header names.

## Documentation

- `MamboLite/docs/SOW.md` - Scope, deliverables, acceptance criteria, out-of-scope, and assumptions. Export to PDF if needed.
- The prior Pricing.pdf has been removed per scope change.

## GitHub Project Kanban export

- Option A: Trigger GitHub Action (recommended)
  - In GitHub, go to Actions -> Create MamboLite Kanban -> Run workflow.
  - This uses the built-in GITHUB_TOKEN to create the project, columns, and issues.
- Option B: Run locally with a personal token

- `MamboLite/scripts/project_plan.yml` - Timeline, milestones, columns, and tasks.
- `MamboLite/scripts/export_kanban.py` - Creates a classic GitHub Project, columns, milestones, and issues, and places issues into columns.

Example:

```bash
export GH_TOKEN=ghp_yourtoken
python MamboLite/scripts/export_kanban.py \
  --repo yourorg/yourrepo \
  --project-name "MamboLite Phase 1" \
  --plan MamboLite/scripts/project_plan.yml
```

## Next steps (optional future work)

- Merge multiple CSVs
- Fuzzy dedupe (name+company)
- Excel export with M1-M4 tabs & summary
- One-click Windows `.exe` and small desktop GUI bundle
- Google/LinkedIn/CRM API importers

## Windows packaging (.exe)

Create single-file executables for CLI and GUI with PyInstaller:

1. Install: `pip install pyinstaller`
2. From repo root, run:
   ```bash
   pyinstaller --noconfirm --onefile MamboLite/mambo_lite.py \
     --add-data "MamboLite/lookups;lookups" \
     --add-data "MamboLite/smtp.json.example;." \
     --name MamboLiteCLI

   pyinstaller --noconfirm --onefile --windowed MamboLite/mambo_lite_gui.py \
     --add-data "MamboLite/lookups;lookups" \
     --add-data "MamboLite/smtp.json.example;." \
     --name MamboLite
   ```
3. Executables are in `dist/`.

Notes:
- On macOS/Linux, replace the `;` in `--add-data` with `:`.
- The app auto-detects bundled resources via PyInstaller when available.

## Roadmap

- See `ROADMAP.md` for Phases 2–7: multi-file intake, fuzzy dedupe, Excel output, data quality, GUI settings, integrations, advanced matching, and packaging/ops.


