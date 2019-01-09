# Things you need to know

## 1- Firmare Installation

- Go on MATLAB into the directory 'home/robotarium_matlab_backend/'
Run server_init.m to startup everything

- Run Robotarium in command window to get number of active Robots
Note: This is kind of status check to see if the number you're expecting is correct.

- To obtain IPs of robots that are currently on:
```
sudo python3 get_ip_by_mac.py ../config/mac_list.json wlp5s0

```
First argument is the json file containing all the ip addresses and second argument is the interface.

- ssh into the desired robot
- Check if git and docker are installed
- If git is not there:
```
sudo apt-get install git
```
- Install gritsbot2 repo (includes firmware file that we need to run):
```
git clone https://github.com/robotarium/gritsbot_2
```
- Change rc.local file so that all the necessary software is installed on the next startup
```
sudo nano /etc/rc.local
```
Note: Add the line "/home/pi/setup_service start" right before "exit 0" (last line).
- Restart PI to install firmware
```
sudo shutdown -r now
```
- Note
No need to remove the line we added to rc.local since the files "setup" & "setup_service" will be automatically removed upon the completion of the installation.
- Note 2
Normally, setup files should be already there already and installation should automatically happen upon the first boot. This is thanks to the fact that we already add the setup files when we flash the SD card.
- To check what's going on with the installation
This assuming that you gave the PI enough time to reboot of course.
Re-ssh into the PI and run:
```
tail -f /var/log/setup_firmware.log 
```
The command simply tells you what the log file contains. You should see it installing the different pieces of software such as python and docker.

- To check if everything is working after installation 
While ssh-ed, run:
```
docker ps
```
To know which containers are running.

You can also run:
```
docker logs firmware --follow --tail 50
```
To know what the container firware is printing for example. 
Note: The flag "follow" is to show what's being printed in a live fashion. The flag "tail" simply shows you the last x lines (in this case 50).


