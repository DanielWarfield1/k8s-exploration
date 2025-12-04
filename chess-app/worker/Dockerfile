FROM python:3.10-slim

# Install Stockfish engine binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends stockfish && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

# documenting where stockfish lives (on Debian it's usually /usr/games/stockfish)
ENV STOCKFISH_EXECUTABLE=/usr/games/stockfish

CMD ["python", "worker.py"]
