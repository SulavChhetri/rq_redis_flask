FROM python:3.8-buster as base
WORKDIR /src

ARG GITHUB_ACCESS_TOKEN=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
RUN git config --global url."https://${GITHUB_ACCESS_TOKEN}@github.com".insteadOf "ssh://git@github.com"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY requirements-in-house.txt .
RUN pip install -r requirements-in-house.txt

COPY setup.py .

FROM base as prod
RUN pip install -e .

FROM base as dev
RUN pip install -e .[develop]