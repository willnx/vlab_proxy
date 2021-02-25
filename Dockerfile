FROM nginx:1.19-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY server.* /etc/ssl/
