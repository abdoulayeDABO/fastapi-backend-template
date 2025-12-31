#######################################
# Using pip to install dependencies
#######################################


# FROM python:3.12-slim-trixie

# WORKDIR /app

# COPY ./requirements.txt /app/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# RUN python -m venv /app/.venv

# ENV PATH="/app/.venv/bin::$PATH"

# COPY ./scripts /app/scripts

# COPY ./app /app/app

# COPY ./tests /app/tests

# COPY ./alembic.ini /app/

# ENV PYTHONPATH=/app

# EXPOSE 8000

# CMD ["fastapi", "run", "app/main.py", "--port", "8000"]



#######################################
# Using uv to install dependencies
#######################################


FROM python:3.12-slim-trixie

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.9.18  /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Disable development dependencies
ENV UV_NO_DEV=1

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Copy project files
COPY ./scripts /app/scripts

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

COPY ./app /app/app
COPY ./tests /app/tests

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
