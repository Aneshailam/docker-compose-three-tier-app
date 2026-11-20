# Containerized Three-Tier Web Application with Docker

![CI](https://github.com/Aneshailam/docker-compose-three-tier-app/actions/workflows/ci.yml/badge.svg)

A three-tier web application packaged into three containers and run with Docker Compose: an Nginx reverse-proxy frontend, a Flask REST API backend and a MySQL database. It runs the same way on a laptop and on an AWS EC2 instance.

## Architecture

```
                 Browser
                    |
              port 80 (only published port)
                    |
   +----------------v-----------------+
   |  nginx  (static site + reverse   |   frontend_net
   |          proxy for /api)         |
   +----------------+-----------------+
                    |
   +----------------v-----------------+
   |  backend  (Flask + Gunicorn)     |   frontend_net + backend_net
   +----------------+-----------------+
                    |
   +----------------v-----------------+
   |  db  (MySQL 8.0)                 |   backend_net only
   |  volume: db_data                 |
   +----------------------------------+
```

## Tech stack

| Tier | Technology |
|------|------------|
| Frontend and reverse proxy | Nginx (Alpine) |
| Backend API | Python, Flask, Gunicorn |
| Database | MySQL 8.0 |
| Orchestration | Docker Compose |
| Hosting | AWS EC2 |
| CI | GitHub Actions (build, start and smoke test the stack) |

## Design highlights

- **Three containers, two networks.** Nginx and the backend share `frontend_net`. The backend and database share `backend_net`. The database cannot be reached from Nginx or from outside.
- **One published port.** Only Nginx exposes port 80 to the host.
- **Persistent data.** The MySQL data lives in the `db_data` named volume, so it survives container restarts and re-creation.
- **Multi-stage backend image.** Dependencies are installed in a build stage and only the result is copied into a slim runtime image. The app runs as a non-root user.
- **Health checks and start order.** The database and backend have health checks. The backend starts after the database is healthy, and Nginx starts after the backend is healthy.
- **Configuration through environment variables.** Passwords live in `.env`, which is excluded from Git. `.env.example` shows the required variables.

## API

| Method and path | Description |
|-----------------|-------------|
| `GET /api/health` | Health check, includes database status |
| `GET /api/tasks` | List tasks |
| `POST /api/tasks` | Create a task (`{"title": "..."}`) |
| `DELETE /api/tasks/{id}` | Delete a task |

## Repository structure

```
docker-compose.yml      The three services, networks and volume
.env.example            Required environment variables (copy to .env)
nginx/                  Nginx config and Dockerfile
frontend/               Static web page served by Nginx
backend/                Flask API and multi-stage Dockerfile
db/init.sql             Creates the tasks table on first start
docs/deploy-ec2.md      Step-by-step deployment on AWS EC2
.github/workflows/      CI workflow
```

## Run locally

Requires Docker with the Compose plugin.

```bash
git clone https://github.com/Aneshailam/docker-compose-three-tier-app.git
cd docker-compose-three-tier-app

cp .env.example .env      # then edit .env and set your own passwords
docker compose up -d --build
docker compose ps
```

Open http://localhost, or test the API:

```bash
curl http://localhost/api/health
curl -X POST http://localhost/api/tasks -H "Content-Type: application/json" -d '{"title":"first task"}'
curl http://localhost/api/tasks
```

Stop the stack:

```bash
docker compose down        # keeps the database volume
docker compose down -v     # also deletes the database volume
```

## Deploy on AWS EC2

See [`docs/deploy-ec2.md`](docs/deploy-ec2.md) for the instance setup, security group rules, Docker installation, deployment, persistence check and cleanup.

## Possible improvements

- Add HTTPS with a certificate (for example Let's Encrypt, or an ALB with ACM).
- Move the database to Amazon RDS for managed backups and failover.
- Push images to a registry (Amazon ECR) and deploy them from CI.
- Add automated unit tests for the API.
- Add resource limits and log rotation to the Compose services.
