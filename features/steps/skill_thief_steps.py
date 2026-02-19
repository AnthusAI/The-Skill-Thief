import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from behave import given, when, then

ROOT = Path.cwd()


def run_cmd(cmd, cwd):
    return subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


@given("a clean workspace")
def step_clean_workspace(context):
    context.tmpdir = Path(tempfile.mkdtemp(prefix="skillthief-features-"))
    context.skills_dir = context.tmpdir / "skills"
    os.chdir(context.tmpdir)


@given("a config file with two skills")
def step_config_two_skills(context):
    make_skill_source(context, "alpha")
    make_skill_source(context, "beta", with_subdir=True)
    config = {
        "version": 1,
        "install_path": "./skills",
        "skills": [
            {"name": "alpha", "source": str(context.alpha_src)},
            {"name": "beta", "source": str(context.beta_src), "subdir": "sub/skill"},
        ],
    }
    write_yaml(context.tmpdir / ".skill-thief.yaml", config)


def write_yaml(path: Path, data):
    import yaml

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)


def make_skill_source(context, name: str, with_subdir: bool = False):
    src = context.tmpdir / f"src-{name}"
    src.mkdir(parents=True, exist_ok=True)
    skill_root = src
    if with_subdir:
        skill_root = src / "sub" / "skill"
        skill_root.mkdir(parents=True, exist_ok=True)
    (skill_root / "SKILL.md").write_text("""---
name: %s
description: test skill
---
Body
""" % name)
    setattr(context, f"{name}_src", src)


@given('skill "{name}" is installed')
def step_skill_installed(context, name):
    context.execute_steps(f"When I run \"skill-thief install {name}\"")


@given("no config file exists")
def step_no_config(context):
    cfg = context.tmpdir / ".skill-thief.yaml"
    if cfg.exists():
        cfg.unlink()


@given("an invalid config file")
def step_invalid_config(context):
    write_yaml(context.tmpdir / ".skill-thief.yaml", {"bad": "config"})


@given("config skill \"{name}\" points to a source missing SKILL.md")
def step_missing_skill_md(context, name):
    src = context.tmpdir / f"src-{name}-missing"
    src.mkdir(parents=True, exist_ok=True)
    context.missing_src = src
    config = {
        "version": 1,
        "install_path": "./skills",
        "skills": [{"name": name, "source": str(src)}],
    }
    write_yaml(context.tmpdir / ".skill-thief.yaml", config)


@given("a git repo source for \"{name}\"")
def step_git_repo(context, name):
    repo_dir = context.tmpdir / f"git-{name}"
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "SKILL.md").write_text("""---
name: %s
description: git skill
---
Body
""" % name)
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "add", "SKILL.md"], cwd=repo_dir, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir, check=True, stdout=subprocess.PIPE)
    config = {
        "version": 1,
        "install_path": "./skills",
        "skills": [{"name": name, "source": f"git+{repo_dir}"}],
    }
    write_yaml(context.tmpdir / ".skill-thief.yaml", config)


@when('I run "{cmd}"')
def step_run(context, cmd):
    import sys

    if cmd.startswith("skill-thief"):
        # Run via current Python to avoid PATH issues in test env
        parts = cmd.split(" ", 1)
        rest = parts[1] if len(parts) > 1 else ""
        cmd = f'"{sys.executable}" -m skill_thief.cli {rest}'.strip()
    result = run_cmd(cmd, cwd=context.tmpdir)
    context.last_result = result


@then('skill "{name}" should be installed')
def step_skill_installed_check(context, name):
    path = context.skills_dir / name
    assert path.exists(), f"Skill {name} not installed"


@then('skill "{name}" should not be installed')
def step_skill_not_installed(context, name):
    path = context.skills_dir / name
    assert not path.exists(), f"Skill {name} should not be installed"


@then('SKILL.md for "{name}" should have name "{expected}"')
def step_skill_md_name(context, name, expected):
    path = context.skills_dir / name / "SKILL.md"
    assert path.exists(), "SKILL.md missing"
    content = path.read_text()
    assert f"name: {expected}" in content


@then("the output should contain \"{text}\"")
def step_output_contains(context, text):
    output = context.last_result.stdout + context.last_result.stderr
    assert text in output, f"Output did not contain {text}"


@then("the command should fail")
def step_command_fail(context):
    assert context.last_result.returncode != 0
