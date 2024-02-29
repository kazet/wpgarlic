<?php

$_garlic_the_shortcode = $_SERVER['argv'][1];

include("/fuzzer/magic_payloads.php");
include('/var/www/html/wp-load.php');

reinitialize_magic();

wp_set_current_user(2, "subscriber");

echo call_user_func($shortcode_tags[$_garlic_the_shortcode], new MagicArrayOrObject("shortcode args", false));
