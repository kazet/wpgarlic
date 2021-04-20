<?php

include("/fuzzer/functions.php");
include('/var/www/html/wp-load.php');

function startswith($text, $prefix ) {
  return strpos($text, $prefix) === 0;
}

foreach (rest_get_server()->get_routes() as $key=>$handlers) {
	if (
			$key == '/' ||
			startswith($key, "/batch/") ||
			startswith($key, "/oembed/") ||
			startswith($key, "/wp/") ||
			startswith($key, "/wp-site-health/")) {
		continue;
	}
	foreach($handlers as $handler_key => $handler) {
		echo "REST_ROUTE: " . $key . "@" . $handler_key . "\n";
	}
}
