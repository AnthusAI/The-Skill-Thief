from __future__ import annotations

import os
import subprocess
import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config, ConfigError
from .install import install_all, InstallError
from .validate import validate_skill_dir

app = typer.Typer(help="Install and update Agent Skills from git or local paths")
console = Console()


def _load_config_or_exit() -> "Config":
    try:
        return load_config(os.getcwd())
    except ConfigError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=1)


def _run_skills_ref(path: str) -> List[str]:
    """Invoke skills-ref if available; return warnings."""
    try:
        subprocess.run(["skills-ref", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    try:
        result = subprocess.run(["skills-ref", "validate", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            return [result.stderr.decode("utf-8") or result.stdout.decode("utf-8") or "skills-ref validation failed"]
        return []
    except Exception as exc:  # pragma: no cover
        return [f"skills-ref validation error: {exc}"]


@app.command()
def install(name: Optional[List[str]] = typer.Argument(None, help="Skill names to install (default: all)")):
    """Install skills from config."""
    config = _load_config_or_exit()
    try:
        results = install_all(config, names=name)
    except InstallError as exc:
        console.print(f"[red]Install error:[/red] {exc}")
        raise typer.Exit(code=1)

    for skill_name, warnings in results:
        path = os.path.join(config.install_path, skill_name)
        warnings += _run_skills_ref(path)
        if warnings:
            console.print(f"[yellow]{skill_name} installed with warnings:[/yellow]")
            for w in warnings:
                console.print(f" - {w}")
        else:
            console.print(f"[green]{skill_name} installed successfully[/green]")


@app.command()
def update(name: Optional[List[str]] = typer.Argument(None, help="Skill names to update (default: all)")):
    """Update skills (same as install but overwrites)."""
    install(name)


@app.command()
def list():  # type: ignore[override]
    """List configured skills and status."""
    config = _load_config_or_exit()
    table = Table(title="Skills")
    table.add_column("Name")
    table.add_column("Source")
    table.add_column("Ref")
    table.add_column("Install Path")
    table.add_column("Status")

    for skill in config.skills:
        target = os.path.join(config.install_path, skill.name)
        exists = os.path.isdir(target)
        warnings = validate_skill_dir(target, skill.name) if exists else ["not installed"]
        status = "ok" if exists and not warnings else "; ".join(warnings)
        table.add_row(skill.name, skill.source, skill.ref or "", target, status)

    console.print(table)


if __name__ == "__main__":
    app()
