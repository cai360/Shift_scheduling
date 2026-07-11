import ShiftCalendarView from '../components/shifts/ShiftCalendarView';
import { useCompanyContext } from '../contexts/useCompanyContext';
import { useEffect, useState } from 'react';
import { getShifts, type Shift } from '../services/shift.api';

type DateRange = {
  from: string;
  to: string;
};

// const getCurrentMonthRange = () => {
//   const now = new Date();

//   const from = new Date(now.getFullYear(), now.getMonth(), 1);
//   const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);

//   return {
//     from: from.toISOString().slice(0, 10),
//     to: to.toISOString().slice(0, 10),
//   };
// };

const ShiftManagementPage = () => {
  const { currentCompanyId } = useCompanyContext();
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [range, setRange] = useState<DateRange | null>(null);

  useEffect(() => {
    if (!currentCompanyId || !range) return;

    getShifts(currentCompanyId, {
      from: range.from,
      to: range.to,
    }).then((data) => {
      console.log('shifts:', data);
      setShifts(data);
    });
  }, [currentCompanyId, range]);

  return (
    <ShiftCalendarView
      shifts={shifts}
      onRangeChange={(from, to) => {
        setRange({ from, to });
      }}
    />
  );
};

export default ShiftManagementPage;
