# Dockerfile

FROM python:3.12.5-alpine

WORKDIR /backend
COPY . /backend

# Install required packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN adduser -D celeryuser

# Set permissions for the backend directory
RUN chown -R celeryuser:celeryuser /backend

# Switch to the non-root user
USER celeryuser

# Make the script executable
RUN chmod +x /backend/start.sh

EXPOSE 8082

# Use the start script as the entry point
CMD ["sh", "/backend/start.sh"]
