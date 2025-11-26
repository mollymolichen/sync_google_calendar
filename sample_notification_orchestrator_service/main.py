import asyncio
from notification_orchestrator_v2 import NotificationOrchestratorServiceAsync

async def main():
    service = NotificationOrchestratorServiceAsync()
    out = await service.notify("user123", "Hello world")
    print(out)

asyncio.run(main())
