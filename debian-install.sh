#!/bin/bash

clear

echo "------------------------------------"
echo " UPDATE APT SOURCES"
echo "------------------------------------"
apt-get update

echo ""
echo "------------------------------------"
echo " INSTALL PYTHON-DEV"
echo "------------------------------------"
apt-get --yes --force-yes install python-dev

echo ""
echo "------------------------------------"
echo " INSTALL PYTHON-DEV"
echo "------------------------------------"
apt-get --yes --force-yes install python-setuptools

echo ""
echo "------------------------------------"
echo " INSTALL PAHO-MQTT"
echo "------------------------------------"
easy_install paho-mqtt

echo ""
echo "------------------------------------"
echo " INSTALL PYSERIAL"
echo "------------------------------------"
easy_install pyserial

