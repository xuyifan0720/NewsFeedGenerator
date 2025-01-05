from abc import ABC, abstractmethod
from typing import List 
import praw
import boto3
from news_feed_generator.utils.constants import POST_TABLE
from typing import Mapping
from decimal import Decimal

class PostDataClient(ABC):
    @abstractmethod
    def write_post(self, posts: List[praw.models.Submission]):
        pass 

class PostDataDDBClient(PostDataClient):
    def __init__(self, ddb_resource: boto3.resources.factory.ServiceResource):
        self.ddb = ddb_resource
        self.table = self.ddb.Table(POST_TABLE)

    @staticmethod
    def to_ddb_item(post: praw.models.Submission) -> Mapping[str, str | float]:
        result = {
            "post_id": post.id, 
            "created_at": Decimal(str(post.created_utc)),
            "title": post.title, 
            "upvotes": post.score, 
            "url": post.url
        }
        return result 
    
    def write_post(self, posts: List[praw.models.Submission]):
        items = list(map(PostDataDDBClient.to_ddb_item, posts))
        try:
            with self.table.batch_writer() as batch_writer:
                for item in items:
                    batch_writer.put_item(
                        Item=item
                    )
            print("Batch write successful. All items have been added to DynamoDB.")
        except Exception as e:
            print(f"Failed to batch write items: {e}")
