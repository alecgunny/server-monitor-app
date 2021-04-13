FROM python:3.8-slim-buster
ENV DEBIAN_FRONTEND="noninteractive"
RUN set -ex \
        \
        && apt-get update && apt-get install -y --no-install-recommends git \
        \
        && pip install \
            attrs \
            flask \
            numpy \
            nvidia-pyindex==1.0.6 \
            pandas \
            requests \
            tblib \
            git+https://github.com/alecgunny/stillwater@multistream \
        && pip install tritonclient[all] \
        \
        && rm -rf /var/lib/apt/lists/*

EXPOSE 5000
ADD app.py app.py
ENV FLASK_APP=app.py LC_ALL=C.UTF-8 LANG=C.UTF-8
ENTRYPOINT flask run --host=0.0.0.0