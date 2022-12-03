#!/bin/bash

if [ "$1" == '--reverse' ]; then
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_is_array(/is_array(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_parse_str(/parse_str(/g' {} +
else
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bis_array(/__garlic_is_array(/g' {} +
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bparse_str(/__garlic_parse_str(/g' {} +
fi
