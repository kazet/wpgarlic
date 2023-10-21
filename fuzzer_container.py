import json
import subprocess
import tempfile
import time
import typing
from os.path import basename
from zipfile import ZipFile

from nonces_storage import get_valid_nonces_for_plugin


def _run_in_container(cmd: typing.List[str]) -> None:
    subprocess.call(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "wordpress1",
        ]
        + cmd
    )


def _run_in_container_wp_cli(cmd: typing.List[str]) -> None:
    _run_in_container(
        [
            "/fuzzer/nodebug.sh",
            "php.orig",
            "/wp-cli.phar",
            "--allow-root",
        ]
        + cmd
    )


def _copy_plugin_into_container(file_path: str) -> str:
    file_name = basename(file_path)
    new_file_path = f"/fuzzer/plugin_{file_name}"
    subprocess.call(["docker", "cp", file_path, f"wordpress1:{new_file_path}"])
    return new_file_path


def copy_nonces_into_container(plugin_name: str) -> None:
    nonces = get_valid_nonces_for_plugin(plugin_name)
    with tempfile.NamedTemporaryFile() as f:
        f.write("\n".join(nonces).encode("utf-8"))
        f.flush()
        new_file_path = "/fuzzer/valid_nonces.txt"
        subprocess.call(["docker", "cp", f.name, f"wordpress1:{new_file_path}"])


def run_in_container_and_get_output(cmd: typing.List[str]) -> bytes:
    return subprocess.check_output(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "wordpress1",
        ]
        + cmd
    )


def get_plugin_name_from_file(file_path: str) -> str:
    with ZipFile(file_path) as zip_file:
        for listed in zip_file.namelist():
            if listed[-1] != "/":
                continue
            return listed[:-1]
    return ""


def install_dependency(dependency: str) -> None:
    install_plugin_from_slug(dependency)


def install_plugin_from_slug(slug: str, version: str = None):
    if version:
        additional_install_options = ["--version=" + version]
    else:
        additional_install_options = []
    _run_in_container_wp_cli(
        [
            "plugin",
            "install",
            slug,
        ]
        + additional_install_options
    )


def install_plugin_from_file(file_path: str) -> None:
    new_file_path = _copy_plugin_into_container(file_path)
    _run_in_container_wp_cli(["plugin", "install", new_file_path])


def activate_plugin(slug: str) -> None:
    _run_in_container_wp_cli(
        [
            "plugin",
            "activate",
            slug,
        ]
    )


def set_webroot_ownership() -> None:
    _run_in_container(
        [
            "chown",
            "-R",
            "www-data:www-data",
            "/var/www/html/",
        ]
    )


def patch_wordpress(reverse: bool = False) -> None:
    additional_parameters = []
    if reverse:
        additional_parameters = ["--reverse"]

    _run_in_container(["/fuzzer/patch_wordpress.sh"] + additional_parameters)


def patch_plugins(reverse: bool = False) -> None:
    additional_parameters = []
    if reverse:
        additional_parameters = ["--reverse"]

    _run_in_container(["/fuzzer/patch_plugins.sh"] + additional_parameters)


def get_container_id() -> bytes:
    return subprocess.check_output(
        [
            "docker",
            "compose",
            "ps",
            "-q",
            "wordpress1",
        ]
    ).strip()


def disconnect_network(container_id: bytes) -> int:
    networks = subprocess.check_output(
        ["docker", "network", "ls", "--format", "{{.Name}}"]
    ).decode("utf-8")

    network_name = "wpgarlic_network2"

    if network_name not in networks.split():
        raise Exception(
            f"Network {network_name} not found. Make sure the folder name "
            "where the tool is stored is `wpgarlic`"
        )

    return subprocess.call(
        ["docker", "network", "disconnect", network_name, container_id]
    )


def disconnect_dns() -> None:
    _run_in_container(["/fuzzer/disconnect_dns.sh"])


def visit_admin_homepage() -> None:
    # This is to execute plugin hooks in case it needs to do something
    # on the first admin visit
    _run_in_container(
        [
            "/fuzzer/just_visit_admin_homepage.sh",
        ]
    )


