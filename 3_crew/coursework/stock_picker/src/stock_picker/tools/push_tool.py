import os

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

import requests


class PushNotificationInput(BaseModel):
    """Input schema for PushNotificationTool."""
    title: str = Field(default="Investment Decision",
                       description="Title of the notification. Defaults to 'Investment Decision' if not provided.")
    message: str = Field(..., description="Message content of the notification")


class PushNotificationTool(BaseTool):
    name: str = "push_notification"
    description: str = (
        "Sends a push notification to the user's phone. "
        "Requires a 'message' with the notification content; 'title' is optional."
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, title: str = "Investment Decision", message: str = "") -> str:
        token = os.getenv("PUSHOVER_TOKEN")
        user = os.getenv("PUSHOVER_USER")
        if token and user:
            return self._send_pushover(token, user, title, message)
        return self._send_ntfy(title, message)

    def _send_pushover(self, token: str, user: str, title: str, message: str) -> str:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={"token": token, "user": user, "title": title, "message": message},
            timeout=30,
        )
        if response.status_code == 200 and response.json().get("status") == 1:
            return f"Push notification sent successfully via Pushover: {title} - {message}"
        else:
            return f"Failed to send push notification via Pushover: {response.status_code} {response.text}"

    def _send_ntfy(self, title: str, message: str) -> str:
        response = requests.post(
            "https://ntfy.sh/stock-picker-alerts",
            data=message.encode("utf-8"),
            headers={"Title": title.encode("utf-8")},
            timeout=30,
        )
        if response.status_code == 200:
            return f"Push notification sent successfully via ntfy.sh: {title} - {message}"
        else:
            return f"Failed to send push notification via ntfy.sh: {response.status_code}"
