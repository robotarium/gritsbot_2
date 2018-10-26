# Deploying the Docker registry

Once you've build the firmware, which is by default tagged as robotarium:firmware, you'll need to push it to the registry.  To do so, tag the robotarium:firmware container with the IP of the registry.  For example,
```
docker tag robotarium:firmware 192.168.1.8:5000/firmware
```

Then, push the re-tagged image.  For example,
```
docker push 192.168.1.8:5000/firmware
```
