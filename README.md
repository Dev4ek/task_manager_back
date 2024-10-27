# Task Manager Backend

Есть три созданных аккаунта

АДМИН
логин: admin
пароль: admin

Участник
логин: member
пароль: member

ГОСТЬ
логин: guest
пароль: guest




## Prerequisites

Посмотрите установлен ли докер

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Dev4ek/task_manager_backend.git
   cd taskManager_backend

2. Build and run the application:

    ```bash
    docker-compose up --build

3. Access the application:

Once everything is running, you can access the FastAPI application at:

    ```bash
    http://localhost:8082/docs

4. Environment variables
SQLALCHEMY_DATABASE_URL: Connection string for asynchronous PostgreSQL.
SQLALCHEMY_DATABASE_SYNC_URL: Connection string for synchronous PostgreSQL.
SECRET_KEY: Secret key for cryptographic operations.
REFRESH_SECRET_KEY: Secret key for refresh tokens.
BROKER_URL: URL for the Redis broker.
CRYPTOGRAPHY_KEY: Key used for encryption.
ELASTICSEARCH_URL: URL for Elasticsearch service.

