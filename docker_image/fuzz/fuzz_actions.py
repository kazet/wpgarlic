import json
import random
import subprocess
import sys

from utils import fuzz_command, load_blocklists

payload_id = sys.argv[1]
actions_to_fuzz = sys.argv[2]
plugin_slug = sys.argv[3]
become_admin = len(sys.argv) > 4 and sys.argv[4] == "BECOME_ADMIN"

if actions_to_fuzz == "ALL":
    actions_to_fuzz = subprocess.check_output(
        [
            "php.orig",
            "/fuzzer/get_fuzzable_entrypoints/get_ajax_actions_to_fuzz.php",
        ]
    )

    actions_to_fuzz = [
        action.strip().replace("AJAX: ", "")
        for action in actions_to_fuzz.decode("ascii", errors="ignore").split("\n")
        if action.startswith("AJAX: ")
    ]

    random.shuffle(actions_to_fuzz)
else:
    actions_to_fuzz = actions_to_fuzz.split(",")

actions_to_skip = load_blocklists("actions", plugin_slug)

command_results = []
for action in actions_to_fuzz:
    if action in actions_to_skip:
        continue

    sys.stderr.write(f"Fuzzing: {action}\n")
    sys.stderr.flush()

    if become_admin:
        cmd = "do_action_as_admin"
        prefix = "TOP_LEVEL_NAVIGATION_ONLY=1 "
    else:
        cmd = "do_action"
        prefix = ""

    object_name = action + (" (admin)" if become_admin else "")
    command_results += fuzz_command(
        f"{prefix}php /fuzzer/execute/{cmd}.php '{action}'", payload_id, object_name
    )

print(json.dumps(command_results))
