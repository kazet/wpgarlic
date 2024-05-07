#!/bin/bash

if [ "$1" == '--reverse' ]; then
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__GARLIC_PHP_SAPI\b/PHP_SAPI/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_php_sapi_name(/php_sapi_name(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_trigger_error(/trigger_error(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_srand(/srand(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_array_key_exists(/array_key_exists(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_getallheaders(/getallheaders(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_array_merge(/array_merge(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_file_exists(/file_exists(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_is_array(/is_array(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_parse_str(/parse_str(/g' {} +
else
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bPHP_SAPI\b/__GARLIC_PHP_SAPI/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bphp_sapi_name(/__garlic_php_sapi_name(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\btrigger_error(/__garlic_trigger_error(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bsrand(/__garlic_srand(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\barray_key_exists(/__garlic_array_key_exists(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bgetallheaders(/__garlic_getallheaders(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\barray_merge(/__garlic_array_merge(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bfile_exists(/__garlic_file_exists(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bis_array(/__garlic_is_array(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bparse_str(/__garlic_parse_str(/g' {} +
fi

# TODO reverse
python3 /fuzzer/strip_php_array_annotations.py
