FROM nginx:1.25-alpine

RUN apk add --no-cache curl tzdata \
    && rm -rf /var/cache/apk/*

ENV TZ=America/Sao_Paulo

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
