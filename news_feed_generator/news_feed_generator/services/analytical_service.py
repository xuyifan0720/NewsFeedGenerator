import numpy as np 
from news_feed_generator.dto.post_dto import PostDTO
from typing import List

class AnalyticalService: 
    def __init__(self):
        self.cutoffs = {}

    # all post in posts should be in the sub_reddit
    def analyse_posts(self, sub_reddit: str, cutoff_percentile: int, posts: List[PostDTO]):
        if (sub_reddit, cutoff_percentile) in self.cutoffs:
            return 
        else:
            average_scores = list(map(lambda post: post.average_score, posts))
            cutoff_score = np.percentile(average_scores, cutoff_percentile)
            self.cutoffs[(sub_reddit, cutoff_percentile)] = cutoff_score

    def post_popular(self, post: PostDTO, cutoff_percentile: int) -> bool:
        cutoff_score = self.cutoffs.get((post.sub_reddit, cutoff_percentile), 0)
        return post.average_score >= cutoff_score
    