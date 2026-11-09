ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM ${BUILD_FROM}
RUN apk add --no-cache python3 librsvg ttf-dejavu
COPY climate_png.py climate.j2 run.sh /
RUN chmod a+x /run.sh
CMD ["/run.sh"]
