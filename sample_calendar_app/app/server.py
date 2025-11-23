import grpc
from concurrent import futures
import calendar_pb2_grpc, calendar_pb2
from google_client import build_service_from_tokens, make_oauth_flow, SCOPES
from models import UserCalendar, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from googleapiclient.errors import HttpError
import uuid, datetime, json, os

# Config
CLIENT_SECRETS_FILE = os.environ.get("GOOGLE_CLIENT_SECRETS", "client_secret.json")
REDIRECT_URI = os.environ.get("OAUTH_REDIRECT_URI", "https://yourdomain.com/oauth2callback")
CLIENT_ID = "<from file>"
CLIENT_SECRET = "<from file>"

engine = create_engine("sqlite:///calendars.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class CalendarSyncServicer(calendar_pb2_grpc.CalendarSyncServicer):
    def GetOAuthUrl(self, request, context):
        flow = make_oauth_flow(REDIRECT_URI, CLIENT_SECRETS_FILE)
        auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
        return calendar_pb2.OAuthUrl(url=auth_url)

    def StoreTokens(self, request, context):
        # request contains access_token, refresh_token, expiry_epoch, user_id
        session = Session()
        u = session.query(UserCalendar).filter_by(user_id=request.user_id).first()
        expiry = datetime.datetime.utcfromtimestamp(request.expiry_epoch)
        if not u:
            u = UserCalendar(user_id=request.user_id)
        u.access_token = request.access_token
        u.refresh_token = request.refresh_token
        u.token_expiry = expiry
        u.opted_out = False
        session.add(u)
        session.commit()
        session.close()
        return Empty()

    def OptOut(self, request, context):
        session = Session()
        u = session.query(UserCalendar).filter_by(user_id=request.user_id).first()
        if u:
            u.opted_out = True
            # optionally revoke tokens via token revocation endpoint
            u.access_token = None
            u.refresh_token = None
            # delete webhook channel data so we stop watching
            u.webhook_channel_id = None
            u.webhook_resource_id = None
            session.add(u)
            session.commit()
        session.close()
        return Empty()

    def CreateEvent(self, request, context):
        session = Session()
        # auth
        u = session.query(UserCalendar).filter_by(user_id=request.user_id).first()
        if not u or u.opted_out:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "user not synced or opted out")

        svc = build_service_from_tokens(u.access_token, u.refresh_token, u.token_expiry, CLIENT_ID, CLIENT_SECRET)

        # new event object
        event_body = {
            "user_id": request.user_id,
            "summary": request.title,
            "description": request.description,
            "start": {"dateTime": request.start_iso},
            "end": {"dateTime": request.end_iso},
            "extendedProperties": {"private": {"event_type": request.event_type}} # extendedProperties.private.event_type is used to persist your internal event type into the Google event so you can read it back later. Google’s event schema supports extendedProperties.
        }
        created = svc.events().insert(calendarId=request.calendar_id or u.calendar_id, body=event_body).execute()
        # return mapping
        ev = calendar_pb2.Event(
            id=created["id"],
            title=created.get("summary", ""),
            description=created.get("description",""),
            start=created["start"].get("dateTime",""),
            end=created["end"].get("dateTime",""),
            event_type=created.get("extendedProperties",{}).get("private",{}).get("event_type","")
        )
        session.close()
        return ev

    def UpdateEvent(self, request, context):
        session = Session()
        u = session.query(UserCalendar).filter_by(user_id=request.user_id).first()
        if not u or u.opted_out:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "user not synced or opted out")
        svc = build_service_from_tokens(u.access_token, u.refresh_token, u.token_expiry, CLIENT_ID, CLIENT_SECRET)
        # fetch event
        ev = svc.events().get(calendarId=request.calendar_id or u.calendar_id, eventId=request.event_id).execute()
        ev["summary"] = request.title
        ev["description"] = request.description
        ev["start"] = {"dateTime": request.start_iso}
        ev["end"] = {"dateTime": request.end_iso}
        if "extendedProperties" not in ev:
            ev["extendedProperties"] = {"private": {}}
        ev["extendedProperties"]["private"]["event_type"] = request.event_type
        updated = svc.events().update(calendarId=request.calendar_id or u.calendar_id, eventId=request.event_id, body=ev).execute()
        resp = calendar_pb2.Event(
            id=updated["id"],
            title=updated.get("summary",""),
            description=updated.get("description",""),
            start=updated["start"].get("dateTime",""),
            end=updated["end"].get("dateTime",""),
            event_type=updated.get("extendedProperties",{}).get("private",{}).get("event_type","")
        )
        session.close()
        return resp

    def DeleteEvent(self, request, context):
        session = Session()
        u = session.query(UserCalendar).filter_by(user_id=request.user_id).first()
        if not u or u.opted_out:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "user not synced or opted out")
        svc = build_service_from_tokens(u.access_token, u.refresh_token, u.token_expiry, CLIENT_ID, CLIENT_SECRET)
        svc.events().delete(calendarId=request.calendar_id or u.calendar_id, eventId=request.event_id).execute()
        session.close()
        return Empty()

    def ListEvents(self, request, context):
        session = Session()
        u = session.query(UserCalendar).filter_by(user_id=request.user_id).first()
        if not u or u.opted_out:
            return calendar_pb2.ListEventsResp()
        svc = build_service_from_tokens(u.access_token, u.refresh_token, u.token_expiry, CLIENT_ID, CLIENT_SECRET)
        events = []
        resp = svc.events().list(calendarId=request.calendar_id or u.calendar_id,
                                 timeMin=request.time_min,
                                 timeMax=request.time_max,
                                 singleEvents=True,
                                 orderBy="startTime").execute()
        for it in resp.get("items", []):
            events.append(calendar_pb2.Event(
                id=it.get("id",""),
                title=it.get("summary",""),
                description=it.get("description",""),
                start=it.get("start",{}).get("dateTime",""),
                end=it.get("end",{}).get("dateTime",""),
                event_type=it.get("extendedProperties",{}).get("private",{}).get("event_type","")
            ))
        session.close()
        return calendar_pb2.ListEventsResp(events=events)

    def HandlePushNotification(self, request, context):
        # Called from webhook receiver; pull changes using syncToken if available
        session = Session()
        u = session.query(UserCalendar).filter_by(user_id=request.user_id).first()
        if not u or u.opted_out:
            return Empty()
        svc = build_service_from_tokens(u.access_token, u.refresh_token, u.token_expiry, CLIENT_ID, CLIENT_SECRET)
        params = {"calendarId": u.calendar_id, "singleEvents": True, "orderBy":"startTime", "showDeleted":True}
        if u.sync_token:
            params["syncToken"] = u.sync_token
        else:
            # first sync: set timeMin to now - 30 days (or choose appropriate window)
            params["timeMin"] = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat() + "Z"
        try:
            results = svc.events().list(calendarId=u.calendar_id, **params).execute()
        except HttpError as e:
            # if syncToken expired, we'll need a full sync (remove token)
            if e.status_code == 410:
                u.sync_token = None
                session.add(u)
                session.commit()
                session.close()
                return Empty()
            raise
        # process changes
        for it in results.get("items", []):
            # example: log or push into your app event store
            print("change:", it.get("id"), it.get("status"))
        # update sync token
        if "nextSyncToken" in results:
            u.sync_token = results["nextSyncToken"]
            session.add(u)
            session.commit()
        session.close()
        return Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calendar_pb2_grpc.add_CalendarSyncServicer_to_server(CalendarSyncServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
