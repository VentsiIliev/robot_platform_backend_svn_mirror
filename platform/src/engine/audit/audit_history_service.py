from src.engine.audit.i_audit_history_service import IAuditHistoryService
from src.engine.auth.account_operation_runner import AccountOperationRunner
from src.engine.auth.account_store import IAccountStore
from src.engine.auth.i_access_policy import IAccessPolicy
from src.engine.auth.i_session_service import ISessionService
from src.shared_contracts.accounts.events import HistoryQuery
from src.shared_contracts.authorization.actions import AuditAction
from src.shared_contracts.authorization.access import ResourceRef
from src.shared_contracts.authorization.errors import ErrorCode
from src.shared_contracts.authorization.results import Success


class AuditHistoryService(IAuditHistoryService):
    def __init__(self, store: IAccountStore, session: ISessionService, policy: IAccessPolicy) -> None:
        self._operations = AccountOperationRunner(store, session, policy)

    def list_events(self, query: HistoryQuery):
        if (not isinstance(query.target_id, str) or not query.target_id
                or type(query.limit) is not int or not 1 <= query.limit <= 500
                or type(query.offset) is not int or query.offset < 0):
            return self._operations.failure(ErrorCode.INVALID_INPUT)
        def read(transaction, actor, target):
            return Success(transaction.history(query))
        return self._operations.execute(AuditAction.VIEW, ResourceRef("account_history", query.target_id), None, read)
