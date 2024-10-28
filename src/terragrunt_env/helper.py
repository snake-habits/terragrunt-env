import json
import os
import pathlib
import platform
import urllib.error
import urllib.request
from typing import List

import typer

TGENV_ROOT = pathlib.Path(__file__).parent
VERSIONS_DIR = pathlib.Path(TGENV_ROOT) / "versions"
VERSIONS_DIR.mkdir(exist_ok=True)

TGENV_ARCH = os.environ.get("TGENV_ARCH", "amd64")
_OS = platform.system().lower()
_SUFFIX = "" if _OS != "windows" else ".exe"
_BIN_FILE_NAME = f"terragrunt{_SUFFIX}"


def detect_arch() -> str:
    match platform.machine().lower():
        case "amd64" | "x86_64":
            return "amd64"
        case "aarch64" | "arm64":
            return "arm64"
        case "i386" | "i686":
            return "386"
        case _:
            return "amd64"


def parse_version(v: str) -> str:
    return v


def remove_version(version: str) -> None:
    version_dir = VERSIONS_DIR / version
    if version_dir.exists():
        (version_dir / "terragrunt").unlink(missing_ok=True)
        (version_dir / "terragrunt.exe").unlink(missing_ok=True)
        version_dir.rmdir()
        print(f"Terragrunt {version=} uninstalled.")
    else:
        print(f"There is no Terragrunt {version=}.")


def get_version(version: str = "latest") -> str | None:
    v = get_version_from_file()
    if v is None:
        v = check_remote_version(version)
    return parse_version(v)


def use_version(
    version: str = "latest", local: bool = True, installation: bool = False
) -> None:
    if installation:
        path = TGENV_ROOT / "version"
    elif local:
        path = pathlib.Path.cwd() / ".terragrunt-version"
    else:
        path = pathlib.Path.home() / ".terragrunt-version"

    save_version(path, version)


def save_version(path: pathlib.Path, version: str) -> None:
    with open(path, "w") as f:
        f.write(version)
        f.write("\n")


def get_version_from_file() -> str | None:
    path = get_version_file()
    if path:
        with open(path, "r") as f:
            return f.read().strip()
    return None


def get_version_file() -> pathlib.Path | None:
    local_version = pathlib.Path.cwd() / ".terragrunt-version"
    if local_version.exists():
        return local_version

    global_version = pathlib.Path.home() / ".terragrunt-version"
    if global_version.exists():
        return global_version

    recent_version = TGENV_ROOT / "version"
    if recent_version.exists():
        return recent_version

    return None


def is_version_installed(version: str) -> bool:
    return get_version_path(version).exists()


def get_version_path(version: str) -> pathlib.Path:
    return VERSIONS_DIR / version / _BIN_FILE_NAME


def check_remote_version(version: str) -> str | None:
    if version != "latest":
        version = f"v{version}"
    url = f"https://github.com/gruntwork-io/terragrunt/releases/{version}"
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return None
    return response.url.split("/")[-1][1:] if response.code == 200 else None


def get_remote_versions(limit: int = 10) -> List[str]:
    url = f"https://api.github.com/repos/gruntwork-io/terragrunt/tags?per_page={limit}"
    response = urllib.request.urlopen(url)

    data = json.loads(response.read())
    return [ver["name"].lstrip("v") for ver in data]


def download_version(version: str) -> pathlib.Path:
    _arch = detect_arch()
    url = f"https://github.com/gruntwork-io/terragrunt/releases/download/v{version}/terragrunt_{_OS}_{_arch}{_SUFFIX}"
    download_path = VERSIONS_DIR / version / _BIN_FILE_NAME
    try:
        urllib.request.urlretrieve(url, download_path)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"There is no Terragrunt {version=}.")
            raise typer.Exit(code=1)

    return download_path


def set_execution_permission(path: pathlib.Path) -> None:
    try:
        path.chmod(0o755)
    except PermissionError:
        print("Change rights failed.")
        raise typer.Exit(code=1)
