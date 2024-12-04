import os
import sys
import time
import typing
import bittensor as bt
from datetime import datetime, timezone
from enum import Enum

from template.llms.llama_local import OllamaLocal
from template.llms.open_router import OpenRouter
from template.llms.chat_gpt import ChatGPT
from template.llms.vllm_router import vLLM


class LLM(Enum):
    OLLAMA_LOCAL = 1
    OPEN_ROUTER = 2
    CHAT_GPT = 3
    VLLM = 4


class LLMFactory:

    @staticmethod
    def query_llm(server: LLM, model: str, 
                  system_prompt="You are a helpful assistant", 
                  temp=0.1, user_prompt="") -> str:
        match server:
            case LLM.OLLAMA_LOCAL:
                return OllamaLocalInterface(model, system_prompt, temp).query(user_prompt)
            case LLM.OPEN_ROUTER:
                return OpenRouterInterface(model, system_prompt, temp).query(user_prompt)
            case LLM.CHAT_GPT:
                return ChatGPTInterface(model, system_prompt, temp).query(user_prompt)
            case LLM.VLLM:
                return VllmInterface(model, system_prompt, temp).query(user_prompt)
            case _:
                raise ValueError("Unknown LLM server")
            
    @staticmethod
    def try_get_enum(value: str) -> LLM:        
        match value.upper():
            case "OLLAMA_LOCAL":
                return LLM.OLLAMA_LOCAL
            case "OPEN_ROUTER":
                return LLM.OPEN_ROUTER
            case "CHAT_GPT":
                return LLM.CHAT_GPT
            case "VLLM":
                return LLM.VLLM
            case _:
                raise ValueError("Unknown LLM server")
        
        
class OllamaLocalInterface:
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp        
        self.OLLAMA_LOCAL_URL = os.environ.get("OLLAMA_LOCAL_URL")
        if not self.OLLAMA_LOCAL_URL:
             bt.logging.error("OLLAMA_LOCAL_URL not set.")        
    
    def query(self, user_prompt) -> str:
        llm = OllamaLocal(ollama_url=self.OLLAMA_LOCAL_URL, model=self.model, 
                          system_prompt=self.system_prompt, temp=self.temp)
        return llm.ask_ollama(user_prompt)
    
    
class OpenRouterInterface:
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
        self.OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set")
    
    def query(self, user_prompt) -> str:
        router = OpenRouter(self.OPENROUTER_API_KEY, model=self.model, 
                            system_prompt=self.system_prompt, temp=self.temp)
        return router.call_open_router(user_prompt)
    
    
class ChatGPTInterface:
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
        self.CHATGPT_API_KEY = os.environ.get("CHATGPT_API_KEY")
        if not self.CHATGPT_API_KEY:            
            raise ValueError("CHATGPT_API_KEY is not set")
        
    def query(self, user_prompt) -> str:
        router = ChatGPT(self.CHATGPT_API_KEY, model=self.model, 
                         system_prompt=self.system_prompt, temp=self.temp)
        return router.call_chat_gpt(user_prompt)
    
    
class VllmInterface:
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
        self.VLLM_API_KEY = os.environ.get("VLLM_API_KEY", "")
        if not self.VLLM_API_KEY:            
            raise ValueError("VLLM_API_KEY is not set")
    
    def query(self, user_prompt) -> str:
        router = vLLM(key=self.VLLM_API_KEY, model=self.model, 
                      system_prompt=self.system_prompt, temp=self.temp)
        return router.call_vllm(user_prompt)