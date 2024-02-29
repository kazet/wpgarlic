import json
import random
import subprocess
import sys

from utils import fuzz_command, load_blocklists

payload_id = sys.argv[1]
shortcodes_to_fuzz = sys.argv[2]
plugin_slug = sys.argv[3]

if shortcodes_to_fuzz == "ALL":
    shortcodes_to_fuzz = subprocess.check_output(
        [
            "php.orig",
            "/fuzzer/get_fuzzable_entrypoints/get_shortcodes_to_fuzz.php",
        ]
    )

    shortcodes_to_fuzz = [
        shortcode.strip().replace("SHORTCODE: ", "")
        for shortcode in shortcodes_to_fuzz.decode("ascii", errors="ignore").split("\n")
        if shortcode.startswith("SHORTCODE: ")
    ]

    random.shuffle(shortcodes_to_fuzz)
else:
    shortcodes_to_fuzz = shortcodes_to_fuzz.split(",")

shortcodes_to_skip = load_blocklists("shortcodes", plugin_slug)

command_results = []
for shortcode in shortcodes_to_fuzz:
    if shortcode in shortcodes_to_skip:
        continue

    sys.stderr.write(f"Fuzzing: {shortcode}\n")
    sys.stderr.flush()

    cmd = "do_shortcode"
    prefix = ""

    command_results += fuzz_command(f"{prefix}php /fuzzer/execute/{cmd}.php '{shortcode}'", payload_id, shortcode)

print(json.dumps(command_results))
