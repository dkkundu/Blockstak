# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies required for building mysqlclient (using mariadb-dev)
RUN apt-get update && \
    apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the fixed FastAPI port (8000)
EXPOSE 8000

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
