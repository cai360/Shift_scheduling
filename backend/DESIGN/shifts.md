# Shift Module Design (Draft)

## Purpose
The Shift module manages planned working time slots defined by company managers.
These shifts act as the base entities for downstream workflows such as assignment, leave requests, and takeovers.

The module focuses on shift generation and lifecycle control, not on employee assignment.

## Domain
- A Shift represents a concrete, time-bound working slot.
- A Shift is not an assignment and does not imply that any employee is assigned.
- Shifts are created in bulk based on generation rules defined by managers.

## Domain
- A shift represents a planned working time slot created by manager
- A shift is not an assignment

## Core Rules
- A shifts belongs to exactly one company
- Only company managers can create, updates, or deletes shifts
- employee have read-only access
- Shifts are soft-deleted by default.
- Hard deletion is only allowed when a shift has not produced any assignments or related records.
- Once a shift is published, it becomes immutable to prevent breaking downstream workflows such as assignments, leave requests, and takeovers.

## APIs 
- POST  /componies/{company_id}/shifts/bulk （manager only）
- GET   /componies/{company_id}/shifts （get all shift）
- PATCH /shifts/{shift_id} (draft only)
- DELETE /shifts/{shift_id} (draft only)
- POST /componies/{company_id}/shifts/publish （manager only）

API Notes
- Bulk creation is the primary creation method.
- Individual update / delete operations are restricted to draft shifts only.
- Publishing a shift is an explicit, irreversible state transition.

### Shift Creation (Bulk)
Shifts are not created one by one by managers, manager defined a time-range and generation rule, and the system generatres individual shift records accordingly. 

request payload would look like this 
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


	•	start_date / end_date
Define the date range for shift generation.
	•	start_time / end_time
Define a single continuous daily working period.
	•	Overnight periods (e.g. 22:00 → 06:00) are supported.
	•	interval_minutes
Defines the slot length for generated shifts.
	•	capacity
Defines how many employees can be assigned to each shift.

## Time Handling Rules
	•	Shift generation is based on wall-clock time, not elapsed real time.
	•	Daily working periods are interpreted in the business timezone.
	•	Generated shift records are stored in UTC to ensure DST safety.
	•	Overnight shifts are handled by advancing the end datetime to the next day when needed.


## MVP Scope Decision

For the MVP:
	•	Only one continuous working period per day is supported.
	•	Lunch breaks or split shifts are not exposed in the API.
	•	This constraint simplifies validation and reduces user error.

Internally, the generation logic is designed so that:
	•	multiple working periods can be supported later
	•	without changing the database schema
	•	and without refactoring existing shift records

## Future Extensions(Out of MVP Scope)

The current design intentionally keeps generation rules stateless and request-based.

The following extensions can be added without breaking existing behavior:
	1.	Breaks / Non-working Periods
	•	Support multiple working periods per day (e.g. lunch breaks).
	2.	Variable Shift Durations
	•	Allow different interval lengths within different working periods.
	3.	Time-based Capacity Variations
	•	Capacity rules that vary by time of day.
	4.	Shift Templates / Rule Persistence
	•	Persist reusable generation rules.
