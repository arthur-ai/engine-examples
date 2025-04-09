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
import logging
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
            json={"response": response, "context": context},
        )
        response.raise_for_status()

        return

    def inlet(
        self, body: dict, __user__: Optional[dict] = None, __event_emitter__=None
    ) -> dict:
        # Skip validation if no task ID is configured
        if not self.valves.ENGINE_TASK_ID:
            return body

        # Check if messages array exists and has elements
        if not body.get("messages") or len(body["messages"]) == 0:
            return body

        # Get the most recent message
        latest_message = body["messages"][-1]

        logging.warning(f"Validating message body: {json.dumps(body, indent=2)}")

        inference_id = self.send_prompt_validation(latest_message["content"])
        body["metadata"].setdefault("inference_id", inference_id)

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Skip validation if no task ID is configured
        if not self.valves.ENGINE_TASK_ID:
            return body

        # Check if messages array exists and has elements
        if not body.get("messages") or len(body["messages"]) == 0:
            return body

        # Get the most recent message
        latest_message = body["messages"][-1]
        inference_id = body["metadata"].get("inference_id")

        if not inference_id:
            return body

        # TODO: Figure out what the right context is
        self.send_response_validation(
            inference_id,
            latest_message["content"],
            body,  # Pass in entire body object (inc. message history) for context
        )

        return body
