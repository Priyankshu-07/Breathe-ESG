SAP — Fuel & Procurement
What was researched: SAP transactions MB51 and SE16 for goods movement exports, the MSEG/MKPF tables, and BAPI_GOODSMVT_GETDETAIL. IDoc and OData were investigated and rejected (see DECISIONS.md).
Key findings:

Flat file exports are semicolon-delimited, dates in YYYYMMDD (or DD.MM.YYYY regionally), headers in the system language (German: Buchungsdatum, Menge, Werk)
Units are SAP internal codes: L litre, KG kilogram, M3 cubic metre, ST piece
Movement type determines consumption vs receipt: 201 (cost center), 261 (production order), 262 (reversal of 261). Type 101 (goods receipt) is excluded.
Plant codes are client-specific and meaningless without a per-client lookup table

Sample data (sap_export.txt): 20 rows, semicolon-delimited, German headers, YYYYMMDD dates. Covers mixed movement types, FUEL/DSL material prefixes, one missing quantity, and one unknown plant code.
Known gaps for production:

Plant code lookup needs importing from SAP's T001W table per client
Material code → fuel type mapping breaks with client-specific numbering schemes
Encoding can be UTF-8, Latin-1, or CP1252; CP1252 edge cases may fail
German decimal format (1.234,56) — thousands separator not fully handled
50k+ rows per quarter would time out synchronous processing; needs Celery


Utility — Electricity
What was researched: PG&E and National Grid portal CSV formats, the Green Button / ESPI standard, OFGEM smart meter guidance.
Key findings:

Most portal exports include a BOM (\ufeff) — a Microsoft Excel artifact
Column headers vary by provider (PG&E: "Electric Usage (kWh)"; National Grid: "Consumption" + separate "Units" column)
Billing periods rarely align with calendar months
Only active power (kWh) is relevant; some exports also include reactive power (kVAr)
Grid emission factors: UK DEFRA 2023 = 0.20493 kg CO2e/kWh; US EPA 2023 = 0.386 kg CO2e/kWh

Sample data (utility_export.csv): 12 rows, UTF-8 with BOM, two meter IDs, mixed kWh/MWh units, one missing consumption value, one ambiguous period string ("Jan 2023").
Known gaps for production:

Grid emission factor not yet applied — requires client location and annual factor updates
GHG Protocol Scope 2 requires both location-based and market-based calculations; only location-based is supported
Parser assumes one row per billing period; interval data (15/30-min smart meter exports) would break it
PDF bills not supported
Multi-fuel meters (electricity + gas) not supported


Corporate Travel
What was researched: Concur and Navan API documentation, DEFRA 2023 conversion factors, ICAO methodology, GHG Protocol Scope 3 Category 6.
Key findings:

Concur structures data as trips containing typed segments (air, hotel, car, rail)
Flight distance is often absent and must be calculated from airport coordinates
Hotel nights may need to be derived from check-in/check-out dates
DEFRA 2023 factors (kg CO2e/km): economy 0.255, business 0.573, first 1.020; unknown defaults to economy
DEFRA 2023 hotel factor: 0.0713 kg CO2e/room night
DEFRA 2023 ground factors (kg CO2e/km): taxi 0.149, car 0.168, train 0.035, bus 0.105

Sample data (travel_export.json): 5 trips with mixed flight/hotel/ground segments. Covers known and unknown routes, mixed cabin classes, explicit and date-derived hotel nights, and a missing distance value.
Known gaps for production:

Only 6 hardcoded flight routes; unknown routes default to 0 km (silently wrong)
Cabin class as IATA booking codes (Y/C/F) not handled — plain English only
Spend-based emission factors not implemented (would require currency normalization)
Radiative forcing index (RFI) multiplier not applied — some clients will ask for it
All trips assumed corporate; no personal/corporate flag
