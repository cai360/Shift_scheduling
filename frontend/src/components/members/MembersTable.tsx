import { Member, type Role } from '../../services/members.api';
import { Table, Space, Modal, Radio, message } from 'antd';
import type { TableColumnsType, TableProps } from 'antd';
import { useState } from 'react';
import styles from './MembersTable.module.css';

type MembersTableProps = {
  members: Member[];
  onUpdateRole: (userId: string, role: Role) => Promise<void>;
  onTransferOwnership: (userId: string) => Promise<void>;
  currentUserId?: string;
};

const MembersTable = ({
  members,
  onUpdateRole,
  onTransferOwnership,
  currentUserId,
}: MembersTableProps) => {
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<Member | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);

  const showRoleModal = (member: Member) => {
    console.log('selected member:', member);
    setSelectedUser(member);
    setSelectedRole(member.role);
    setIsRoleModalOpen(true);
  };

  const handleOk = async () => {
    if (!selectedUser) return;
    if (!selectedRole) return;
    if (selectedRole === selectedUser.role) {
      message.warning("can't update the same role");
      return;
    }
    try {
      await onUpdateRole(selectedUser.user_id, selectedRole);
      resetRoleModal();
    } catch {
      message.error('Request fail');
    }
  };

  const resetRoleModal = () => {
    setIsRoleModalOpen(false);
    setSelectedRole(null);
    setSelectedUser(null);
  };

  const handleCancel = () => {
    resetRoleModal();
  };

  const onTableChange: TableProps<Member>['onChange'] = (
    pagination,
    filters,
    sorter,
    extra,
  ) => {
    console.log('params', pagination, filters, sorter, extra);
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
    {
      title: 'Action',
      key: 'operation',
      render: (_, record) => (
        <Space size="middle">
          <button onClick={() => showRoleModal(record)}>UpdateRole</button>
          <button onClick={() => onTransferOwnership(record.user_id)}>
            Transfer
          </button>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Table<Member>
        rowKey="user_id"
        columns={columns}
        dataSource={members}
        onChange={onTableChange}
        showSorterTooltip={{ target: 'sorter-icon' }}
        rowClassName={(record) =>
          record.user_id === currentUserId ? styles['current-user-row'] : ''
        }
      />
      <Modal
        title="Basic Modal"
        closable={{ 'aria-label': 'Custom Close Button' }}
        open={isRoleModalOpen}
        onOk={handleOk}
        onCancel={handleCancel}
      >
        <Radio.Group
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value as Role)}
          style={{ width: '100%' }}
          options={[
            { label: 'Manager', value: 'manager' },
            { label: 'Employee', value: 'employee' },
          ]}
        />
      </Modal>
    </>
  );
};

export default MembersTable;
