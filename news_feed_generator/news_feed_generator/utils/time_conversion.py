from datetime import datetime, timezone
import praw
import time

def to_local_time(utc_timestamp: float) -> str: 
    utc_time = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')

def get_average_score(post: praw.models.Submission) -> float:
    curr_time = time.time()
    time_diff = curr_time - post.created_utc
    average_score = float(post.score)/time_diff
    return average_score


