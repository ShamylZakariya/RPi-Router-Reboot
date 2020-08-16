#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

systemctl stop internet-monitor.service
systemctl start internet-monitor.service
