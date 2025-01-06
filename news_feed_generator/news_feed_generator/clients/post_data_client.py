from abc import ABC, abstractmethod
from typing import List 
from news_feed_generator.dto.post_dto import PostDTO
import boto3
from news_feed_generator.utils.constants import POST_TABLE, FAR_PAST_TIME, FAR_FUTURE_TIME
from typing import Mapping, Optional
from decimal import Decimal
from boto3.dynamodb.conditions import Key

class PostDataClient(ABC):
    @abstractmethod
    def write_post(self, posts: List[PostDTO]):
        pass 

    @abstractmethod
    def get_posts(self, post_id: str, start: Optional[float] = None, end: Optional[float] = None) -> List[PostDTO]:
        pass


class PostDataDDBClient(PostDataClient):
    def __init__(self, ddb_resource: boto3.resources.factory.ServiceResource):
        self.ddb = ddb_resource
        self.table = self.ddb.Table(POST_TABLE)
    
    def write_post(self, posts: List[PostDTO]):
        items = list(map(lambda post: post.to_ddb_item(), posts))
        try:
            with self.table.batch_writer() as batch_writer:
                for item in items:
                    batch_writer.put_item(
                        Item=item
                    )
            print("Batch write successful. All items have been added to DynamoDB.")
        except Exception as e:
            print(f"Failed to batch write items: {e}")

    def get_posts(self, sub_reddit: str, start: Optional[float] = None, end: Optional[float] = None) -> List[PostDTO]:
        if not start:
            start = FAR_PAST_TIME 
        if not end:
            end = FAR_FUTURE_TIME
        try:
            response = self.table.query(
                KeyConditionExpression=Key('sub_reddit').eq(sub_reddit) & 
                                    Key('created_at').between(Decimal(str(start)), Decimal(str(end)))
            )
        except Exception as e:
            print(e)
            return []
        ddb_items = response.get('Items', [])
        dto_items = list(map(PostDTO.from_ddb_item, ddb_items))
        print(dto_items)
        return dto_items
