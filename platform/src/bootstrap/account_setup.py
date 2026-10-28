"""Explicit fresh account-store setup; never run as a login-error fallback."""
import argparse
from pathlib import Path
import sys


def main(argv=None, *, defaults=None):
    parser = argparse.ArgumentParser(description="Initialize a fresh platform account installation")
    for flag, name in (("--database", "database"), ("--state", "state"), ("--operator-key", "operator_key")):
        parser.add_argument(flag, required=defaults is None, type=Path,
                            default=getattr(defaults, name, None))
    args = parser.parse_args(argv)
    if not all(path.is_absolute() for path in (args.database, args.state, args.operator_key)):
        print("Specify absolute database, state, and private key paths.", file=sys.stderr)
        return 2
    if not __package__:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.engine.auth.account_installation import AccountInstallation, AccountInstallationPaths
    from src.shared_contracts.authorization.errors import ServiceException
    from src.shared_contracts.authorization.results import Failure

    try:
        installation = AccountInstallation(AccountInstallationPaths(args.database, args.state, args.operator_key))
        result = installation.initialize_new()
        if isinstance(result, Failure):
            print(f"Setup refused: {result.error.code.value}; {result.error.message_key}; "
                  f"reference {result.error.correlation_id}.", file=sys.stderr)
            return 2
        print(f"Account installation ready: {result.value.installation_id}.")
        print("Provision Manufacturer access and complete first-Admin setup before handover.")
        return 0
    except ServiceException as exc:
        print(f"Setup failed: {exc.error.code.value}; reference {exc.error.correlation_id}.", file=sys.stderr)
        return 4
    except ValueError:
        print("Use distinct database/state paths and a separate private key directory.", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Setup cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
