FROM python:3.12.14-alpine3.24@sha256:d09d15e60962ca365d1cd544a48773bac9d33f2fb1b00f2aa0deec78ade7dc31 AS runtime

LABEL org.opencontainers.image.title="WindesAPI API-client" \
      org.opencontainers.image.description="Lokale onderwijsclient met Python, requests en curl" \
      org.opencontainers.image.vendor="Windesheim cybersecurityonderwijs" \
      org.opencontainers.image.licenses="MIT"

COPY client/requirements.txt /tmp/requirements.txt
RUN apk upgrade --no-cache \
    && apk add --no-cache curl \
    && pip install --no-cache-dir --disable-pip-version-check -r /tmp/requirements.txt \
    && adduser -D -u 10001 labclient

COPY client/entrypoint.sh /usr/local/bin/client-entrypoint
COPY LICENSE /usr/share/licenses/windesapi/LICENSE
RUN chmod 755 /usr/local/bin/client-entrypoint \
    && mkdir -p /workspace \
    && chown labclient:labclient /workspace

USER labclient
WORKDIR /workspace
ENV API_BASE_URL=http://api:8000

ENTRYPOINT ["client-entrypoint"]
CMD ["python", "/workspace/client.py"]
