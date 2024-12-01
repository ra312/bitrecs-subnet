import os
from openai import OpenAI

class ChatGPT:
    def __init__(self, key):
        self.CHATGPT_API_KEY = key
        if not self.CHATGPT_API_KEY:
            raise ValueError("CHATGPT_API_KEY is not set in .env file")

    def call_chat_gpt(self, prompt, model="gpt-4o-mini"):
        if not prompt or len(prompt) < 10:
            raise ValueError()

        client = OpenAI(api_key=self.CHATGPT_API_KEY)

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://bitrecs.ai",
                "X-Title": "bitrecs"
            },
            model=model,
            messages=[
            {
                "role": "user",
                "content": prompt,
            }]
        )

        thing = completion.choices[0].message.content                
        return thing