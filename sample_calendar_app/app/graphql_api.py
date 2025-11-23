# graphql_api.py
import strawberry
from server_stub import CalendarSyncStub
import grpc
from google_protos import calendar_pb2

channel = grpc.insecure_channel("localhost:50051")
client = CalendarSyncStub(channel)

'''Event Type'''
@strawberry.type
class Event:
    id: str
    title: str
    description: str
    start: str
    end: str
    event_type: str

'''Queries for Events'''
@strawberry.type
class Query:
    @strawberry.field
    def list_events(self, user_id: str, time_min: str = None, time_max: str = None):
        resp = client.ListEvents(calendar_pb2.ListEventsReq(user_id=user_id, time_min=(time_min or ""), time_max=(time_max or "")))
        return [Event(id=e.id, title=e.title, description=e.description, start=e.start, end=e.end, event_type=e.event_type) for e in resp.events]

'''Mutations for Events'''
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_event(self, user_id: str, title: str, desc: str, start_iso: str, end_iso: str, event_type: str):
        req = calendar_pb2.CreateEventReq(user_id=user_id, title=title, description=desc, start_iso=start_iso, end_iso=end_iso, event_type=event_type)
        ev = client.CreateEvent(req)
        return Event(id=ev.id, title=ev.title, description=ev.description, start=ev.start, end=ev.end, event_type=ev.event_type)

schema = strawberry.Schema(query=Query, mutation=Mutation)
