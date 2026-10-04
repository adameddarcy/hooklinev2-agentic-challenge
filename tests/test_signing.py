import hashlib
import hmac

from hookline.services.signing import (
    SIGNATURE_PREFIX,
    generate_secret,
    sign_payload,
    verify_signature,
)

SECRET = "whsec_test"
BODY = b'{"id":"evt_1","payload":{},"type":"ping"}'
TIMESTAMP = 1_700_000_000


def test_signature_matches_documented_scheme() -> None:
    expected = hmac.new(
        SECRET.encode(), f"{TIMESTAMP}.".encode() + BODY, hashlib.sha256
    ).hexdigest()
    assert sign_payload(SECRET, BODY, TIMESTAMP) == f"sha256={expected}"


def test_signature_is_deterministic() -> None:
    assert sign_payload(SECRET, BODY, TIMESTAMP) == sign_payload(SECRET, BODY, TIMESTAMP)


def test_verify_accepts_valid_signature() -> None:
    signature = sign_payload(SECRET, BODY, TIMESTAMP)
    assert verify_signature(SECRET, BODY, TIMESTAMP, signature)


def test_verify_rejects_tampered_body() -> None:
    signature = sign_payload(SECRET, BODY, TIMESTAMP)
    assert not verify_signature(SECRET, BODY + b" ", TIMESTAMP, signature)


def test_verify_rejects_different_timestamp() -> None:
    signature = sign_payload(SECRET, BODY, TIMESTAMP)
    assert not verify_signature(SECRET, BODY, TIMESTAMP + 1, signature)


def test_verify_rejects_wrong_secret() -> None:
    signature = sign_payload(SECRET, BODY, TIMESTAMP)
    assert not verify_signature("other", BODY, TIMESTAMP, signature)


def test_generate_secret_is_random_and_long() -> None:
    first, second = generate_secret(), generate_secret()
    assert first != second
    assert len(first) >= 40
    assert not first.startswith(SIGNATURE_PREFIX)
