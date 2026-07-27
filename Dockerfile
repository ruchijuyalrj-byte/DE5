FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ ./src/
COPY data/ ./data/

RUN pip install --no-cache-dir .

CMD ["python", "-m", "data_processing.run_pipeline"]
