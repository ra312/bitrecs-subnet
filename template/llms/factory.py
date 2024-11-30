

import os
import sys
import time
import typing
import bittensor as bt
import random
from datetime import datetime, timezone
from enum import Enum

class LLM(Enum):
    OLLAMA_LOCAL = 1
    OPEN_ROUTER = 2
    CHAT_GPT = 3
    VLLM = 4


class LLMFactory:

    def query_llm(self, server=LLM.OLLAMA_LOCAL, model="", system_prompt="You are a helpful assistant", temp=0.1) -> str:
        match server:
            case LLM.OLLAMA_LOCAL:
                return OllamaLocalLLM(model, system_prompt, temp)
            case LLM.OPEN_ROUTER:
                return OpenRouterLLM(model, system_prompt, temp)
            case LLM.CHAT_GPT:
                return ChatGPTLLM(model, system_prompt, temp)
            case LLM.VLLM:
                return VLLMLLM(model, system_prompt, temp)
            case _:
                raise ValueError("Unknown LLM server")
        