# Setup Process for the gritsbot\_2

# 1 - Making the Base Image

This section details how to make the base image.  Relatively few changes are made to keep the image small.  Once the changes in this section have been made, copy the new image to an SD card and use that as the base image.

## 1 - Load the RPi image onto an SD card

Install latest Raspbian lite to an SD card.  Your .zip file may have a different name. Now, connect the SD card to your computer and unmount it with 
```
umount /dev/<your card>
``` 

You can see the card (probably) with 
```
lsblk
```

```
unzip -p 2018-10-09-raspbian-stretch-lite.zip | sudo dd status=progress of=/dev/sdX bs=4M conv=fsync 
```
 
Navigate to boot partition.  Place ssh, and wpa\_supplicant.conf files in boot partition.

```
cd <path_to>/boot
touch ssh 
touch wpa_supplicant.conf
```

Now, edit the wpa\_supplicant.conf file to something like the following.  Example WPA supplicant file:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
     ssid="Your network name/SSID"
     psk="Your WPA/WPA2 security key"
     key_mgmt=WPA-PSK
}
```

## 2 - Raspi Config

Boot the PI and ssh to it.  Then, launch

```
sudo raspi-config
```

Disable the **SSH console options, splash, and waiting for network on boot.** Enable **boot to the CLI**.  Remain SSHd to the RPi for the next steps.

## 3 - Disable Unused Services 

Add to /boot/config.txt the text

```
# Disable bluetooth
dtoverlay=pi3-disable-bt
```

# 2 - Automated Setup

This section assumes that you have built a base image as previously detailed.

## 1 - Automatic Installation

To install the firmware automatically, move the setup script to the directory /home/pi on the SD card.  Then, place the script setup\_service in the /etc/init.d directory.  When the pi starts, the items in this section will be automatically executed; then, the script deletes itself.  The log for the installation process can be viewed at /var/log/setup\_firmware.log

## 2 - Manual Installation

This section details the installation process for the firmware.  This process can be made automatic via the setup scripts.

### 1 Remove Unused Services

Remove plymouth with 

```
sudo apt-get purge --remove plymouth
```

Disable unused services with 

```
sudo systemctl disable triggerhappy.service
sudo systemctl disable hciuart.service
sudo systemctl disable keyboard-setup.service
sudo systemctl disable dphys-swapfile.service
```

### 2 - Install Docker

This section follows from the official (Docker)[https://docs.docker.com/install/linux/docker-ce/ubuntu/].  First, remove old versions of Docker.

```
sudo apt-get remove docker docker-engine docker.io
```

Next, install Docker using the convenience script.

```
curl -fsSL get.docker.com -o get-docker.sh && export VERSION=18.06 && sh get-docker.sh
```

Now tie Docker to the pi user so that we don't need sudo to use Docker.

```
sudo usermod -aG docker pi
```

### 3 - Clone Git Repos and install Deps

Install pip for python3

```
sudo apt-get install python3-pip
```

To clone the firmware, run
```
sudo apt-get install git
git clone https://github.com/robotarium/gritsbot_2
```

Also, install the MAC discovery repository
```
git clone https://github.com/robotarium/mac_discovery
```

as well as the python serial library used to communicate to the robot.

```
python3 -m pip install pyserial
```

### 4 - WiFi Power Management

Turn off power management by adding the line
```
/sbin/iw dev wlan0 set power_save off
```

in the file /etc/rc.local.  This line disables WiFi power management on boot.

### 5 - Start necessary containers

From wherever the git repository is cloned, run 
```
cd <path_to_gritsbot_2_repo>/docker
./docker_run.sh
./docker_watch.sh
```
which will permanently start a Docker container running the firmware and the watchtower container.  Watchtower watches containers and automatically updates them from Dockerhub.  This watchtower instance
checks and updates **all running containers**, so this instance will also update the MAC container as well.

Start MAC discovery as well with
```
cd <path_to_mac_discovery_repo>/docker
./docker_run.sh
```

# DEPRECATED - Setup Auto Deployment

Most of this info is from the (docker guide to registries)[https://docs.docker.com/registry/deploying/].

Alternatively, you may set up automatic deployment so that each robot updates on its own.  In this case, navigate to the registry directory and 
start the registry for the container.  

Obtain the registry on the **HOST** computer by running 
```
docker run -d -p 5000:5000 --restart=always --name registry registry:2
```
which will pull and run the container.  To only pull,
```
docker pull registry:2
```
should work

Under whatever the registry's computer's IP is, allow this in the file located at 
```
/etc/docker/daemon.json
```
In particular, add the lines
```
{ "insecure-registries": ["<ip_of_registry_computer>:5000"] }
```
Put in the IP right away.  **Errors in this script will kill the Docker service, so be careful!**

For example,
```
{ "insecure-registries": ["192.168.1.8:5000"] }
```
These lines must be added on the **host machine** as well as **all the robots.**  After you've added these lines, restart the Docker service with 
```
sudo /etc/init.d/docker restart
```

Push the firmware to the registry with 
```
docker tag robotarium:firmware <ip_of_registry_computer>:5000/firmware
docker push 192.168.1.8:5000/firmware
```
which will push the firmware container to the registry under the name firmware and the (default) latest tag.

You can check the current images maintained by the registry by checking the catalog with the command
```
curl -X GET 192.168.1.8:5000/v2/_catalog
```

Now, on the robot, navigate to the docker/deploy directory and build the robotarium:updater container.  This container will automatically update 
and restart the firmware container by pulling from the designated registry.


