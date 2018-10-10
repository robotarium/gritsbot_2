# gritsbot_2

# Setup Process

## 1 

Install latest Raspbian to SD card.  Your .zip file may have a different name.

```
unzip -p 2018-04-18-raspbian-stretch.zip | sudo dd status=progress of=/dev/sdX bs=4M conv=fsync 
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

Disable the *SSH console options, splash, and boot to the CLI*. Disable waiting for network on boot 

## 3 - Disable Unused Services 

Add to /boot/config.txt the text

```
# Disable the rainbow splash screen
disable_splash=1

# Disable bluetooth
dtoverlay=pi3-disable-bt
```

Suppress some output on boot by adding the 'quiet' flag to /boot/cmdline.txt.  The exact line may
be different.  However, you should just add the quiet flag at the specified location.

```
dwc\_otg.lpm\_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=32e07f87-02 rootfstype=ext4 elevator=deadline fsck.repair=yes quiet rootwait
```

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

## 2 - Install Docker

This section follows from the official (Docker)[https://docs.docker.com/install/linux/docker-ce/ubuntu/].  First, remove old versions of Docker.

```
sudo apt-get remove docker docker-engine docker.io
```

Next, install Docker using the convenience script.

```
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
```

Now tie Docker to the pi user so that we don't need sudo to use Docker.

```
sudo usermod -aG docker pi
```

