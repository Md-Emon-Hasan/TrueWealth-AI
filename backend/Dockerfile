FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 5001 (as used in main.py)
EXPOSE 5001

# Set python path to current directory so app module is found
ENV PYTHONPATH=/app

CMD ["python", "-m", "app.main"]
