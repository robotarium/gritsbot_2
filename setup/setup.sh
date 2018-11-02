#!/bin/sh

DEL="-------"
FIN="DONE"

print_start() {
	echo "$DEL ""$1"" $DEL"
}

print_end() {
	echo "$DEL ""$FIN ""$1"" $DEL"	
}

STR="INSTALLING DOCKER"
print_start "$STR"
sudo apt-get remove docker docker-engine docker.io
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo usermod -aG docker pi
print_end "$STR"

STR="INSTALLING PYTHON AND DEPS"
print_start "$STR"
sudo apt-get install -y python3-pip git
sudo python3 -m pip install pyserial
print_end "$STR"

STR="DISABLING BLUETOOTH"
print_start "$STR"
sudo echo "# Disable bluetooth" >> /boot/config.txt
sudo echo "dtoverlay=pi3-disable-bt" >> /boot/config.txt
print_end "$STR"

STR="DISABLING UNUSED SERVICES"
print_start "$STR"
sudo apt-get purge --remove plymouth
sudo systemctl disable triggerhappy.service
sudo systemctl disable hciuart.service
sudo systemctl disable keyboard-setup.service
sudo systemctl disable dphys-swapfile.service
print_end "$STR"

STR="CLONING GIT REPOS"
print_start "$STR"
cd ~/
mkdir git
cd ~/git
git clone https://github.com/robotarium/gritsbot_2
git clone https://github.com/robotarium/mac_discovery
print_end "$STR"

STR="TURNING OFF WIFI POWER MANAGEMENT"
print_start "$STR"
sudo echo "/sbin/iw dev wlan0 set power_save off" >> /etc/rc.local
print_end "$STR"

STR="STARTING CONTAINERS"
print_start "$STR"
cd ~/git/gritsbot_2/docker
sudo ./docker_run.sh
sudo ./docker_watch.sh
cd ~/git/mac_discovery/docker
sudo ./docker_run.sh
print_end "$END"

# Delete me
#rm $0

