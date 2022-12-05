FROM python:3.8-buster as base
WORKDIR /src

ARG GITHUB_ACCESS_TOKEN
RUN git config --global url."https://${GITHUB_ACCESS_TOKEN}@github.com".insteadOf "ssh://git@github.com"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY setup.py .

FROM base as prod
RUN pip install -e .

FROM base as dev
RUN pip install -e .[develop]