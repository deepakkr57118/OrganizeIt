FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create a working folder for files
RUN mkdir /app/data

EXPOSE 8501

CMD ["streamlit", "run", "pre.py", "--server.port=8501", "--server.address=0.0.0.0"]
