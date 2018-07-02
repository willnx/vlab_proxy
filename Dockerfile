FROM nginx:1.15.0-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY server.* /etc/ssl/
