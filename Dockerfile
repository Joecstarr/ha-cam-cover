ARG BUILD_FROM
FROM $BUILD_FROM
RUN apk add --update --no-cache py3-opencv py3-requests py3-pillow py3-pyzbar
COPY ha_cam_cover /opt/ha_cam_cover
WORKDIR /opt
ENTRYPOINT [ "/usr/bin/python3", "-mha_cam_cover" ]
