import { Descriptions, Modal, Space, Tag, Typography } from 'antd';
import type { ShiftDetail } from '../../services/shift.api';
import { formatBusinessDate, formatBusinessTime } from '../../utils/datetime';

type Props = {
  shift: ShiftDetail | null;
  showStatus: boolean;
  onClose: () => void;
};

const ShiftDetailModal = ({ shift, showStatus, onClose }: Props) => {
  const title = (
    <Space size="small">
      <span>{shift ? formatBusinessDate(shift.start_at) : 'Shift detail'}</span>
      {shift && showStatus && (
        <Tag color={shift.status === 'published' ? 'green' : 'orange'}>
          {shift.status}
        </Tag>
      )}
    </Space>
  );

  return (
    <Modal title={title} open={shift !== null} onCancel={onClose} footer={null}>
      {shift && (
        <Descriptions bordered column={1} size="small">
          <Descriptions.Item label="Time">
            {formatBusinessTime(shift.start_at)}
            {' – '}
            {formatBusinessTime(shift.end_at)}
          </Descriptions.Item>

          <Descriptions.Item label="Staffing">
            <Space size="middle" wrap>
              <Typography.Text strong>
                {shift.assignment_count} / {shift.capacity} assigned
              </Typography.Text>
              {shift.remaining_capacity === 0 ? (
                <Tag color="green">Fully staffed</Tag>
              ) : (
                <Tag color="gold">
                  {shift.remaining_capacity}{' '}
                  {shift.remaining_capacity === 1 ? 'opening' : 'openings'}
                </Tag>
              )}
            </Space>
          </Descriptions.Item>

          <Descriptions.Item label="Employees">
            {shift.assignments.length > 0 ? (
              <Space size={[4, 8]} wrap>
                {shift.assignments.map((assignment) => (
                  <Tag key={assignment.id}>{assignment.name}</Tag>
                ))}
              </Space>
            ) : (
              <Typography.Text type="secondary">
                No employees assigned
              </Typography.Text>
            )}
          </Descriptions.Item>
        </Descriptions>
      )}
    </Modal>
  );
};

export default ShiftDetailModal;
