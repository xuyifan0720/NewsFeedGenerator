from dataclasses import dataclass, field
from typing import List, Mapping, Optional
import json
from news_feed_generator.utils.constants import DEFAULT_MAX_OUTPUT_TOKEN
import logging 

logger = logging.getLogger(__name__)

@dataclass 
class Image:
    data: str
    media_type: str


@dataclass 
class Message:
    text_input: str = ""
    image_datas: List[Image] = field(default_factory=list)
    role: str = "user"

    def to_invoke_model_request_body(self) -> Mapping[str, str | List[str]]:
        result = {
            "role": self.role
        }
        contents: List[str] = []
        if self.text_input:
            contents.append({
                "type": "text", 
                "text": self.text_input,
            })
        if self.image_datas:
            for image in self.image_datas:
                contents.append({
                    "type": "image",
                    "media_type": image.media_type, 
                    "data": image.data
                })
        if contents:
            result["content"] = contents
        return result

@dataclass
class PromptDTO:
    max_token: int = DEFAULT_MAX_OUTPUT_TOKEN
    messages: List[Message] = field(default_factory=list)

    def to_invoke_model_request_body(self) -> Optional[str]:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_token,
            "messages": [],
        }
        has_valid_message = False 
        for message in self.messages:
            message_dict = message.to_invoke_model_request_body()
            if "content" in message_dict:
                body["messages"].append(message_dict)
                has_valid_message = True 
        if has_valid_message:
            return json.dumps(body)
        else:
            return None
