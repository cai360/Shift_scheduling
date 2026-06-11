export const CompanyRoles = {
  OWNER: 'owner',
  MANAGER: 'manager',
  EMPLOYEE: 'employee',
} as const;

export type CompanyRole = (typeof CompanyRoles)[keyof typeof CompanyRoles];
