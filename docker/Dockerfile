FROM arm32v6/alpine:3.8

COPY qemu-arm-static /usr/bin

RUN apk update && apk upgrade

# Get python + deps.  Most of these are actually for netifaces install
RUN apk add --no-cache git python3 python3-dev py3-pip gcc musl-dev linux-headers

ADD https://api.github.com/repos/robotarium/vizier/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/vizier
RUN cd vizier && python3 -m pip install .

ADD https://api.github.com/repos/robotarium/gritsbot_2/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/gritsbot_2
RUN cd gritsbot_2 && python3 -m pip install .

ARG ROBO_HOST
ARG ROBO_PORT

ENV ROBO_HOST ${ROBO_HOST}
ENV ROBO_PORT ${ROBO_PORT}

# Has to be in this format!  Docker doesn't like to interpret the env variables properly in JSON form
ENTRYPOINT python3 gritsbot_2/gritsbot/firmware.py -host ${ROBO_HOST} -port ${ROBO_PORT} gritsbot_2/config/mac_list.json
CMD [ ]
