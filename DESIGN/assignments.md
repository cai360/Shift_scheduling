# Assignment Module Design (Draft)

## Purpose
The Assignment module manages the allocation of employees to shifts, ensuring that assignments are valid and conflict-free.

---

## Domain
- A ShiftAssignment represents a relationship between a user and a shift.
- Assignments are created and managed by managers (or owners).
- Assignments do not define shifts; they only attach users to existing shifts.
- Assignments can be created on both draft and published shifts.
- Employees can only see assignments on **published shifts**.

---

## Core Rules
- Assignments belong indirectly to a company via shifts.
- Only managers/owners can assign or unassign users.
- A user must be an active company member to be assigned.

### Validation Rules
- No duplicate assignment:
  - same `user_id` + same `shift_id`
  - `assignment.deleted_at IS NULL`

- Capacity constraint:
  - total active assignments ≤ shift.capacity

- Shift must be valid:
  - `shift.deleted_at IS NULL`

- No overlap with user unavailability:
  - `unavailability.start_at < shift.end_at`
  - `unavailability.end_at > shift.start_at`

- No employee shift overlap:
  - A user cannot be assigned to a shift that overlaps in time with another shift they are already assigned to
  - Applies regardless of whether shifts are draft or published

---

## APIs

- POST   /companies/{company_id}/assignments           (manager/owner only)
- POST   /companies/{company_id}/assignments/unassign  (manager/owner only)

---

## Assignment Creation

### Request Example
```
{
  "user_id": "uuid",
  "shift_ids": ["uuid1", "uuid2"]
}
```

### Behavior
- Input `shift_ids` must be unique.
- All shifts must:
  - belong to the company
  - not be deleted
  - (draft or published both accepted)
- Operation is **all-or-nothing**:
  - if any shift fails validation → entire request fails
- Assignments are created in batch.

---

## Assignment Deletion (Unassign)

### Request Example
```
{
  "assignment_ids": ["uuid1", "uuid2"]
}
```

- Uses soft delete (`deleted_at`)
- Only allowed if:
  - assignment belongs to the company
  - assignment is active (`deleted_at IS NULL`)

### Behavior
- Partial success is not allowed:
  - if any assignment is invalid → reject request

---

## MVP Scope Decisions

- Assignments are mutable (no locking mechanism).
- No approval or publish step for assignments.
- No support for shift swapping (takeover).
- No historical versioning of assignments.

---

## Future Extensions (Out of MVP Scope)

1. Assignment Locking
   - Introduce `assignment_published_at`
   - Prevent modification after publishing

2. Takeover / Swap
   - Allow users to request shift swaps

3. Approval Flow
   - Manager approval for assignment changes

4. Schedule Period (Roster)
   - Group assignments into fixed planning windows

5. Assignment Locking by Payroll Period
   - Prevent modification after payroll period is frozen
