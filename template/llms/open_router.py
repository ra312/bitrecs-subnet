import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel
from openai import OpenAI


class OpenRouter(BaseModel):
    def __init__(self):
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set in .env file")


    def call_open_router(self, prompt, model="openai/gpt-3.5-turbo"):   
        if not prompt or len(prompt) < 10:
            raise ValueError()

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.OPENROUTER_API_KEY,
        )

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://janus.ai",
                "X-Title": "janusdotai"
            },
            model=model,
            messages=[
            {
                "role": "user",
                "content": prompt,
            }]
        )
        thing = completion.choices[0].message.content
        #print(thing)
        print("call_open_router COMPLETE")
        return thing