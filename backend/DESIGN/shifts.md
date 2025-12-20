# Shift Module Design (Draft)

## Purpose
The Shift module stores time slots defined by managers that represent available work periods within a company.
Shifts serve as the base entity for later assignment, leave, and takeover workflows.

## Core Rules
- A shifts belongs to exactly one company
- Only company managers can create, updates, or deletes shifts
- employee have read-only access
- Shifts are soft-deleted by default.
- Hard deletion is only allowed when a shift has not produced any assignments or related records.
- Once a shift is published, it becomes immutable to prevent breaking downstream workflows such as assignments, leave requests, and takeovers.

## APIs 
- POST  /componies/{company_id}/shifts
- GET   /componies/{company_id}/shifts
- PATCH / shifts/{shift_id}
- DELETE /shifts/{shift_id}


