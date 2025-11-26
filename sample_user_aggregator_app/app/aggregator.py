# app/aggregator.py
from typing import Optional, Dict, Any

from app.clients.identity_client import IdentityClient
from app.clients.profile_client import ProfileClient
from app.clients.contacts_client import ContactsClient

class UserAggregatorService:
    """
    Original design: sequential calls; merges into a dict; passes same auth token downstream.
    """

    def __init__(self, identity_client: IdentityClient, profile_client: ProfileClient, contacts_client: ContactsClient):
        self.identity_client = identity_client
        self.profile_client = profile_client
        self.contacts_client = contacts_client

    # Make async
    # Centralize auth rather than passing the same auth token downstream to all 3 services
    def get_user_aggregate(self, user_id: str, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Sequentially fetches data from Identity, Profile, and Contacts services,
        merges all returned JSON into a single dict (later fields may overwrite earlier ones).
        """
        aggregate: Dict[str, Any] = {}

        # 1) Identity (REST) - uses timeout already set in the client
        identity_data = self.identity_client.fetch_identity(user_id, auth_token=auth_token)
        aggregate["identity"] = identity_data

        # 2) Profile (gRPC)
        profile_data = self.profile_client.fetch_profile(user_id, auth_token=auth_token)
        aggregate["profile"] = profile_data

        # 3) Contacts (REST)
        contacts_data = self.contacts_client.fetch_contacts(user_id, auth_token=auth_token)
        aggregate["contacts"] = contacts_data

        # Flattening strategy: produce top-level convenience fields
        # (original design said: UserAggregatorService would merge user data into a dict)
        # We'll copy some common fields into top-level for consumers.
        if "identity" in aggregate:
            aggregate["id"] = aggregate["identity"].get("id")
            aggregate["email"] = aggregate["identity"].get("email")
            aggregate["name"] = aggregate["identity"].get("name")

        if "profile" in aggregate:
            aggregate["bio"] = aggregate["profile"].get("bio")
            aggregate["avatar_url"] = aggregate["profile"].get("avatar_url")

        # Note: original design did NOT include phone number in GraphQL response.
        # If phone numbers live in contacts_data, we intentionally do not expose them further here.
        return aggregate
    
