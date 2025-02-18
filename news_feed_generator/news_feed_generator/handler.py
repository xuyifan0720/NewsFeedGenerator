import praw 
from news_feed_generator.clients.reddit_client import RedditClient 
from news_feed_generator.clients.post_data_client import PostDataDDBClient
from news_feed_generator.utils.constants import DEFAULT_AWS_REGION
from news_feed_generator.dto.post_dto import PostDTO
import os
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from news_feed_generator.utils.time_conversion import to_local_time
from news_feed_generator.services.analytical_service import AnalyticalService
from news_feed_generator.services.llm_service import LLMService
from news_feed_generator.clients.subscription_data_client import SubscriptionDDBClient
from news_feed_generator.dto.subscription_dto import SubscriptionDTO
from typing import List, Mapping, Set, Tuple
import logging 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', DEFAULT_AWS_REGION)
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="python:news_feed_generator:v1.0 (by u/yeetlan)"
)
reddit_client = RedditClient(reddit)

try:
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
except Exception as e:
    logger.error(f"Error initializing DynamoDB: {e}")
    exit(1)

post_data_client = PostDataDDBClient(dynamodb)
subscription_data_client = SubscriptionDDBClient(dynamodb)
analytical_service = AnalyticalService()
bedrock_client = boto3.client("bedrock-runtime")
llm_service = LLMService(bedrock_client)

def base_reddit_test():
    all_subscriptions: List[SubscriptionDTO] = subscription_data_client.scan_table()
    post_summarize: Mapping[str, str] = {}
    top_posts_map: Mapping[str, List[praw.models.Submission]] = {}
    existing_posts_map: Mapping[str, List[PostDTO]] = {}
    for subsciption in all_subscriptions:
        for sub_mapping in subsciption.subs_and_cutoffs:
            for sub_reddit, cutoff_percentile in sub_mapping.items():
                # Currently storing daily top posts in memory and not in external database
                if sub_reddit in top_posts_map:
                    top_posts = top_posts_map[sub_reddit]
                else:
                    top_posts = reddit_client.get_top_posts(sub_reddit)
                    top_posts_map[sub_reddit] = top_posts
                    post_data_client.write_post(list(map(lambda post: PostDTO.from_reddit_submission(post, sub_reddit), top_posts)))
                if sub_reddit in existing_posts_map:
                    existing_posts = existing_posts_map[sub_reddit]
                else:
                    existing_posts = post_data_client.get_posts(sub_reddit)
                analytical_service.analyse_posts(sub_reddit, cutoff_percentile, existing_posts)
                for post in top_posts:
                    logger.info(f"Title: {post.title}")
                    if analytical_service.post_popular(sub_reddit, post, cutoff_percentile):
                        if post.id in post_summarize:
                            post_content = post_summarize[post.id]
                        else:
                            post_content = llm_service.summarize_post(post)
                            post_summarize[post.id] = post_content
                        logger.info(post_content)

def handler(event, context):
    response = {
        "message": "success"
    }
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def simple_test():
    top_posts = reddit_client.get_top_posts("singularity")
    post_data_client.write_post(list(map(lambda post: PostDTO.from_reddit_submission(post, "singularity"), top_posts)))
    existing_posts = post_data_client.get_posts("singularity")
    analytical_service.analyse_posts("singularity", 1, existing_posts)
    for post in top_posts:
        logger.info(f"Title: {post.title}")
        if analytical_service.post_popular('singularity', post, 1):
            logger.info(llm_service.summarize_post(post))


def base_ddb_test():
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )
    except NoCredentialsError:
        print("AWS credentials are missing or incorrect.")
        exit(1)
    except PartialCredentialsError:
        print("Incomplete AWS credentials found.")
        exit(1)
    except Exception as e:
        print(f"Error initializing DynamoDB: {e}")
        exit(1)
    post_data_client = PostDataDDBClient(dynamodb)
    posts = post_data_client.get_posts("singularity")
    for post in posts:
        print(post)

def add_subscription():
    subscriptions = [
        SubscriptionDTO(email= "xuyifan0720@gmail.com", subs_and_cutoffs = [
            {"singularity": 50}, 
            {"pics": 50}, 
            {"dataisbeautiful": 50}, 
        ])
    ]
    subscription_data_client.add_subscription(subscriptions)
