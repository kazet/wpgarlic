import os
import subprocess
import sys
import typing

from config import TIMEOUT_SECONDS, VARIABLE_INTERCEPT_PROBABILITIES


def load_blocklists(blocklist_type: str, plugin_slug: str) -> typing.List[str]:
    """
    See blocklists/README.txt
    """
    base_path = f"/fuzzer/blocklists/{blocklist_type}"

    if os.path.exists(os.path.join(base_path, "common")):
        with open(os.path.join(base_path, "common")) as f:
            blocklist = [line.strip() for line in f.readlines()]
    else:
        blocklist = []

    for item in os.listdir(base_path):
        if item != plugin_slug:
            with open(os.path.join(base_path, item)) as f:
                blocklist += [line.strip() for line in f.readlines()]

    return blocklist


def fuzz_command(
    cmd: str,
    payload_id: str,
    object_name: str,
) -> typing.List[typing.Dict]:
    command_results = []
    for intercept_prob in VARIABLE_INTERCEPT_PROBABILITIES:
        cmd_prefixed = f"export INTERCEPT_PROB={intercept_prob}; export PAYLOAD_ID={payload_id.strip()}; " + cmd
        cmd_wrapped = ["bash", "-c", cmd_prefixed]

        try:
            output = subprocess.run(
                cmd_wrapped,
                capture_output=True,
                timeout=TIMEOUT_SECONDS,
                input=b"<GARLIC>",
            )
            command_results.append(
                {
                    "cmd": cmd_prefixed,
                    "object_name": object_name,
                    "return_code": output.returncode,
                    "stdout": output.stdout.decode("ascii", errors="ignore"),
                    "stderr": output.stderr.decode("ascii", errors="ignore"),
                }
            )
            sys.stderr.write(".")
            sys.stderr.flush()
        except subprocess.TimeoutExpired:
            command_results.append(
                {
                    "cmd": cmd_prefixed,
                    "object_name": object_name,
                    "timeout": True,
                }
            )
            sys.stderr.write("T")
            sys.stderr.flush()
    sys.stderr.write("\n")
    return command_results
