import shutil

import pytest

from terragrunt_env.helper import TGENV_ROOT, VERSIONS_DIR


@pytest.fixture(scope="session", autouse=True)
def clean_up():
    yield
    (TGENV_ROOT / "version").unlink(missing_ok=True)
    shutil.rmtree(VERSIONS_DIR)
