FROM safir_nginx:2.0.0

COPY /dockerfile/prod/nginx/nginx.conf /etc/nginx/nginx.conf

ENTRYPOINT ["nginx", "-g", "daemon off;"]