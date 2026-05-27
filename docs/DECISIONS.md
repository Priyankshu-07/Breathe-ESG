SAP — Fuel & Procurement
Format: Semicolon-delimited CSV, since this is what facilities teams actually export from SAP (via SE16 or MB51). IDocs are for system-to-system integration; OData requires Fiori/Gateway setup most clients don't have.
Bilingual headers: SAP instances in Europe often export German headers (Buchungsdatum, Menge). The parser handles both via a single column map.
What's in scope: Goods issue movements only (types 201, 261, 262). Receipts, transfers, and POs are out.
Fuel detection: Material codes with FUEL/DSL/PETROL/CNG/LPG/HSD prefixes = fuel. Everything else = procurement.
Open questions for PM: Plant code lookup source? Scope 3 treatment for procurement rows? SAP module (MM or FI)?

Utility — Electricity
Format: Portal CSV export (PG&E, National Grid, etc.). PDF parsing is brittle; utility APIs require per-provider OAuth that doesn't exist universally.
BOM handling: utf-8-sig encoding strips the hidden \ufeff character Excel adds to CSV exports.
What's in scope: Electricity only (kWh/MWh/GWh, normalized to kWh). Gas and water are out.
Billing periods: Three formats supported — explicit start/end dates, a single month string, or missing (ingested with a warning).
Open questions for PM: Multiple meters per site — aggregate how? Location-based or national grid emission factor?

Corporate Travel
Format: JSON modeled on Concur/Navan's API structure. Travel data is nested (one trip → multiple segments), which CSV handles poorly.
Missing flight distances: A lookup table covers common routes; unknowns default to 0 km with a warning. Production would use great-circle calculation.
Emission factors (DEFRA 2023):

Flight: economy 0.255 / business 0.573 / first 1.020 kg CO2e/km
Hotel: 0.0713 kg CO2e/night
Ground: taxi 0.149, car 0.168, train 0.035, bus 0.105 kg CO2e/km

Open questions for PM: Concur vs Navan (JSON shape differs)? Unknown cabin class — default to economy or flag?

Ingestion Pipeline
Synchronous processing: Sufficient for a 4-day prototype. A comment in the code marks where ingest_and_normalize.delay(job.id) (Celery) would go in production.
File upload vs API pull: Works across all three sources without per-client credentials, and matches how sustainability teams actually operate today.
raw_data vs parsed_data: raw_data is the immutable original. parsed_data is what normalization uses. Currently identical at ingestion time; split kept for future use.

Review Workflow
Approved vs locked: Approved = analyst sign-off. Locked = submitted to auditor, no further changes. Matches real ESG audit workflows.
Row locking: select_for_update() inside transaction.atomic prevents two analysts approving the same row simultaneously.
Reject → approve: Not allowed directly. Rejected rows must be edited or re-ingested first, to ensure re-review actually happens.

Auth & Data Model
Token auth: Stateless, works cleanly with a React frontend. Session auth included as fallback for Django admin.
UUID primary keys: No sequential ID leakage, safe to generate client-side, consistent across models.
Decimal over Float: Rounding errors in float arithmetic compound across large datasets. Emission reporting requires exact arithmetic