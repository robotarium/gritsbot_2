docker run -d \
	-v /var/run/docker.sock:/var/run/docker.sock \
	--name=updater \
	--restart=always \
	robotarium:auto_update $1 $2
