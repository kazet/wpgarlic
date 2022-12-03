<?php

$_garlic_the_action = $_SERVER['argv'][1];
$_garlic_the_user = (int) $_SERVER['argv'][2];

include("/fuzzer/magic_payloads.php");
include("/fuzzer/user.php");
$current_user = new FakeUser($_garlic_the_user);

define('WP_ADMIN', true);

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
