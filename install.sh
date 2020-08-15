#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

cp internet-monitor.service /etc/systemd/system/internet-monitor.service
systemctl daemon-reload
systemctl start internet-monitor.service
systemctl enable internet-monitor.service
