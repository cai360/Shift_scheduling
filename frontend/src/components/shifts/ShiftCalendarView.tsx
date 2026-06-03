import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import { type Shift } from '../../services/shift.api';
import { useMemo } from 'react';
import type { EventInput } from '@fullcalendar/core';

type Props = {
  shifts: Shift[];
};

const ShiftCalendarView = ({ shifts }: Props) => {
  const events: EventInput[] = useMemo(() => {
    return shifts.map((shift) => ({
      id: shift.id,
      title: `${shift.assignment_count}/${shift.capacity}`,
      start: shift.start_at,
      end: shift.end_at,
    }));
  }, [shifts]);

  return (
    <FullCalendar
      plugins={[timeGridPlugin]}
      initialView="timeGridWeek"
      weekends={true}
      events={events}
    />
  );
};

export default ShiftCalendarView;
