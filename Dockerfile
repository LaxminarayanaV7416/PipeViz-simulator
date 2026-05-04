FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install bun in a system path so nonroot can execute it
ENV BUN_INSTALL=/usr/local/bun
RUN apt-get update \
 && apt-get install -y curl zip unzip \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL https://bun.sh/install | bash \
 && chmod -R a+rx /usr/local/bun

ENV PATH="/usr/local/bun/bin:/app/.venv/bin:$PATH"


# Setup a non-root user (same as backend Dockerfile)
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

# -------- Backend (pipeviz) --------
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

WORKDIR /app/pipeviz
COPY pipeviz/uv.lock pipeviz/pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY pipeviz /app/pipeviz
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# -------- Frontend (pipeviz-ui) --------
WORKDIR /app/pipeviz-ui
COPY pipeviz-ui/package.json pipeviz-ui/bun.lock ./
RUN bun install --frozen-lockfile
COPY pipeviz-ui /app/pipeviz-ui
RUN chown -R nonroot:nonroot /app/pipeviz-ui

# Switch to non-root user
USER nonroot

EXPOSE 5001
EXPOSE 5173

# Run both dev servers (backend + frontend)
CMD ["sh", "-c", "cd /app/pipeviz && uv run main.py --port 5001 & cd /app/pipeviz-ui && bun run dev -- --host 0.0.0.0 --port 5173"]
