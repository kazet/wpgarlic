import binascii
import json
import os
import re
import subprocess
import sys

import termcolor
import typer
from tqdm import tqdm

import crash_detector
import filtering
import fuzzer_output_regexes


def colored(text: str, with_color: bool, **kwargs):
    if with_color:
        return termcolor.colored(text, **kwargs)
    else:
        return text


def trim_if_too_long(data: str, max_length: int = 2000):
    if len(data) > max_length:
        return data[:max_length] + "... [trimmed, too long]"
    else:
        return data


class FindingsPrinter:
    def __init__(self):
        self._header_printed = None
        self._already_printed = set()

    def print_findings(
        self,
        output: str,
        fuzzer_output_path: str,
        active_installs: int,
        file_or_action: str,
        with_color: bool,
    ) -> bool:
        intercepted_variables_info = []
        for match in fuzzer_output_regexes.INTERCEPT_RE.finditer(output):
            try:
                intercepted_variable_info = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

            intercepted_variable_info_as_string = (
                f"{intercepted_variable_info['name']}"
                f"[{intercepted_variable_info['key']}] = "
                f"{intercepted_variable_info['payload']}"
            )
            intercepted_variables_info.append(intercepted_variable_info_as_string)

        for match in fuzzer_output_regexes.COULD_AS_WELL_BE_EQUAL_RE.finditer(output):
            intercepted_variables_info.append(
                "May as well be equal: "
                + binascii.unhexlify(match.group(1)).decode("ascii", "ignore")
                + " and "
                + binascii.unhexlify(match.group(2)).decode("ascii", "ignore")
            )

        call_matches = list(fuzzer_output_regexes.CALL_RE.finditer(output))
        header_matches = list(fuzzer_output_regexes.HEADER_RE.finditer(output))

        output = re.sub(fuzzer_output_regexes.NOT_IMPLEMENTED_RE, "", output)
        output = re.sub(fuzzer_output_regexes.INTERCEPT_RE, "", output)
        output = re.sub(fuzzer_output_regexes.COULD_AS_WELL_BE_EQUAL_RE, "", output)
        output = re.sub(fuzzer_output_regexes.CALL_RE, "", output)
        output = re.sub(fuzzer_output_regexes.HEADER_RE, "", output)
        output = filtering.filter_false_positives(
            output, file_or_action, fuzzer_output_path
        )

        lcontext = 300
        rcontext = 500
        max_match_size = 100
        # If we are in admin panel or user profile, the fact that someone can see e-mails or file names
        # is nothing interesting, therefore we don't report this.
        in_admin_or_profile = (
            file_or_action.startswith("menu:")
            or file_or_action == "ADMIN OUTPUT"
            or file_or_action.endswith(" (admin)")
            or "/var/www/html/wp-admin/profile.php" in file_or_action
        )
        matchers = crash_detector.get_matchers(in_admin_or_profile)
        to_print = []

        while True:
            min_match = None
            min_match_position = None
            for matcher in matchers:
                match = matcher.search(output)
                if not match:
                    continue

                if min_match_position is None or min_match_position > match.start():
                    min_match = match
                    min_match_position = match.start()

            if min_match is None:
                break

            match_position = min_match.start()
            match_size = min(max_match_size, min_match.end() - min_match.start())

            match = output[match_position : match_position + match_size]
            left_context = output[max(0, match_position - lcontext) : match_position]
            right_context = output[
                match_position
                + match_size : min(len(output), match_position + match_size + rcontext)
            ]
            data = (
                colored(left_context, color="green", with_color=with_color)
                + match
                + colored(right_context, color="green", with_color=with_color)
            )

            to_print.append(data)
            output = output[match_position + match_size :]

        for match in header_matches:
            header = binascii.unhexlify(match.group(1)).decode("ascii", "ignore")

            if filtering.is_header_interesting(
                header, fuzzer_output_path, file_or_action, intercepted_variables_info
            ):
                to_print.append(f"Header: {header}")

        for match in call_matches:
            try:
                call_information = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

            if filtering.is_call_interesting(
                call_information,
                in_admin_or_profile,
                fuzzer_output_path,
                file_or_action,
            ):
                to_print.append(
                    f"Call: {call_information['what']} arguments={call_information['data']}"
                )

        for data in to_print:
            data = trim_if_too_long(data)

            if data in self._already_printed:
                continue
            self._already_printed.add(data)

            if self._header_printed != file_or_action:
                self._header_printed = file_or_action
                print(
                    colored(
                        "%s (%s active installs) %s"
                        % (
                            fuzzer_output_path,
                            active_installs,
                            file_or_action,
                        ),
                        color="blue",
                        attrs=["bold"],
                        with_color=with_color,
                    )
                )
            print(
                data,
                colored(
                    trim_if_too_long("&".join(intercepted_variables_info)),
                    color="yellow",
                    with_color=with_color,
                ),
            )
        return len(to_print) > 0


def print_findings_from_folder(
    output_folder: str,
    min_active_installs: int = typer.Option(0),
    show_only_paths_containing: str = typer.Option(None),
):
    file_names = []
    for file_name in os.listdir(output_folder):
        if file_name.endswith(".json"):
            file_names.append(file_name)

    os.makedirs(os.path.join(output_folder, "scanned"), exist_ok=True)

    if show_only_paths_containing:
        file_names = [
            file_name
            for file_name in file_names
            if show_only_paths_containing in file_name
        ]

    file_names = list(
        reversed(
            sorted(
                file_names,
                key=lambda file_name: os.path.getmtime(
                    os.path.join(output_folder, file_name)
                ),
            )
        )
    )

    num_paths_with_printed_reports = 0

    use_console_features = sys.stdout.isatty()

    for file_name in tqdm(file_names) if use_console_features else file_names:
        file_path = os.path.join(output_folder, file_name)
        print(file_path)
        with open(file_path, "r") as f:
            if os.fstat(f.fileno()).st_size == 0:
                results = {}
            else:
                results = json.load(f)

        if int(results.get("active_installs", 0)) < min_active_installs:
            continue

        anything_printed = False

        if "command_results" in results:
            findings_printer = FindingsPrinter()
            for command in results["command_results"]:
                if "output" not in command:
                    command["output"] = ""
                if "stdout" not in command:
                    command["stdout"] = ""
                if "stderr" not in command:
                    command["stderr"] = ""

                anything_printed |= findings_printer.print_findings(
                    (command["output"] + command["stdout"] + command["stderr"])
                    .replace("\n", " ")
                    .replace("\r", " "),
                    file_path,
                    results["active_installs"],
                    command["object_name"],
                    with_color=use_console_features,
                )

        if anything_printed:
            num_paths_with_printed_reports += 1
        else:
            print(f"Nothing found in {file_name}. Archiving the report...")
            os.rename(
                os.path.join(output_folder, file_name),
                os.path.join(output_folder, "scanned", file_name),
            )
            subprocess.call(
                [
                    "gzip",
                    "-v9",
                    os.path.join(output_folder, "scanned", file_name),
                ]
            )

    print(f"Unique filepaths total: {len(file_names)}")

    if len(file_names) == 0:
        print("No reports to print. Maybe all have been archived?")
    else:
        print(
            f"Filepaths with report printed: {num_paths_with_printed_reports} "
            f"({100.0 * num_paths_with_printed_reports / len(file_names):.02f}%)"
        )


if __name__ == "__main__":
    typer.run(print_findings_from_folder)
