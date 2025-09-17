#!/bin/bash

# Health check script for FileCompareHub

echo "Checking FileCompareHub services..."

# Check if docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose is not installed"
    exit 1
fi

# Check if services are running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "All services are running"
else
    echo "Some services are not running"
    docker-compose -f docker-compose.prod.yml ps
    exit 1
fi

# Check backend API
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "Backend API is responding"
else
    echo "Backend API is not responding"
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "Frontend is responding"
else
    echo "Frontend is not responding"
    exit 1
fi

echo "All checks passed!"