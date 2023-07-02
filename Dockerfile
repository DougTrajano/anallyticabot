FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -U -r requirements.txt

# Set the entrypoint
ENTRYPOINT ["python", "src/cli.py"]