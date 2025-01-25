import hashlib
import json
import os
import re
import sys

from llmhomeautomation.modules.llm.openai.openai import OpenAILLM

class APIHandler:
    def __init__(self, cache_dir: str = "api_cache"):
        """
        Initialize the API handler with the API key and cache directory.
        :param cache_dir: Directory where cached responses are stored.
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(f"Configuration value for OPENAI_KEY is not set or empty in your .env file.")

        self.client = OpenAILLM()
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)  # Ensure the cache directory exists

    def _generate_hash(self, messages: list, model: str) -> str:
        """
        Generate a hash of the request (messages + model).
        :param messages: List of messages to send to the API.
        :param model: The model to use for the request.
        :return: A hash string representing the request.
        """
        # Combine the messages and model into a single string
        request_string = json.dumps({"messages": messages, "model": model}, sort_keys=True)
        # Generate an MD5 hash
        return hashlib.md5(request_string.encode('utf-8')).hexdigest()

    def get_response(self, messages: list, model: str = "gpt-4o") -> str:
        """
        Send a request to the OpenAI API and get the response. Cache the response if it doesn't exist.
        :param prompt: Prompt in string format.
        :param model: The model to use for the request.
        :return: Content of the response message.
        """

        # Generate a unique hash for the request
        request_hash = self._generate_hash(messages, model)
        cache_file = os.path.join(self.cache_dir, f"{request_hash}.txt")

        # Check if the response is already cached
        if os.path.exists(cache_file):
            print(f"Cache hit: {cache_file}")
            with open(cache_file, "r") as f:
                return f.read()

        # If not cached, send the request to the API
        print("Cache miss. Sending request to the API...")
        print(messages)
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )

        # Extract the message content
        response_dict = response.to_dict()
        message_content = self.clean_content(response_dict["choices"][0]["message"]["content"])

        # Cache the response
        with open(cache_file, "w") as f:
            f.write(message_content)

        return message_content

    @staticmethod
    def clean_content(content: str) -> str:
        """
        Cleans API response content by removing code block markers for any language.
        Example: Removes ```python, ```json, and closing ```.
        """
        return re.sub(r"^\s*```[a-zA-Z0-9]*\s*|\s*```$", "", content, flags=re.MULTILINE)
