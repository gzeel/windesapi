FROM python:3.12.14-alpine3.24@sha256:d09d15e60962ca365d1cd544a48773bac9d33f2fb1b00f2aa0deec78ade7dc31 AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/lab

RUN apk upgrade --no-cache

COPY requirements.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

FROM base AS test

COPY requirements-test.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements-test.txt
COPY app ./app
COPY tests ./tests
COPY docs ./docs
COPY compose.yaml ./compose.yaml
COPY lab-settings.json ./lab-settings.json
COPY solution ./solution
ENV LAB_SETTINGS_PATH=/opt/lab/lab-settings.json \
    LAB_DB_PATH=/tmp/lab-test.db \
    LAB_AUDIT_LOG_PATH=/tmp/lab-audit.log
CMD ["pytest", "-q"]

FROM base AS runtime

LABEL org.opencontainers.image.title="WindesAPI API-lab" \
      org.opencontainers.image.description="Bewust kwetsbaar lokaal onderwijs-lab; geen productievoorbeeld" \
      org.opencontainers.image.vendor="Windesheim cybersecurityonderwijs" \
      org.opencontainers.image.licenses="MIT"

COPY app /opt/lab-template/app
COPY lab-settings.json /opt/lab-template/lab-settings.json
COPY templates /opt/lab-template/templates
COPY docker/labctl.py /usr/local/lib/labctl.py
COPY LICENSE /usr/share/licenses/windesapi/LICENSE

RUN adduser -D -u 10001 labuser \
    && for command in lab-help lab-reset lab-start lab-check lab-status lab-log; do \
         ln -s /usr/local/lib/labctl.py "/usr/local/bin/$command"; \
       done \
    && chmod 755 /usr/local/lib/labctl.py \
    && mkdir -p /workspace \
    && chown -R labuser:labuser /workspace /opt/lab-template

USER labuser
WORKDIR /workspace

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["lab-start"]
