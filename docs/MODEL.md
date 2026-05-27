# MODEL.md — Data Model Documentation

## Overview

The data model is built around a core pipeline: raw files come in, get parsed into
rows, get normalized into emission records, get reviewed by analysts, and get locked
for audit. Every stage is traceable back to the source.

---

## Entity Map

```
Organisation (tenant anchor)
└── IngestionJob (one upload = one job)
    └── IngestionRow (one row per parsed record)
        └── NormalizedEmission (one normalized record per valid row)
            └── ReviewAction (every approve/reject/flag/lock action)

AuditEvent (generic — points at any model)
User (belongs to one Organisation, has a role)
```

---

## Multi-Tenancy

Every model that holds data has a direct or indirect FK to `Organisation`.
Tenant isolation is enforced at two levels:

**Queryset level** — every view filters by `request.user.organisation`:
```python
NormalizedEmission.objects.filter(organisation=request.user.organisation)
```

**Object level** — `IsTenantMember.has_object_permission` resolves the
organisation from the object and compares it to the requesting user's organisation.
This handles nested objects (IngestionRow → IngestionJob → Organisation).

A user without an organisation cannot pass `has_permission` at all.

---

## Models

### Organisation
Tenant anchor. Every piece of data belongs to one organisation.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | CharField | Display name |
| slug | SlugField | Unique, URL-safe identifier |
| created_at | DateTimeField | Auto |

---

### User
Extends Django's AbstractUser. Role-based access control.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| organisation | FK → Organisation | Null allowed for superusers |
| role | CharField | admin / analyst / viewer |

Roles are checked in `IsAnalyst` and `IsAdmin` permission classes.
Only analysts and admins can upload files or perform review actions.

---

### IngestionJob
One record per file upload. Tracks the full lifecycle of an ingestion.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| organisation | FK → Organisation | Tenant scoping |
| uploaded_by | FK → User | SET_NULL — survives user deletion |
| source_type | CharField | sap / utility / travel |
| status | CharField | pending / processing / done / failed |
| file | FileField | Stored under uploads/YYYY/MM/DD/ |
| raw_filename | CharField | Original filename preserved |
| row_count | IntegerField | Total rows parsed |
| error_count | IntegerField | Rows that failed or warned |
| created_at | DateTimeField | Auto |
| completed_at | DateTimeField | Null until job finishes |

---

### IngestionRow
One record per parsed row from the source file. Never modified after creation —
it is the source of truth for what came in.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| job | FK → IngestionJob | Cascade delete |
| row_index | IntegerField | Original row position in file |
| raw_data | JSONField | Exact parsed output, never touched |
| parsed_data | JSONField | Same at ingestion; updated by normalization |
| status | CharField | ok / warning / error |
| error_message | TextField | Human-readable parse/normalization errors |
| created_at | DateTimeField | Auto |

---

### NormalizedEmission
The core record. One per valid IngestionRow. All values normalized to SI units
and kg CO2e. Original values preserved for traceability.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| organisation | FK → Organisation | Tenant scoping |
| source_row | OneToOneField → IngestionRow | One emission per row |
| scope | CharField | scope1 / scope2 / scope3 |
| category | CharField | fuel_combustion / electricity / flight / hotel / ground / procurement |
| activity_value | Decimal(18,6) | Normalized quantity |
| activity_unit | CharField | kWh / litres / km / nights |
| co2e_kg | Decimal(18,6) | Calculated kg CO2e — null if EF not available |
| period_start | DateField | Normalized period start |
| period_end | DateField | Normalized period end |
| original_value | Decimal(18,6) | Raw value from source file |
| original_unit | CharField | Raw unit from source file |
| emission_factor_used | Decimal(18,8) | EF applied — null for SAP/utility |
| emission_factor_source | CharField | e.g. "DEFRA 2023" |
| status | CharField | pending_review / approved / rejected / locked |
| is_edited | BooleanField | True if analyst changed activity_value |
| created_at | DateTimeField | Auto |
| updated_at | DateTimeField | Auto |

**Why preserve original_value and original_unit?**
Auditors need to verify that the normalization was correct. Storing both the
original and normalized values means any transformation can be audited.

**Why is co2e_kg nullable?**
SAP and utility rows don't have emission factors applied at normalization time —
the factor depends on fuel type (SAP) or grid emission factor (utility), which
requires lookup tables not yet implemented. Travel rows get co2e_kg calculated
immediately using DEFRA 2023 factors. This is a known limitation documented in
TRADEOFFS.md.

**Scope assignment:**
| Category | Scope |
|---|---|
| fuel_combustion | Scope 1 |
| electricity | Scope 2 |
| business_travel_flight | Scope 3 |
| business_travel_hotel | Scope 3 |
| business_travel_ground | Scope 3 |
| procurement | Scope 3 |

---

### ReviewAction
Immutable log of every analyst action on an emission record.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| emission | FK → NormalizedEmission | Cascade |
| analyst | FK → User | SET_NULL — survives user deletion |
| action | CharField | approve / reject / flag / edit / lock |
| note | TextField | Optional analyst note |
| previous_value | JSONField | Snapshot before edit |
| created_at | DateTimeField | Auto |

---

### AuditEvent
Generic audit trail. Can point at any model via GenericForeignKey.
Records every significant system event — ingestion, approval, edit, lock.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| organisation | FK → Organisation | Tenant scoped |
| actor | FK → User | SET_NULL — survives user deletion |
| content_type | FK → ContentType | Which model was affected |
| object_id | UUID | Which instance was affected |
| verb | CharField | e.g. "approved", "ingested", "locked_for_audit" |
| detail | JSONField | Before/after values, counts, notes |
| timestamp | DateTimeField | Auto |

**Why GenericForeignKey?**
A single audit table that works across all models is cleaner than separate
audit tables per model. The tradeoff is that you can't do DB-level joins on
content_object — but audit logs are read sequentially, not joined.

---

## Audit Trail

Every mutation in the system creates an AuditEvent:

| Action | Verb | Detail |
|---|---|---|
| File uploaded + processed | ingested | source_type, filename, row counts |
| Emission edited | emission_updated | before/after activity_value and co2e_kg |
| Emission approved | approved | old_status → new_status |
| Emission rejected | rejected | old_status → new_status + note |
| Emission flagged | flagged | note |
| Emission locked | locked_for_audit | — |

Locked emissions cannot be edited or re-reviewed. This is enforced at both
the service layer (`_assert_not_locked`) and the serializer layer
(`EmissionUpdateSerializer.validate`).

---

## Source-of-Truth Tracking

Every NormalizedEmission links back to:
- The IngestionRow (raw + parsed data)
- The IngestionJob (which file, who uploaded it, when)
- The Organisation (which client)

This chain means any emission record can be traced back to the exact row
in the exact file uploaded by the exact user at the exact time.