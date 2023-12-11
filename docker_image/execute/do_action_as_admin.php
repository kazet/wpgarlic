<?php

$_garlic_the_action = $_SERVER['argv'][1];

define('DOING_AJAX', true);
define('WP_ADMIN', true);

include("/fuzzer/magic_payloads.php");
include("/fuzzer/user.php");
include("/fuzzer/set_admin.php");
include('/var/www/html/wp-load.php');

require_once '/var/www/html/wp-admin/includes/admin.php';

reinitialize_magic();

$_SERVER['SCRIPT_FILENAME'] = "/wp-admin/admin-ajax.php";

do_action('admin_init');

/*
 * This is to fix if some filtering of $_GET that may have
 * happened when loading plugins
 */
reinitialize_magic();

do_action($_garlic_the_action);
