#!/bin/bash

if [ "$1" == '--reverse' ]; then
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\b__garlic_is_array(/is_array(/g' {} +
else
    find /var/www/html/ -name "*.php" -type f -exec sed -i 's/\bis_array(/__garlic_is_array(/g' {} +
fi
