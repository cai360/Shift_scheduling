import ShiftCalendarView from '../components/shifts/ShiftCalendarView';
import { useCompanyContext } from '../contexts/useCompanyContext';
import { useEffect, useState } from 'react';
import ShiftDetailModal from '../components/shifts/ShiftDetailModal';
import { CompanyRoles } from '../types/company';
import {
  getShifts,
  getShiftDetail,
  type Shift,
  type ShiftDetail,
} from '../services/shift.api';

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
  const { companies, currentCompanyId } = useCompanyContext();
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [range, setRange] = useState<DateRange | null>(null);
  const [selectedShift, setSelectedShift] = useState<ShiftDetail | null>(null);

  const currentCompany = companies.find(
    (company) => company.company_id === currentCompanyId,
  );
  const canManageShifts =
    currentCompany?.role === CompanyRoles.OWNER ||
    currentCompany?.role === CompanyRoles.MANAGER;

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

  const handleShiftClick = async (shiftId: string) => {
    if (!currentCompanyId) return;

    try {
      const detail = await getShiftDetail(currentCompanyId, shiftId);
      setSelectedShift(detail);
      console.log('shift detail: ', detail);
    } catch (error) {
      console.error('Failed to get shift detail:', error);
    }
  };

  return (
    <>
      <ShiftCalendarView
        shifts={shifts}
        onRangeChange={(from, to) => {
          setRange({ from, to });
        }}
        onShiftClick={handleShiftClick}
      />

      <ShiftDetailModal
        shift={selectedShift}
        showStatus={canManageShifts}
        onClose={() => {
          setSelectedShift(null);
        }}
      />
    </>
  );
};

export default ShiftManagementPage;
