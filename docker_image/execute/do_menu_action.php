<?php

$_garlic_the_action = $_SERVER['argv'][1];

define('WP_ADMIN', true);

include("/fuzzer/magic_payloads.php");
include("/fuzzer/set_admin.php");
include('/var/www/html/wp-load.php');
include('/var/www/html/wp-admin/includes/admin.php');

include('/var/www/html/wp-admin/menu.php');

reinitialize_magic();

do_action('admin_init');

/*
 * This is to fix if some filtering of $_GET that may have
 * happened when loading plugins
 */
reinitialize_magic();

do_action($_garlic_the_action);
