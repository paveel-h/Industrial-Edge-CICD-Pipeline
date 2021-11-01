FROM ubuntu:20.04
RUN apt-get -y update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN pip install requests-toolbelt
COPY ie-app-publisher-linux /usr/bin
RUN mkdir -p /app/src/workspace
WORKDIR /app/src/workspace
RUN ie-app-publisher-linux ws init