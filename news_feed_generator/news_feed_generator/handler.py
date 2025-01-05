import praw 
from news_feed_generator.clients.reddit_client import RedditClient 
from news_feed_generator.clients.post_data_client import PostDataDDBClient
from news_feed_generator.utils.constants import DEFAULT_AWS_REGION
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

load_dotenv()

def base_reddit_test():
    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        user_agent="python:news_feed_generator:v1.0 (by u/yeetlan)"
    )
    reddit_client = RedditClient(reddit)
    top_posts = reddit_client.get_top_posts("singularity")
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', DEFAULT_AWS_REGION)
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
    post_data_client.write_post(top_posts)

