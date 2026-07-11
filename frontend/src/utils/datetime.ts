export const BUSINESS_TZ = 'Asia/Taipei';

const businessPartsFormatter = new Intl.DateTimeFormat('en-CA', {
  timeZone: BUSINESS_TZ,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
});

export const toBusinessParts = (isoString: string) => {
  const parts = Object.fromEntries(
    businessPartsFormatter
      .formatToParts(new Date(isoString))
      .map((p) => [p.type, p.value]),
  );
  return {
    dateKey: `${parts.year}-${parts.month}-${parts.day}`,
    minutesOfDay: Number(parts.hour) * 60 + Number(parts.minute),
  };
};

// Formats a calendar-grid boundary Date as a BUSINESS_TZ date-only string, not the browser's local date.
export const toBusinessDateOnly = (date: Date) => {
  const parts = Object.fromEntries(
    businessPartsFormatter.formatToParts(date).map((p) => [p.type, p.value]),
  );
  return `${parts.year}-${parts.month}-${parts.day}`;
};

// For format FullCalendar slot time, accept 24:00:00
export const formatFullCalendarSlotTime = (minutes: number) => {
  const clamped = Math.min(24 * 60, Math.max(0, minutes));
  const hours = Math.floor(clamped / 60)
    .toString()
    .padStart(2, '0');
  const mins = (clamped % 60).toString().padStart(2, '0');
  return `${hours}:${mins}:00`;
};
