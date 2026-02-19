# Agent Guide: The Skill Thief

Minimal, token-efficient instructions for agents working in this repo.

## Quick Start
- Create venv: `python3 -m venv .venv && source .venv/bin/activate`
- Install deps + Behave: `pip install -e '.[dev]'`
- Run specs (required, 100% coverage): `behave`

## What the tool does
- CLI `skill-thief` installs/updates skills defined in `.skill-thief.yaml` (project root only).
- Default install path if omitted: `./skills`.
- Supports git URLs (git+https/ssh) and local paths; optional `ref` (branch/tag/commit) and `subdir`.
- Validation: warns if `SKILL.md` missing/invalid; runs `skills-ref validate` if available, otherwise internal checks.

## Key Commands
- Install all or named: `skill-thief install [name ...]`
- Update (same as install): `skill-thief update [name ...]`
- List status: `skill-thief list`

## Config schema (.skill-thief.yaml)
```yaml
version: 1
install_path: ./skills  # optional; defaults to ./skills
skills:
  - name: alpha
    source: git+https://example.com/repo.git
    ref: main          # optional
    subdir: skills/a   # optional
```

## Behave BDD
- Features: `features/skill_thief.feature`
- Steps: `features/steps/skill_thief_steps.py`
- Behave uses the current Python to invoke the CLI module directly; no PATH fiddling needed.
- Keep new behaviors covered with scenarios; failing to add a scenario breaks "100% spec coverage" policy.

## CI
- GitHub Actions matrix Python 3.9–3.12 runs `python -m behave` (see `.github/workflows/ci.yml`).

## File Map
- CLI + logic: `src/skill_thief/cli.py`, `config.py`, `install.py`, `gitutils.py`, `validate.py`
- Docs: `README.md`
- License: `LICENSE`

## Release
- Build: `python -m build`
- Publish: `twine upload dist/*` (requires creds)
