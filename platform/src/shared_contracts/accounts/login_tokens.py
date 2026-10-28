from dataclasses import dataclass, field


@dataclass(frozen=True)
class IssueLoginToken:
    account_id: str
    expected_revision: int


@dataclass(frozen=True)
class IssuedLoginToken:
    account_id: str
    payload: str = field(repr=False)
