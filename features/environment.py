import os
import shutil
from pathlib import Path

ROOT = Path.cwd()


def before_all(context):
    # Ensure coverage picks up subprocesses
    if os.getenv("COVERAGE_PROCESS_START"):
        os.environ["COVERAGE_PROCESS_START"] = os.getenv("COVERAGE_PROCESS_START")
    # Make src importable when running Behave via coverage
    os.environ.setdefault("PYTHONPATH", str(ROOT))


def after_scenario(context, scenario):
    os.chdir(ROOT)
    if hasattr(context, "tmpdir"):
        shutil.rmtree(context.tmpdir, ignore_errors=True)
