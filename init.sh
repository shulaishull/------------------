#!/bin/bash

# Create data directory
mkdir -p ./data

# Set permissions
chmod 755 ./data

# Create necessary subdirectories
mkdir -p ./data/certs
mkdir -p ./data/logs

# Set permissions for subdirectories
chmod 755 ./data/certs
chmod 755 ./data/logs

echo "Data directory initialized successfully"