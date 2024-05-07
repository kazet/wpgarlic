import os
import subprocess
import tempfile
import typing
import unittest


def retry(num=5):
    def decorate(function):
        def wrapped_function(*args, **kwargs):
            for i in range(num):
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    if i == num - 1:
                        raise e
                    else:
                        print("Retrying because of %s" % e)

        return wrapped_function

    return decorate


class FuzzerE2ETest(unittest.TestCase):
    def _assert_any_of_expected_strings_in_output(self, output_path: str, expected_strings: typing.List[str]):
        print(f"Verifying expected_strings={expected_strings} " f"output_path={output_path}")
        findings_printer_result = subprocess.check_output(
            [
                "python3",
                os.path.join(os.path.dirname(__file__), "..", "print_findings.py"),
                output_path,
            ]
        ).decode("utf-8", errors="ignore")

        found = False
        for expected_string in expected_strings:
            if expected_string in findings_printer_result:
                found = True
        self.assertTrue(
            found,
            msg=f"none of expected_strings={expected_strings} found in findings " f"printer result for {output_path}",
        )

    def _fuzz_file_and_check_expected_strings(
        self,
        plugin: str,
        version_or_revision_args: typing.List[str],
        filename: str,
        expected_strings: typing.List[str],
    ):
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                plugin,
                "--skip-fuzzing-second-time-without-dependencies",
                "--enabled-features",
                "files",
                "--file-or-folder-to-fuzz",
                filename,
                "--output-path",
                output_path,
            ]
            + version_or_revision_args
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    def _fuzz_rest_route_and_check_expected_strings(
        self,
        plugin: str,
        version_or_revision_args: typing.List[str],
        rest_route: str,
        expected_strings: typing.List[str],
    ):
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                plugin,
                "--skip-fuzzing-second-time-without-dependencies",
                "--enabled-features",
                "rest_routes",
                "--rest-routes-to-fuzz",
                rest_route,
                "--output-path",
                output_path,
            ]
            + version_or_revision_args
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    def _fuzz_action_and_check_expected_strings(
        self,
        plugin: str,
        version_or_revision_args: typing.List[str],
        action: str,
        expected_strings: typing.List[str],
    ):
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                plugin,
                "--skip-fuzzing-second-time-without-dependencies",
                "--enabled-features",
                "actions",
                "--actions-to-fuzz",
                action,
                "--output-path",
                output_path,
            ]
            + version_or_revision_args
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    def _fuzz_all_menu_and_check_expected_strings(
        self,
        plugin: str,
        version_or_revision_args: typing.List[str],
        expected_strings: typing.List[str],
    ):
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                plugin,
                "--skip-fuzzing-second-time-without-dependencies",
                "--enabled-features",
                "menu_admin",
                "--output-path",
                output_path,
            ]
            + version_or_revision_args
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    def _fuzz_menu_and_check_expected_strings(
        self,
        plugin: str,
        version_or_revision_args: typing.List[str],
        action: str,
        expected_strings: typing.List[str],
    ):
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                plugin,
                "--skip-fuzzing-second-time-without-dependencies",
                "--enabled-features",
                "menu_admin",
                "--menu-actions-to-fuzz",
                action,
                "--output-path",
                output_path,
            ]
            + version_or_revision_args
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    @retry()
    def test_CVE_2021_24973(self):
        # Test that the fuzzer would detect
        # Stored XSS in site-reviews
        # https://wpscan.com/vulnerability/0118f245-0e6f-44c1-9bdb-5b3a5d2403d6
        expected_strings = ["type=site-review&page=glsr-tools"]
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "site-reviews",
                "--skip-fuzzing-second-time-without-dependencies",
                "--version",
                "5.17.1",
                "--enabled-features",
                "actions,find_in_admin_after_fuzzing",
                "--actions-to-fuzz",
                "wp_ajax_glsr_action",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    @retry()
    def test_CVE_2021_25077(self):
        # Test that the fuzzer would detect
        # Reflected XSS in woocommerce-store-toolkit
        # https://wpscan.com/vulnerability/53868650-aba0-4d07-89d2-a998bb0ee5f6
        self._fuzz_menu_and_check_expected_strings(
            "woocommerce-store-toolkit",
            ["--version", "2.3"],
            "woocommerce_page_woo_st",
            [
                "<code>tabs-GARLIC GARLIC\\'",
                "template file <code>tabs-</GARLIC",
            ],
        )

    @retry()
    def test_CVE_2022_0313(self):
        # Test that the fuzzer would detect
        # CSRF menu deletion in float-menu
        # https://wpscan.com/vulnerability/1ce6c8f4-6f4b-4d56-8d11-43355ef32e8c
        self._fuzz_menu_and_check_expected_strings(
            "float-menu",
            ["--version", "4.3"],
            "wow-plugins_page_float-menu",
            [
                "Call: query arguments=DELETE FROM `wp_wow_fmp`",
            ],
        )

    @retry()
    def test_CVE_2021_24906(self):
        # Test that the fuzzer would detect
        # plugin deactivation in protect-wp-admin
        # https://wpscan.com/vulnerability/4204682b-f657-42e1-941c-bee7a245e9fd
        self._fuzz_file_and_check_expected_strings(
            "protect-wp-admin",
            ["--revision", "2581706"],
            "/var/www/html/wp-content/plugins/protect-wp-admin/lib/pwa-deactivate.php",
            ["Call: update_option arguments={'name': 'active_plugins', 'value': 'Array"],
        )

    @retry()
    def test_CVE_2022_0164(self):
        # Test that the fuzzer would detect
        # unauthorized e-mail sending in coming-soon-page
        # https://wpscan.com/vulnerability/942535f9-73bf-4467-872a-20075f03bc51
        self._fuzz_action_and_check_expected_strings(
            "coming-soon-page",
            ["--version", "3.6.5"],
            "wp_ajax_coming_soon_send_mail",
            [
                "Call: wp_mail arguments={'to': ",
            ],
        )

    @retry()
    def test_CVE_2021_34641(self):
        # Test that the fuzzer would detect
        # unauthorized post metadata update in wp-seopress
        # https://nvd.nist.gov/vuln/detail/CVE-2021-34641
        self._fuzz_rest_route_and_check_expected_strings(
            "wp-seopress",
            ["--version", "5.0.3"],
            "/seopress/v1/posts/(?P<id>\\d+)/title-description-metas@1",
            ["Call: update_post_meta arguments={"],
        )

    @retry()
    def test_CVE_2021_24919(self):
        # Test that the fuzzer would detect
        # SQL injection in wicked-folders
        # https://wpscan.com/vulnerability/f472ec7d-765c-4266-ab9c-e2d06703ebb4
        self._fuzz_action_and_check_expected_strings(
            "wicked-folders",
            ["--version", "2.18.6"],
            "wp_ajax_wicked_folders_save_sort_order",
            [
                "GARLIC\\'\\\"` AND p.ID NOT IN ",
                "example.com AND p.ID NOT IN ",
                "GARLIC\\ AND p.ID NOT",
            ],
        )

    @retry()
    def test_CVE_2021_39321(self):
        # Test that the fuzzer would detect
        # object injection in sassy-social-share
        # described in
        # fmt: off
        # https://www.wordfence.com/blog/2021/10/vulnerability-patched-in-sassy-social-share-plugin/
        # fmt: on
        self._fuzz_action_and_check_expected_strings(
            "sassy-social-share",
            ["--version", "3.3.23"],
            "wp_ajax_heateor_sss_import_config",
            ["Call: maybe_unserialize arguments=O:21:"],
        )

    @retry()
    def test_CVE_2021_42359(self):
        # Test that the fuzzer would detect
        # arbitrary post deletion in shapepress-dsgvo
        # described in
        # fmt: off
        # https://www.wordfence.com/blog/2021/11/vulnerability-in-wp-dsgvo-tools-gdpr-plugin-allows-unauthenticated-page-deletion/
        # fmt: on
        self._fuzz_action_and_check_expected_strings(
            "shapepress-dsgvo",
            ["--version", "3.1.12"],
            "wp_ajax_admin-dismiss-unsubscribe",
            [
                "Call: wp_delete_post",
            ],
        )

    @retry(5)
    def test_CVE_2021_25110(self):
        # Test that the fuzzer would detect
        # e-mail leak in futurio-extra
        # https://wpscan.com/vulnerability/b655fc21-47a1-4786-8911-d78ab823c153
        self._fuzz_action_and_check_expected_strings(
            "futurio-extra",
            ["--version", "1.6.2"],
            "wp_ajax_dilaz_mb_query_select",
            [
                "Call: get_users",
            ],
        )

    @retry()
    def test_CVE_2021_24876_but_with_getting_all_menu_actions(self):
        # Test that the fuzzer would detect
        # reflected XSS in registrations-for-the-events-calendar
        # described in
        # https://wpscan.com/vulnerability/e77c2493-993d-418d-9629-a1f07b5a2b6f
        self._fuzz_all_menu_and_check_expected_strings(
            "registrations-for-the-events-calendar",
            ["--version", "2.7.4"],
            [
                "&tab=echo GARLIC",
                "&tab=GARLIC",
            ],
        )

    @retry()
    def test_event_manager_arbitrary_option_reset(self):
        # https://wpscan.com/vulnerability/75212a4d-02e6-4164-8337-74219b2607b7
        self._fuzz_action_and_check_expected_strings(
            "mage-eventpress",
            ["--version", "3.4.8"],
            "wp_ajax_mep_wl_ajax_license_deactivate",
            [
                "Call: update_option arguments={'name': 'invalidfolderGARLIC",
                "Call: update_option arguments={'name': 'http://GARLIC",
                "Call: update_option arguments={'name': 'GARLIC",
            ],
        )

    @retry(15)
    def test_event_manager_arbitrary_template_import(self):
        # https://wpscan.com/vulnerability/85387986-5479-4575-8740-dff59866f9c6
        self._fuzz_action_and_check_expected_strings(
            "mage-eventpress",
            ["--version", "3.4.8"],
            "wp_ajax_mep_import_ajax_template",
            [
                "file_get_contents(/GARLIC",
                "file_get_contents(GARLIC",
                "file_get_contents(</GARLIC",
                "file_get_contents(http://GARLIC",
                "file_get_contents(http://legitimateGARLIC",
                "file_get_contents(http://invalidfolderGARLIC/filenameGARLIC",
                "file_get_contents(legitimate.emailGARLIC@example.com",
            ],
        )

    @retry()
    def test_CVE_2021_24975(self):
        # Test that the fuzzer would detect
        # stored XSS in social-networks-auto-poster-facebook-twitter-g
        # https://wpscan.com/vulnerability/b99dae3d-8230-4427-adc5-4ef9cbfb8ba1
        expected_strings = ["/var/www/html/127.0.0.1:8001/wp-admin/admin.php?page=nxs-log:"]
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "social-networks-auto-poster-facebook-twitter-g",
                "--skip-fuzzing-second-time-without-dependencies",
                "--revision",
                "2609673",
                "--enabled-features",
                "actions,find_in_admin_after_fuzzing",
                "--actions-to-fuzz",
                "wp_ajax_nxs_rfLgo",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    @retry()
    def test_CVE_2021_24385(self):
        # Test that the fuzzer would detect SQL injection in filebird
        # https://wpscan.com/vulnerability/754ac750-0262-4f65-b23e-d5523995fbfa
        expected_strings = [
            "for query SELECT `attachment_id` FROM wp_fbv_attachment_folder "
            "WHERE 1 = 1 AND `folder_id` IN (legitimate",
            "for query SELECT `attachment_id` FROM wp_fbv_attachment_folder " "WHERE 1 = 1 AND `folder_id` IN (</GARL",
        ]
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "filebird",
                "--skip-fuzzing-second-time-without-dependencies",
                "--enabled-features",
                "rest_routes",
                "--revision",
                "2537774",
                "--rest-routes-to-fuzz",
                "/filebird/v1/gutenberg-get-images@0",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    @retry()
    def test_CVE_2021_25074(self):
        # Test that the fuzzer would detect Open Redirect in webp-converter-for-media
        # https://wpscan.com/vulnerability/f3c0a155-9563-4533-97d4-03b9bac83164
        expected_strings = [
            "Location: http://GARLICGARLICGARLIC.example.com",
            "Location: legitimate.emailGARLIC@example.com",
            "Location: legitimateGARLIC",
        ]
        self._fuzz_file_and_check_expected_strings(
            "webp-converter-for-media",
            ["--version", "4.0.2"],
            "/var/www/html/wp-content/plugins/webp-converter-for-media/includes/passthru.php",
            expected_strings,
        )

    @retry()
    def test_CVE_2022_2356(self):
        # Test that the fuzzer would detect arbitrary file upload in user-private-files
        # https://wpscan.com/vulnerability/67f3948e-27d4-47a8-8572-616143b9cf43
        expected_strings = [
            "__GARLIC_ACCESSED__ _FILES[docfile] __ENDGARLIC__",
        ]
        nonces_path = tempfile.mktemp()
        os.environ["NONCE_FILENAME_OVERRIDE"] = nonces_path

        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "user-private-files",
                "--enabled-features actions,pages_not_logged_in",
                "--actions-to-fuzz",
                "wp_ajax_upload_doc_callback",
                "--version",
                "1.1.2",
                "--output-path",
                output_path,
            ]
        )
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "user-private-files",
                "--enabled-features actions,pages_not_logged_in",
                "--actions-to-fuzz",
                "wp_ajax_upload_doc_callback",
                "--version",
                "1.1.2",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    @retry()
    def test_wp_compress_image_optimizer_arbitrary_file_read(self):
        # Test that the fuzzer would detect arbitrary file read in wp-compress-image-optimizer
        # https://www.wordfence.com/threat-intel/vulnerabilities/wordpress-plugins/wp-compress-image-optimizer/wp-compress-image-optimizer-all-in-one-61033-unauthenticated-directory-traversal-via-css
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "wp-compress-image-optimizer",
                "--enabled-features",
                "files",
                "--file-or-folder-to-fuzz",
                "/var/www/html/wp-content/plugins/wp-compress-image-optimizer/fixCss.php",
                "--version",
                "6.10.32",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, ["__FILE_EXISTS_OF_GARLIC_DETECTED__"])

    @retry()
    def test_backup_backup_rce(self):
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "backup-backup",
                "--version",
                "1.3.7",
                "--enabled-features",
                "files",
                "--file-or-folder-to-fuzz",
                "/var/www/html/wp-content/plugins/backup-backup/includes/backup-heart.php",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, ["Warning: require_once(GARLIC GARLIC"])

    @retry()
    def test_ai_assistant_by_10web_arbitrary_plugin_installation(self):
        # https://www.wordfence.com/threat-intel/vulnerabilities/id/229245a5-468d-47b9-8f26-d23d593e91da
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "ai-assistant-by-10web",
                "--enabled-features",
                "actions",
                "--actions-to-fuzz",
                "wp_ajax_install_plugin",
                "--version",
                "1.0.18",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, ["__FILE_EXISTS_OF_GARLIC_DETECTED__"])

    @retry()
    def test_CVE_2024_0835(self):
        # Test that the fuzzer would detect arbitrary transient update in royal-elementor-kit theme
        # https://www.wordfence.com/threat-intel/vulnerabilities/wordpress-themes/royal-elementor-kit/royal-elementor-kit-10116-missing-authorization-to-arbitrary-transient-update
        expected_strings = [
            "Call: update_option arguments={'name': '_transient_GARLIC",
            "Call: update_option arguments={'name': '_transient_http://GARLICGARLICGARLIC",
            "Call: update_option arguments={'name': '_transient_legitimateGARLIC",
            "Call: update_option arguments={'name': '_transient_invalidfolderGARLIC",
            "Call: update_option arguments={'name': '_transient_legitimate.emailGARLIC",
        ]
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "theme",
                "royal-elementor-kit",
                "--enabled-features",
                "actions",
                "--skip-fuzzing-second-time-without-dependencies",
                "--version",
                "1.0.116",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    @retry()
    def test_CVE_2024_1510(self):
        # Test that the fuzzer would detect shortcode contributor+ stored xss in shortcodes-ultimate
        # https://www.wordfence.com/threat-intel/vulnerabilities/id/ee03d780-076b-4501-a353-376198a4bd7b
        expected_strings = [
            '<span class="su-tooltip-title"></GARLIC\'"`></span>',
        ]
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "shortcodes-ultimate",
                "--version",
                "7.0.2",
                "--enabled-features",
                "shortcodes",
                "--shortcodes-to-fuzz",
                "su_tooltip",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)

    @retry()
    def test_CVE_2023_40000(self):
        # Test that the fuzzer would detect stored xss in litespeed-cache
        # https://patchstack.com/articles/xss-vulnerability-in-litespeed-cache-plugin-affecting-4-million-sites/
        expected_strings = ["Call: update_option arguments={'name': 'litespeed.admin_display.messages', "]
        output_path = tempfile.mkdtemp()
        subprocess.call(
            [
                "./bin/fuzz_object",
                "plugin",
                "litespeed-cache",
                "--version=5.7",
                "--enabled-features",
                "rest_routes",
                "--rest-routes-to-fuzz",
                "/litespeed/v1/cdn_status@0",
                "--output-path",
                output_path,
            ]
        )
        self._assert_any_of_expected_strings_in_output(output_path, expected_strings)
