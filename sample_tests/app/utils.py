def normalize_email(email: str) -> str:
    """Normalize email by stripping and lowercasing."""
    if not isinstance(email, str):
        raise TypeError("email must be a string")
    return email.strip().lower()


def safe_div(a, b):
    """Return a/b but return None if b is zero."""
    if b == 0:
        return None
    return a / b
