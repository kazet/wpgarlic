FROM wordpress:6.1.1-php7.4-apache

RUN apt-get update
RUN apt-get -yy install \
    dnsutils \
    vim \
    git \
    default-mysql-client \
    pkg-config \
    build-essential \
    autoconf \
    bison \
    re2c \
    libxml2-dev \
    libsqlite3-dev \
    zlib1g-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libldb-dev \
    libldap2-dev \
    libonig-dev \
    libxslt1-dev \
    python3 \
    curl \
    subversion \
    zip \
    wget

RUN cp /usr/local/bin/php /usr/local/bin/php.orig
COPY compile_php.sh /fuzzer/compile_php.sh
COPY php_source_patch.patch /fuzzer/php_source_patch.patch

RUN /fuzzer/compile_php.sh

RUN docker-php-ext-configure opcache
RUN docker-php-ext-install opcache
RUN docker-php-ext-enable opcache

RUN docker-php-ext-configure sockets
RUN docker-php-ext-install sockets
RUN docker-php-ext-enable sockets

RUN docker-php-ext-configure pcntl
RUN docker-php-ext-install pcntl
RUN docker-php-ext-enable pcntl

# I know there is a still decreasing number of sites with this configuration, but let's
# assume for now we want to observe bugs of that kind.
RUN bash -c 'echo "allow_url_include = On" > /usr/local/etc/php/conf.d/allow.ini'

RUN bash -c "cd / && curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar"
RUN bash -c "cd / && git clone https://github.com/vishnubob/wait-for-it"

COPY apache_config/000-default.conf /etc/apache2/sites-enabled/
COPY apache_config/ports.conf /etc/apache2/

COPY dump.sql /fuzzer/dump.sql

COPY magic_payloads.php /fuzzer/magic_payloads.php
COPY functions.php /fuzzer/functions.php
COPY set_admin.php /fuzzer/set_admin.php
COPY user.php /fuzzer/user.php
COPY blocklists /fuzzer/blocklists

COPY get_fuzzable_entrypoints /fuzzer/get_fuzzable_entrypoints
COPY fuzz /fuzzer/fuzz
COPY execute /fuzzer/execute

COPY strip_php_array_annotations.py /fuzzer/

COPY create_findable_files.sh /fuzzer/create_findable_files.sh
COPY disconnect_dns.sh /fuzzer/disconnect_dns.sh
COPY download_admin.sh /fuzzer/download_admin.sh
COPY download_pages.sh /fuzzer/download_pages.sh
COPY just_visit_admin_homepage.sh /fuzzer/just_visit_admin_homepage.sh
COPY nodebug.sh /fuzzer/nodebug.sh
COPY patch_plugins_themes.sh /fuzzer/patch_plugins_themes.sh
COPY patch_wordpress.sh /fuzzer/patch_wordpress.sh

COPY test /fuzzer/test
COPY wordpress_patches /fuzzer/wordpress_patches

COPY php.ini /usr/local/lib/php.ini
COPY rest.php /fuzzer/rest.php

RUN mkdir /opcache
