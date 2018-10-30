FROM arm32v6/alpine

COPY qemu-arm-static /usr/bin

RUN apk update && apk upgrade

# Get python + deps.  Most of these are actually for netifaces install
RUN apk add git python3 python3-dev gcc musl-dev linux-headers

ADD https://api.github.com/repos/robotarium/vizier/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/vizier
RUN cd vizier && python3 -m pip install .

ADD https://api.github.com/repos/robotarium/gritsbot_2/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/gritsbot_2
RUN cd gritsbot_2 && python3 -m pip install .

ARG ROBO_HOST
ARG ROBO_PORT

ENV ROBOT_HOST ${ROBO_HOST}
ENV ROBOT_PORT ${ROBOT_PORT}

ENTRYPOINT [ "python3", "gritsbot_2/gritsbot/firmware.py", "-host", "$ROBO_HOST", "-port", "$ROBO_PORT", "gritsbot_2/config/maclist.json" ]


