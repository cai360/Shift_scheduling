class AssignmentConflictError(Exception):
    def __init__(self, conflict_shift_ids):
        self.conflict_shift_ids = conflict_shift_ids