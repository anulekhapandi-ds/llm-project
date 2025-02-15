# Dockerfile for LLM-based Automation Agent

# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Set environment variable for AI Proxy Token
ENV AIPROXY_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDA4ODBAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KpMaVgWdPhDF3a3Xy3V8HPM45rxPSZxpzNvyepVqz-4"

# Run the Flask app
CMD ["python", "app.py"]
