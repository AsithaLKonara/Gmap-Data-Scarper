FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
ENV PIP_DEFAULT_TIMEOUT=180
RUN pip install --default-timeout=180 --no-cache-dir -r requirements.txt

COPY . .

# Make the startup script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"] 