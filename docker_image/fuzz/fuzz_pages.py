import json
import random
import sys

from utils import fuzz_command

payload_id = sys.argv[1]
user_id = sys.argv[2]

pages = [
    ("/var/www/html/index.php", ""),
    ("/var/www/html/index.php", "p=1"),
    ("/var/www/html/index.php", "page_id=2"),
    ("/var/www/html/index.php", "page_id=2000"),
    ("/var/www/html/index.php", "p=3"),
    ("/var/www/html/index.php", "p=4"),
    ("/var/www/html/index.php", "p=5"),
    ("/var/www/html/index.php", "p=6"),
    ("/var/www/html/wp-login.php", ""),
    ("/var/www/html/wp-admin/admin.php", ""),
]

random.shuffle(pages)

command_results = []
for file_name, query in pages:
    sys.stderr.write(f"Fuzzing: {file_name} {query}\n")
    sys.stderr.flush()

    object_name = "page: " + file_name + "?" + query
    command_results += fuzz_command(
        f"php /fuzzer/execute/do_page.php '{file_name}' '{query}' {user_id}",
        payload_id,
        object_name,
    )

print(json.dumps(command_results))
