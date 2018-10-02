# gritsbot_2

# Setup Process

## 1 

Install latest Raspbian to SD card 

```
unzip -p 2018-04-18-raspbian-stretch.zip | sudo dd status=progress of=/dev/sdX bs=4M conv=fsync 
```
 
Navigate to boot partition
 
Place ssh, and wpa_supplicant.conf files in boot partition.

Example WPA supplicant file

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

## 2

Boot the PI and ssh to it 
 
Launch

```
sudo raspi-config
```

Disable the SSH console options, splash, and boot to the CLI. Disable waiting for network on boot 

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
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=32e07f87-02 rootfstype=ext4 elevator=deadline fsck.repair=yes quiet rootwait
```

Remove plymouth with 

```
sudo apt-get purge --remove plymouth
```

Disable unused services with 

sudo systemctl disable triggerhappy.service
sudo systemctl disable hciuart.service
#sudo systemctl disable apt-daily.service
sudo systemctl disable keyboard-setup.service
sudo systemctl disable dphys-swapfile.service


