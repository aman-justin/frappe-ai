# Docker Setup Guide for Frappe AI Form Builder

## What You Need

1. **Install Docker Desktop** (this includes everything):
   - **Windows/Mac**: Download from https://www.docker.com/products/docker-desktop
   - **Linux**: 
     ```bash
     curl -fsSL https://get.docker.com -o get-docker.sh
     sudo sh get-docker.sh
     sudo apt install docker-compose-plugin
     ```

2. That's it! Docker includes everything else (Python, Redis, MariaDB, etc.)

---

## Quick Start (3 Commands)

```bash
# 1. Start Docker containers
docker-compose up -d

# 2. Wait 30 seconds for database to start, then create site
docker exec -it frappe-ai-bench bench new-site dev.local \
  --mariadb-root-password admin \
  --admin-password admin \
  --db-host mariadb

# 3. Install the app
docker exec -it frappe-ai-bench bench --site dev.local install-app frappe_ai_form_builder

# 4. Start the server
docker exec -it frappe-ai-bench bench --site dev.local serve --port 8000
```

Open browser: http://localhost:8000
- Username: `Administrator`
- Password: `admin`

---

## What Each Command Does

### `docker-compose up -d`
- Downloads required software (MariaDB, Redis, Frappe)
- Creates isolated containers (like virtual machines)
- Starts all services in background (`-d` = detached mode)

### `docker exec -it frappe-ai-bench bench new-site...`
- Enters the Frappe container
- Creates a new Frappe site
- Sets up database with admin password

### `docker exec -it frappe-ai-bench bench --site dev.local install-app...`
- Installs the AI Form Builder app into the site

---

## Useful Commands

```bash
# See running containers
docker ps

# View logs
docker-compose logs -f frappe

# Stop everything
docker-compose down

# Stop and delete everything (fresh start)
docker-compose down -v

# Enter the container (like SSH)
docker exec -it frappe-ai-bench bash

# Inside container, you can run normal bench commands:
bench migrate
bench build
bench clear-cache
```

---

## For Users (Simple Instructions)

**Prerequisites**: Install Docker Desktop (https://www.docker.com/products/docker-desktop)

```bash
# Clone and start
git clone https://github.com/aman-justin/frappe-ai.git
cd frappe-ai/apps/frappe_ai_form_builder
docker-compose up -d

# Wait 30 seconds, then setup
docker exec -it frappe-ai-bench bench new-site dev.local --mariadb-root-password admin --admin-password admin --db-host mariadb
docker exec -it frappe-ai-bench bench --site dev.local install-app frappe_ai_form_builder
docker exec -it frappe-ai-bench bench --site dev.local serve --port 8000

# Open http://localhost:8000
# Login: Administrator / admin
# Configure API key at Setup > AI Config
```

---

## Troubleshooting

### "Cannot connect to database"
Wait 30-60 seconds after `docker-compose up` for MariaDB to fully start.

### "Port 8000 already in use"
```bash
# Stop whatever is using port 8000
sudo lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

### "Permission denied"
```bash
# Linux only - add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Start Fresh
```bash
docker-compose down -v
docker-compose up -d
# Then run setup commands again
```

---

## Why Docker?

**Before Docker**: 
"Install Python 3.12, Node 18, Redis, MariaDB, configure databases, run 20 commands..."

**With Docker**: 
"Install Docker Desktop. Run 3 commands. Done!"

Users don't need to worry about:
- Python versions
- Database configuration
- Port conflicts
- OS differences (Windows/Mac/Linux)

Everything works the same everywhere! 🎉
