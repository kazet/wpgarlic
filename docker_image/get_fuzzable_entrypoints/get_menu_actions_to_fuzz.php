<?php

$_garlic_the_action = $_SERVER['argv'][1];

define('WP_ADMIN', true);

include("/fuzzer/functions.php");
include("/fuzzer/set_admin.php");
include('/var/www/html/wp-load.php');
include('/var/www/html/wp-admin/includes/admin.php');
include('/var/www/html/wp-admin/menu.php');

foreach($_registered_pages as $key => $value) {
    echo "MENU: " . $key . "\n";
}

