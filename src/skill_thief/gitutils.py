from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Optional

class GitError(Exception):
    """Raised when git operations fail."""


def is_git_url(url: str) -> bool:
    return url.startswith("git+") or url.endswith(".git") or url.startswith("ssh://") or url.startswith("git@")


def clone_to_temp(source: str, ref: Optional[str] = None) -> str:  # pragma: no cover
    # Remove leading git+ if present
    clone_url = source[4:] if source.startswith("git+") else source
    tmpdir = tempfile.mkdtemp(prefix="skillthief-")
    try:
        shallow = not (ref and is_commit_hash(ref))
        cmd = ["git", "clone"]
        if shallow:
            cmd += ["--depth", "1"]
        if ref and shallow:
            cmd += ["--branch", ref]
        cmd += [clone_url, tmpdir]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ref and is_commit_hash(ref):
            subprocess.run(["git", "checkout", ref], cwd=tmpdir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise GitError(exc.stderr.decode("utf-8", errors="ignore")) from exc
    return tmpdir


def is_commit_hash(ref: str) -> bool:  # pragma: no cover
    return len(ref) == 40 and all(c in "0123456789abcdef" for c in ref.lower())
