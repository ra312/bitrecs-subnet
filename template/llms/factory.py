

import os
import sys
import time
import typing
import bittensor as bt
import random
from datetime import datetime, timezone
from enum import Enum

from template.llms.llama_local import OllamaLocal
from template.llms.open_router import OpenRouter

class LLM(Enum):
    OLLAMA_LOCAL = 1
    OPEN_ROUTER = 2
    CHAT_GPT = 3
    VLLM = 4


class LLMFactory:

    def query_llm(self, server: LLM, model: str, system_prompt="You are a helpful assistant", temp=0.1, user_prompt="") -> str:
        match server:
            case LLM.OLLAMA_LOCAL:
                return OllamaLocal(model, system_prompt, temp).query(user_prompt)
            case LLM.OPEN_ROUTER:
                return OpenRouter(model, system_prompt, temp).query(user_prompt)
            case LLM.CHAT_GPT:
                return ChatGPT(model, system_prompt, temp).query(user_prompt)
            case LLM.VLLM:
                return vLLM(model, system_prompt, temp).query(user_prompt)
            case _:
                raise ValueError("Unknown LLM server")
        
        
class OllamaLocal():
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
    
    def query(self, user_prompt):
        return "OllamaLocalLLM"
    
class OpenRouter():
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
    
    def query(self, user_prompt):
        return "OllamaLocalLLM"
    
class ChatGPT():
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
    
    def query(self, user_prompt):
        return "OllamaLocalLLM"
    
class vLLM():
    def __init__(self, model, system_prompt, temp):
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
    
    def query(self, user_prompt):
        return "OllamaLocalLLM"