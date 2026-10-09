export const BUSINESS_TZ = 'Asia/Taipei';

type BusinessDateFormatOptions = {
  locale?: string;
  timeZone?: string;
};

const dateFormatterCache = new Map<string, Intl.DateTimeFormat>();
const timeFormatterCache = new Map<string, Intl.DateTimeFormat>();

const getCachedFormatter = (
  cache: Map<string, Intl.DateTimeFormat>,
  locale: string,
  timeZone: string,
  options: Intl.DateTimeFormatOptions,
) => {
  const cacheKey = `${locale}:${timeZone}`;
  const cachedFormatter = cache.get(cacheKey);

  if (cachedFormatter) return cachedFormatter;

  const formatter = new Intl.DateTimeFormat(locale, {
    ...options,
    timeZone,
  });
  cache.set(cacheKey, formatter);
  return formatter;
};

export const formatBusinessDate = (
  value: string | Date,
  { locale = 'zh-TW', timeZone = BUSINESS_TZ }: BusinessDateFormatOptions = {},
) => {
  const formatter = getCachedFormatter(dateFormatterCache, locale, timeZone, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  });

  return formatter.format(new Date(value));
};

export const formatBusinessTime = (
  value: string | Date,
  { locale = 'zh-TW', timeZone = BUSINESS_TZ }: BusinessDateFormatOptions = {},
) => {
  const formatter = getCachedFormatter(timeFormatterCache, locale, timeZone, {
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  });

  return formatter.format(new Date(value));
};

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
