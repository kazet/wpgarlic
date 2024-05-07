<?php

define('__GARLIC_PHP_SAPI', "cgi");

if (!function_exists("__garlic_php_sapi_name")) {
    function __garlic_php_sapi_name() {
        return "cgi";
    }
}

if (!function_exists("_unpatched_str_in_array")) {
    function _unpatched_str_in_array($needle, $haystack) {
        foreach ($haystack as $item) {
            if (!strcmp($needle, $item))
                return true;
        }
        return false;
    }
}


if (!function_exists("__garlic_array_key_exists")) {
    function __garlic_array_key_exists($key, $array) {
        if ($array instanceof MagicArray) {
            return isset($array[$key]);
        } else {
            return array_key_exists($key, $array);
        }
    }
}

if (!function_exists("__garlic_srand")) {
    function __garlic_srand() {
        echo "__GARLIC_CALL__ srand() __ENDGARLIC__";
    }
}

if (!function_exists("__garlic_trigger_error")) {
    function __garlic_trigger_error($msg, $level = E_USER_NOTICE) {
        # So that we skip fatal errors
        echo("Error: " . $msg);
    }
}

if (!function_exists("__garlic_getallheaders")) {
    function __garlic_getallheaders() {
        return new MagicArrayOrObject('getallheaders output', false);
    }
}

if (!function_exists("getallheaders")) {
    function getallheaders() {
        return __garlic_getallheaders();
    }
}

if (!function_exists('str_contains')) {
    // polyfill
    function str_contains($haystack, $needle) {
        // not using "===" so that we don't trigger the fake equality behavior
        if (!strcmp('', $needle)) {
            return true;
        }

        return false !== strpos($haystack, $needle);
    }
}

if (!function_exists("__garlic_file_exists")) {
    function __garlic_file_exists($path) {
        if (strpos($path, "GARLIC") !== false) {
            echo "__FILE_EXISTS_OF_GARLIC_DETECTED__".$path;
        }
        return file_exists($path);
    }
}


if (!function_exists("__garlic_array_merge")) {
    function __garlic_array_merge($original, ...$arrays) {
        foreach($arrays as $other) {
            if ($other instanceof MagicArray) {
                return $other;
            }
        }
        return array_merge($original, ...$arrays);
    }
}


if (!function_exists("__garlic_is_array")) {
    function __garlic_is_array($obj) {
        return ($obj instanceof MagicArray || is_array($obj));
    }
}

if (!function_exists("__garlic_parse_str")) {
    function __garlic_parse_str($str, &$out) {
        if (is_string($str) && str_contains($str, "GARLIC")) {
            $out = new MagicArrayOrObject('parse_str output', false);
        } else {
            parse_str($str, $out);
        }
    }
}


?>
