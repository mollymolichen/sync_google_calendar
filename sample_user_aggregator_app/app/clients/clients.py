'''
Improved implementation to fetch Identity, Preferences, and Profile in parallel.
'''

# app/clients.py
from typing import Any, Dict, Optional
import asyncio
import json
import httpx
import grpc
import logging

# gRPC: assume you have generated asyncio stubs, e.g. import identity_pb2_grpc, profile_pb2
# from .proto import profile_pb2_grpc, profile_pb2

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 2.0  # seconds per downstream call

class RestIdentityClient:
    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)

    async def get_identity(self, user_id: str, svc_auth_header: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/identities/{user_id}"
        headers = {"Authorization": svc_auth_header}
        resp = await self._client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

class GraphQLPreferencesClient:
    def __init__(self, graphql_url: str, client: Optional[httpx.AsyncClient] = None):
        self.graphql_url = graphql_url
        self._client = client or httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)

    async def get_preferences(self, user_id: str, svc_auth_header: str) -> Dict[str, Any]:
        query = """
        query GetPrefs($uid: ID!) {
          userPreferences(userId: $uid) {
            language
            timezone
            emailNotifications
          }
        }
        """
        payload = {"query": query, "variables": {"uid": user_id}}
        headers = {"Authorization": svc_auth_header, "Content-Type": "application/json"}
        resp = await self._client.post(self.graphql_url, headers=headers, json=payload)
        resp.raise_for_status()
        body = resp.json()
        if "errors" in body:
            raise RuntimeError(f"GraphQL errors: {body['errors']}")
        return body.get("data", {}).get("userPreferences") or {}

class GrpcProfileClient:
    def __init__(self, target: str, channel: Optional[grpc.aio.Channel] = None):
        self.target = target
        self._channel = channel  # or create later

    async def get_profile(self, user_id: str, svc_auth_header: str) -> Dict[str, Any]:
        # IMPORTANT: replace with real grpc stub calls
        # Example pattern:
        # channel = self._channel or grpc.aio.insecure_channel(self.target)
        # stub = profile_pb2_grpc.ProfileServiceStub(channel)
        # req = profile_pb2.GetProfileRequest(user_id=user_id)
        # metadata = (("authorization", svc_auth_header),)
        # resp = await stub.GetProfile(req, metadata=metadata, timeout=DEFAULT_TIMEOUT)
        # return { "display_name": resp.display_name, ...}

        # Demo stubbed response to illustrate the pattern:
        await asyncio.sleep(0)  # yield control
        return {
            "display_name": f"User {user_id}",
            "phone_number": "+1-555-000-000",
            "bio": "This is a mock profile"
        }
