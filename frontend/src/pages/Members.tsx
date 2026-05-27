import { useEffect, useState } from 'react';
import { useCompanyContext } from '../contexts/useCompanyContext';
import {
  getMembers,
  updateRole,
  transferOwner,
  type Member,
} from '../services/members.api';
import { getMyCompanies } from '../services/company.api';
import MembersTable from '../components/members/MembersTable';
import { message } from 'antd';
import { useAuthContext } from '../contexts/useAuthContext';
import type { CompanyRole } from '../types/company';

const MembersPages = () => {
  const { companies, currentCompanyId, setCompanies } = useCompanyContext();
  const { user } = useAuthContext();
  const [members, setMembers] = useState<Member[]>([]);

  const currentCompany = companies.find(
    (c) => c.company_id === currentCompanyId,
  );

  useEffect(() => {
    if (!currentCompanyId) return;

    const fetchMembers = async () => {
      const data = await getMembers(currentCompanyId);
      console.log('api data:', data);
      setMembers(data);
    };

    fetchMembers();
  }, [currentCompanyId]);

  const handleUpdateRole = async (userId: string, role: CompanyRole) => {
    if (!currentCompanyId) return;
    try {
      await updateRole(currentCompanyId, userId, role);
      const data = await getMembers(currentCompanyId);
      message.success('Update success');
      setMembers(data);
    } catch {
      message.error('Update failed');
    }
  };

  const handleTransferOwner = async (targetId: string) => {
    if (!currentCompanyId) return;
    try {
      await transferOwner(currentCompanyId, targetId);
      const members = await getMembers(currentCompanyId);
      setMembers(members);

      const companies = await getMyCompanies();
      setCompanies(companies);

      message.success('Update success');
    } catch {
      message.error('Update failed');
    }
  };

  return (
    <>
      <div>
        <h1>{currentCompany?.company_name}</h1>
        <MembersTable
          members={members}
          onUpdateRole={handleUpdateRole}
          onTransferOwnership={handleTransferOwner}
          currentUserId={user?.id}
          currentUserRole={currentCompany?.role}
        ></MembersTable>
      </div>
    </>
  );
};

export default MembersPages;
