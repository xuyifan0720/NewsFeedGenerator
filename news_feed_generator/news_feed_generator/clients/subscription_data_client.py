import boto3
from news_feed_generator.utils.constants import SUBSCRIPTION_TABLE
from news_feed_generator.dto.subscription_dto import SubscriptionDTO
from typing import List, Optional, Mapping

import logging

logger = logging.getLogger(__name__)

def convert_post(post: SubscriptionDTO) -> Optional[Mapping[str, str | int]]:
    try:
        result = post.to_ddb_item()
        return result 
    except Exception as e:
        logger.error("encountered error {} when converting {} to ddb item".format(e, post))
        return None

class SubscriptionDDBClient:
    def __init__(self, ddb_resource: boto3.resources.factory.ServiceResource):
        self.ddb = ddb_resource
        self.table = self.ddb.Table(SUBSCRIPTION_TABLE)

    def add_subscription(self, subscriptions: List[SubscriptionDTO]):
        items = list(map(convert_post, subscriptions))
        try:
            with self.table.batch_writer() as batch_writer:
                for item in items:
                    if item:
                        batch_writer.put_item(
                            Item=item
                        )
            logger.info("Batch write successful. All items have been added to DynamoDB.")
        except Exception as e:
            logger.error(f"Failed to batch write items: {e}")

    def scan_table(self) -> List[SubscriptionDTO]:
        items = []
        response = self.table.scan()
        items.extend(response.get('Items', []))

        # Keep scanning if there are more items (pagination)
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        return list(map(lambda item: SubscriptionDTO.from_ddb_item(item), items))
