from __future__ import annotations

import os
import re
from typing import Tuple, List

import yaml

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

class ValidationWarning(Exception):
    """Non-fatal validation issue."""


def validate_skill_dir(path: str, expected_name: str) -> List[str]:
    """Return list of warning messages."""
    warnings: List[str] = []
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md):
        return ["Missing SKILL.md in skill root"]

    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        return [f"Failed to read SKILL.md: {exc}"]

    frontmatter, err = _extract_frontmatter(content)
    if err:
        warnings.append(err)
    else:
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not name:
            warnings.append("SKILL.md frontmatter missing name")
        if not description:
            warnings.append("SKILL.md frontmatter missing description")
        if name and not NAME_RE.match(name):
            warnings.append("Skill name in frontmatter violates naming rules")
        if name and expected_name and name != expected_name:
            warnings.append("Skill name in frontmatter does not match directory name")
    return warnings


def _extract_frontmatter(text: str) -> Tuple[dict, str | None]:
    if not text.startswith("---\n"):
        return {}, "SKILL.md missing YAML frontmatter"
    try:
        end = text.find("\n---", 4)
        if end == -1:
            return {}, "SKILL.md frontmatter not closed"
        raw = text[4:end]
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict):
            return {}, "SKILL.md frontmatter must be a mapping"
        return data, None
    except yaml.YAMLError as exc:
        return {}, f"Failed to parse SKILL.md frontmatter: {exc}"
