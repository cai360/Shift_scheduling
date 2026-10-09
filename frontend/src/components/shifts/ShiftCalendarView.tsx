import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import { type Shift } from '../../services/shift.api';
import { useMemo } from 'react';
import type { EventInput } from '@fullcalendar/core';
import {
  toBusinessParts,
  toBusinessDateOnly,
  formatFullCalendarSlotTime,
} from '../../utils/datetime';

type Props = {
  shifts: Shift[];
  onRangeChange: (from: string, to: string) => void;
  onShiftClick: (shiftId: string) => void;
};

const ShiftCalendarView = ({ shifts, onRangeChange, onShiftClick }: Props) => {
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
      const start = toBusinessParts(shift.start_at);
      const end = toBusinessParts(shift.end_at);
      return start.dateKey !== end.dateKey;
    });

    if (hasOvernightShift) {
      return {
        slotMinTime: '00:00:00',
        slotMaxTime: '24:00:00',
      };
    }

    const earliest = Math.min(
      ...shifts.map((shift) => toBusinessParts(shift.start_at).minutesOfDay),
    );

    const latest = Math.max(
      ...shifts.map((shift) => toBusinessParts(shift.end_at).minutesOfDay),
    );

    const slotMinTime = formatFullCalendarSlotTime(earliest - 60);
    const slotMaxTime = formatFullCalendarSlotTime(latest + 60);

    console.log('calendarRange', { slotMinTime, slotMaxTime });

    return { slotMinTime, slotMaxTime };
  }, [shifts]);

  return (
    <FullCalendar
      plugins={[timeGridPlugin]}
      initialView="timeGridWeek"
      height="auto"
      weekends={true}
      events={events}
      slotLabelFormat={{
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }}
      eventTimeFormat={{
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }}
      slotMinTime={calendarRange.slotMinTime}
      slotMaxTime={calendarRange.slotMaxTime}
      datesSet={(arg) => {
        onRangeChange(
          toBusinessDateOnly(arg.start),
          toBusinessDateOnly(arg.end),
        );
      }}
      eventClick={(info) => {
        onShiftClick(info.event.id);
      }}
    />
  );
};

export default ShiftCalendarView;
