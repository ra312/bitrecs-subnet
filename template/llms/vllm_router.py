import bittensor as bt
import requests
from openai import OpenAI

class vLLM:
    def __init__(self, 
                 key, 
                 model="NousResearch/Meta-Llama-3-8B-Instruct", 
                 system_prompt="You are a helpful AI assistant.", 
                 temp=0.0):
        self.key = "abc123H"
        self.model = model
        self.system_prompt = system_prompt
        self.temp = temp


    def call_vllm(self, user_prompt):
        headers = {
            "Authorization": "Bearer {}".format(self.key)
        }
        data = {
            "prompt": "{}".format(user_prompt),
            "max_tokens": 500
        }
        response = requests.post("http://0.0.0.0:8000/v1/completions", json=data, headers=headers)
        
        llm_response = response.json()
        bt.logging.trace("vLLM response: {}".format(llm_response))

        return llm_response["choices"][0]["text"].strip()  # Strip to remove any extraneous whitespace
                
    
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

        
