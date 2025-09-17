# FileCompareHub VPS Deployment Guide

This guide provides detailed instructions for deploying FileCompareHub on a VPS server.

## Prerequisites

1. A VPS server with Ubuntu 20.04 or later (other Linux distributions may work with adjustments)
2. Root or sudo access to the server
3. Docker and Docker Compose installed
4. A domain name pointing to your VPS (optional but recommended)

## Step-by-Step Deployment

### 1. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker and Docker Compose

```bash
# Install Docker
sudo apt install docker.io -y

# Install Docker Compose
sudo apt install docker-compose -y

# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and back in for the group changes to take effect
```

### 3. Clone the Repository

```bash
git clone <repository-url>
cd filecomparehub
```

### 4. Initialize Data Directory

```bash
./init.sh
```

### 5. Configure Environment Variables

Edit the `.env` file and update the values for production:

```bash
nano .env
```

Important changes for production:
- `SECRET_KEY`: Generate a strong random secret key
- `DEFAULT_ADMIN_PASSWORD`: Set a secure password for the admin user
- `REACT_APP_API_BASE_URL`: Set to your domain name

### 6. (Optional) Configure SSL with Let's Encrypt

If you want to use HTTPS (recommended), you can set up Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot -y

# Obtain SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to the data directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./data/certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./data/certs/

# Set proper permissions
sudo chown -R $USER:$USER ./data/certs
```

### 7. Update Nginx Configuration for SSL (if using HTTPS)

Edit `nginx/conf.d/default.conf` to include SSL configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    
    # ... rest of the configuration
}
```

### 8. Start the Application

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### 9. Verify the Deployment

Check that all services are running:

```bash
docker-compose -f docker-compose.prod.yml ps
```

You should see all services in the "Up" state.

### 10. Access the Application

Open your web browser and navigate to:
- http://your-domain.com (or http://your-vps-ip if no domain)

Default login credentials:
- Username: admin
- Password: (whatever you set in the .env file)

## Maintenance

### Viewing Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs backend
```

### Updating the Application

```bash
# Pull the latest code
git pull

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml up --build -d
```

### Backup Data

The application data is stored in the `./data` directory. Regularly backup this directory:

```bash
tar -czf filecomparehub-backup-$(date +%Y%m%d).tar.gz ./data
```

## Troubleshooting

### Common Issues

1. **Permission denied errors**: Ensure your user is in the docker group and log out/in again.

2. **Port already in use**: Check if other services are using ports 80, 443, 3000, or 8000.

3. **Database issues**: If you encounter database errors, check the permissions on the `./data` directory.

### Getting Help

If you encounter issues not covered in this guide, please check the project's GitHub issues or contact support.