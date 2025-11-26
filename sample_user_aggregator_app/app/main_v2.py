# app/main.py
from fastapi import FastAPI, Header, HTTPException
import uvicorn
import logging

from .clients import RestIdentityClient, GrpcProfileClient, GraphQLPreferencesClient
from .aggregator import aggregate_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="UserAggregatorService")

# instantiate clients with real endpoints
IDENTITY_BASE = "https://identity.svc.local"
GRAPHQL_URL = "https://prefs.svc.local/graphql"
GRPC_TARGET = "profile.svc.local:50051"

identity_client = RestIdentityClient(IDENTITY_BASE)
prefs_client = GraphQLPreferencesClient(GRAPHQL_URL)
profile_client = GrpcProfileClient(GRPC_TARGET)


@app.get("/v1/users/me")
async def get_my_user(authorization: str = Header(...)):
    """
    Expects Authorization: Bearer <user-jwt>
    This endpoint validates the incoming token, then calls downstream services in parallel.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="invalid auth header")

    user_token = authorization.split(" ", 1)[1]
    try:
        result = await aggregate_user(
            user_token,
            identity_client,
            profile_client,
            prefs_client,
            per_call_timeout=2.0
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except Exception as e:
        logger.exception("unexpected error in aggregator")
        raise HTTPException(status_code=500, detail="internal error")


# run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
