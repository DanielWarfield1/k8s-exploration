FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy client code
COPY play.py .

# Default API_URL can be overridden at runtime using -e API_URL=http://...
ENV API_URL=http://backend-test:80

# Run interactively (client uses input())
CMD ["python", "play.py"]
