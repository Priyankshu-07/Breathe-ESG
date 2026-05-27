1. Emission Factor Engine
What's missing: SAP fuel rows and utility electricity rows have co2e_kg = null — no factor is applied. Travel factors are hardcoded DEFRA 2023 constants.
What a real system needs:

A versioned factor table (DEFRA updates annually; GHG Protocol has its own set)
Fuel type lookup: SAP material code → fuel type → kg CO2e per litre/kg
Grid factor lookup: meter location → country/region → kg CO2e/kWh (location-based and market-based)
Per-row factor source tracking

Why it was skipped: Building a proper factor engine would have consumed most of the 4-day timeline. Instead, the data model is ready for it — emission_factor_used and emission_factor_source fields exist on every NormalizedEmission record.
Travel factors are hardcoded because they're stable and well-documented. Fuel and electricity factors vary too much by material and location to hardcode responsibly.
Impact: Travel rows get co2e_kg calculated. SAP and utility rows show co2e_kg = null and are flagged for analyst review. The review workflow is fully functional — only the calculation is missing.

2. Asynchronous Ingestion
What's missing: Background task processing. Ingestion and normalization run synchronously inside the upload HTTP request. For large files, this will time out.
What a real system needs: Celery + Redis (or similar). The code has a comment marking exactly where .delay(job.id) would go. The IngestionJob status field (pending / processing / done / failed) is already designed for async — it exists specifically to be polled.
Why it was skipped: Synchronous processing is sufficient for prototype-scale files and eliminates the need to run and configure a separate task queue. The architectural seam is already in place.
Impact: Files with 50k+ rows (realistic for a large SAP client) would time out in production. Fine for a prototype.

3. Market-Based Scope 2 Calculation
What's missing: The prototype calculates electricity emissions using location-based grid factors only. GHG Protocol Scope 2 guidance requires both location-based and market-based calculations.
What a real system needs:

Support for contractual instruments: RECs (Renewable Energy Certificates), PPAs (Power Purchase Agreements), supplier-specific emission rates
A separate co2e_kg_market field on NormalizedEmission (or a second emission record per electricity row)
Client configuration for which instruments they hold

Why it was skipped: Market-based calculations require client-specific contractual data that isn't available in a utility portal export. It's also a significant data modeling decision — parallel location/market records vs a single record with two values — worth discussing with the PM before building.
Impact: Electricity rows will show location-based figures only. Clients with renewable energy contracts will see higher emissions than their market-based position reflects. This should be called out explicitly before any client demo.