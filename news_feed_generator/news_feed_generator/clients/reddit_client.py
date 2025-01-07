import praw
from typing import List
from news_feed_generator.utils.time_conversion import to_local_time

class RedditClient:
    def __init__(self, reddit: praw.reddit.Reddit):
        self.reddit = reddit

    def get_top_posts(self, sub_reddit: str) -> List[praw.models.Submission]: 
        result = []
        # Access subreddit
        subreddit = self.reddit.subreddit(sub_reddit)

        # Fetch top posts
        top_posts = subreddit.top(time_filter='day', limit=5)

        for post in top_posts:
            result.append(post)
        
        return result
