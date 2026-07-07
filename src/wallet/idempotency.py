import hashlib

from .models import IdempotencyKey


def generate_request_hash(data):
    """
    Generate a consistent SHA256 hash from the request data.
    """
    return hashlib.sha256(str(sorted(data.items())).encode()).hexdigest()


def get_existing_request(idempotency_key):
    """
    Returns the stored idempotency record if it exists.
    """
    try:
        return IdempotencyKey.objects.get(key=idempotency_key)
    except IdempotencyKey.DoesNotExist:
        return None


def create_idempotency_record(
    key,
    request_hash,
    response_status,
    response_body,
):
    """
    Store the response so duplicate requests
    can return exactly the same result.
    """
    return IdempotencyKey.objects.create(
        key=key,
        request_hash=request_hash,
        response_status=response_status,
        response_body=response_body,
    )
