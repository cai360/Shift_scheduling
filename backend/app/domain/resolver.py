class ReviewerResolver:
  @staticmethod
  def resolve(user_id, input_reviewer):
    # TODO： reviewer auto assignment
    if not input_reviewer:
      raise ValueError("reviewed_by is required")
    elif input_reviewer == user_id:
      raise ValueError("Cannot assign yourself")
    return input_reviewer