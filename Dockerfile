FROM haproxy:1.8.8-alpine
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
RUN mkdir -p /etc/vlab/proxy
COPY server.pem /etc/vlab/proxy/server.pem
COPY *.http /etc/vlab/proxy/
RUN apk update && apk upgrade
