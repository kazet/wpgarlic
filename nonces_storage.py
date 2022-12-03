import base64
import os
import re
import subprocess
import typing

NONCE_RE = re.compile("__GARLIC_NONCE__(.*?)__ENDGARLIC__")

# We add hostname to the nonce filename to decrease the chance of overriding when rsyncing
NONCE_FILENAME = os.environ.get("NONCE_FILENAME_OVERRIDE", os.path.join(os.path.dirname(__file__), f'nonces-{subprocess.check_output("hostname").decode("ascii").strip()}.txt'))


def collect_nonces(plugin_name: str, outs: typing.List[dict]) -> None:
    matches = []
    for out in outs:
        out_str = out.get('output', '') + out.get('stdout', '') + out.get('stderr', '')

        matches.extend(re.findall(NONCE_RE, out_str))

    for match in set(matches):
        with open(NONCE_FILENAME, 'a') as f:
            f.write("%s %s\n" % (plugin_name, base64.b64encode(match.encode("utf-8")).decode("utf-8")))


def get_valid_nonces_for_plugin(plugin_name: str) -> typing.List[str]:
    if not os.path.exists(NONCE_FILENAME):
        return []

    result = []
    with open(NONCE_FILENAME, 'r') as f:
        for line in f:
            plugin_name_in_line, nonce_base64 = line.split()
            if plugin_name == plugin_name_in_line:
                result.append(base64.b64decode(nonce_base64).decode('utf-8'))
    return result
