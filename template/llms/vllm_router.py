import bittensor as bt
import requests
from openai import OpenAI

class vLLM:
    """
     python3 -m vllm.entrypoints.openai.api_server --model NousResearch/Meta-Llama-3-8B-Instruct --dtype auto --api-key xxxxxxx

    """
    def __init__(self, 
                 key, 
                 model="NousResearch/Meta-Llama-3-8B-Instruct", 
                 system_prompt="You are a helpful AI assistant.", 
                 temp=0.0):
        self.key = key,
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp
        #self.key = "token-abc123H"


    def call_vllm(self, user_prompt) -> str:
        client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key=self.key,
        )
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        #print(completion.choices[0].message.content)
        result = completion.choices[0].message.content
        return result

        
