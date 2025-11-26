'''Calls happen sequentially, increasing latency.
No timeouts, retries, or fallbacks.
No concurrency (poor scalability).
No structured error handling.
No tracing / observability hooks.'''

from typing import Dict, Any

class EmailServiceClient:
    def send(self, user_id: str, message: str) -> Dict[str, Any]:
        # placeholder synchronous API call
        return {"channel": "email", "success": True}


class SMSServiceClient:
    def send(self, user_id: str, message: str) -> Dict[str, Any]:
        return {"channel": "sms", "success": True}


class PushServiceClient:
    def send(self, user_id: str, message: str) -> Dict[str, Any]:
        return {"channel": "push", "success": True}


class NotificationOrchestratorService:
    """
    Sends a message via Email, SMS, and Push sequentially.
    """

    def __init__(self):
        self.email = EmailServiceClient()
        self.sms = SMSServiceClient()
        self.push = PushServiceClient()

    def notify(self, user_id: str, message: str) -> Dict[str, Any]:
        results = {}

        email_result = self.email.send(user_id, message)
        results["email"] = email_result

        sms_result = self.sms.send(user_id, message)
        results["sms"] = sms_result

        push_result = self.push.send(user_id, message)
        results["push"] = push_result

        return {
            "userId": user_id,
            "results": results,
        }