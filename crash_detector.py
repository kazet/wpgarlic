import re
import typing


def get_matchers(
    in_admin_or_profile: bool,
) -> typing.List["re.Pattern"]:
    flags = re.DOTALL | re.IGNORECASE
    matchers = [
        re.compile("fopen\\(.{0,256}GARLIC", flags),
        # [^_D]GARLIC is to exclude __GARLIC and __ENDGARLIC
        re.compile("require\\(.{0,256}[^_D]GARLIC", flags),
        re.compile("include\\(.{0,256}[^_D]GARLIC", flags),
        re.compile("readfile\\(.{0,256}[^_D]GARLIC", flags),
        re.compile("require_once\\(.{0,256}[^_D]GARLIC", flags),
        re.compile("include_once\\(.{0,256}[^_D]GARLIC", flags),
        re.compile("file_get_contents{0,256}GARLIC", flags),
        re.compile("unlink.{0,256}GARLIC", flags),
        re.compile("function '.{0,30}GARLIC.{0,30}' not found", flags),
        re.compile("SQL syntax.{0,2048}GARLIC", flags),
        re.compile("<GARLIC", flags),
        # Forgot quotes that allow xss?
        re.compile("\\s[A-Za-z_0-9-]+\\s*=\\s*[^\\s\"']*GARLIC GARLIC", flags),
        re.compile("^[A-Za-z_0-9-]+\\s*=\\s*[^\\s\"']*GARLIC GARLIC", flags),
        re.compile("GARLIC'\"", flags),
        re.compile(r"GARLIC\\'\\\"", flags),
        re.compile(r"GARLIC\\\\*'\\\\*\"", flags),
        re.compile("Error at offset", flags),
        re.compile("Parse error", flags),
        re.compile("syntax error", flags),
        re.compile("__GARLIC_ACCESSED__", flags),
        re.compile("GARLIC.{0,256}No such file", flags),
        # I decided to skip this one due to a large number of false positives.
        # Feel free to uncomment.
        # re.compile("GARLIC.{0,512}thrown in", flags),
        re.compile("GARLIC.{0,64}[Nn]ot found", flags),
        re.compile("GARLIC.{0,512}failed to open stream", flags),
        re.compile("command not found", flags),
        re.compile("simplexml_load_string().{0,256}error", flags),
        re.compile("simplexml_load_string().{0,256}BAD XML", flags),
    ]

    if not in_admin_or_profile:
        matchers.extend(
            [
                re.compile("get_users", flags),
                re.compile("UserFullName", flags),
                re.compile("fuzz.{0,20}@example.com", flags),
                re.compile("file_GARLIC", flags),
                re.compile("NOT_PUBLIC_CONTENT", flags),
            ]
        )
    return matchers

    return True
