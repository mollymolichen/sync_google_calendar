'''
Handle auth upstream within the UserAggregatorService itself.
'''
# app/auth.py
import jwt  # PyJWT (or any JWT lib)

from typing import Tuple, Dict, Any

# IMPORTANT: in prod, use robust verification, public keys, caching, rotation, etc.
SECRET = "replace-with-real-secret-or-pubkey"

def validate_user_token_and_extract_userid(user_token: str) -> str:
    """
    Validate incoming user token (JWT) and return user_id.
    Raise an exception on invalid token.
    """
    try:
        payload = jwt.decode(user_token, SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("token missing subject")
        return user_id
    except Exception as e:
        raise ValueError(f"invalid token: {e}")

def create_service_auth_header() -> str:
    """
    Create a service-to-service auth header (e.g. signed JWT or mTLS header).
    For demo, return a static string. Replace with secure S2S token.
    """
    return "Bearer svc-token-placeholder"
