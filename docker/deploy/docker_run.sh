docker run -d \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--device $(python3 -m gritsbot.utils.detect_serial):/dev/ttyACM0 \
	--name=updater \
	--restart=always \
	robotarium:auto_update $1 $2
