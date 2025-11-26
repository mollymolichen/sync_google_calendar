'''
Timeouts: IdentityClient and ContactsClient use requests.get(..., timeout=...) per the design note.
Sequential calls: UserAggregatorService.get_user_aggregate calls Identity → Profile → Contacts one after the other (no async/parallel).
No graceful failure: clients call .raise_for_status() or otherwise propagate exceptions; the aggregator does not attempt retries or fallback—service will return 500 to the caller when any downstream fails.
Auth handling: the same auth_token is passed to all downstream calls (contrary to your recommendation to handle auth upstream).
Data structure: results are merged into a nested dict with convenience top-level fields (the design called out using a dict).
GraphQL schema: UserProfile intentionally omits phone to reflect the original bug/omission.
'''

# app/main.py
from fastapi import FastAPI, Request, HTTPException
import uvicorn

from app.clients.identity_client import IdentityClient
from app.clients.profile_client import ProfileClient
from app.clients.contacts_client import ContactsClient
from app.aggregator import UserAggregatorService
from app.graphql_schema import graphql_router, set_aggregator

app = FastAPI(title="UserAggregator (original design)")

# Configure downstream clients (example URLs/targets)
identity_client = IdentityClient(base_url="http://identity-service.local", timeout_seconds=2.0)
profile_client = ProfileClient(target="profile-service.local:50051")
contacts_client = ContactsClient(base_url="http://contacts-service.local", timeout_seconds=2.0)

aggregator = UserAggregatorService(identity_client, profile_client, contacts_client)
set_aggregator(aggregator)

# Mount GraphQL endpoint
app.include_router(graphql_router, prefix="/graphql")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/user/{user_id}/aggregate")
def get_aggregate(user_id: str, request: Request):
    """
    An example REST wrapper for the aggregator (again: sequential calls, passes auth token if provided).
    This endpoint will raise if any downstream client raises (original design's lack of graceful fail).
    """
    auth = None
    auth_header = request.headers.get("authorization")
    if auth_header:
        auth = auth_header.split(" ", 1)[-1]  # naive extraction

    # Add more robust error handling
    try:
        agg = aggregator.get_user_aggregate(user_id, auth_token=auth)
        return agg
    except Exception as exc:
        # Original design: doesn't gracefully handle downstream failures.
        # We surface a 500 to the caller to reflect that behavior.
        raise HTTPException(status_code=500, detail=str(exc))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
