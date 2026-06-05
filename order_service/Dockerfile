# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
# Install system dependencies required for psycopg2 and confluent-kafka
RUN apt-get update && apt-get install -y build-essential libpq-dev librdkafka-dev
COPY requirements.txt .
# Build wheels for dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq5 librdkafka1 && rm -rf /var/lib/apt/lists/*
# Copy compiled wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*
# Copy application code
COPY . .
# Run the Flask API
EXPOSE 5001
CMD ["python", "run.py"]