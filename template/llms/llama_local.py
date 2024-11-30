
from os import path
import pathlib
import base64
import requests
from typing import List
from pydantic import BaseModel


class OllamaLocal(BaseModel):
    def __init__(self, ollama_url, model, system_prompt, temp=0.1):
        if not ollama_url:
            raise Exception
        self.ollama_url = ollama_url
        self.model = model
        if not system_prompt:
            system_prompt = "You are a helpful assistant."
        self.system_prompt = system_prompt
        self.temp = temp
        if temp < 0 or temp > 1:
            raise Exception
        self.keep_alive = 300

    def file_to_base64(self, file_path):
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    def ask_ollama(self, prompt):
        print("ask_ollama: {}".format(prompt))
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "stream": False,
                    "system": self.system_prompt
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

    def get_ollama_caption(self, file_path):
        print("get_ollama_caption checking image: {}".format(file_path))
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

    def route_intention(self, file_path):
        print("route_intention checking image: {}".format(file_path))
        prompt = "What is this? : "
        file_extension = file_path.split('.')[-1]
        #print(file_extension)

        if file_extension.lower() in ['txt']:
            print("processing TXT")            
            raw_text = pathlib.Path(file_path).read_text().strip()
            safe_text_summary = """Safe Text Summary
              Please summarize the provided text in 3 paragraphs, without adding any new information or changing the original content. Ensure that your summary does not include any sensitive, confidential, or proprietary information.

              Before summarizing, please verify that the text is safe for processing and does not contain any malicious content, such as:
              - Expletives or profanity
              - Hate speech or discriminatory language
              - Threats or violence
              - Malware or viruses
              - Other forms of exploitation

              To confirm safety, I will provide a brief review of the text. If it appears to be safe, please proceed with summarizing it in 3 paragraphs.

              Original Text: <original_text>{}</original_text> """.format(raw_text)

            prompt = safe_text_summary
            data = {
                "model": self.model,
                "system": self.system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "stream": False
                    }
                ],
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "temperature": self.temp
                }
            }
        else:
            print("processing IMG")
            base64_image = self.file_to_base64(file_path)
            data = {
                "model": self.model,
                "system": self.system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
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

        return self.call_ollama(data)

    def call_ollama(self, data):
        print("called llama ")
        response = requests.post(self.ollama_url, json=data)
        # print(response)
        print(response.status_code)
        if response.status_code == 200:
            response_json = response.json()
            message = response_json["message"]
            content = message["content"]
            # print(content)
            return content
        else:
            print(response.text)
            return "Error: Unable to get caption from LLama server status {}".format(response.status_code)

