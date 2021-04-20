<?php

include("/fuzzer/functions.php");
include('/var/www/html/wp-load.php');

foreach ($GLOBALS['wp_filter'] as $k => $v) {
        if (substr($k, 0, 8) == "wp_ajax_") echo "AJAX: " . $k . "\n";
}
