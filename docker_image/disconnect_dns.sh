#!/bin/bash

echo "`dig +short db1` db1" >> /etc/hosts
echo "nameserver `dig +short dns1`" > /etc/resolv.conf
