import requests
import os
from dotenv import load_dotenv
from typing import Any, List, Mapping, Optional, Iterator

from langchain_core.callbacks.manager import(
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, AIMessageChunk
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from langchain_core.pydantic_v1 import Field,root_validator

load_dotenv()

def get_env_variable(key:str) -> str:
    value=os.getenv(key)
    if value is None:
        raise ValueError(f"env'{key}' not found")
    return value

class NebiusChatModel(BaseChatModel):
    """
    nebius wrapper
    """
    nebius_api_url:str=Field(default="https://api.studio.nebius.com/v1/chat/completions")
    nebius_api_key:str=Field(default_factory=lambda:get_env_variable("NEBIUS_API_KEY"))
    model_name:str="meta-llama/Llama-3.3-70B-Instruct"
    temperature:float =0.7

    @property
    def _llm_type(self)->str:
        return "nebius_chat_model"

    def _generate(
        self,
        messages:List[BaseMessage],
        stop:Optional[List[str]] = None,
        run_manager:Optional[CallbackManagerForLLMRun]=None,
        **kwargs:Any,
    ) -> ChatResult:
        headers={
            "Authorization":f"Bearer{self.nebius_api_key}",
            "Content-Type":"application/json",
        }

        message_dicts=[]
        for msg in messages:
            if isinstance(msg,HumanMessage):
                message_dicts.append({"role": "user", "content": msg.content})
            elif isinstance(msg,AIMessage):
                message_dicts.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg,SystemMessage):
                message_dicts.append({"role": "system", "content": msg.content})

        payload={
            "model":self.model_name,
            "messages":message_dicts,
            "temperature":self.temperature,
            **kwargs,
        }
        if stop:
            payload["stop"]=stop
        
        try:
            response=requests.post(self.nebius_api_url, json=payload, headers=headers)
            response.raise_for_status()
            response_json=response.json()

            if not response_json.get("choices") or not response_json["choices"][0].get("message"):
                raise ValueError(f"invalid repsonse{response.text}")

            assistant_message_content=response_json["choices"][0]["message"].get("content")
            if assistant_message_content is None:
                assistant_message_content=""

            generations=[
                ChatGeneration(message=AIMessage(content=assistant_message_content))
            ]
            return ChatResult(generations=generations, llm_output=response_json.get("usage"))

        except requests.exceptions.RequestException as e:
            raise ValueError(f"error calling nebius {e}")
        except (KeyError, IndexError, TypeError, ValueError) as e:
            raise ValueError(f"error getting response {e} - Response: {response.text if 'response' in locals() else 'No response object'}")

