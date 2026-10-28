"""SQLite backend with account/credential/audit consistency in one transaction."""
from contextlib import contextmanager
from dataclasses import asdict
import json
import os
from pathlib import Path
import sqlite3
from uuid import uuid4

from src.engine.auth.account_store import (
    IAccountStore, IAccountTransaction, RecoveryAttempts, RecoveryVerifier, StoredAccount,
)
from src.shared_contracts.accounts.events import AuditEvent, FieldChange, HistoryQuery
from src.shared_contracts.accounts.maintenance import OperatingSystemActor
from src.shared_contracts.accounts.records import AccountSummary
from src.shared_contracts.authorization.errors import (
    AuditPersistenceError, ServiceUnavailableError, StorageIntegrityError,
)

_SCHEMA = (
    "CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    """CREATE TABLE accounts (
        account_id TEXT PRIMARY KEY, login_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL, last_name TEXT NOT NULL, role TEXT NOT NULL,
        email TEXT NOT NULL, enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
        revision INTEGER NOT NULL CHECK(revision > 0),
        created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)""",
    """CREATE TABLE credentials (
        account_id TEXT PRIMARY KEY REFERENCES accounts(account_id) ON DELETE CASCADE,
        version INTEGER NOT NULL CHECK(version > 0),
        password_hash TEXT NOT NULL, operator_ciphertext BLOB)""",
    """CREATE TABLE audit_events (
        sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE NOT NULL,
        target_id TEXT NOT NULL, payload TEXT NOT NULL)""",
    "CREATE INDEX audit_target ON audit_events(target_id, sequence)",
    "CREATE TABLE permissions (app_id TEXT PRIMARY KEY, roles TEXT NOT NULL)",
    """CREATE TABLE recovery_codes (
        account_id TEXT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
        credential_version INTEGER NOT NULL CHECK(credential_version > 0),
        digest TEXT NOT NULL, PRIMARY KEY(account_id, digest))""",
    """CREATE TABLE recovery_attempts (
        key TEXT PRIMARY KEY, failures INTEGER NOT NULL CHECK(failures >= 0),
        window_started REAL NOT NULL)""",
    """CREATE TABLE login_tokens (
        account_id TEXT PRIMARY KEY REFERENCES accounts(account_id) ON DELETE CASCADE,
        digest TEXT UNIQUE NOT NULL, credential_version INTEGER NOT NULL)""",
    """CREATE TABLE authentication_attempts (
        key TEXT PRIMARY KEY, failures INTEGER NOT NULL CHECK(failures >= 0),
        window_started REAL NOT NULL)""",
    """CREATE TRIGGER preserve_audit_updates BEFORE UPDATE ON audit_events
        BEGIN SELECT RAISE(ABORT, 'Audit history is append-only'); END""",
    """CREATE TRIGGER preserve_audit_deletes BEFORE DELETE ON audit_events
        BEGIN SELECT RAISE(ABORT, 'Audit history is append-only'); END""",
)


class SQLiteAccountStore(IAccountStore):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path).absolute()
        with self.transaction() as transaction:
            if transaction.metadata("schema_version") != "1":
                raise StorageIntegrityError()

    @classmethod
    def initialize(cls, path: str | Path) -> "SQLiteAccountStore":
        """Explicit commissioning/migration only; never replace an existing file."""
        path = Path(path).absolute()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
        except FileExistsError as exc:
            raise StorageIntegrityError() from exc
        except OSError as exc:
            raise ServiceUnavailableError() from exc
        connection = None
        try:
            connection = sqlite3.connect(str(path), isolation_level=None)
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("BEGIN IMMEDIATE")
            for statement in _SCHEMA:
                connection.execute(statement)
            connection.execute("INSERT INTO metadata VALUES ('schema_version', '1')")
            connection.execute("INSERT INTO metadata VALUES ('commissioned', '0')")
            connection.execute("INSERT INTO metadata VALUES ('installation_id', ?)", (uuid4().hex,))
            connection.commit()
        except sqlite3.Error as exc:
            if connection is not None:
                connection.rollback()
            raise StorageIntegrityError() from exc
        finally:
            if connection is not None:
                connection.close()
        return cls(path)

    @contextmanager
    def transaction(self):
        connection = None
        try:
            # mode=rw prevents accidental first-run setup after database loss.
            connection = sqlite3.connect(self._path.as_uri() + "?mode=rw", uri=True,
                                         isolation_level=None, timeout=5)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("BEGIN IMMEDIATE")
            yield SQLiteAccountTransaction(connection)
            connection.commit()
        except sqlite3.OperationalError as exc:
            if connection is not None:
                connection.rollback()
            if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                raise ServiceUnavailableError() from exc
            raise StorageIntegrityError() from exc
        except sqlite3.DatabaseError as exc:
            if connection is not None:
                connection.rollback()
            raise StorageIntegrityError() from exc
        except BaseException:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if connection is not None:
                connection.close()


class SQLiteAccountTransaction(IAccountTransaction):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def _select(self, where="", parameters=()) -> tuple[StoredAccount, ...]:
        rows = self._connection.execute(
            """SELECT a.*, c.version, c.password_hash, c.operator_ciphertext
               FROM accounts a LEFT JOIN credentials c USING(account_id) """ + where,
            parameters,
        )
        rows = tuple(rows)
        if any(row["version"] is None or row["password_hash"] is None for row in rows):
            raise StorageIntegrityError()
        return tuple(StoredAccount(
            AccountSummary(*(row[name] if name != "enabled" else bool(row[name])
                             for name in AccountSummary.__dataclass_fields__)),
            row["version"], row["password_hash"], row["operator_ciphertext"],
        ) for row in rows)

    def get(self, account_id):
        accounts = self._select("WHERE a.account_id=?", (account_id,))
        return accounts[0] if accounts else None

    def get_by_login(self, login_id):
        accounts = self._select("WHERE a.login_id=?", (login_id,))
        return accounts[0] if accounts else None

    def list_accounts(self):
        return self._select("ORDER BY a.login_id")

    def insert(self, account):
        data = asdict(account.summary)
        names = tuple(data)
        self._connection.execute(
            f"INSERT INTO accounts ({','.join(names)}) VALUES ({','.join('?' for _ in names)})",
            tuple(data.values()),
        )
        self._connection.execute("INSERT INTO credentials VALUES (?, ?, ?, ?)", (
            account.summary.account_id, account.credential_version, account.password_hash,
            account.operator_ciphertext,
        ))

    def replace(self, account):
        data = asdict(account.summary)
        identity = data.pop("account_id")
        self._connection.execute(
            f"UPDATE accounts SET {','.join(name + '=?' for name in data)} WHERE account_id=?",
            (*data.values(), identity),
        )
        self._connection.execute(
            "UPDATE credentials SET version=?, password_hash=?, operator_ciphertext=? WHERE account_id=?",
            (account.credential_version, account.password_hash, account.operator_ciphertext, identity),
        )

    def delete(self, account_id):
        self._connection.execute("DELETE FROM accounts WHERE account_id=?", (account_id,))

    def append_event(self, event):
        try:
            self._connection.execute("INSERT INTO audit_events(event_id,target_id,payload) VALUES (?,?,?)",
                                     (event.event_id, event.target_id, json.dumps(asdict(event))))
        except sqlite3.Error as exc:
            raise AuditPersistenceError() from exc

    def history(self, query):
        if not 1 <= query.limit <= 500 or query.offset < 0:
            raise ValueError("Invalid history page bounds")
        rows = self._connection.execute(
            "SELECT payload FROM audit_events WHERE target_id=? ORDER BY sequence DESC LIMIT ? OFFSET ?",
            (query.target_id, query.limit, query.offset),
        )
        try:
            result = []
            for row in rows:
                data = json.loads(row[0])
                data["changes"] = tuple(FieldChange(**change) for change in data["changes"])
                if data.get("os_actor") is not None:
                    data["os_actor"] = OperatingSystemActor(**data["os_actor"])
                result.append(AuditEvent(**data))
            return tuple(result)
        except (ValueError, KeyError, TypeError) as exc:
            raise StorageIntegrityError() from exc

    def metadata(self, key):
        row = self._connection.execute("SELECT value FROM metadata WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def set_metadata(self, key, value):
        self._connection.execute("INSERT INTO metadata VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?",
                                 (key, value, value))

    def read_permissions(self):
        try:
            result = {}
            for row in self._connection.execute("SELECT app_id,roles FROM permissions"):
                roles = json.loads(row["roles"])
                if not isinstance(roles, list) or any(not isinstance(role, str) or not role for role in roles):
                    raise ValueError("Invalid persisted role grants")
                result[row["app_id"]] = tuple(roles)
            return result
        except (ValueError, TypeError) as exc:
            raise StorageIntegrityError() from exc

    def write_permissions(self, app_id, roles):
        self._connection.execute("INSERT INTO permissions VALUES (?,?) ON CONFLICT(app_id) DO UPDATE SET roles=?",
                                 (app_id, json.dumps(roles), json.dumps(roles)))

    def recovery_verifiers(self, account_id):
        rows = self._connection.execute(
            "SELECT credential_version,digest FROM recovery_codes WHERE account_id=? ORDER BY digest", (account_id,),
        )
        verifiers = tuple(RecoveryVerifier(row[0], row[1]) for row in rows)
        if any(type(v.credential_version) is not int or v.credential_version < 1
               or not isinstance(v.digest, str) or len(v.digest) != 64
               or any(character not in "0123456789abcdef" for character in v.digest) for v in verifiers):
            raise StorageIntegrityError()
        return verifiers

    def replace_recovery_verifiers(self, account_id, verifiers):
        self._connection.execute("DELETE FROM recovery_codes WHERE account_id=?", (account_id,))
        self._connection.executemany("INSERT INTO recovery_codes VALUES (?,?,?)", (
            (account_id, verifier.credential_version, verifier.digest) for verifier in verifiers
        ))

    def recovery_attempts(self, key):
        row = self._connection.execute("SELECT failures,window_started FROM recovery_attempts WHERE key=?",
                                       (key,)).fetchone()
        return RecoveryAttempts(row[0], row[1]) if row else None

    def set_recovery_attempts(self, key, state):
        self._connection.execute(
            """INSERT INTO recovery_attempts VALUES (?,?,?) ON CONFLICT(key)
               DO UPDATE SET failures=excluded.failures, window_started=excluded.window_started""",
            (key, state.failures, state.window_started),
        )

    def prune_recovery_attempts(self, older_than):
        self._connection.execute("DELETE FROM recovery_attempts WHERE window_started<=?", (older_than,))

    def replace_login_token(self, account_id, digest, credential_version):
        self._connection.execute(
            """INSERT INTO login_tokens VALUES (?,?,?) ON CONFLICT(account_id)
               DO UPDATE SET digest=excluded.digest, credential_version=excluded.credential_version""",
            (account_id, digest, credential_version),
        )

    def account_for_login_token(self, digest):
        row = self._connection.execute("SELECT account_id,credential_version FROM login_tokens WHERE digest=?", (digest,)).fetchone()
        if row is None:
            return None
        account = self.get(row[0])
        return account if account and account.credential_version == row[1] else None

    def authentication_attempts(self, key):
        row = self._connection.execute("SELECT failures,window_started FROM authentication_attempts WHERE key=?", (key,)).fetchone()
        return RecoveryAttempts(row[0], row[1]) if row else None

    def set_authentication_attempts(self, key, state):
        self._connection.execute(
            """INSERT INTO authentication_attempts VALUES (?,?,?) ON CONFLICT(key)
               DO UPDATE SET failures=excluded.failures, window_started=excluded.window_started""",
            (key, state.failures, state.window_started),
        )

    def prune_authentication_attempts(self, older_than):
        self._connection.execute("DELETE FROM authentication_attempts WHERE window_started<=?", (older_than,))
