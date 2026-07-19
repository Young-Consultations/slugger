FROM python:3.11-slim@sha256:baf89808ec37adeaab83cec287adb4a2afa4a11c1d51e961c7ec737877e61af6

ENV PYTHONNOUSERSITE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY constraints-ci.txt /tmp/slugger-constraints-ci.txt
RUN python -m pip download \
        --only-binary=:all: \
        --dest /opt/slugger-wheelhouse \
        --requirement /tmp/slugger-constraints-ci.txt \
    && python -m pip install \
        --no-index \
        --find-links /opt/slugger-wheelhouse \
        --constraint /tmp/slugger-constraints-ci.txt \
        pip setuptools wheel pytest \
    && groupadd --gid 1000 verifier \
    && useradd --uid 1000 --gid 1000 --create-home --home-dir /home/verifier verifier

ENV PIP_NO_INDEX=1 \
    SLUGGER_WHEELHOUSE=/opt/slugger-wheelhouse

WORKDIR /slugger
USER 1000:1000
