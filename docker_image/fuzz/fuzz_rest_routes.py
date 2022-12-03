import json
import random
import subprocess
import sys

from utils import fuzz_command, load_blocklists

payload_id = sys.argv[1]
routes = sys.argv[2]
plugin_slug = sys.argv[3]
become_admin = len(sys.argv) > 4 and sys.argv[4] == "BECOME_ADMIN"

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

    if become_admin:
        cmd = "do_rest_route_as_admin"
        prefix = "TOP_LEVEL_NAVIGATION_ONLY=1 "
    else:
        cmd = "do_rest_route"
        prefix = ""

    object_name = route + (" (admin)" if become_admin else "")
    command_results += fuzz_command(
        f"{prefix} php /fuzzer/execute/{cmd}.php '{route}'",
        payload_id,
        object_name,
    )

print(json.dumps(command_results))
