<?php

$_garlic_file = $_SERVER['argv'][1];
$_garlic_query = $_SERVER['argv'][2];
$_garlic_user_id = $_SERVER['argv'][3];

$_garlic_query_parsed = array();
parse_str($_garlic_query, $_garlic_query_parsed);

include("/fuzzer/magic_payloads.php");
include("/fuzzer/user.php");
reinitialize_magic($_garlic_query_parsed, true, true);

if ($_garlic_user_id) {
       $user_id = (int) $_garlic_user_id;
       function wp_validate_auth_cookie($_1) {
               global $user_id;
               return $user_id;
       }
}

include($_garlic_file);
