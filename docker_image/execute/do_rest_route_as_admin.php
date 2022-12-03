<?php

$_garlic_the_route = explode("@", $_SERVER['argv'][1]);

include("/fuzzer/magic_payloads.php");
include('/var/www/html/wp-load.php');
include("/fuzzer/rest.php");

do_rest_route_with_user(1, "admin");
