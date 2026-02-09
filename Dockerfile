# Use a lightweight Ubuntu-like image
FROM python:3.13-slim AS build

RUN apt-get update && apt-get install -y git

RUN useradd -m appuser
USER appuser

WORKDIR /src
#COPY requirements.txt .

COPY pyproject.toml LICENSE README.md .
COPY .git .git
COPY mcp_trusted_python mcp_trusted_python
# Install python packages for linting and security scanning
#RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt
# RUN ls -al; exit 1
RUN set -x && python -m venv build \
    && . build/bin/activate \
    && pip install -U pip hatchling hatch-vcs \
    && pip install .[dev] \
    && hatch build
# RUN pip install -e .[dev]; hatch build

FROM python:3.13-slim
WORKDIR /src/dist
COPY --from=build /src/dist/*.whl /src/dist
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* 
# Add non-root user
RUN useradd -m appuser
USER appuser

WORKDIR /app

#COPY mcp_tool.py /app/mcp_tool.py
ENV PYTHONUNBUFFERED=1 \
    PATH=$PATH:/home/appuser/.local/bin
RUN pip install --user /src/dist/*whl
# entrypoint
ENTRYPOINT ["mcp-trusted-python"]
