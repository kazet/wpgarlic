<?php


if (!function_exists("__garlic_is_array")) {
    function __garlic_is_array($obj) {
        return ($obj instanceof MagicArray || is_array($obj));
    }
}


?>
