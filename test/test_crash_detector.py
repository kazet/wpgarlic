import re
import subprocess
import typing
import unittest

import crash_detector
from fuzzer_container import (
    fuzz_file_or_folder,
    reinitialize_containers,
    run_in_container,
    run_in_container_and_get_output,
)


class CrashDetectorTest(unittest.TestCase):
    @staticmethod
    def setUpClass():
        reinitialize_containers()

    @staticmethod
    def tearDownClass():
        subprocess.call(["docker", "compose", "stop"])

    @staticmethod
    def assertAnyMatcherWouldDetect(output: typing.Union[bytes, str]):
        if isinstance(output, bytes):
            output = output.decode("utf-8")
        for matcher in crash_detector.get_matchers(in_admin_or_profile=False):
            match = re.search(matcher, output)
            if match:
                return
        raise Exception(f"Unable to detect crash in '{output}'")

    def test_lack_of_quotes_after_parameter_value_is_detected(self):
        output = run_in_container_and_get_output(["php", "-r", 'echo "<a b-p-G_ref=page.php?GARLIC GARLIC";'])
        self.assertAnyMatcherWouldDetect(output)
        output = run_in_container_and_get_output(["php", "-r", 'echo "<a b-p-G_ref=GARLIC GARLIC";'])
        self.assertAnyMatcherWouldDetect(output)
        output = run_in_container_and_get_output(["php", "-r", 'echo "\nhref=GARLIC GARLIC";'])
        self.assertAnyMatcherWouldDetect(output)

    def test_weridly_escaped_payloads_are_detected(self):
        output = run_in_container_and_get_output(["php", "-r", "echo 'GARLIC\\\\\\\\\\'\\\\\\\\\\\"';"])
        self.assertAnyMatcherWouldDetect(output)

        output = run_in_container_and_get_output(["php", "-r", "echo 'GARLIC\\\\\\\\\\\\\\\\\\'\\\\\\\\\\\\\\\\\"';"])
        self.assertAnyMatcherWouldDetect(output)

    def test_phpinfo_or_env_is_detected(self):
        output = run_in_container_and_get_output(["php", "-r", 'phpinfo();'])
        self.assertAnyMatcherWouldDetect(output)

    def test_libxml_crashes_are_detected(self):
        output = run_in_container_and_get_output(["php", "-r", 'simplexml_load_string("BAD XML");'])
        self.assertAnyMatcherWouldDetect(output)

    def test_file_write_crashes_are_detected(self):
        output = run_in_container_and_get_output(
            [
                "php",
                "-r",
                'file_put_contents("invalidfolderGARLIC/filenameGARLIC", "test");',
            ]
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_file_download_crashes_are_detected(self):
        output = run_in_container_and_get_output(
            ["php", "-r", 'file_get_contents("http://GARLICGARLICGARLIC.example.com");']
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_call_user_func_crashes_are_detected(self):
        output = run_in_container_and_get_output(
            ["php", "-r", 'call_user_func("http://GARLICGARLICGARLIC.example.com");']
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_call_user_func_array_crashes_are_detected(self):
        output = run_in_container_and_get_output(
            [
                "php",
                "-r",
                'call_user_func_array("http://GARLICGARLICGARLIC.example.com", array());',
            ]
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_error_silencing_is_detected(self):
        output = run_in_container_and_get_output(
            [
                "bash",
                "-c",
                'php -r \'include("/fuzzer/magic_payloads.php"); @file_get_contents("GARLIC");\' 2>&1',
            ]
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_srand(self):
        run_in_container(["cp", "/fuzzer/test/srand.php", "/var/www/html"])
        run_in_container(["/fuzzer/patch_plugins_themes.sh"])
        commands = fuzz_file_or_folder("0", "/var/www/html/srand.php")
        run_in_container(["/fuzzer/patch_plugins_themes.sh", "--reverse"])
        output = commands[0]["stdout"]
        self.assertAnyMatcherWouldDetect(output)
