#!/bin/bash
set -e

echo "Starting deployment process..."

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Build and start the docker containers
echo "Building and starting Docker containers..."
docker compose up -d --build

# Wait a few seconds for the database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Run migrations inside the container
echo "Running database migrations..."
docker compose exec web python manage.py migrate

# Collect static files inside the container
echo "Collecting static files..."
docker compose exec web python manage.py collectstatic --no-input

echo "Deployment successful!"
echo ""
echo "Please ensure Nginx is configured with the provided nginx.conf."
echo "You can copy it to Nginx configuration directory and reload:"
echo "  sudo cp nginx.conf /etc/nginx/sites-available/django-pub-hackathon"
echo "  sudo ln -sf /etc/nginx/sites-available/django-pub-hackathon /etc/nginx/sites-enabled/"
echo "  sudo nginx -t && sudo systemctl reload nginx"
