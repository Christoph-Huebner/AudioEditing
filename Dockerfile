# Use a lightweight Python image
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ffmpeg-python \
    && apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY  *.py /app/

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["python", "main.py"]

#ffmpeg-python && pip install --no-cache-dir -r pip-packages.txt \
#docker run --rm -v "$(pwd)/files:/app/files" -v "$(pwd)/config.toml:/app/config.toml:ro" getaudiofromyt:latest "https://www.youtube.com/watch?v=E8T17Eg2wbM" --convert --format mp3
#docker run --rm audioediting:latest -h
