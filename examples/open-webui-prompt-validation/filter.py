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

    def does_prompt_fail_to_validate(self, prompt):
        # Call validate_prompt endpoint
        engine_client = self.get_engine_client()
        response = engine_client.post(
            f"{engine_client.base_url}/api/v2/tasks/{self.valves.ENGINE_TASK_ID}/validate_prompt",
            json={"prompt": prompt},
        )
        response.raise_for_status()

        validation_result = response.json()
        # Check if any rules failed by looking at rule_results
        if validation_result.get("rule_results"):
            for rule_result in validation_result["rule_results"]:
                if rule_result["result"] == "Fail":
                    return True

        return False

    def inlet(
        self, body: dict, __user__: Optional[dict] = None, __event_emitter__=None
    ) -> dict:
        # Modify the request body or validate it before processing by the chat completion API.
        # This function is the pre-processor for the API where various checks on the input can be performed.
        # It can also modify the request before sending it to the API.

        # Skip validation if no task ID is configured
        if not self.valves.ENGINE_TASK_ID:
            return body

        # Check if messages array exists and has elements
        if not body.get("messages") or len(body["messages"]) == 0:
            return body

        # Get the most recent message
        latest_message = body["messages"][-1]

        # Only proceed if it's a user message with content
        if latest_message["role"] != "user" or not latest_message.get("content"):
            return body

        # Check if the latest message contains a prompt injection
        if self.does_prompt_fail_to_validate(latest_message["content"]):
            # Replace the latest message with a placeholder
            body["messages"][-1] = {
                "role": "user",
                "content": "[Message removed due to security concerns]"
            }

            # Add a security notification message
            body["messages"].append({
                "role": "user",
                "content": "Please provide a quick comment explaining that the user's most recent message was blocked because it was detected as violating organization security policies (eg: prompt injection, PII, governance policies, etc.)."
            })


        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify or analyze the response body after processing by the API.
        # This function is the post-processor for the API, which can be used to modify the response
        # or perform additional checks and analytics.
        print(f"outlet:{__name__}")
        print(f"outlet:body:{body}")
        print(f"outlet:user:{__user__}")

        return body
