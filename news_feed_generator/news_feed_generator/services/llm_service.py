import boto3 
import praw
from botocore.client import BaseClient
from typing import Mapping, List, Optional
from news_feed_generator.utils.constants import POST_TEXT_LIMIT, SONNET
import logging
import requests
from news_feed_generator.dto.prompt_dto import Image, Message, PromptDTO
import base64
import json

logger = logging.getLogger(__name__)

def get_image_from_url(image_url: str) -> Optional[Image]: 
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Ensure the request was successful
        encoded_image = base64.b64encode(response).decode("utf-8")
        if image_url.endswith(".jpeg"):
            return Image(data=encoded_image, media_type="image/jpeg")
        elif image_url.endswith(".jpg"):
            return Image(data=encoded_image, media_type="image/jpg")
        elif image_url.endswith(".png"):
            return Image(data=encoded_image, media_type="image/png")
        else:
            logger.error("image type unsuppported for {}".format(image_url))
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch image {}".format(e))
        return None

class LLMService:
    def __init__(self, bedrock: BaseClient):
        self.bedrock = bedrock 

    def summarize_post(self, post: praw.models.Submission) -> str: 
        post_hint = getattr(post, 'post_hint', None)
        logger.info("post hint is {}".format(post_hint))
        if not post_hint:
            # text post 
            if post.is_self:
                logger.info("analyzing a text post")
                post_body = self.build_llm_prompt_for_text_post(post) 
                return self.query_llm(post_body)
            elif hasattr(post, 'media') and post.media:
                return "post {} can't be summarized but it contains media {}".format(post.title, post.media)
            elif post.url:
                return "post {} can't be summarized but it contains url {}".format(post.title, post.url)
            else:
                return "Post {} can't be summarized, better look it up yourself".format(post.title)
        elif post_hint == "image": 
            logger.info("analyzing an image post {} with url {}".format(post.title, post.url))
            post_body = self.build_llm_prompt_for_post_with_images(post, [post.url])
            if post_body:
                return self.query_llm(post_body)
            else:
                return "Post {} contains images but cannot be parsed".format(post.title)
        else:
            return "AI summarizing for this post type isn't supported yet"


    def query_llm(self, prompt: PromptDTO, model_id: str = SONNET) -> str:
        try: 
            body = prompt.to_invoke_model_request_body()
            if body:
                response = self.bedrock.invoke_model(
                    modelId=model_id,
                    body=body, 
                    contentType='application/json',  
                )
                response_body = response['body'].read().decode('utf-8')
                parsed_response = json.loads(response_body)
                return parsed_response
            else:
                return "unable to build the prompt correctly"
        except Exception as e:
            error_msg = "got error while querying the LLM {}".format(e)
            logger.error(error_msg)
            return error_msg

    def build_llm_prompt_for_text_post(self, post: praw.models.Submission) -> PromptDTO:
        text_prompt = self.build_text_prompt(post)
        message = Message(text_input=text_prompt, role="user")
        prompt_dto = PromptDTO(messages=[message])
        return prompt_dto
    
    def build_text_prompt(self, post: praw.models.Submission) -> str:
        over_sized = len(post.selftext) > POST_TEXT_LIMIT
        post_text = post.selftext if not over_sized else self.post_text[:10000]
        if over_sized:
            prompt = "Summarize the reddit post with following title {} and the following text.".format(post.title)
            prompt += "Note that only the first {} characters of the post is included \n{}".format(POST_TEXT_LIMIT, post_text)
        else:
            prompt = "Summarize the reddit post with following title {} and the following text. \n {}".format(post.title, post_text)
        return prompt
    
    def build_llm_prompt_for_post_with_images(self, post: praw.models.Submission, image_urls: List[str]) -> PromptDTO:
        images = list(map(get_image_from_url, image_urls))
        valid_images = list(map(lambda image: image, images))
        prompt = ""
        if post.selftext:
            prompt = self.build_text_prompt(post)
        if valid_images:
            if prompt:
                prompt = prompt + " and the post has the following images attached"
            else:
                prompt = "Summarize the reddit post with following tile {} and the following images attached".format(post.title)
            message = Message(text_input=prompt, image_datas=valid_images, role="user")
            prompt_dto = PromptDTO(messages=[message])
            return prompt_dto
        else:
            return None



    

