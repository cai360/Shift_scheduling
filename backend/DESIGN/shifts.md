# Shift Module Design (Draft)

## Purpose
The Shift module stores time slots defined by managers that represent available work periods within a company.
Shifts serve as the base entity for later assignment, leave, and takeover workflows.

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
- GET   /componies/{company_id}/shifts
- PATCH /shifts/{shift_id} (draft only)
- DELETE /shifts/{shift_id} (draft only)
- POST /shifts/{shift_id}/publish


### Shift Creation (Bulk)
Shifts are not created one by one by managers, manager defined a time-range and generation rule, and the system generatres individual shift records accordingly. 

request payload would look like this 
```
{
  "start_date": "2025-03-01",
  "end_date": "2025-03-07",
  "start_time": "09:00",
  "end_time": "18:00",
  "interval_minutes": 120,
  "capacity": 3
}
```

## Future Extensions
1. Breaks / Non-working Periods Within a Day
2. Variable Shift Duration (Non-uniform Intervals)
3. Time-based Capacity Variations
4. Shift Templates and Rule Persistence
    If generation rules need to be reused, we might add tables such as company_shift_templates
