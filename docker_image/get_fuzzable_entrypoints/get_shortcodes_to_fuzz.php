<?php

include("/fuzzer/functions.php");
include('/var/www/html/wp-load.php');

foreach ($shortcode_tags as $k => $v) {
        echo "SHORTCODE: " . $k . "\n";
}
