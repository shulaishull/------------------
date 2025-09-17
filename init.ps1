# Create data directory
New-Item -ItemType Directory -Path "./data" -Force

# Create necessary subdirectories
New-Item -ItemType Directory -Path "./data/certs" -Force
New-Item -ItemType Directory -Path "./data/logs" -Force

Write-Host "Data directory initialized successfully"