from __future__ import annotations

import os
import shutil
import tempfile
from typing import List, Optional

from .config import Config, SkillEntry
from .gitutils import is_git_url, clone_to_temp
from .validate import validate_skill_dir

class InstallError(Exception):
    pass


def install_all(config: Config, names: Optional[List[str]] = None) -> List[tuple[str, List[str]]]:
    results = []
    selected = {n for n in names} if names else None
    for skill in config.skills:
        if selected and skill.name not in selected:
            continue
        warnings = _install_skill(config.install_path, skill)
        results.append((skill.name, warnings))
    return results


def _install_skill(base_path: str, skill: SkillEntry) -> List[str]:
    target_dir = os.path.join(base_path, skill.name)
    os.makedirs(base_path, exist_ok=True)
    tmpdir = None
    try:
        if is_git_url(skill.source):
            tmpdir = clone_to_temp(skill.source, skill.ref)
            src_root = tmpdir
        else:
            src_root = os.path.abspath(skill.source)
            if not os.path.exists(src_root):
                raise InstallError(f"Local source does not exist: {skill.source}")
        src_path = os.path.join(src_root, skill.subdir) if skill.subdir else src_root
        if not os.path.exists(src_path):
            raise InstallError(f"Subdir not found: {skill.subdir or '.'}")
        # Replace target
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(src_path, target_dir)
        warnings = validate_skill_dir(target_dir, skill.name)
        return warnings
    finally:
        if tmpdir and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)
