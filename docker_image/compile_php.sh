#!/bin/bash

cd /fuzzer

git clone https://github.com/php/php-src

cd php-src/

git checkout php-7.4.16

git apply /fuzzer/php_source_patch.patch

./buildconf --force
./configure \
  --enable-mbstring \
  --with-curl \
  --with-openssl \
  --enable-soap \
  --with-mysqli \
  --with-ldap \
  --enable-intl \
  --with-xsl \
  --with-zlib
make
make install
