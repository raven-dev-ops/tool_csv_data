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

Additional components

```
dashboard/
- web-next/                 # Next.js bootstrap (Phase 3 web dashboard)
- api-python/               # FastAPI app skeleton (Phase 3 API)

.github/
- workflows/                # Actions for Kanban & Releases (Phases 1–4)
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

## Housekeeping

- Legacy scripts and local build artifacts have been removed from the root.
- Use GitHub Actions to generate Kanban boards and Releases with executables.
- Executables are published as release assets; they are not stored in the repo.

## Troubleshooting

- CSV encoding issues
  - Symptom: UnicodeDecodeError or garbled characters
  - Fix: The tool auto-tries UTF-8, UTF-8-SIG, CP1252, and Latin-1. If input still fails, re-export as UTF-8 or open/save in a spreadsheet as CSV (UTF-8).

- Outlook email option not working
  - Symptom: “Outlook (pywin32) is not installed or unavailable.”
  - Fix: Install Outlook desktop and `pywin32` (`pip install pywin32`). Use SMTP as an alternative.

- SMTP send fails
  - Symptom: Auth or connection error
  - Fix: Verify host/port (587/TLS or 465/SSL), username/password, and that your firewall allows outbound SMTP. Some providers require app passwords.

- Executable flagged by SmartScreen
  - Symptom: “Windows protected your PC”
  - Fix: Click “More info” -> “Run anyway”, or use a code-signed build. See “Code signing”.

- Missing DLLs on a fresh Windows
  - Symptom: App fails to start
  - Fix: Ensure you’re using the distributed `.exe` from Releases. If persistent, report the error so we can include missing redistributables.

## Code signing (optional)

Release workflows support code signing if you provide secrets:
- `CODE_SIGN_PFX_BASE64`: Base64 of your .pfx certificate (with private key)
- `CODE_SIGN_PASSWORD`: Password to the PFX

The workflow will decode and sign both executables using SHA256 and a timestamp server. If not provided, executables are still produced but may prompt SmartScreen on first run.


