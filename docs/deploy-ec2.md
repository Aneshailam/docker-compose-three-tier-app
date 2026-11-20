# Deploy on AWS EC2

## 1. Launch the instance

1. Launch an **Amazon Linux 2023** instance (`t3.micro` or larger) with a key pair.
2. Security group inbound rules:

| Port | Source | Purpose |
|------|--------|---------|
| 22 | Your IP only | SSH |
| 80 | 0.0.0.0/0 | Web access |

Do not open port 3306 or 5000. The database and API are reachable only inside Docker networks.

## 2. Install Docker, Compose and Git

```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

Log out and back in so the `docker` group applies, then check:

```bash
docker --version
docker compose version
```

## 3. Get the code and configure it

```bash
git clone https://github.com/Aneshailam/docker-compose-three-tier-app.git
cd docker-compose-three-tier-app
cp .env.example .env
nano .env        # set strong passwords
```

## 4. Start the stack

```bash
docker compose up -d --build
docker compose ps
```

All three services should show as running, and `db` and `backend` as healthy.

## 5. Test

```bash
curl http://localhost/api/health
curl -X POST http://localhost/api/tasks -H "Content-Type: application/json" -d '{"title":"first task"}'
curl http://localhost/api/tasks
```

Open `http://<EC2-public-IP>` in a browser to use the web page.

## 6. Check that data persists

```bash
docker compose down        # removes containers, keeps the volume
docker compose up -d
curl http://localhost/api/tasks     # the task is still there
```

## 7. Compare image sizes (multi-stage build)

```bash
docker images
```

The backend image contains only the runtime and installed packages, not the build tools used to create it.

## Useful commands

```bash
docker compose logs -f backend      # follow API logs
docker compose restart backend      # restart one service
git pull && docker compose up -d --build   # deploy an update
```

## Back up the database

```bash
docker compose exec db sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' > backup.sql
```

## Clean up

```bash
docker compose down -v     # also deletes the database volume
```

Then terminate the EC2 instance to stop charges.
