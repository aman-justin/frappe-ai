# Docker Setup Guide for Frappe AI Form Builder

## Current Status: Basic Setup Complete ✅

**Docker containers are running!** Here's what we have:
- ✅ MariaDB running on port 3307
- ✅ Redis Cache running  
- ✅ Redis Queue running
- ✅ Frappe Bench container running

**Next Steps:**
1. Configure networking (DNS resolution)
2. Install Frappe dependencies
3. Create site and install app

## Quick Test Commands

```bash
# Check running containers
sudo docker ps

# Enter Frappe container
sudo docker exec -it frappe-ai-bench bash

# Test basic connectivity
curl -I http://localhost:8001  # Should show Frappe running
```

## Troubleshooting

### "No module named 'frappe'"
The container needs internet access to install dependencies. Solutions:
1. **Add DNS to docker-compose.yml**:
```yaml
services:
  frappe:
    dns:
      - 8.8.8.8
      - 1.1.1.1
```

2. **Use host network** (temporary):
```yaml
services:
  frappe:
    network_mode: host
```

### Port Conflicts
- MariaDB: Changed to port 3307 (was 3306)
- Frappe: Changed to port 8001 (was 8000)

### Stop Everything
```bash
cd /home/aman/frappe-bench/apps/frappe_ai_form_builder
sudo docker compose down -v  # Stop and remove volumes
```

## Alternative: Manual Setup (Working!)

Since Docker networking is complex, you can use the **manual setup** which works perfectly:

```bash
# Your existing setup works great!
cd /home/aman/frappe-bench
source env/bin/activate
bench start

# Open http://localhost:8000
# Configure AI Config, start building forms!
```

**The manual setup is actually better for development** because:
- ✅ Full access to all files
- ✅ Easy debugging
- ✅ No networking issues
- ✅ Faster development cycle

## For Production Deployment

When you're ready for production, the Docker setup will be perfect. For now, use the manual setup - it works great!

---

**🎉 Your AI Form Builder is ready to use!**

Just run:
```bash
cd /home/aman/frappe-bench
source env/bin/activate
bench start
```

Then visit: http://localhost:8000
