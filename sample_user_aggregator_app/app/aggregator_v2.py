'''
Improvements from v1:
Parallelism — asyncio.gather / custom _safe_call + asyncio.wait_for pattern runs calls concurrently and enforces per-call timeouts. That reduces p99 latency compared with sequential blocking calls.
Graceful failure — each call returns (name, ok, payload-or-error) so we can reply with partial success rather than failing the entire aggregator. The response includes errors and partial: true to indicate incompleteness.
Upstream auth — we validate_user_token_and_extract_userid inside aggregator and create a service auth header (create_service_auth_header()), so downstream services receive S2S credentials instead of the user's raw token. This helps centralize auth and reduces token juggling in downstream services.
Timeouts & exception handling — httpx raises HTTPStatusError for non-2xx (we catch and include the error). gRPC calls should also use RPC timeouts and metadata; replace stub example with real await stub.Method(req, timeout=..., metadata=...).
Merging — we merge under keys identity, profile, preferences. Business logic can prioritize one source when overlapping fields exist (example above copies phone number to top-level).
Backpressure / Bandwidth considerations — concurrency limits: for many simultaneous aggregator requests, you should use a bounded semaphore / connection pool to limit concurrent downstream calls. Example: wrap calls with a global asyncio.Semaphore(50) to avoid overwhelming downstream.
Retries / Exponential backoff — not included here but often useful. Be careful: retries under latency-sensitive aggregator calls can increase p99; prefer short/capped retries or only retry idempotent calls.
Circuit breaker — for a robust system, add a circuit-breaker per downstream service to avoid cascading failures.
Observability — add structured logs, tracing (OpenTelemetry), metrics (latency, errors per downstream call), and tag each result as cached/miss/served-from-fallback if relevant.
gRPC notes — use grpc.aio client and real code generation. Pass metadata for auth (metadata is a sequence of tuples). Also set channel options and keepalive if needed.
'''
# app/aggregator_v2.py
from typing import Dict, Any, Tuple
import asyncio
import logging

from .clients import RestIdentityClient, GrpcProfileClient, GraphQLPreferencesClient
from .auth import validate_user_token_and_extract_userid, create_service_auth_header

logger = logging.getLogger(__name__)

async def aggregate_user(user_token: str,
                         identity_client: RestIdentityClient,
                         profile_client: GrpcProfileClient,
                         prefs_client: GraphQLPreferencesClient,
                         per_call_timeout: float = 2.0) -> Dict[str, Any]:
    """
    Validate token upstream, then call 3 downstream services in parallel
    and merge results. Return partial results and an 'errors' section describing failures.
    """
    # 1) Auth validation (upstream)
    user_id = validate_user_token_and_extract_userid(user_token)
    svc_auth = create_service_auth_header()

    # 2) prepare coroutines
    coros = [
        _safe_call(identity_client.get_identity, user_id, svc_auth, "identity"),
        _safe_call(profile_client.get_profile, user_id, svc_auth, "profile"),
        _safe_call(prefs_client.get_preferences, user_id, svc_auth, "preferences"),
    ]

    # 3) run concurrently with overall timeout
    results = await asyncio.gather(*coros, return_exceptions=False)

    # results is a list of (name, success_bool, payload_or_error)
    merged: Dict[str, Any] = {}
    errors = {}

    for name, ok, payload in results:
        if ok:
            # merge payload under a sensible key
            if name == "identity":
                merged["identity"] = payload
            elif name == "profile":
                merged["profile"] = payload
            elif name == "preferences":
                merged["preferences"] = payload
        else:
            errors[name] = str(payload)

    # Business logic: create combined 'user' dict
    user: Dict[str, Any] = {}
    # Example priorities: identity -> profile -> preferences
    if "identity" in merged:
        user.update(merged["identity"])
    if "profile" in merged:
        user["profile"] = merged["profile"]
        # copy phone_number into top-level if present
        if merged["profile"].get("phone_number"):
            user["phone_number"] = merged["profile"]["phone_number"]
    if "preferences" in merged:
        user["preferences"] = merged["preferences"]

    response = {
        "user_id": user_id,
        "user": user,
        "errors": errors or None,
        "partial": bool(errors)
    }
    return response

async def _safe_call(fn, user_id: str, svc_auth: str, name: str, timeout: float = 2.0) -> Tuple[str, bool, Any]:
    """
    Call `fn(user_id, svc_auth)` and return a tuple (name, ok, payload_or_exc).
    This helper ensures timeouts and exception capture.
    """
    try:
        # use asyncio.wait_for to enforce per-call timeout
        result = await asyncio.wait_for(fn(user_id, svc_auth), timeout=timeout)
        return (name, True, result)
    except asyncio.TimeoutError as te:
        logger.warning("%s call timed out: %s", name, te)
        return (name, False, f"timeout after {timeout}s")
    except httpx.HTTPStatusError as he:
        logger.warning("%s http error: %s", name, he)
        return (name, False, f"http error: {str(he)}")
    except Exception as e:
        logger.exception("error calling %s: %s", name, e)
        return (name, False, f"exception: {e}")
