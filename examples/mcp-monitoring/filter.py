"""
title: Arthur Engine Filter
author: Zach Fry (Arthur)
author_url: https://github.com/fryz
funding_url: https://github.com/arthur-ai
version: 0.1
"""

from pydantic import BaseModel, Field
from typing import Optional
import requests
import json


class Filter:
    class Valves(BaseModel):
        ENGINE_BASE_URL: str = Field(default="http://host.docker.internal:3030")
        ENGINE_API_KEY: str = Field(default="")
        ENGINE_TASK_ID: str = Field(default="")

    def __init__(self):
        # Indicates custom file handling logic. This flag helps disengage default routines in favor of custom
        # implementations, informing the WebUI to defer file-related operations to designated methods within this class.
        # Alternatively, you can remove the files directly from the body in from the inlet hook
        # self.file_handler = True

        # Initialize 'valves' with specific configurations. Using 'Valves' instance helps encapsulate settings,
        # which ensures settings are managed cohesively and not confused with operational flags like 'file_handler'.
        self.valves = self.Valves()
        pass

    def get_engine_client(self):
        # Create session with base configuration
        session = requests.Session()

        # Configure base headers if API key is provided
        if self.valves.ENGINE_API_KEY:
            session.headers.update(
                {"Authorization": f"Bearer {self.valves.ENGINE_API_KEY}"}
            )

        # Configure base URL and return session
        session.base_url = self.valves.ENGINE_BASE_URL.rstrip("/")
        return session

    def send_prompt_validation(self, prompt):
        """Send prompt in for validation, but do nothing with result"""
        engine_client = self.get_engine_client()
        response = engine_client.post(
            f"{engine_client.base_url}/api/v2/tasks/{self.valves.ENGINE_TASK_ID}/validate_prompt",
            json={"prompt": prompt},
        )
        response.raise_for_status()

        return response.json().get("inference_id")

    def send_response_validation(self, inference_id, response, context=""):
        """Send response in for validation, but do nothing with result"""
        engine_client = self.get_engine_client()
        response = engine_client.post(
            f"{engine_client.base_url}/api/v2/tasks/{self.valves.ENGINE_TASK_ID}/validate_response/{inference_id}",
            json={"response": response, "context": json.dumps(context)},
        )
        response.raise_for_status()

        return

    def inlet(
        self, body: dict, __user__: Optional[dict] = None, __event_emitter__=None
    ) -> dict:
        return body

    def extract_conversation_data(self, messages):
        """
        Extract prompt, response, and context from a list of messages.

        Args:
            messages: List of message objects with properties like id, role, content, and timestamp

        Returns:
            dict: Object containing prompt, response, and context
        """
        if not messages or len(messages) < 2:
            return {"prompt": "", "response": "", "context": []}

        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda x: x.get("timestamp", 0))

        # Find the most recent user message (prompt) and assistant message (response) in one pass
        prompt = ""
        response = ""
        prompt_index = -1
        response_index = -1

        for i, msg in enumerate(sorted_messages):
            if msg.get("role") == "user":
                prompt = msg["content"]
                prompt_index = i
            elif msg.get("role") == "assistant":
                response = msg["content"]
                response_index = i

        # Extract context (all messages between prompt and response, non-inclusive)
        context = []
        if (
            prompt_index != -1
            and response_index != -1
            and prompt_index < response_index
        ):
            context = [
                msg.get("content", "")
                for msg in sorted_messages[prompt_index + 1 : response_index]
            ]
        return {"prompt": prompt, "response": response, "context": context}

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Skip validation if no task ID is configured
        if not self.valves.ENGINE_TASK_ID:
            return body

        turn_messages = self.extract_conversation_data(body["messages"])

        prompt = turn_messages["prompt"]
        response = turn_messages["response"]
        context = turn_messages["context"]

        inference_id = self.send_prompt_validation(prompt)

        self.send_response_validation(
            inference_id,
            response,
            context,
        )

        return body
