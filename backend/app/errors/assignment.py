class AssignmentConflictError(Exception):
    def __init__(self, conflict_shift_ids, reason="assignment_conflict"):
        self.conflict_shift_ids = conflict_shift_ids
        self.reason = reason

class AssignmentCapacityExceededError(Exception):
    def __init__(self, shift_ids):
        self.shift_ids = shift_ids