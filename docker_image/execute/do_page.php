<?php

$_garlic_file = $_SERVER['argv'][1];
$_garlic_query = $_SERVER['argv'][2];

$_garlic_query_parsed = array();
parse_str($_garlic_query, $_garlic_query_parsed);

include("/fuzzer/magic_payloads.php");
reinitialize_magic($_garlic_query_parsed, true, true);
include($_garlic_file);
