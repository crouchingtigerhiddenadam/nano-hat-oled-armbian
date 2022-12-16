#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please re-run as root user."
  exit
fi

# Get dependencies from APT
apt -y install libjpeg-dev libfreetype6-dev git python3 python3-dev \
  python3-pip python3-setuptools python3-smbus python3-wheel ttf-dejavu \
  zlib1g-dev python3-libgpiod

# Install image and pillow
pip3 install image pillow

# Get the code
if [ -d "/tmp/nano-hat-oled-armbian" ]
then
  rm /tmp/nano-hat-oled-armbian -rf
fi
cd /tmp
git clone https://github.com/crouchingtigerhiddenadam/nano-hat-oled-armbian
cd ./nano-hat-oled-armbian

# Make the program directory
if [ ! -d "/usr/share/nanohatoled" ]
then
  mkdir /usr/share/nanohatoled
fi

# Copy program files
mv oled-start3.py /usr/share/nanohatoled/
mv splash.png /usr/share/nanohatoled/

# Copy service file
mv nanohatoled.service /etc/systemd/system
systemctl daemon-reload

# Move to directory
cd /usr/share/nanohatoled/

# Start OLED
systemctl enable nanohatoled.service
systemctl start nanohatoled.service
