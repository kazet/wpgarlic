#!/bin/bash

touch /var/www/html/test_file_GARLIC
touch /var/www/html/wp-content/test_file_GARLIC
touch /var/www/html/wp-content/plugins/test_file_GARLIC
touch /var/www/html/wp-content/themes/test_file_GARLIC
touch /var/www/html/wp-admin/test_file_GARLIC
touch /var/www/html/wp-includes/test_file_GARLIC
chown -R www-data:www-data /var/www/html/
