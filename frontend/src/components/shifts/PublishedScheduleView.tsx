import { message, Spin } from 'antd';
import { useEffect, useState } from 'react';
import {
  getShiftDetail,
  getShifts,
  type Shift,
  type ShiftDetail,
} from '../../services/shift.api';
import ShiftCalendarView from './ShiftCalendarView';
import ShiftDetailModal from './ShiftDetailModal';
import styles from './PublishedScheduleView.module.css';

type DateRange = {
  from: string;
  to: string;
};

type Props = {
  companyId: string;
  showStatus: boolean;
};

const PublishedScheduleView = ({ companyId, showStatus }: Props) => {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [range, setRange] = useState<DateRange | null>(null);
  const [selectedShift, setSelectedShift] = useState<ShiftDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!range) return;

    let cancelled = false;

    const fetchPublishedShifts = async () => {
      setIsLoading(true);

      try {
        const data = await getShifts(companyId, {
          status: 'published',
          from: range.from,
          to: range.to,
        });

        if (!cancelled) setShifts(data);
      } catch (error) {
        if (!cancelled) {
          setShifts([]);
          console.error('Failed to get published shifts:', error);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    void fetchPublishedShifts();

    return () => {
      cancelled = true;
    };
  }, [companyId, range]);

  const handleShiftClick = async (shiftId: string) => {
    try {
      const detail = await getShiftDetail(companyId, shiftId);
      setSelectedShift(detail);
    } catch (error) {
      message.error('無法取得班次資料');
      console.error('Failed to get shift detail:', error);
    }
  };

  return (
    <section className={styles.scheduleSection}>
      <Spin spinning={isLoading}>
        <ShiftCalendarView
          shifts={shifts}
          onRangeChange={(from, to) => setRange({ from, to })}
          onShiftClick={handleShiftClick}
        />
      </Spin>

      <ShiftDetailModal
        shift={selectedShift}
        showStatus={showStatus}
        onClose={() => setSelectedShift(null)}
      />
    </section>
  );
};

export default PublishedScheduleView;
