#!/bin/bash

if [ "$1" == '--reverse' ]; then
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_getallheaders(/getallheaders(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_array_merge(/array_merge(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_file_exists(/file_exists(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_is_array(/is_array(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_parse_str(/parse_str(/g' {} +
else
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bgetallheaders(/__garlic_getallheaders(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\barray_merge(/__garlic_array_merge(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bfile_exists(/__garlic_file_exists(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bis_array(/__garlic_is_array(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bparse_str(/__garlic_parse_str(/g' {} +
fi
