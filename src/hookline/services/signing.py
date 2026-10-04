"""HMAC-SHA256 signing of outbound webhook requests.

The signed message is ``f"{timestamp}.{body}"``, so receivers can reject replayed
requests by checking the timestamp. The signature header value has the form
``sha256=<hex digest>``.
"""

import hashlib
import hmac
import secrets

SIGNATURE_PREFIX = "sha256="
SECRET_BYTES = 32


def generate_secret() -> str:
    """Return a new random signing secret."""
    return secrets.token_urlsafe(SECRET_BYTES)


def sign_payload(secret: str, body: bytes, timestamp: int) -> str:
    """Return the signature header value for ``body`` sent at ``timestamp``."""
    message = f"{timestamp}.".encode() + body
    digest = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return f"{SIGNATURE_PREFIX}{digest}"


def verify_signature(secret: str, body: bytes, timestamp: int, signature: str) -> bool:
    """Check ``signature`` in constant time. Receivers can use this as a reference."""
    expected = sign_payload(secret, body, timestamp)
    return hmac.compare_digest(expected, signature)
