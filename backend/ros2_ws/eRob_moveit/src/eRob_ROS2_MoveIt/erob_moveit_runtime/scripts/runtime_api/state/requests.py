"""State queries have no mutable body; identifiers are validated before gateway calls."""


def plan_identifier(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError('plan_id must be a non-empty string of at most 256 characters')
    return value
