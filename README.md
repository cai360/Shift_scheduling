![Entity Relationship Diagram](./ERD.png)

# Local Development

## Start

docker compose up --build

## Run Migration

docker compose exec backend flask db upgrade

## URLs

Frontend:
http://localhost:5173

Backend:
http://localhost:5000

Database:
localhost:5432

## Stop

docker compose down
