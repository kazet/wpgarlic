import re

try:
    import filtering_custom
except ImportError:
    filtering_custom = None


def is_call_interesting(
    call: dict, in_admin_or_profile: bool, fuzzer_output_path: str, file_or_action: str
):
    if filtering_custom:
        if filtering_custom.filter_call(
            call, in_admin_or_profile, fuzzer_output_path, file_or_action
        ):
            return False

    if call["what"] in ["delete_option", "delete_site_option"]:
        if call["data"]["name"].startswith("_transient_"):
            return False
        # For now, let's take into account only the possibility to delete
        # arbitrary options
        return "GARLIC" in call["data"]["name"]

    if call["what"] in ["wp_delete_user", "wp_update_user"]:
        return True

    if call["what"] in ["update_post_meta"]:
        return "GARLIC" in str(call)

    if call["what"] in ["update_user_meta"]:
        if call["data"]["meta_key"] == "wc_last_active":
            return False
        return True

    if call["what"] in ["wp_insert_post"]:
        return "GARLIC" in str(call)

    if call["what"] in ["wp_mail"]:
        if (
            call["data"]["to"] == "fuzzer@example.com"
            and call["data"]["subject"]
            == "[fuzz] Your Site is Experiencing a Technical Issue"
        ):
            return False
        return True

    if call["what"] in ["update_option", "update_site_option"]:
        if call["data"]["name"] in [
            "_transient_doing_cron",
            "fs_options",
            "fs_accounts",
            "jetpack_connection_xmlrpc_errors",
            "jetpack_connection_xmlrpc_verified_errors",
            "wpins_block_notice",
            "wpins_allow_tracking",
        ]:
            return False

        call["data"]["name"] = str(call["data"]["name"])
        if call["data"]["name"].startswith("_transient_timeout_"):
            return False

        if (
            "_admin_notice" in call["data"]["name"]
            and "two_week_review" in call["data"]["value"]
        ):
            return False

        if call["data"]["name"] in ["active_plugins", "auto_update"]:
            return True

        return "GARLIC" in call["data"]["name"] or "GARLIC" in call["data"]["value"]

    if call["what"] == "maybe_unserialize":
        # One of our payloads is a serialized string. We catch only attempts to unserialize
        # this string to decrease the amount of false positives
        # (such as e.g. maybe_unserialize("s:11:\"<GARLIC...>\"");)
        if (
            isinstance(call["data"], str)
            and call["data"].startswith("O:21:")
            and "GARLICNonexistentClass" in call["data"]
        ):
            return True
        else:
            return False

    if call["what"] == "get_users" and in_admin_or_profile:
        # There is nothing interesting that get_users() is called on a page or endpoint
        # with admin privileges
        return False

    if call["what"] == "query":
        if not call["data"]:
            return False

        query = call["data"].lower().strip()

        # Looked like it's mostly false positives. Feel free to investigate them more.
        if query.startswith("delete from wp_usermeta where umeta_id in"):
            return False

        if query.startswith("delete from wp_wc_admin_note_actions"):
            return False

        if query.startswith("delete from `wp_woocommerce_sessions`"):
            return False

        # Already covered by wp_delete_option
        if query.startswith("delete from `wp_options` where `option_name` = "):
            return False

        return query.startswith("truncate ") or query.startswith("delete ")
    return True


def is_header_interesting(header: str, fuzzer_output_path: str):
    header = header.lower()

    if filtering_custom:
        if filtering_custom.filter_header(header, fuzzer_output_path):
            return False

    if (
        header.startswith("location")
        and not header.startswith("location: https://127.0.0.1:8001/")
        and not header.startswith("location: http://127.0.0.1:8001/")
        and not header.startswith("location: https://:8001/")
        and not header.startswith("location: http://:8001/")
        and not header.startswith("location: ://:8001/")
        and not header.startswith("location: https://elementor.com/pro/")
        and not header.startswith("location: ?")
        and "garlic" in header
    ):
        return True

    return False


