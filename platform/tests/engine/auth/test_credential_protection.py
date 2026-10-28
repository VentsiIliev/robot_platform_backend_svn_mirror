from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import stat
import tempfile
import unittest

from src.engine.auth.fernet_credential_protector import FernetCredentialProtector
from src.engine.auth.protected_file_key_provider import ProtectedFileKeyProvider
from src.shared_contracts.authorization.errors import (
    CredentialIntegrityError, ErrorCode, KeyIntegrityError, KeyMismatchError,
    KeyUnavailableError, UnsafeKeyStorageError,
)
from src.shared_contracts.authorization.results import Failure, Success


class CredentialProtectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / "secrets" / "operator.key"
        self.provider = ProtectedFileKeyProvider(self.path)

    def provision(self):
        result = self.provider.provision_new()
        self.assertIsInstance(result, Success)
        return FernetCredentialProtector(self.provider, key_fingerprint=result.value.fingerprint)

    def test_explicit_provisioning_sets_permissions_and_never_overwrites(self):
        first = self.provider.provision_new()
        before = self.path.read_bytes()
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.path.parent.stat().st_mode), 0o700)
        again = self.provider.provision_new()
        self.assertIsInstance(again, Failure)
        self.assertEqual(again.error.code, ErrorCode.ALREADY_EXISTS)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.provider.load_key().fingerprint, first.value.fingerprint)
        self.assertNotIn(before.strip().decode(), repr(self.provider.load_key()))

    def test_missing_key_load_never_creates_directory_or_key(self):
        with self.assertRaises(KeyUnavailableError):
            self.provider.load_key()
        self.assertFalse(self.path.parent.exists())

    def test_authenticated_unicode_roundtrip_uses_randomized_ciphertext(self):
        credentials = self.provision()
        secret = "парола with spaces 123"
        first = credentials.encrypt_operator_password(secret)
        second = credentials.encrypt_operator_password(secret)
        self.assertNotEqual(first, second)
        self.assertNotIn(secret.encode(), first)
        self.assertEqual(credentials.decrypt_operator_password(first), secret)

    def test_tampered_or_unrecognized_ciphertext_has_structured_integrity_failure(self):
        credentials = self.provision()
        encrypted = credentials.encrypt_operator_password("test secret")
        for value in (b"plain text", encrypted[:-5] + b"XXXXX", "not bytes"):
            with self.subTest(value_type=type(value)):
                with self.assertRaises(CredentialIntegrityError):
                    credentials.decrypt_operator_password(value)

    def test_key_loss_does_not_prevent_password_hashing_or_verification(self):
        credentials = self.provision()
        encoded = credentials.hash_password("test secret")
        ciphertext = credentials.encrypt_operator_password("operator secret")
        self.path.unlink()
        self.assertTrue(credentials.verify_password("test secret", encoded))
        with self.assertRaises(KeyUnavailableError):
            credentials.decrypt_operator_password(ciphertext)
        self.assertFalse(self.path.exists())

    def test_wrong_replacement_key_is_rejected_before_encrypting_or_decrypting(self):
        credentials = self.provision()
        ciphertext = credentials.encrypt_operator_password("operator secret")
        self.path.unlink()
        self.provider.provision_new()
        with self.assertRaises(KeyMismatchError):
            credentials.decrypt_operator_password(ciphertext)
        with self.assertRaises(KeyMismatchError):
            credentials.encrypt_operator_password("new secret")

    def test_corrupt_key_is_not_repaired_or_overwritten(self):
        self.provision()
        self.path.write_bytes(b"invalid-key")
        with self.assertRaises(KeyIntegrityError):
            self.provider.load_key()
        self.assertIsInstance(self.provider.provision_new(), Failure)
        self.assertEqual(self.path.read_bytes(), b"invalid-key")

    def test_insecure_key_or_directory_permissions_are_rejected_without_chmod(self):
        credentials = self.provision()
        self.path.chmod(0o644)
        with self.assertRaises(UnsafeKeyStorageError):
            credentials.encrypt_operator_password("secret")
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o644)
        self.path.chmod(0o600)
        self.path.parent.chmod(0o755)
        with self.assertRaises(UnsafeKeyStorageError):
            self.provider.load_key()

    def test_symlinks_and_nonregular_files_are_rejected(self):
        self.path.parent.mkdir(mode=0o700)
        elsewhere = self.root / "elsewhere"
        elsewhere.write_bytes(b"not a key")
        self.path.symlink_to(elsewhere)
        with self.assertRaises(UnsafeKeyStorageError):
            self.provider.load_key()
        self.path.unlink()
        os.mkfifo(self.path, mode=0o600)
        with self.assertRaises(UnsafeKeyStorageError):
            self.provider.load_key()
        directory_link = self.root / "linked"
        directory_link.symlink_to(self.path.parent, target_is_directory=True)
        with self.assertRaises(UnsafeKeyStorageError):
            ProtectedFileKeyProvider(directory_link / "operator.key").load_key()

    def test_read_only_private_key_is_supported(self):
        credentials = self.provision()
        self.path.chmod(0o400)
        self.assertEqual(credentials.decrypt_operator_password(credentials.encrypt_operator_password("secret")), "secret")

    def test_restore_original_backup_recovers_ciphertext_without_reencrypting(self):
        credentials = self.provision()
        original = self.path.read_bytes()
        ciphertext = credentials.encrypt_operator_password("operator secret")
        self.path.unlink()
        self.path.write_bytes(original)
        self.path.chmod(0o600)
        self.assertEqual(credentials.decrypt_operator_password(ciphertext), "operator secret")

    def test_key_must_be_explicitly_bound_to_database_fingerprint(self):
        self.provider.provision_new()
        credentials = FernetCredentialProtector(self.provider, key_fingerprint=None)
        with self.assertRaises(KeyUnavailableError):
            credentials.encrypt_operator_password("secret")

    def test_concurrent_provisioning_publishes_exactly_one_complete_key(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.provider.provision_new(), range(2)))
        successes = [result for result in results if isinstance(result, Success)]
        failures = [result for result in results if isinstance(result, Failure)]
        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 1)
        self.assertEqual(self.provider.load_key().fingerprint, successes[0].value.fingerprint)


if __name__ == "__main__":
    unittest.main()
