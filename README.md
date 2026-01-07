# Atelier Cauchemar — Telegram bot

This repository contains the Atelier Cauchemar Telegram bot implemented with aiogram.

Running locally (dev):

- Build and run with Docker:

```bash
# build
docker build -t atelier_cauchemar:local .
# run (mount a volume for DB)
docker run -e BOT_TOKEN=$BOT_TOKEN -v $(pwd)/data:/shared atelier_cauchemar:local
```

CI/CD

- The repository includes a GitHub Actions workflow `.github/workflows/main.yml` that lints, builds, pushes a Docker image, deploys via SSH, and sends a notification.
- Secrets to configure in the repo: DOCKER_USERNAME, DOCKER_PASSWORD, HOST, USER, SSH_KEY, BOT_TOKEN, TELEGRAM_NOTIFY_TO

Database

- The bot uses SQLite file located at `/shared/atelier.db` inside the container. A Docker volume or host bind should be mounted to `/shared` so the DB persists.
  > > > > > > > 63e2652 (create repo)
