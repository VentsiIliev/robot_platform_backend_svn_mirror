"""Bounded SVN feed reads using the station user's existing SVN authentication."""
import subprocess
import tempfile
import threading

from .environment import subprocess_environment


def fetch(config, url, target, limit):
    if config.token_file is not None:
        raise ValueError('SVN sources use cached SVN credentials, not token_file')
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(['svn', 'cat', '--non-interactive', url], stdout=subprocess.PIPE,
                                   stderr=errors, env=subprocess_environment())
        expired = threading.Event()

        def timeout():
            expired.set()
            if process.poll() is None:
                process.kill()

        timer = threading.Timer(config.timeout_seconds, timeout)
        timer.daemon = True
        timer.start()
        try:
            total = 0
            with target.open('wb') as output:
                while chunk := process.stdout.read(1024 * 1024):
                    total += len(chunk)
                    if total > limit:
                        raise ValueError('Update download limit exceeded')
                    output.write(chunk)
            code = process.wait()
            if expired.is_set():
                raise TimeoutError('SVN update download timed out')
            if code:
                errors.seek(0)
                reason = errors.read(2048).decode(errors='replace').strip()
                raise ValueError('SVN update download failed: ' + reason)
        finally:
            timer.cancel()
            if process.poll() is None:
                process.kill()
            process.wait()
            process.stdout.close()
