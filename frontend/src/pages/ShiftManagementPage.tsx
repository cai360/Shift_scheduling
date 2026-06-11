import ShiftCalendarView from '../components/shifts/ShiftCalendarView';
import { useCompanyContext } from '../contexts/useCompanyContext';
import { useEffect, useMemo, useState } from 'react';
import { getShifts, type Shift } from '../services/shift.api';

const getCurrentMonthRange = () => {
  const now = new Date();

  const from = new Date(now.getFullYear(), now.getMonth(), 1);
  const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);

  return {
    from: from.toISOString().slice(0, 10),
    to: to.toISOString().slice(0, 10),
  };
};

const ShiftManagementPage = () => {
  const { currentCompanyId } = useCompanyContext();
  const [shifts, setShifts] = useState<Shift[]>([]);

  const monthRange = useMemo(() => getCurrentMonthRange(), []);

  useEffect(() => {
    if (!currentCompanyId) return;

    getShifts(currentCompanyId, {
      from: monthRange.from,
      to: monthRange.to,
    }).then((data) => {
      console.log('shifts:', data);
      setShifts(data);
    });
  }, [currentCompanyId, monthRange]);

  return <ShiftCalendarView shifts={shifts} />;
};

export default ShiftManagementPage;
