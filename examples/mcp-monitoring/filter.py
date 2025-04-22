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
import re
import logging
import html


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

    def decode_html(self, text):
        """
        Decode all HTML entities in the text using Python's html module.

        Args:
            text: String that may contain HTML entities

        Returns:
            str: String with all HTML entities decoded
        """
        return html.unescape(text)

    def decode_response(self, text):
        """
        Decode HTML entities and escape sequences in the response.

        Args:
            text: String that may contain HTML entities and escape sequences

        Returns:
            str: Decoded string
        """
        # First decode all HTML entities
        decoded = self.decode_html(text)

        # Then handle escape sequences
        # Handle double-escaped sequences first
        decoded = decoded.replace("\\\\n", "\n")
        decoded = decoded.replace("\\\\r", "\n")
        decoded = decoded.replace("\\\\t", "\t")
        decoded = decoded.replace('\\\\"', '"')
        decoded = decoded.replace("\\\\", "\\")

        # Then handle single-escaped sequences
        decoded = decoded.replace("\\n", "\n")
        decoded = decoded.replace("\\r", "\n")
        decoded = decoded.replace("\\t", "\t")
        decoded = decoded.replace('\\"', '"')

        # Handle literal \r\n sequences that might still be present
        decoded = decoded.replace("\\r\\n", "\n")

        # Normalize all newlines to \n
        decoded = decoded.replace("\r\n", "\n")
        decoded = decoded.replace("\r", "\n")

        return decoded

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
        user_messages = [
            msg["content"] for msg in sorted_messages if msg.get("role") == "user"
        ]
        assistant_messages = [
            msg["content"] for msg in sorted_messages if msg.get("role") == "assistant"
        ]
        prompt = user_messages[-1] if user_messages else ""
        response_with_context = assistant_messages[-1] if assistant_messages else ""

        # Decode the response
        decoded_response = self.decode_response(response_with_context)
        logging.warn(f"decoded_response: {decoded_response}")

        # Extract response and context from the decoded response
        response, context = self.get_response_and_context(decoded_response)

        return {"prompt": prompt, "response": response, "context": context}

    def get_response_and_context(self, response_with_context):
        """
        Extract response and context from a string that may contain <details> tags.

        Args:
            response_with_context: String that may contain <details> tags

        Returns:
            tuple: (response, context) where:
                - response is the text not wrapped in <details> tags
                - context is a list of full <details> tags as strings
        """

        # Extract all <details> tags as context
        details_pattern = r"<details[^>]*>.*?</details>"
        details_matches = re.findall(details_pattern, response_with_context, re.DOTALL)

        # Convert match objects to strings if needed
        context = [str(match) for match in details_matches]

        # Remove all <details> tags from the prompt
        response = re.sub(details_pattern, "", response_with_context, flags=re.DOTALL)

        # Clean up the prompt by removing extra whitespace
        response = re.sub(r"\s+", " ", response).strip()

        return response, context

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:

        # Skip validation if no task ID is configured
        if not self.valves.ENGINE_TASK_ID:
            return body

        turn_messages = self.extract_conversation_data(body["messages"])

        prompt = turn_messages["prompt"]
        response = turn_messages["response"]
        context = turn_messages["context"]

        logging.warn(f"prompt: {prompt}")
        logging.warn(f"response: {response}")
        logging.warn(f"context: {context}")

        inference_id = self.send_prompt_validation(prompt)

        self.send_response_validation(
            inference_id,
            response,
            context,
        )

        return body