def reinitialize_containers():
    subprocess.call(
        [
            "docker",
            "compose",
            "stop",
        ],
        stderr=subprocess.DEVNULL,
    )
    subprocess.call(
        [
            "docker",
            "compose",
            "rm",
            "-f",
            "-v",
            "db1",
            "wordpress1",
        ],
        stderr=subprocess.DEVNULL,
    )
    subprocess.call(
        [
            "docker",
            "compose",
            "build",
        ]
    )
    subprocess.call(
        [
            "docker",
            "compose",
            "up",
            "-d",
        ]
    )
    _run_in_container(
        ["/wait-for-it/wait-for-it.sh", "-h", "db1", "-p", "3306", "-t", "0"]
    )
    time.sleep(2)
    _run_in_container(["chown", "-R", "www-data:www-data", "/var/www/html"])
    _run_in_container(["/fuzzer/create_findable_files.sh"])
    _run_in_container(
        [
            "bash",
            "-c",
            "mysql --host=db1 -u wordpress --password=wordpress wordpress < /fuzzer/dump.sql",
        ]
    )
    _run_in_container(["php.orig", "/wp-cli.phar", "--allow-root", "core", "update"])
    _run_in_container(["php.orig", "/wp-cli.phar", "--allow-root", "core", "update-db"])


def install_plugin_from_svn(slug: str, revision: str):
    _run_in_container(
        [
            "svn",
            "co",
            "https://plugins.svn.wordpress.org/" + slug + "/",
            "-r",
            revision,
        ]
    )
    _run_in_container(["mv", slug, slug + ".tmp"])
    _run_in_container(["mv", slug + ".tmp/trunk", slug])
    _run_in_container(
        [
            "zip",
            "-r",
            slug + ".zip",
            slug,
        ]
    )
    _run_in_container(
        [
            "/fuzzer/nodebug.sh",
            "php.orig",
            "/wp-cli.phar",
            "--allow-root",
            "plugin",
            "install",
            slug + ".zip",
        ]
    )


def fuzz_file_or_folder(payload_id: str, path: str):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_file_or_folder.py",
                payload_id,
                path,
            ]
        )
    )


def fuzz_pages(payload_id: str, user_id: int):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_pages.py",
                payload_id,
                str(user_id),
            ]
        )
    )


def fuzz_actions_admin(payload_id: str, actions_to_fuzz: str, plugin_slug: str):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_actions.py",
                payload_id,
                actions_to_fuzz,
                plugin_slug,
                "BECOME_ADMIN",
            ]
        )
    )


def fuzz_actions(payload_id: str, actions_to_fuzz: str, plugin_slug: str):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_actions.py",
                payload_id,
                actions_to_fuzz,
                plugin_slug,
            ]
        )
    )


def fuzz_menu(payload_id: str, actions_to_fuzz: str, plugin_slug: str, user_id: int):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_menu.py",
                payload_id,
                actions_to_fuzz,
                plugin_slug,
                str(user_id),
            ]
        )
    )


def fuzz_rest_routes(payload_id: str, routes_to_fuzz: str, plugin_slug: str):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_rest_routes.py",
                payload_id,
                routes_to_fuzz,
                plugin_slug,
            ]
        )
    )


def fuzz_rest_routes_admin(payload_id: str, routes_to_fuzz: str, plugin_slug: str):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_rest_routes.py",
                payload_id,
                routes_to_fuzz,
                plugin_slug,
                "BECOME_ADMIN",
            ]
        )
    )


def _grep_garlic_in_path(path: str) -> str:
    # Here we assume the path comes from a trusted source. We aren't
    # immune to command injection here.
    return run_in_container_and_get_output(
        [
            "bash",
            "-c",
            "grep --text --context=3 -R GARLIC " + path + " || true",
        ]
    ).decode("utf-8", "ignore")


def find_payloads_in_files():
    output = _grep_garlic_in_path("/var/www/html")

    command_results = []
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue

        try:
            path, line = tuple(line.split(":", 1))
        except ValueError:
            continue

        if (
            "functions.php" in path
            or "pluggable.php" in path
            or "user.php" in path
            or "post.php" in path
            or "option.php" in path
        ):
            continue
        command_results.append(
            {
                "cmd": "",
                "object_name": path,
                "return_code": 0,
                "output": line,
            }
        )
    return command_results


def find_payloads_in_admin():
    _run_in_container(["/fuzzer/download_admin.sh"])
    output = _grep_garlic_in_path("/var/www/html/127.0.0.1:8001")

    command_results = []
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        command_results.append(
            {
                "cmd": "",
                "object_name": "ADMIN OUTPUT",
                "return_code": 0,
                "output": line,
            }
        )
    return command_results


def find_payloads_in_pages():
    _run_in_container(["/fuzzer/download_pages.sh"])
    output = _grep_garlic_in_path("/var/www/html/pages")

    command_results = []
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        command_results.append(
            {
                "cmd": "",
                "object_name": "PAGES OUTPUT",
                "return_code": 0,
                "output": line,
            }
        )
    return command_results
