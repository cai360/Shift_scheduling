import { Member } from '../../services/members.api';
import { Table } from 'antd';
import type { TableColumnsType, TableProps } from 'antd';

type MembersTableProps = {
  members: Member[];
};

const columns: TableColumnsType<Member> = [
  {
    title: 'Role',
    dataIndex: 'role',
    sorter: (a, b) => a.role.localeCompare(b.role),
    filters: [
      { text: 'Owner', value: 'owner' },
      { text: 'Manager', value: 'manager' },
      { text: 'Employee', value: 'employee' },
    ],
    onFilter: (value, record) => record.role === value,
  },
  {
    title: 'Name',
    dataIndex: 'username',
    sorter: (a, b) => a.username.localeCompare(b.username),
  },
  {
    title: 'Email',
    dataIndex: 'email',
  },
];

const onChange: TableProps<Member>['onChange'] = (
  pagination,
  filters,
  sorter,
  extra,
) => {
  console.log('params', pagination, filters, sorter, extra);
};

const MembersTable = ({ members }: MembersTableProps) => {
  return (
    <Table<Member>
      rowKey="userId"
      columns={columns}
      dataSource={members}
      onChange={onChange}
      showSorterTooltip={{ target: 'sorter-icon' }}
    />
  );
};

export default MembersTable;
