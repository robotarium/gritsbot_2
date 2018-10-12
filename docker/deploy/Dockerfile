FROM arm32v6/docker

RUN apk add --no-cache bash

COPY ./update.sh /
COPY ./start_container.sh /

ENTRYPOINT [ "/update.sh" ]
CMD [ ]
