# MamboLite Phase 4 – Business Card OCR & Scanning (Proposal)

## Objectives

- Let users scan business cards via web (camera) or mobile and transcribe to contact cards in their account.
- Map fields to unified schema and dedupe into existing contacts.

## OCR Options

- Local: Tesseract (desktop or WASM in-browser)
  - Pros: No data leaves client/server, low cost
  - Cons: Lower accuracy without tuning; complex in-browser
- Cloud: AWS Textract / Google Vision
  - Pros: High accuracy, layout detection, language support
  - Cons: Ongoing cost, PII handling

## Proposed Pipeline

1. Capture image (web or mobile)
2. Pre-process (deskew, crop, contrast)
3. OCR engine (local/cloud)
4. Field extraction (regex/NLP) -> name, title, company, phones, emails, address, website
5. Confidence scoring per field; user review UI
6. Normalize and dedupe into contacts_unified

## Data & Privacy

- Images stored in object storage (S3/Azure Blob) with encryption-at-rest
- Signed URLs for access; short TTLs
- Retention control (delete on request)

## UI/UX

- Web capture (getUserMedia), crop/adjust, preview
- Optional mobile app (React Native/Capacitor) for better camera UX
- Review form with highlighted extraction and editable fields

## Integration Points

- Reuse mapping/normalization from MamboLite
- Call dedupe on review-submit
- Store original image + extracted fields + final contact

## Milestones

1) OCR engine & data model
2) Capture (web/mobile)
3) Extraction & validation
4) Dashboard integration + UAT

