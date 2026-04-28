import { useEffect, useState } from 'react';
import { useCompanyContext } from '../contexts/useCompanyContext';
import { getMembers, updateRole, type Member } from '../services/members.api';
import MembersTable from '../components/members/MembersTable';
import { message } from 'antd';

const MembersPages = () => {
  const { companies, currentCompanyId } = useCompanyContext();
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

  const handleUpdateRole = async (userId: string, role: string) => {
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

  return (
    <>
      <div>
        <h1>{currentCompany?.company_name}</h1>
        <MembersTable
          members={members}
          onUpdateRole={handleUpdateRole}
        ></MembersTable>
      </div>
    </>
  );
};

export default MembersPages;
