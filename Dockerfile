FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable stdout/stderr autoflush
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies, install Python requirements, then clean up apt lists to
# keep the final image smaller. Keep installs minimal; add more if your packages
# require them.
RUN apt-get update \
		&& apt-get install -y --no-install-recommends \
			 gcc \
			 libssl-dev \
			 libffi-dev \
			 build-essential \
		&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user to run the app
RUN useradd -m -u 1000 app || true

# Copy application files and set ownership to non-root user
COPY --chown=app:app . /app

# Ensure logs directory exists and is writable by the app user
RUN mkdir -p /app/utility/logs \
		&& chown -R app:app /app/utility/logs

# Switch to non-root user for runtime
USER app

# Lightweight python-based healthcheck that verifies imports
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD ["python", "/app/healthcheck.py"]

CMD ["python", "app_runner.py"]
