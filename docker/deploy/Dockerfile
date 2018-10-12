#FROM arm32v6/alpine
ARG REPO=""
FROM ${REPO}docker

RUN apk add --no-cache bash

COPY ./update.sh /
COPY ./start_container.sh /

RUN apk update && apk upgrade

# Get python + deps.  Most of these are actually for netifaces install
RUN apk add --no-cache bash git python3 python3-dev gcc musl-dev linux-headers

ADD https://api.github.com/repos/robotarium/vizier/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/vizier
RUN cd vizier && python3 -m pip install .

ADD https://api.github.com/repos/robotarium/gritsbot_2/git/refs/heads/master version.json
RUN git clone https://github.com/robotarium/gritsbot_2
RUN cd gritsbot_2 && python3 -m pip install .

ENTRYPOINT [ "/update.sh" ]
CMD [ ]
