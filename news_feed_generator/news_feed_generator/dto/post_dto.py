import praw 
from dataclasses import dataclass, fields
import time
from typing import Mapping
from decimal import Decimal
from news_feed_generator.utils.time_conversion import get_average_score

def transform_ddb_value(value):
    if isinstance(value, Decimal):
        return float(value)
    else:
        return value

@dataclass
class PostDTO:
    sub_reddit: str
    created_at: float 
    post_id: str 
    title: str 
    score: int 
    url: str 
    average_score: float
    expiration_time: float

    def to_ddb_item(self) -> Mapping[str, str | Decimal]: 
        result = {}
        for field in fields(self):
            field_name = field.name
            field_value = getattr(self, field_name)
            if field.type == float:
                result[field_name] = Decimal(str(field_value))
            else:
                result[field_name] = field_value 
        return result
    
    @classmethod 
    def from_reddit_submission(cls, post: praw.models.Submission, sub_reddit: str) -> 'PostDTO':
        average_score = get_average_score(post)
        # expire 6 days after it's created
        expiration_time = post.created_utc + 6 * 24 * 3600
        return PostDTO(sub_reddit, post.created_utc, post.id, post.title, post.score, post.url, average_score, expiration_time)
    
    @classmethod
    def from_ddb_item(cls, ddb_item: Mapping[str, str | Decimal]) -> 'PostDTO':
        transformed_items = {key: transform_ddb_value(value) for key, value in ddb_item.items()}
        return PostDTO(**transformed_items)
    