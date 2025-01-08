import numpy as np 
from news_feed_generator.dto.post_dto import PostDTO
from typing import List
import praw 
from news_feed_generator.utils.time_conversion import get_average_score
import logging 

logger = logging.getLogger(__name__)

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

    def post_popular(self, sub_reddit: str, post: praw.models.Submission, cutoff_percentile: int) -> bool:
        cutoff_score = self.cutoffs.get((sub_reddit, cutoff_percentile), 0)
        average_score = get_average_score(post)
        logger.info("average score is {}, cutoff_score is {}".format(average_score, cutoff_score))
        return average_score >= cutoff_score
    