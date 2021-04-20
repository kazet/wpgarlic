#!/bin/sh

mkdir pages

wget http://127.0.0.1:8001/ -O pages/index.html

for i in `seq 1 10`; do
    wget http://127.0.0.1:8001/?p=$i -O pages/$i".html" -q
done
