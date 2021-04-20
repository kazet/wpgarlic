import re
import subprocess
import unittest

import crash_detector
from fuzzer_container import reinitialize_containers, run_in_container_and_get_output


class CrashDetectorTest(unittest.TestCase):
    @staticmethod
    def setUpClass():
        reinitialize_containers()

    @staticmethod
    def tearDownClass():
        subprocess.call(["docker-compose", "stop"])

    @staticmethod
    def assertAnyMatcherWouldDetect(output: bytes):
        output = output.decode("utf-8")
        for matcher in crash_detector.get_matchers(in_admin=False):
            match = re.search(matcher, output)
            if match:
                return
        raise Exception(f"Unable to detect crash in '{output}'")

    def test_lack_of_quotes_after_parameter_value_is_detected(self):
        output = run_in_container_and_get_output(
            ["php", "-r", 'echo "<a b-p-G_ref=page.php?GARLIC GARLIC";']
        )
        self.assertAnyMatcherWouldDetect(output)
        output = run_in_container_and_get_output(
            ["php", "-r", 'echo "<a b-p-G_ref=GARLIC GARLIC";']
        )
        self.assertAnyMatcherWouldDetect(output)
        output = run_in_container_and_get_output(
            ["php", "-r", 'echo "\nhref=GARLIC GARLIC";']
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_weridly_escaped_payloads_are_detected(self):
        output = run_in_container_and_get_output(
            ["php", "-r", "echo 'GARLIC\\\\\\\\\\'\\\\\\\\\\\"';"]
        )
        self.assertAnyMatcherWouldDetect(output)

        output = run_in_container_and_get_output(
            ["php", "-r", "echo 'GARLIC\\\\\\\\\\\\\\\\\\'\\\\\\\\\\\\\\\\\"';"]
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_libxml_crashes_are_detected(self):
        output = run_in_container_and_get_output(
            ["php", "-r", 'simplexml_load_string("BAD XML");']
        )
        self.assertAnyMatcherWouldDetect(output)

    def test_file_download_crashes_are_detected(self):
        output = run_in_container_and_get_output(
            ["php", "-r", 'file_get_contents("http://GARLICGARLICGARLIC.example.com");']
        )
        self.assertAnyMatcherWouldDetect(output)
