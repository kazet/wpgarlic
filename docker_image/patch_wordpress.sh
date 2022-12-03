#!/bin/bash

if [ "$1" == '--reverse' ]; then
    cp /var/www/html/wp-includes/formatting.php.orig /var/www/html/wp-includes/formatting.php
    cp /var/www/html/wp-settings.php.orig /var/www/html/wp-settings.php
    cp /var/www/html/wp-load.php.orig /var/www/html/wp-load.php
    cp /var/www/html/wp-includes/option.php.orig /var/www/html/wp-includes/option.php
    cp /var/www/html/wp-includes/post.php.orig /var/www/html/wp-includes/post.php
    cp /var/www/html/wp-includes/functions.php.orig /var/www/html/wp-includes/functions.php
    cp /var/www/html/wp-includes/pluggable.php.orig /var/www/html/wp-includes/pluggable.php
    cp /var/www/html/wp-includes/user.php.orig /var/www/html/wp-includes/user.php
    cp /var/www/html/wp-includes/wp-db.php.orig /var/www/html/wp-includes/wp-db.php
else
    cp /var/www/html/wp-includes/formatting.php /var/www/html/wp-includes/formatting.php.orig
    cp /var/www/html/wp-settings.php /var/www/html/wp-settings.php.orig
    cp /var/www/html/wp-load.php /var/www/html/wp-load.php.orig
    cp /var/www/html/wp-includes/option.php /var/www/html/wp-includes/option.php.orig
    cp /var/www/html/wp-includes/post.php /var/www/html/wp-includes/post.php.orig
    cp /var/www/html/wp-includes/functions.php /var/www/html/wp-includes/functions.php.orig
    cp /var/www/html/wp-includes/pluggable.php /var/www/html/wp-includes/pluggable.php.orig
    cp /var/www/html/wp-includes/user.php /var/www/html/wp-includes/user.php.orig
    cp /var/www/html/wp-includes/wp-db.php /var/www/html/wp-includes/wp-db.php.orig

    sed -i '/^function update_option(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "update_option", "data" => array("name" => $option, "value" => print_r($value, true)))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/option.php
    sed -i '/^function delete_option(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "delete_option", "data" => array("name" => $option))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/option.php
    sed -i '/^function update_site_option(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "update_site_option", "data" => array("name" => $option, "value" => print_r($value, true)))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/option.php
    sed -i '/^function delete_site_option(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "delete_site_option", "data" => array("name" => $option))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/option.php
    sed -i '/^function wp_delete_post(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "wp_delete_post", "data" => array("id" => $postid))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/post.php
    sed -i '/^function wp_insert_post(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "wp_insert_post", "data" => $postarr)) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/post.php
    sed -i '/^function wp_update_post(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "wp_update_post", "data" => $postarr)) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/post.php
    sed -i '/^function update_post_meta(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "update_post_meta", "data" => array("post_id"=>$post_id, "meta_key"=>$meta_key, "meta_value"=>$meta_value))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/post.php
    sed -i '/^function maybe_unserialize(/a if (strpos($data, "GARLIC") !== false) { fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "maybe_unserialize", "data" => $data)) . "__ENDGARLIC__\\n"); }' \
        /var/www/html/wp-includes/functions.php
    sed -i '/^\s*function wp_mail(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "wp_mail", "data" => array("to" => $to, "subject" => $subject))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/pluggable.php
    # These are nonces that are easy to obtain (wp_rest and when the action is user-controlled), therefore
    # let's treat is as correct nonce.
    sed -i '/^\s*function wp_create_nonce(/a return "__GARLIC_NONCE__" . $action . "__ENDGARLIC__"; ' \
        /var/www/html/wp-includes/pluggable.php
    sed -i '/^\s*function wp_verify_nonce(/a global $_garlic_found_nonces; if ($action == "wp_rest" || strstr($action, "GARLIC") > 0 || in_array($action, $_garlic_found_nonces)) { return 1; }' \
        /var/www/html/wp-includes/pluggable.php
    sed -i '/^function wp_insert_user(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "wp_insert_user", "data" => $userdata)) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/user.php
    sed -i '/^function get_users(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "get_users", "data" => $args)) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/user.php
    sed -i '/^function wp_delete_user(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "wp_delete_user", "data" => array("id"=>$id))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/user.php
    sed -i '/^function update_user_meta(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "update_user_meta", "data" => array("user_id"=>$user_id, "meta_key"=>$meta_key, "meta_value"=>$meta_value))) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/user.php
    sed -i '/^\s*public function query(/a fwrite(STDERR,  "__GARLIC_CALL__" . json_encode(array("what" => "query", "data" => $query)) . "__ENDGARLIC__\\n");' \
        /var/www/html/wp-includes/wp-db.php

    patch /var/www/html/wp-settings.php /fuzzer/wordpress_patches/wp-settings.php.patch
    patch /var/www/html/wp-load.php /fuzzer/wordpress_patches/wp-load.php.patch

    # This patch fixes esc_url so that it doesn't use equality but strcmp. Because equalty is hacked
    # so that our payloads randomly compare as equal to anything, this caused that URLs sometimes were
    # returned unescaped - and led to false positives.
    patch /var/www/html/wp-includes/formatting.php /fuzzer/wordpress_patches/formatting.php.patch
fi
