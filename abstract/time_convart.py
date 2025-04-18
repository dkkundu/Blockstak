from datetime import datetime
from zoneinfo import ZoneInfo


def convert_utc_to_local(utc_string: str, local_timezone: str = "Asia/Dhaka") -> datetime:
    try:
        # Convert string to aware UTC datetime
        utc_time = datetime.fromisoformat(utc_string.replace("Z", "+00:00")).astimezone(ZoneInfo("UTC"))
        # Convert to local timezone
        local_time = utc_time.astimezone(ZoneInfo(local_timezone))
        # Return naive datetime for DB
        return local_time.replace(tzinfo=None)
    except Exception as e:
        raise ValueError(f"Failed to convert timezone: {e}")
