import bittensor as bt
import requests
from openai import OpenAI

class vLLM:
    def __init__(self, 
                 key, 
                 model="NousResearch/Meta-Llama-3-8B-Instruct", 
                 system_prompt="You are a helpful AI assistant.", 
                 temp=0.0):
        self.key = "token-abc123"
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp


    def call_vllm(self, user_prompt):
        
        client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="token-abc123",
        )

        completion = client.chat.completions.create(
            model="NousResearch/Meta-Llama-3-8B-Instruct",
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        print(completion.choices[0].message)

        return completion.choices[0].message

    
    def call_vllm2(self, user_prompt):        
        openai_api_key = self.key
        openai_api_base = "http://localhost:8000/v1"
        client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_api_base,
        )
        try:

            completion = client.completions.create(model=self.model, prompt=user_prompt, max_tokens=500)
            result = completion.choices[0].text
            return result

        except Exception as e:
            bt.logging.error("Error calling vLLM: {}".format(e))
            raise e

        
