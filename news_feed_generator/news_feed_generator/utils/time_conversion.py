from datetime import datetime, timezone

def to_local_time(utc_timestamp: float) -> str: 
    utc_time = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
