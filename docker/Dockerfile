FROM arm32v6/alpine

RUN apk update && apk upgrade

# Get python
RUN apk add git python3 python3-dev gcc musl-dev linux-headers

ARG GIT-RECLONE

RUN git clone https://github.com/robotarium/vizier
RUN cd vizier && python3 -m pip install .

RUN git clone https://github.com/robotarium/gritsbot_2
RUN cd gritsbot_2 && python3 -m pip install .
