"""Interactive OS-root maintenance for the new SQLite account backend.

    python -m src.bootstrap.account_maintenance --help

Production invocation must use trusted installed code/interpreter. See
docs/engine/auth/account_recovery_runbook.md for authority and recovery procedures.
"""
import argparse
import getpass
from pathlib import Path
import sys
import warnings


def _numeric_login(value):
    if not value.isdigit():
        raise argparse.ArgumentTypeError("Manufacturer login ID must be numeric for the platform login form")
    return value


def _parser():
    parser = argparse.ArgumentParser(description="OS-authorized Manufacturer account maintenance")
    parser.add_argument("--database", required=True, type=Path,
                        help="Absolute path to an initialized SQLite account database")
    commands = parser.add_subparsers(dest="action", required=True)
    inspect = commands.add_parser("inspect-manufacturer", help="Inspect a Manufacturer account without secrets")
    inspect.add_argument("--login-id", required=True)
    reset = commands.add_parser("reset-manufacturer", help="Set a new Manufacturer password")
    reset.add_argument("--login-id", required=True)
    create = commands.add_parser("create-manufacturer", help="Provision a Manufacturer account")
    create.add_argument("--login-id", required=True, type=_numeric_login)
    create.add_argument("--first-name", required=True)
    create.add_argument("--last-name", required=True)
    create.add_argument("--email", default="")
    return parser


def _read_password():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError("Password changes require an interactive terminal.")
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        first = getpass.getpass("New password: ")
        second = getpass.getpass("Confirm new password: ")
    if not first or first != second:
        raise ValueError("Passwords must be nonempty and match.")
    return first


def main(argv=None):
    args = _parser().parse_args(argv)
    # Direct execution with a trusted installed Python -I also works. Only add
    # the root of this trusted installation, never a caller-supplied search path.
    if not __package__:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.engine.auth.unix_maintenance_authority import UnixMaintenanceAuthority
    from src.shared_contracts.authorization.errors import ServiceException
    from src.shared_contracts.authorization.results import Failure

    authority = UnixMaintenanceAuthority()
    ownership = None
    try:
        authorized = authority.current_actor()
        if isinstance(authorized, Failure):
            print("OS administrator authorization is required.", file=sys.stderr)
            return 3
        if not args.database.is_absolute() or not args.database.is_file():
            print("Specify an absolute path to an existing account database.", file=sys.stderr)
            return 2
        from src.engine.auth.account_maintenance_service import AccountMaintenanceService
        from src.engine.auth.password_hasher import ScryptPasswordHasher
        from src.engine.auth.sqlite_account_store import SQLiteAccountStore
        from src.shared_contracts.accounts.maintenance import CreateManufacturer, ResetManufacturerPassword
        from src.engine.auth.account_runtime_lock import AccountRuntimeLock

        if args.action != "inspect-manufacturer":
            ownership = AccountRuntimeLock.acquire(args.database)

        service = AccountMaintenanceService(SQLiteAccountStore(args.database), authority, ScryptPasswordHasher())
        if args.action in ("inspect-manufacturer", "reset-manufacturer"):
            target = service.inspect_manufacturer(args.login_id)
            if isinstance(target, Failure):
                return _report_failure(target)
            summary = target.value
            print(f"Manufacturer login: {summary.login_id}; account: {summary.account_id}; "
                  f"revision: {summary.revision}; enabled: {summary.enabled}")
            if args.action == "inspect-manufacturer":
                return 0
            result = service.reset_manufacturer_password(ResetManufacturerPassword(
                summary.account_id, summary.revision, _read_password(),
            ))
        else:
            result = service.create_manufacturer(CreateManufacturer(
                args.login_id, args.first_name, args.last_name, _read_password(), args.email,
            ))
        if isinstance(result, Failure):
            return _report_failure(result)
        print("Manufacturer account updated and audit committed. Log in through the platform normally.")
        return 0
    except ServiceException as exc:
        print(f"Maintenance failed: {exc.error.code.value}; reference {exc.error.correlation_id}.", file=sys.stderr)
        return 2 if exc.error.code.value == "busy" else 4
    except (ValueError, EOFError, getpass.GetPassWarning) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Maintenance cancelled.", file=sys.stderr)
        return 130
    finally:
        if ownership is not None:
            ownership.close()


def _report_failure(result):
    print(f"Maintenance refused: {result.error.code.value}; {result.error.message_key}; "
          f"reference {result.error.correlation_id}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
