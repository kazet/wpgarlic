#!/bin/sh

curl 'http://127.0.0.1:8001/wp-login.php' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: wordpress_test_cookie=WP%20Cookie%20check' \
  --data-raw 'log=admin&pwd=admin&wp-submit=Log+In&testcookie=1' -c /tmp/cookies.jar

sed -i -e "s/^#HttpOnly_//" /tmp/cookies.jar

timeout 240 wget \
    --quiet \
    --recursive \
    --level=3 \
    --load-cookies=/tmp/cookies.jar \
    --keep-session-cookies=on \
    --include-directories=/wp-admin/ \
    --domains=127.0.0.1 \
    --reject-regex='.*(customize.php|theme-editor.php|plugins.php|update.php|/js/|plugin-install.php|plugin-editor.php|site-health.php).*' \
    http://127.0.0.1:8001/wp-admin/
