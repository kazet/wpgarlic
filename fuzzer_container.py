import json
import subprocess
import time
import typing


def run_in_container(cmd: typing.List[str]) -> None:
    subprocess.call(
        [
            "docker-compose",
            "exec",
            "-T",
            "wordpress1",
        ]
        + cmd
    )


def run_in_container_and_get_output(cmd: typing.List[str]) -> bytes:
    return subprocess.check_output(
        [
            "docker-compose",
            "exec",
            "-T",
            "wordpress1",
        ]
        + cmd
    )


def reinitialize_containers():
    subprocess.call(
        [
            "docker-compose",
            "stop",
        ],
        stderr=subprocess.DEVNULL,
    )
    subprocess.call(
        [
            "docker-compose",
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
            "docker-compose",
            "build",
        ]
    )
    subprocess.call(
        [
            "docker-compose",
            "up",
            "-d",
        ]
    )
    run_in_container(
        ["/wait-for-it/wait-for-it.sh", "-h", "db1", "-p", "3306", "-t", "0"]
    )
    time.sleep(2)
    run_in_container(["/fuzzer/create_findable_files.sh"])
    run_in_container(
        [
            "bash",
            "-c",
            "mysql --host=db1 -u wordpress --password=wordpress wordpress < /fuzzer/dump.sql",
        ]
    )


def install_plugin_from_svn(slug: str, revision: str):
    run_in_container(
        [
            "svn",
            "co",
            "https://plugins.svn.wordpress.org/" + slug + "/",
            "-r",
            revision,
        ]
    )
    run_in_container(["mv", slug, slug + ".tmp"])
    run_in_container(["mv", slug + ".tmp/trunk", slug])
    run_in_container(
        [
            "zip",
            "-r",
            slug + ".zip",
            slug,
        ]
    )
    run_in_container(
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


def fuzz_pages(payload_id: str):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_pages.py",
                payload_id,
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


def fuzz_menu(payload_id: str, actions_to_fuzz: str, plugin_slug: str):
    return json.loads(
        run_in_container_and_get_output(
            [
                "python3",
                "/fuzzer/fuzz/fuzz_menu.py",
                payload_id,
                actions_to_fuzz,
                plugin_slug,
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


def grep_garlic_in_path(path: str) -> str:
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
    output = grep_garlic_in_path("/var/www/html")

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
    run_in_container(["/fuzzer/download_admin.sh"])
    output = grep_garlic_in_path("/var/www/html/127.0.0.1:8001")

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
    run_in_container(["/fuzzer/download_pages.sh"])
    output = grep_garlic_in_path("/var/www/html/pages")

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
