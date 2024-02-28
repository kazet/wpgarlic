import binascii
import enum
import json
import os
import random
import string
import traceback
from typing import List, Optional

import requests
import typer

import config
from fuzzer_container import *
from nonces_storage import collect_nonces


class ObjectType(str, enum.Enum):
    plugin = "plugin"
    theme = "theme"


def get_dependencies(slug: str, description: str) -> List[str]:
    dependencies = []
    if ("cf7" in slug or "contact-form-7" in description.lower()) and slug != "contact-form-7":
        dependencies.append("contact-form-7")

    if ("woo" in slug or "woocommerce" in description.lower()) and slug != "woocommerce":
        dependencies.append("woocommerce")

    if ("elementor" in slug or "elementor" in description.lower()) and slug != "elementor":
        dependencies.append("elementor")

    if (
        "the-events-calendar" in slug or "the-events-calendar" in description.lower()
    ) and slug != "the-events-calendar":
        dependencies.append("the-events-calendar")
    return dependencies


def fuzz_object(
    object_type: ObjectType,
    slug_or_path: str,
    version: Optional[str] = None,
    revision: Optional[str] = None,
    enabled_features: Optional[str] = None,
    skip_fuzzing_second_time_without_dependencies: bool = False,
    actions_to_fuzz: str = "ALL",
    shortcodes_to_fuzz: str = "ALL",
    rest_routes_to_fuzz: str = "ALL",
    menu_actions_to_fuzz: str = "ALL",
    file_or_folder_to_fuzz: str = "OBJECT_ROOT",
    output_path: str = "data/object_fuzz_results",
):
    if not enabled_features:
        enabled_features = config.DEFAULT_ENABLED_FEATURES
    else:
        enabled_features = enabled_features.split(",")

    if slug_or_path.endswith(".zip") and os.path.exists(slug_or_path):
        slug = get_object_name_from_file(slug_or_path)
        object_info_dict = {
            "version": 0,
            "active_installs": 0,
            "sections": {"description": ""},
        }
        from_file = True
    else:
        slug = slug_or_path
        assert all([letter in string.ascii_letters + string.digits + "-_" for letter in slug])

        print("Looking for", slug)
        object_info_dict = requests.get(
            f"https://api.wordpress.org/{object_type.value}s/info/1.2/?action={object_type.value}_information"
            f"&request[slug]={slug}"
        ).json()
        from_file = False
        if "active_installs" not in object_info_dict:
            object_info_dict["active_installs"] = 1

    if file_or_folder_to_fuzz == "OBJECT_ROOT":
        file_or_folder_to_fuzz = f"/var/www/html/wp-content/{object_type}s/{slug}"

    if version is None:
        version = object_info_dict["version"]
    active_installs = object_info_dict["active_installs"]
    description = object_info_dict["sections"]["description"]

    dependencies = get_dependencies(slug, description)

    def fuzz(install_dependencies: bool):
        reinitialize_containers()

        try:
            if install_dependencies:
                for dependency in dependencies:
                    install_dependency(dependency)
                    activate_plugin(dependency)
                    visit_admin_homepage()

            if from_file:
                if object_type != ObjectType.plugin:
                    raise NotImplementedError()

                install_plugin_from_file(plugin_path)
                activation_problem = None
            elif revision:
                if object_type != ObjectType.plugin:
                    raise NotImplementedError()

                install_plugin_from_svn(slug, revision)
            else:
                if object_type == ObjectType.plugin:
                    install_plugin_from_slug(slug, version)
                elif object_type == ObjectType.theme:
                    install_theme_from_slug(slug, version)
                else:
                    raise NotImplementedError()
            try:
                if object_type == ObjectType.plugin:
                    activate_plugin(slug)
                elif object_type == ObjectType.theme:
                    activate_theme(slug)
                else:
                    raise NotImplementedError()
                activation_problem = None
            except Exception as e:
                activation_problem = repr(e)

            set_webroot_ownership()

            # This is to execute hooks in case it needs to do something
            # on first admin visit. Let's do this multiple times for sure.
            for i in range(3):
                visit_admin_homepage()

            copy_nonces_into_container(slug)
            patch_wordpress()
            patch_plugins_themes()

            container_id = get_container_id()

            exit_code = disconnect_network(container_id)
            assert exit_code == 0  # we don't want to fuzz on enabled networking

            disconnect_dns()

            command_results = []
            command_results_but_not_for_nonces = []
            tasks = list(
                {
                    "actions",
                    "actions_admin",
                    "menu_subscriber",
                    "menu_admin",
                    "files",
                    "pages_subscriber",
                    "pages_not_logged_in",
                    "rest_routes",
                    "rest_routes_admin",
                    "shortcodes",
                }
                & set(enabled_features)
            )
            random.shuffle(tasks)

            for task in tasks:
                try:
                    if task == "files":
                        command_results += fuzz_file_or_folder("RANDOM", file_or_folder_to_fuzz)
                    elif task == "actions":
                        command_results += fuzz_actions("RANDOM", actions_to_fuzz, slug)
                    elif task == "actions_admin":
                        command_results_but_not_for_nonces += fuzz_actions_admin("RANDOM", actions_to_fuzz, slug)
                    elif task == "rest_routes":
                        command_results += fuzz_rest_routes("RANDOM", rest_routes_to_fuzz, slug)
                    elif task == "rest_routes_admin":
                        command_results_but_not_for_nonces += fuzz_rest_routes_admin(
                            "RANDOM", rest_routes_to_fuzz, slug
                        )
                    elif task == "menu_subscriber":
                        command_results_but_not_for_nonces += fuzz_menu("RANDOM", menu_actions_to_fuzz, slug, 2)
                    elif task == "menu_admin":
                        command_results_but_not_for_nonces += fuzz_menu("RANDOM", menu_actions_to_fuzz, slug, 1)
                    elif task == "pages_subscriber":
                        command_results += fuzz_pages("RANDOM", 2)
                    elif task == "pages_not_logged_in":
                        command_results += fuzz_pages("RANDOM", 0)
                    elif task == "shortcodes":
                        command_results += fuzz_shortcodes("RANDOM", shortcodes_to_fuzz, slug)
                    else:
                        assert False
                except Exception:
                    traceback.print_exc()
                    continue

            # After fuzzing (when we're just looking for results), we unpatch
            # plugins/themes because we stop using the module that e.g. defines
            # __garlic_is_array.
            patch_plugins_themes(True)

            # We also need WordPress to not emit any logs that e.g. update_option
            # got called, because this would pollute output.
            patch_wordpress(True)

            if "find_in_files_after_fuzzing" in enabled_features:
                command_results_but_not_for_nonces += find_payloads_in_files()

            if "find_in_pages_after_fuzzing" in enabled_features:
                command_results += find_payloads_in_pages()

            if "find_in_admin_after_fuzzing" in enabled_features:
                command_results_but_not_for_nonces += find_payloads_in_admin()

            collect_nonces(slug, command_results)

            output = {
                "version": version,
                "active_installs": active_installs,
                "command_results": command_results + command_results_but_not_for_nonces,
                "activation_problem": activation_problem,
            }
        except Exception as e:
            traceback.print_exc()
            output = {
                "version": version,
                "active_installs": active_installs,
                "error": repr(e),
            }
        random_token = binascii.hexlify(os.urandom(16)).decode("ascii")
        with open(
            os.path.join(output_path, f"{slug}_{random_token}.json"),
            "w",
        ) as f:
            json.dump(output, f)

    fuzz(install_dependencies=True)
    if dependencies != [] and not skip_fuzzing_second_time_without_dependencies:
        fuzz(install_dependencies=False)


if __name__ == "__main__":
    typer.run(fuzz_object)
