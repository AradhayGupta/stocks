# python image with requirements, runs the streamlit site as non-root user
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
		&& apt-get install -y --no-install-recommends \
			 gcc \
			 libssl-dev \
			 libffi-dev \
			 build-essential \
		&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 app || true

COPY --chown=app:app . /app

RUN mkdir -p /app/utility/logs \
		&& chown -R app:app /app/utility/logs

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD ["python", "/app/healthcheck.py"]

CMD streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true
