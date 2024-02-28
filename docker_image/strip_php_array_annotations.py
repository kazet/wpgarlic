import glob
import re

for file in glob.glob("/var/www/html/**/*.php", recursive=True):
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()
    with open(file, "w") as f:
        for i in range(10):
            data = re.sub(r"(function[^(]*\([^)]*)array (\$[^)]*\))", r"\1\2", data, re.MULTILINE)
        f.write(data)
