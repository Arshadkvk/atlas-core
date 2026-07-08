# atlas-core

## Project Overview

Atlas Core is a Django REST API for managing player wallets, inventory purchases, and reward claims. The project uses PostgreSQL for development and Docker Compose for local containerized runs.

## Installation

### Local setup

1. Create and activate a virtual environment.
2. Install dependencies from the `src` folder:

   ```bash
   pip install -r src/requirements.txt
   ```

3. Create a `.env` file in the project root with the database settings shown below.
4. Run migrations and start the server.

### Docker setup

1. Install Docker Desktop and make sure Docker Compose is available.
2. Create the same `.env` file in the project root.
3. Start the services:

   ```bash
   docker compose up --build
   ```

4. If you need to run migrations inside Docker, use:

  ```bash
  docker compose exec web python manage.py migrate
  ```

## Environment Variables

Create a `.env` file in the project root with:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=atlas_db
DB_USER=atlas_user
DB_PASSWORD=atlas__secure_pass2026
DB_HOST=localhost
DB_PORT=5432
```

Docker Compose uses the same values for the database container. When running with Docker, the web app is exposed on port `8001` and PostgreSQL is exposed on port `5433` on the host.

## Migrations

Run migrations from the `src` directory for local development:

```bash
cd src
python manage.py migrate
```

If you need to create new migrations after model changes locally:

```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

If you are running the app in Docker, apply migrations inside the container:

```bash
docker compose exec web python manage.py migrate
```

## Run Server

### Local server

```bash
cd src
python manage.py runserver
```

Local URL: `http://127.0.0.1:8000/`

### Docker server

```bash
docker compose up --build
```

Docker URL: `http://127.0.0.1:8001/`

To stop the containers:

```bash
docker compose down
```

To remove the database volume and reset the data:

```bash
docker compose down -v
```

## API Endpoints

Base path: `/v1`

### Wallets

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/v1/wallets/<player_id>/` | Get wallet details for a player |
| `POST` | `/v1/wallets/<player_id>/credit/` | Credit coins to a wallet |
| `POST` | `/v1/wallets/<player_id>/purchase/` | Purchase an item using wallet balance |

### Rewards

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/v1/rewards/<reward_id>/claim/` | Claim a reward for a player |

All `POST` endpoints require an `Idempotency-Key` header.

## Example Requests

### Get wallet details

```bash
curl http://127.0.0.1:8000/v1/wallets/player-123/
```

### Credit a wallet

```bash
curl -X POST http://127.0.0.1:8000/v1/wallets/player-123/credit/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 8d4b4c6a-4f66-4f0f-9c7f-5a9f2fd2c111" \
  -d '{
    "amount": 100,
    "reason": "welcome bonus"
  }'
```

### Purchase an item

```bash
curl -X POST http://127.0.0.1:8000/v1/wallets/player-123/purchase/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 71f4f9f1-0d1b-4d63-b2d3-0f0c9f8bb222" \
  -d '{
    "itemId": "sword-001",
    "price": 50
  }'
```

### Claim a reward

```bash
curl -X POST http://127.0.0.1:8000/v1/rewards/reward-001/claim/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 2f2abf53-8d52-4a8d-9f6c-3d1d9cbf3333" \
  -d '{
    "playerId": "player-123"
  }'
```
