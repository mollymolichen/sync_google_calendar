import asyncio
from typing import Dict, Any

# use asyncio for concurrency and to decrease E2E latency
class EmailServiceClient:
    async def send(self, user_id: str, message: str) -> Dict[str, Any]:
        await asyncio.sleep(0.05)  # simulate network delay
        return {"channel": "email", "success": True}


class SMSServiceClient:
    async def send(self, user_id: str, message: str) -> Dict[str, Any]:
        await asyncio.sleep(0.05)
        return {"channel": "sms", "success": True}


class PushServiceClient:
    async def send(self, user_id: str, message: str) -> Dict[str, Any]:
        await asyncio.sleep(0.05)
        return {"channel": "push", "success": True}


class NotificationOrchestratorServiceAsync:
    """
    Orchestrates notifications in parallel using asyncio.
    Includes graceful degradation, timeouts, and partial failures.
    """

    def __init__(self, timeout_seconds: float = 1.5):
        self.email = EmailServiceClient()
        self.sms = SMSServiceClient()
        self.push = PushServiceClient()
        self.timeout = timeout_seconds

    # safe error handling + graceful degradation
    async def _safe_call(self, coro):
        try:
            return await asyncio.wait_for(coro, timeout=self.timeout)
        except asyncio.TimeoutError:
            return {"success": False, "error": "timeout"}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def notify(self, user_id: str, message: str) -> Dict[str, Any]:
        email_task = self._safe_call(self.email.send(user_id, message))
        sms_task = self._safe_call(self.sms.send(user_id, message))
        push_task = self._safe_call(self.push.send(user_id, message))

        # Fire all 3 coroutines at the same time
        email, sms, push = await asyncio.gather(
            email_task, sms_task, push_task, return_exceptions=False
        )

        return {
            "userId": user_id,
            "results": {
                "email": email,
                "sms": sms,
                "push": push,
            },
            "overallSuccess": all(r.get("success") for r in [email, sms, push]),
        }
