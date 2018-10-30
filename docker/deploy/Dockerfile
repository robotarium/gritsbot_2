FROM arm32v6/docker 

RUN apk add --no-cache bash

COPY ./update.sh /
COPY ./start_container.sh /

ARG BASE_IMAGE
ARG REGISTRY

ENV BASE_IMAGE ${BASE_IMAGE}
ENV REGISTRY ${REGISTRY}

ENTRYPOINT [ "/update.sh" ]
CMD [ ]
