import praw 
from news_feed_generator.clients.reddit_client import RedditClient 
import os

def base_reddit_test():
    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        user_agent="python:news_feed_generator:v1.0 (by u/yeetlan)"
    )
    reddit_client = RedditClient(reddit)
    top_posts = reddit_client.get_top_posts("singularity")
    print("total number of posts is {}".format(len(top_posts)))

