import json
import os
import random
import subprocess
import sys

from utils import fuzz_command

payload_id = sys.argv[1]
file_or_folder = sys.argv[2]

paths = subprocess.check_output(["find", file_or_folder])

paths = paths.decode("ascii", errors="ignore").split()
random.shuffle(paths)

command_results = []
for path in paths:
    if path.endswith(".php"):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        sys.stderr.write(f"Fuzzing: {path}\n")

        # We shouldn't skip fuzzing when we think the plugin exits where ABSPATH is not
        # defined - if we would skip such files, we wouldn't find CVE-2021-24906
        # as sometimes these checks in plugins are buggy.

        command_results += fuzz_command(
            f"cd {dirname} && php /fuzzer/execute/run_file.php '{basename}'",
            payload_id,
            path,
        )

print(json.dumps(command_results))
