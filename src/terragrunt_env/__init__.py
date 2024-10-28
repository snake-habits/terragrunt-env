import subprocess
import sys
from typing import Optional

import typer

from .helper import (VERSIONS_DIR, check_remote_version, download_version,
                     get_remote_versions, get_version, get_version_from_file,
                     get_version_path, is_version_installed, remove_version,
                     set_execution_permission, use_version)
from .version import Version

app = typer.Typer(add_completion=False, no_args_is_help=True, name="tgenv")


@app.command(name="install")
def cmd_install(
    version: str = typer.Argument(
        "latest", help="The version of Terragrun to install.", show_default=False
    )
):
    v = check_remote_version(version)
    if is_version_installed(v):
        print(f"Terragrunt version {v} already installed.")
        raise typer.Exit(code=0)
    else:
        version_dir = VERSIONS_DIR / v
        version_dir.mkdir(exist_ok=True)

    print(f"Installing Terragrunt version {v}...")
    bin_file_path = download_version(v)
    set_execution_permission(bin_file_path)

    print(f"Installation of Terragrunt version {v} successful.")

    use_version(v, installation=True)


@app.command(name="use")
def cmd_use(
    version: str = typer.Argument(
        ..., help="The version of Terragrun to use.", show_default=False
    ),
    local: Optional[bool] = typer.Option(True, "--local/--global"),
):
    use_version(version, local)


@app.command(name="uninstall")
def cmd_uninstall(
    version: str = typer.Argument(
        ..., help="The version of Terragrunt to uninstall.", show_default=False
    )
):
    remove_version(version)


@app.command(name="list")
def cmd_list():
    for item in VERSIONS_DIR.iterdir():
        if item.is_dir():
            print(item.name)


@app.command(name="list-remote")
def cmd_list_remote(limit: int = typer.Option(10), beta: bool = typer.Option(True)):
    versions = get_remote_versions(limit)
    for v in versions:
        _v = Version(v)
        if not _v.is_prerelease:
            print(v)
        elif _v.is_prerelease and beta:
            print(v)


@app.command(
    name="exec",
    add_help_option=False,
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)
def cmd_exec():
    v = get_version()
    if is_version_installed(v):
        path = get_version_path(v)
        subprocess.run([path] + sys.argv[2:], check=True)
    else:
        print(f"Missing Terragrunt version {v}")
        print(f"Please run `{app.info.name} install {v}`")
