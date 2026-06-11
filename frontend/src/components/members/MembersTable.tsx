import { Member } from '../../services/members.api';
import { Table, Space, Modal, Radio, message, Popconfirm } from 'antd';
import type { TableColumnsType, TableProps } from 'antd';
import { useState } from 'react';
import styles from './MembersTable.module.css';
import type { CompanyRole } from '../../types/company';
import {
  hasMemberPermission,
  MemberPermissions,
} from '../../permissions/companyPermissions';

type MembersTableProps = {
  members: Member[];
  onUpdateRole: (userId: string, role: CompanyRole) => Promise<void>;
  onTransferOwnership: (userId: string) => Promise<void>;
  currentUserId?: string;
  currentUserRole: CompanyRole;
};

const MembersTable = ({
  members,
  onUpdateRole,
  onTransferOwnership,
  currentUserId,
  currentUserRole,
}: MembersTableProps) => {
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<Member | null>(null);
  const [selectedRole, setSelectedRole] = useState<CompanyRole | null>(null);

  const showRoleModal = (member: Member) => {
    console.log('selected member:', member);
    setSelectedUser(member);
    setSelectedRole(member.role);
    setIsRoleModalOpen(true);
  };

  const handleUpdateRoleOk = async () => {
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

  const handleUpdateRoleCancel = () => {
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

  const canViewActions = hasMemberPermission(
    currentUserRole,
    MemberPermissions.VIEW_ACTIONS,
  );

  const canTransferOwnership = hasMemberPermission(
    currentUserRole,
    MemberPermissions.TRANSFER_OWNERSHIP,
  );

  const canUpdateRole = hasMemberPermission(
    currentUserRole,
    MemberPermissions.UPDATE_ROLE,
  );

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

      render: (_, record) => {
        if (!canViewActions) return null;
        return (
          <Space size="middle">
            {canUpdateRole && (
              <button onClick={() => showRoleModal(record)}>UpdateRole</button>
            )}
            {canTransferOwnership && record.user_id !== currentUserId && (
              <Popconfirm
                title="Transfer ownership"
                description="This will transfer company ownership to this member."
                okText="Transfer"
                cancelText="Cancel"
                okButtonProps={{ danger: true }}
                onConfirm={() => onTransferOwnership(record.user_id)}
              >
                <button>Transfer</button>
              </Popconfirm>
            )}
          </Space>
        );
      },
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
        onOk={handleUpdateRoleOk}
        onCancel={handleUpdateRoleCancel}
      >
        <Radio.Group
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value as CompanyRole)}
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
