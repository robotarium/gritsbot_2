#FROM arm32v6/alpine
#ARG REPO=""
FROM arm32v6/docker

RUN apk add --no-cache bash

RUN apk add python3 git
RUN python3 -m pip install pyserial

COPY ./update.sh /
COPY ./start_container.sh /

ADD https://api.github.com/repos/robotarium/gritsbot_2/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/gritsbot_2

ENTRYPOINT [ "/update.sh" ]
CMD [ ]
