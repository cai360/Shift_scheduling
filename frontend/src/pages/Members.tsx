import { useEffect, useState } from 'react';
import { useCompanyContext } from '../contexts/useCompanyContext';
import { getMembers, type Member } from '../services/members.api';
import MembersTable from '../components/members/MembersTable';

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

  return (
    <>
      <div>
        <h1>{currentCompany?.company_name}</h1>
        <MembersTable members={members}></MembersTable>
      </div>
    </>
  );
};

export default MembersPages;
