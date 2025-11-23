from fastapi import FastAPI, Request, Header, HTTPException
import uvicorn
from sqlalchemy.orm import sessionmaker
from models import UserCalendar
from server_stub import CalendarSyncStub # gRPC client stub

app = FastAPI()
# create gRPC client (channel)
import grpc
channel = grpc.insecure_channel("localhost:50051")
client = CalendarSyncStub(channel)

@app.post("/webhook/calendar")
async def google_push(request: Request,
                      x_goog_channel_id: str = Header(None),
                      x_goog_resource_id: str = Header(None),
                      x_goog_channel_token: str = Header(None)):
    # Lookup which user this channel belongs to
    session = Session()
    u = session.query(UserCalendar).filter_by(webhook_channel_id=x_goog_channel_id).first()
    if not u:
        # unknown channel: ignore
        session.close()
        return {"status":"ignored"}
    # optionally verify x_goog_resource_id matches u.webhook_resource_id
    # notify gRPC server to perform sync
    client.HandlePushNotification(UserId(user_id=u.user_id))
    session.close()
    return {"status":"ok"}
