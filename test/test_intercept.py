import collections
import re
import subprocess
import unittest

import fuzzer_container
import fuzzer_output_regexes


class FuzzerInterceptTest(unittest.TestCase):
    @staticmethod
    def setUpClass():
        fuzzer_container.reinitialize_containers()

    @staticmethod
    def tearDownClass():
        subprocess.call(["docker", "compose", "stop"])

    @staticmethod
    def _clean(s: str):
        s = re.sub(fuzzer_output_regexes.HEADER_RE, "", s)
        s = re.sub(fuzzer_output_regexes.INTERCEPT_RE, "", s)
        result = ""
        for line in s.split("\n"):
            if line.startswith("Warning:"):
                continue
            result += line + "\n"
        return result.strip()

    def test_payload_randomization(self):
        stdouts = []
        for i in range(15):
            commands = fuzzer_container.fuzz_file_or_folder(
                "RANDOM", "/fuzzer/test/echo.php"
            )
            for command in commands:
                self.assertIn(
                    command["cmd"],
                    [
                        "export INTERCEPT_PROB=100; export PAYLOAD_ID=RANDOM; "
                        "cd /fuzzer/test && php /fuzzer/execute/run_file.php 'echo.php'",
                        "export INTERCEPT_PROB=50; export PAYLOAD_ID=RANDOM; "
                        "cd /fuzzer/test && php /fuzzer/execute/run_file.php 'echo.php'",
                        "export INTERCEPT_PROB=33; export PAYLOAD_ID=RANDOM; "
                        "cd /fuzzer/test && php /fuzzer/execute/run_file.php 'echo.php'",
                        "export INTERCEPT_PROB=25; export PAYLOAD_ID=RANDOM; "
                        "cd /fuzzer/test && php /fuzzer/execute/run_file.php 'echo.php'",
                    ],
                )
                stdouts.append(self._clean(command["stdout"]))

        counter = collections.Counter(stdouts)
        self.assertGreaterEqual(counter["GARLIC GARLIC\\'\\\"`"], 5)
        self.assertGreaterEqual(counter["invalidfolderGARLIC/filenameGARLIC"], 5)
        self.assertGreaterEqual(counter["magic"], 5)
        self.assertGreaterEqual(counter["legitimateGARLIC"], 5)

    def test_php_input_stream(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/system_php_input.php"
        )
        self.assertEqual(
            self._clean(commands[0]["stderr"]),
            "sh: 1: Syntax error: end of file unexpected",
        )

    def test_sql_query(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "1", "/fuzzer/test/mysql_query.php"
        )
        self.assertTrue("GARLIC" in commands[0]["stdout"])
        self.assertTrue("error in your SQL syntax" in commands[0]["stdout"])

    def test_file_listing(self):
        commands = fuzzer_container.fuzz_file_or_folder("0", "/fuzzer/test/listing.php")
        self.assertTrue(
            "/var/www/html/wp-content/test_file_GARLIC" in commands[0]["stdout"]
        )

    def test_GET(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/system_get.php"
        )
        self.assertEqual(
            self._clean(commands[0]["stderr"]), "sh: 1: legitimateGARLIC: not found"
        )

    def test_POST(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/system_post.php"
        )
        self.assertEqual(
            self._clean(commands[0]["stderr"]), "sh: 1: legitimateGARLIC: not found"
        )

    def test_COOKIE(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/system_cookie.php"
        )
        self.assertEqual(
            self._clean(commands[0]["stderr"]), "sh: 1: legitimateGARLIC: not found"
        )

    def test_REQUEST(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/system_request.php"
        )
        self.assertEqual(
            self._clean(commands[0]["stderr"]), "sh: 1: legitimateGARLIC: not found"
        )

    def test_HTTP_USER_AGENT_header(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/system_server_http_user_agent.php"
        )
        self.assertEqual(
            self._clean(commands[0]["stderr"]), "sh: 1: legitimateGARLIC: not found"
        )

    def test_echo(self):
        commands = fuzzer_container.fuzz_file_or_folder("1", "/fuzzer/test/echo.php")
        self.assertTrue("</GARLIC" in commands[0]["stdout"])

    def test_include(self):
        commands = fuzzer_container.fuzz_file_or_folder("0", "/fuzzer/test/include.php")
        self.assertTrue(
            "GARLIC): failed to open stream: No such file or directory"
            in commands[0]["stdout"]
        )

    def test_json_decode(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/system_json_decode.php"
        )
        self.assertEqual(
            self._clean(commands[0]["stderr"]), "sh: 1: legitimateGARLIC: not found"
        )

    def test_file_get_contents(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "0", "/fuzzer/test/file_get_contents.php"
        )
        self.assertTrue(
            "GARLIC): failed to open stream: No such file or directory"
            in commands[0]["stdout"]
        )

    def test_probabilistic_intercept(self):
        commands = fuzzer_container.fuzz_file_or_folder("0", "/fuzzer/test/echo.php")

        num_all = 0
        num_intercepted = 0
        for command in commands:
            self.assertIn(
                command["cmd"],
                [
                    "export INTERCEPT_PROB=100; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'echo.php'",
                    "export INTERCEPT_PROB=50; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'echo.php'",
                    "export INTERCEPT_PROB=33; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'echo.php'",
                    "export INTERCEPT_PROB=25; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'echo.php'",
                ],
            )
            if "GARLIC" in command["stdout"]:
                num_intercepted += 1
            num_all += 1

        self.assertGreaterEqual(num_intercepted, 10)
        self.assertLessEqual(num_intercepted, num_all - 3)

    def test_we_are_immune_to_sleep(self):
        commands = fuzzer_container.fuzz_file_or_folder("0", "/fuzzer/test/sleep.php")

        num_all = 0
        num_intercepted = 0
        for command in commands[1:]:
            self.assertIn(
                command["cmd"],
                [
                    "export INTERCEPT_PROB=100; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'sleep.php'",
                    "export INTERCEPT_PROB=50; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'sleep.php'",
                    "export INTERCEPT_PROB=33; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'sleep.php'",
                    "export INTERCEPT_PROB=25; export PAYLOAD_ID=0; cd /fuzzer/test && "
                    "php /fuzzer/execute/run_file.php 'sleep.php'",
                ],
            )
            if "GARLIC" in command.get("stdout", ""):
                num_intercepted += 1
            num_all += 1

        self.assertGreaterEqual(num_intercepted, 3)
        self.assertLessEqual(num_intercepted, num_all / 2 - 3)

    def test_patched_equality(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "RANDOM", "/fuzzer/test/equality.php"
        )
        counter = collections.Counter(
            [self._clean(command["stdout"]) for command in commands]
        )

        self.assertGreaterEqual(counter["bool(false)"], 20)
        self.assertGreaterEqual(counter["bool(true)"], 10)

    def test_patched_strict_equality(self):
        commands = fuzzer_container.fuzz_file_or_folder(
            "RANDOM", "/fuzzer/test/strict_equality.php"
        )
        counter = collections.Counter(
            [self._clean(command["stdout"]) for command in commands]
        )

        self.assertGreaterEqual(counter["bool(false)"], 20)
        self.assertGreaterEqual(counter["bool(true)"], 10)
