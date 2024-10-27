# Task Manager Backend

This is a FastAPI-based backend application for a task manager. It uses PostgreSQL as the database, Redis for caching, and Elasticsearch for search functionality. This guide will help you set up and run the application using Docker.

## Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/taskManager_backend.git
   cd taskManager_backend

Build and run the application:

You can use Docker Compose to build and run the application. Run the following command:

bash
docker-compose up --build
This command will start the FastAPI app, PostgreSQL database, and Redis server. It may take a few moments for the containers to start.

Access the application:

Once everything is running, you can access the FastAPI application at:

arduino
Копировать код
http://localhost:8082
You can also explore the automatically generated API documentation at:

bash
Копировать код
http://localhost:8082/docs
Stopping the application:

To stop the running containers, you can use:

bash
Копировать код
docker-compose down
Environment Variables
The application uses several environment variables that are defined in the docker-compose.yml file. Here are the key variables:

SQLALCHEMY_DATABASE_URL: Connection string for asynchronous PostgreSQL.
SQLALCHEMY_DATABASE_SYNC_URL: Connection string for synchronous PostgreSQL.
SECRET_KEY: Secret key for cryptographic operations.
REFRESH_SECRET_KEY: Secret key for refresh tokens.
BROKER_URL: URL for the Redis broker.
CRYPTOGRAPHY_KEY: Key used for encryption.
ELASTICSEARCH_URL: URL for Elasticsearch service.