def filter_false_positives(output: str, endpoint: str, fuzzer_output_path: str) -> str:
    SHORT_STRING = "(.|\n){1,256}?"

    output = re.sub(
        r"Stack trace: #0 "
        + SHORT_STRING
        + " #1 "
        + SHORT_STRING
        + " #2 "
        + SHORT_STRING
        + "#3 "
        + SHORT_STRING
        + "#4 "
        + SHORT_STRING
        + "#5 ",
        "--false-positive--",
        output,
        flags=re.M,
    )

    output = re.sub(
        r"Stack trace: #0 "
        + SHORT_STRING
        + " #1 "
        + SHORT_STRING
        + " #2 "
        + SHORT_STRING
        + "#3 "
        + SHORT_STRING
        + "#4 ",
        "--false-positive--",
        output,
        flags=re.M,
    )
    output = re.sub(
        r"Stack trace: #0 "
        + SHORT_STRING
        + " #1 "
        + SHORT_STRING
        + " #2 "
        + SHORT_STRING
        + "#3 ",
        "--false-positive--",
        output,
        flags=re.M,
    )
    output = re.sub(
        r"Stack trace: #0 " + SHORT_STRING + " #1 " + SHORT_STRING + " #2 ",
        "--false-positive--",
        output,
        flags=re.M,
    )
    output = re.sub(
        r"Notice: Undefined index:.{0,5}?GARLIC.{0,1024}?on line",
        "--false-positive--",
        output,
        flags=re.M,
    )

    # Not the kind of parse rrors we are interested in
    output = re.sub(
        r"<value><string>parse error. not well formed</string>",
        "--false-positive--",
        output,
        flags=re.M,
    )

    # Correctly escaped
    output = re.sub(
        r"The username <strong>"
        + SHORT_STRING
        + "</strong> is not registered on this site.",
        "--false-positive--",
        output,
        flags=re.M,
    )

    # This one needs correct hash
    output = re.sub(
        r"Error at offset [0-9]* of [0-9]* bytes in /var/www/html/wp-includes/blocks/legacy-widget.php on line 52",
        "--false-positive--",
        output,
        flags=re.M,
    )

    # Each SQL crash is repeated twice, once in the error logs and the second time in the HTML
    # output. Let's nuke one of these crashes
    output = re.sub(
        "SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near "
        + SHORT_STRING
        + " at line [0-9]*.<br /><code>[^<]*?</code>",
        "--duplicate-sql-error--",
        output,
        flags=re.M,
    )

    output = re.sub(
        r'Fatal error: Uncaught InvalidArgumentException: Invalid action status: "'
        + SHORT_STRING
        + '". in /var/www/html/wp-content',
        "--false-positive--",
        output,
        flags=re.M,
    )
    output = re.sub(
        "Fatal error: Uncaught Exception: DateTime::__construct\\(\\): Failed to parse time string "
        + SHORT_STRING
        + " at position",
        "--false-positive--",
        output,
        flags=re.M,
    )
    output = re.sub(
        "doesn't exist for query " + SHORT_STRING + "made by",
        "--false-positive--",
        output,
        flags=re.M,
    )
    output = re.sub(
        "Warning: Illegal string offset '"
        + SHORT_STRING
        + "' in /var/www/html/wp-content",
        "--false-positive--",
        output,
        flags=re.M,
    )

    # Elementor, looks correctly escaped
    output = re.sub(
        r"var ecs_ajax_params = {.{0,3000}?</script>",
        "--false-positive--",
        output,
        flags=re.M,
    )

    output = output.replace(
        "Fatal error: Uncaught Error: Call to undefined function "
        "get_plugin_data() in /var/www/html/wp-content/plugins/",
        "--false-positive--",
    )

    output = output.replace(
        "made by include('wp-load.php'), require_once('wp-config.php'), "
        "require_once('wp-settings.php'), do_action('init')",
        "--false-positive--",
    )

    output = output.replace(
        "confirm your email by clicking on the link we sent to fuzzer@example.com. "
        "This makes sure youre not a bot",
        "--false-positive--",
    )

    output = re.sub(
        r"__GARLIC_NONCE__.{0,300}?__ENDGARLIC__",
        "",
        output,
        flags=re.M,
    )

    output = re.sub(
        r"WordPress database error Not unique table/alias: 'trel' "
        r"for query.{0,3000}? made by",
        "--false-positive--",
        output,
        flags=re.M,
    )

    if filtering_custom:
        output = filtering_custom.filter_false_positives(
            output, endpoint, fuzzer_output_path
        )

    return output
