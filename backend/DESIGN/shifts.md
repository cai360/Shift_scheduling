# Shift Module Design (Draft)

## Purpose
The Shift module manages planned working time slots defined by company managers and owner.
These shifts act as the base entities for downstream workflows such as assignment, leave requests, and takeovers.

The module focuses on shift generation and lifecycle control, not on employee assignment.
---

## Domain
- A Shift represents a concrete, time-bound working slot.
- A Shift is not an assignment and does not imply that any employee is assigned.
- Shifts are created in bulk based on generation rules defined by managers.
---

## Core Rules
- Shifts belong to exactly one company.
- Only company managers and owners can create, update, or delete shifts.
- Employees have read-only access to shifts.
- Draft shifts:
  - can be updated
  - can be hard-deleted
  - may overlap with other draft shifts
- Published shifts:
  - are immutable
  - must not overlap with any other published shift in the same company
  - can only be canceled in future iterations (out of MVP scope)
---

## APIs
- POST   /companies/{company_id}/shifts/bulk  (manager/owner only)
- GET    /companies/{company_id}/shifts       (list shifts)
- PATCH  /shifts/{shift_id}                  (draft only)
- DELETE /shifts/{shift_id}                  (draft only)
- POST   /companies/{company_id}/shifts/publish (manager/owner only)

API Notes
- Bulk creation is the primary creation method.
- Individual update / delete operations are restricted to draft shifts only.
- Publishing is treated as irreversible in MVP.
- Bulk publish is **all-or-nothing**:
  - If any shift is invalid, already published, deleted, or not in the company, the request fails.
- Canceling published shifts is out of MVP scope.
---
## Shift Creation (Bulk)
Shifts are not created one by one by managers, manager defined a time-range and generation rule, and the system generatres individual shift records accordingly. 

request payload example
```
{
  "start_date": "2025-03-01",
  "end_date": "2025-03-30",
  "start_time": "09:00",
  "end_time": "18:00",
  "interval_minutes": 120,
  "capacity": 3
}
```

### Field Definitions
- **start_date / end_date**  
  Define the date range for shift generation.

- **start_time / end_time**  
  Define a continuous daily working period.  
  Overnight periods (e.g. 22:00 → 06:00) are supported.

- **interval_minutes**  
  Defines slot length for generated shifts.

- **capacity**  
  Defines how many employees can be assigned to each shift.

### Behavior
- Draft shifts may overlap.
- Exact duplicate slots (same start_at, end_at) are rejected 
- Overlap validation is NOT enforced during creation.
- Overlap validation is enforced at publish time only.
---

## Publish Validation Rules

When publishing shifts, the system enforces:

### 1. Candidate vs Candidate
- No overlap among shifts being published in the same request.

### 2. Candidate vs Existing Published
- No overlap between candidate shifts and already published shifts.

### Overlap Definition
```
A.start_at < B.end_at AND A.end_at > B.start_at
```
---

## Time Handling Rules
	•	Shift generation is based on wall-clock time, not elapsed real time.
	•	Daily working periods are interpreted in the business timezone.
	•	Generated shift records are stored in UTC to ensure DST safety.
	•	Overnight shifts are handled by advancing the end datetime to the next day when needed.

## MVP Scope Decisions
- Only one continuous working period per day is supported.
- No breaks or split shifts exposed in API.
- Simplifies validation and reduces user error.

Design allows:
- future extension without DB schema changes
- backward compatibility with existing shift records
---

## Future Extensions(Out of MVP Scope)

The following extensions can be added without breaking existing behavior:
	1.	Breaks / Non-working Periods
	•	Support multiple working periods per day (e.g. lunch breaks).
	2.	Variable Shift Durations
	•	Allow different interval lengths within different working periods.
	3.	Time-based Capacity Variations
	•	Capacity rules that vary by time of day.
	4.	Shift Templates / Rule Persistence
	•	Persist reusable generation rules.