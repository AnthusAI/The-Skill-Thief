from __future__ import annotations

import os
import yaml
from dataclasses import dataclass
from typing import List, Optional

DEFAULT_INSTALL_PATH = "./skills"
CONFIG_FILENAME = ".skill-thief.yaml"

class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""

@dataclass
class SkillEntry:
    name: str
    source: str
    ref: Optional[str] = None
    subdir: Optional[str] = None

@dataclass
class Config:
    version: int
    install_path: str
    skills: List[SkillEntry]

    @property
    def install_abs(self) -> str:
        return os.path.abspath(self.install_path)


def load_config(cwd: str = ".") -> Config:
    path = os.path.join(cwd, CONFIG_FILENAME)
    if not os.path.exists(path):
        raise ConfigError(f"Config file {CONFIG_FILENAME} not found in {os.path.abspath(cwd)}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Config root must be a mapping")

    version = data.get("version")
    if version is None:
        raise ConfigError("Config must include version")
    if version != 1:
        raise ConfigError("Unsupported config version; expected 1")

    install_path = data.get("install_path", DEFAULT_INSTALL_PATH)
    if not isinstance(install_path, str) or not install_path:
        raise ConfigError("install_path must be a non-empty string")

    skills_raw = data.get("skills")
    if not isinstance(skills_raw, list) or not skills_raw:
        raise ConfigError("skills must be a non-empty list")

    skills: List[SkillEntry] = []
    for idx, item in enumerate(skills_raw):
        if not isinstance(item, dict):
            raise ConfigError(f"skills[{idx}] must be a mapping")
        name = item.get("name")
        source = item.get("source")
        ref = item.get("ref")
        subdir = item.get("subdir")
        if not isinstance(name, str) or not name:
            raise ConfigError(f"skills[{idx}].name must be a non-empty string")
        if not isinstance(source, str) or not source:
            raise ConfigError(f"skills[{idx}].source must be a non-empty string")
        if ref is not None and not isinstance(ref, str):
            raise ConfigError(f"skills[{idx}].ref must be a string if set")
        if subdir is not None and not isinstance(subdir, str):
            raise ConfigError(f"skills[{idx}].subdir must be a string if set")
        skills.append(SkillEntry(name=name, source=source, ref=ref, subdir=subdir))

    return Config(version=version, install_path=install_path, skills=skills)
