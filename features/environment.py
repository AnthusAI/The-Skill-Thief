import os
import shutil
from pathlib import Path

ROOT = Path.cwd()


def after_scenario(context, scenario):
    os.chdir(ROOT)
    if hasattr(context, "tmpdir"):
        shutil.rmtree(context.tmpdir, ignore_errors=True)
