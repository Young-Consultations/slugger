FROM python:3.11-slim@sha256:baf89808ec37adeaab83cec287adb4a2afa4a11c1d51e961c7ec737877e61af6

ENV PYTHONNOUSERSITE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m pip install --no-cache-dir setuptools==70.3.0 wheel==0.43.0 pytest==8.3.5 \
    && groupadd --gid 1000 verifier \
    && useradd --uid 1000 --gid 1000 --create-home --home-dir /home/verifier verifier

ENV PIP_NO_INDEX=1

WORKDIR /slugger
USER 1000:1000
