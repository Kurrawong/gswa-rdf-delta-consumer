ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-alpine

COPY --from=ghcr.io/astral-sh/uv:0.4.18 /uv /bin/uv

ADD . /app
WORKDIR /app
RUN uv sync --frozen
CMD ["uv", "run", "src/consumer.py"]
