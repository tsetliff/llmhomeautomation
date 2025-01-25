import os
import openai
from llmhomeautomation.modules.module import Module
import hashlib
import json
import os
import re
from llmhomeautomation.modules.module import Module

class OpenAILLM(Module):
    def __init__(self, cache_dir: str = "api_cache"):
        super().__init__()
        self.client = openai
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)  # Ensure the cache directory exists

    def _generate_hash(self, messages: list, model: str) -> str:
        request_string = json.dumps({"messages": messages, "model": model}, sort_keys=True)
        return hashlib.md5(request_string.encode('utf-8')).hexdigest()

    def _generate_hash(self, messages: list, model: str) -> str:
        request_string = json.dumps({"messages": messages, "model": model}, sort_keys=True)
        return hashlib.md5(request_string.encode('utf-8')).hexdigest()

    def llm_request(self, messages: list, model: str = "gpt-4o") -> str:
        request_hash = self._generate_hash(messages, model)
        cache_file = os.path.join(self.cache_dir, f"{request_hash}.txt")

        if os.path.exists(cache_file):
            print(f"Cache hit: {cache_file}")
            with open(cache_file, "r") as f:
                return f.read()

        print("Cache miss. Sending request to the API...")
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )

        response_dict = response.to_dict()
        message_content = self.clean_content(response_dict["choices"][0]["message"]["content"])

        with open(cache_file, "w") as f:
            f.write(message_content)

        return message_content

    @staticmethod
    def clean_content(content: str) -> str:
        return re.sub(r"^\s*```[a-zA-Z0-9]*\s*|\s*```$", "", content, flags=re.MULTILINE)

class OpenAI(Module):
    def __init__(self):
        super().__init__()
    def llm_request(self, messages: list, model: str = "gpt-4o") -> str:
        request_hash = self._generate_hash(messages, model)
        cache_file = os.path.join(self.cache_dir, f"{request_hash}.txt")

        if os.path.exists(cache_file):
            print(f"Cache hit: {cache_file}")
            with open(cache_file, "r") as f:
                return f.read()

        print("Cache miss. Sending request to the API...")
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )

        response_dict = response.to_dict()
        message_content = self.clean_content(response_dict["choices"][0]["message"]["content"])

        with open(cache_file, "w") as f:
            f.write(message_content)

        return message_content
