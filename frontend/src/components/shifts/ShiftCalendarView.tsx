import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import { type Shift } from '../../services/shift.api';
import { useMemo } from 'react';
import type { EventInput } from '@fullcalendar/core';

type Props = {
  shifts: Shift[];
  onRangeChange: (from: string, to: string) => void;
};

const ShiftCalendarView = ({ shifts, onRangeChange }: Props) => {
  const events: EventInput[] = useMemo(() => {
    return shifts.map((shift) => ({
      id: shift.id,
      title: `${shift.assignment_count}/${shift.capacity}`,
      start: shift.start_at,
      end: shift.end_at,
    }));
  }, [shifts]);

  const calendarRange = useMemo(() => {
    if (shifts.length === 0) {
      return {
        slotMinTime: '08:00:00',
        slotMaxTime: '18:00:00',
      };
    }
    const hasOvernightShift = shifts.some((shift) => {
      const start = new Date(shift.start_at);
      const end = new Date(shift.end_at);
      return start.toDateString() !== end.toDateString();
    });

    if (hasOvernightShift) {
      return {
        slotMinTime: '00:00:00',
        slotMaxTime: '24:00:00',
      };
    }

    const earliest = Math.min(
      ...shifts.map((shift) => new Date(shift.start_at).getTime()),
    );

    const latest = Math.max(
      ...shifts.map((shift) => new Date(shift.end_at).getTime()),
    );

    const earliestDate = new Date(earliest);
    const latestDate = new Date(latest);

    earliestDate.setHours(Math.max(0, earliestDate.getHours() - 1));
    latestDate.setHours(Math.min(23, latestDate.getHours() + 1));

    return {
      slotMinTime: `${earliestDate
        .getHours()
        .toString()
        .padStart(2, '0')}:00:00`,

      slotMaxTime: `${latestDate.getHours().toString().padStart(2, '0')}:00:00`,
    };
  }, [shifts]);

  return (
    <FullCalendar
      plugins={[timeGridPlugin]}
      initialView="timeGridWeek"
      weekends={true}
      events={events}
      slotMinTime={calendarRange.slotMinTime}
      slotMaxTime={calendarRange.slotMaxTime}
      datesSet={(arg) => {
        onRangeChange(arg.start.toISOString(), arg.end.toISOString());
      }}
    />
  );
};

export default ShiftCalendarView;
