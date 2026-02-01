from dateutil.parser import isoparse
from app.config import BUSINESS_TZ, UTC_TZ

def parse_datetime(value: str):
    dt = isoparse(value)

    # naive datetime → assume business timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=BUSINESS_TZ)

    return dt.astimezone(UTC_TZ)