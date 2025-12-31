# Deployment Guide

This guide covers the deployment of the FastAPI backend to a production server using Docker Compose with Nginx and SSL certificates.

But you have to configure a couple things first. 🤓

## Prerequisites

- A server running Ubuntu/Debian (VPS, cloud instance, etc.)
- Docker and Docker Compose installed
- A domain name pointing to your server's IP address
- Root or sudo access
- Configure the DNS records of your domain to point to the IP of the server you just created.*

## Recommendation

Use non root user for deployment.

## Step 1: Clone the Repository

```bash
# Clone your repository
git clone https://github.com/abdoulayeDABO/fastapi-backend-template.git
cd fastapi-backend-template
```

## Step 2: Generate Secret Keys

Generate secure secret keys for your environment variables:

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate another for FIRST_SUPERUSER_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate another for POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Save these values!** You'll need them in the next step.

## Step 3: Configure Environment Variables

Create and edit the `.env` file:

```bash
# Copy the example env file
cp .env.example .env

# Edit the .env file
nano .env
```

Update the following values with the secrets you generated:

```bash
# Security
SECRET_KEY=your_generated_secret_key_here
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=your_generated_password_here

# Database
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_generated_postgres_password_here
POSTGRES_DB=app

# Domain
DOMAIN=api.example.com  # Change to your domain

# Email (optional, for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@example.com
```

## Step 4: Update Nginx Configuration

Edit the Nginx configuration file:

```bash
nano nginx/nginx.conf
```

Replace `www.example.com` with your actual domain name (e.g., `api.example.com`):

```nginx
server_name api.example.com;  # Your domain

ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
```

## Step 5: Generate SSL Certificate

Install Certbot and generate SSL certificates:

```bash
# Install Certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Generate certificate (method 1: HTTP challenge)
sudo certbot certonly --standalone -d api.example.com

# OR method 2: DNS challenge (for wildcard)
sudo certbot certonly --manual --preferred-challenges dns \
  -d example.com -d *.example.com
```

Follow the prompts:

- Enter your email address
- Agree to Terms of Service
- For DNS challenge: Add the TXT record to your DNS provider

Verify the certificates are created:

```bash
sudo ls -la /etc/letsencrypt/live/api.example.com/
```

You should see:

- `fullchain.pem`
- `privkey.pem`
- `cert.pem`
- `chain.pem`


## Step 6: Build and Start the Services

```bash
# Build the Docker images
docker compose build

# Start all services in detached mode
docker compose up -d

# Check if containers are running
docker compose ps

# View logs
docker compose logs -f
```

## Step 7: Verify Deployment

### Check API health

```bash
curl https://api.example.com/api/v1/health-check/
```

## Step 8: Setup SSL Auto-Renewal

Let's Encrypt certificates expire after 90 days. Setup automatic renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e
```

Add this line to check for renewal twice daily:

```cron
0 0,12 * * * certbot renew --quiet --post-hook "docker compose -f /path/to/fastapi-backend/docker-compose.yml restart nginx"
```

## Security Checklist

- ✅ All secrets changed from default values
- ✅ SSL certificate installed and working
- ✅ Firewall configured (only ports 80, 443, 22 open)
- ✅ `.env` file not committed to git
- ✅ Database password is strong and unique
- ✅ Superuser password is strong and unique
- ✅ Auto-renewal for SSL certificates configured
- ✅ Regular backups scheduled

## Production Best Practices

1. **Regular backups**: Schedule automatic database backups
2. **Monitoring**: Setup error tracking and uptime monitoring
3. **Updates**: Keep Docker images and system packages updated
4. **Logs**: Configure log rotation to prevent disk space issues
5. **Testing**: Test deployments in staging before production
6. **Rollback plan**: Keep previous deployment ready for quick rollback

## Support

For issues or questions:

- Check the [GitHub Issues](https://github.com/abdoulayeDABO/fastapi-backend-template/issues)
- Review FastAPI documentation: https://fastapi.tiangolo.com
- Review Docker documentation: https://docs.docker.com

**Congratulations! 🎉** Your FastAPI backend is now deployed and running in production!
