import { CompanyRoles, type CompanyRole } from '../types/company';

export const MemberPermissions = {
  VIEW_ACTIONS: 'member.viewActions',
  UPDATE_ROLE: 'member.updateRole',
  TRANSFER_OWNERSHIP: 'member.transferOWnership',
} as const;

export type MemberPermission =
  (typeof MemberPermissions)[keyof typeof MemberPermissions];

const rolePermissions: Record<CompanyRole, MemberPermission[]> = {
  [CompanyRoles.OWNER]: [
    MemberPermissions.VIEW_ACTIONS,
    MemberPermissions.UPDATE_ROLE,
    MemberPermissions.TRANSFER_OWNERSHIP,
  ],

  [CompanyRoles.MANAGER]: [],

  [CompanyRoles.EMPLOYEE]: [],
};

export const hasMemberPermission = (
  role: CompanyRole,
  permission: MemberPermission,
) => {
  if (!role) return false;
  return rolePermissions[role].includes(permission) ?? false;
};
