# from services.companyUser_service import CompanyUserService

class ReviewerResolver:
    @staticmethod
    def resolve(user_id, company_id, input_reviewer):
      if not input_reviewer:
        raise ValueError("reviewed_by is required")
      return input_reviewer
      # TODO： Auto find manager