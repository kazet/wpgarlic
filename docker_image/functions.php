<?php


if (!function_exists("__garlic_is_array")) {
    function __garlic_is_array($obj) {
        return ($obj instanceof MagicArray || is_array($obj));
    }
}

if (!function_exists("__garlic_parse_str")) {
    function __garlic_parse_str($str, &$out) {
        if (str_contains($str, "GARLIC")) {
            $out = new MagicArrayOrObject('parse_str output', false);
        } else {
            parse_str($str, $out);
        }
    }
}


?>
