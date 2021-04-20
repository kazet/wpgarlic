import json
import random
import subprocess
import sys

from utils import fuzz_command, load_blocklists

payload_id = sys.argv[1]
routes = sys.argv[2]
plugin_slug = sys.argv[3]

if routes == "ALL":
    routes = subprocess.check_output(
        [
            "php.orig",
            "/fuzzer/get_fuzzable_entrypoints/get_rest_routes_to_fuzz.php",
        ]
    )

    routes = [
        route.strip().replace("REST_ROUTE: ", "")
        for route in routes.decode("ascii", errors="ignore").split("\n")
        if route.startswith("REST_ROUTE: ")
    ]

    random.shuffle(routes)
else:
    routes = routes.split(",")

routes_to_skip = load_blocklists("rest", plugin_slug)

command_results = []
for route in routes:
    if route in routes_to_skip:
        continue

    sys.stderr.write(f"Fuzzing: {route}\n")
    sys.stderr.flush()

    command_results += fuzz_command(
        f"php /fuzzer/execute/do_rest_route.php '{route}'",
        payload_id,
        route,
    )

print(json.dumps(command_results))
