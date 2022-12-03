<?php

$_garlic_the_action = $_SERVER['argv'][1];

define('DOING_AJAX', true);
define('WP_ADMIN', true);

include("/fuzzer/magic_payloads.php");
include('/var/www/html/wp-load.php');

require_once '/var/www/html/wp-admin/includes/admin.php';

reinitialize_magic();

do_action( 'admin_init' );

if (strstr($_garlic_the_action, '_nopriv_') === false) {
    wp_set_current_user(2, "subscriber");
}

/*
 * This is to fix if some filtering of $_GET that may have
 * happened when loading plugins
 */
reinitialize_magic();

do_action($_garlic_the_action);
