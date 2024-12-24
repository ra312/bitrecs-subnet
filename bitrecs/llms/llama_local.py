
from os import path
import os
import pathlib
import base64
import requests


class OllamaLocal():
    def __init__(self, 
                 ollama_url: str, 
                 model: str, 
                 system_prompt: str, 
                 temp=0.0):
        
        if not ollama_url:
            raise Exception
        self.ollama_url = ollama_url
        self.model = model
        if not system_prompt:
            system_prompt = "You are a helpful assistant."
        self.system_prompt = system_prompt        
        if temp < 0 or temp > 1:
            raise Exception
        self.temp = temp
        self.keep_alive = 1800


    def file_to_base64(self, file_path) -> str:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
        
    def ask_ollama(self, prompt) -> str:
        data = {
            "model": self.model,
            "system": self.system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "temperature": self.temp,
            }
        }
        # print(data)
        return self.call_ollama(data)
        

    # def ask_ollama_long_ctx(self, prompt) -> str:
    #     options = {
    #         "temperature": self.temp,
    #     }
        
    #     if os.environ.get("num_ctx") is not None:
    #         num_ctx = int(os.environ.get('num_ctx'))
    #         print(f"CUSTOM CTX LENGTH {num_ctx}")
    #         options = {
    #             "temperature": self.temp,
    #             "num_ctx": num_ctx
    #         }

    #     data = {
    #         "model": self.model,       
    #         "system": self.system_prompt,    
    #         "messages": [              
    #             {
    #                 "role": "user",
    #                 "content": prompt
    #             }
    #         ],
    #         "stream": False,
    #         "keep_alive": self.keep_alive,
    #         "options": options
    #     }
    #     # print(data)
    #     return self.call_ollama(data)
    

    def get_ollama_caption(self, file_path) -> str:        
        base64_image = self.file_to_base64(file_path)
        data = {
            "model": self.model,
            "system": self.system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": "What is this?",
                    "stream": False,
                    "images": [base64_image]
                }
            ],
            "stream": False,
            "keep_alive": self.keep_alive,
             "options": {
                "temperature": self.temp
            }
        }
        # print(data)
        return self.call_ollama(data)   


    def call_ollama(self, data) -> str:        
        response = requests.post(self.ollama_url, json=data)
        if response.status_code == 200:
            response_json = response.json()
            message = response_json["message"]
            content = message["content"]            
            return content
        else:
            print(response.text)
            return "Error: Unable to get caption from LLama server status {}".format(response.status_code)

