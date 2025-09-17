# Health check script for FileCompareHub

Write-Host "Checking FileCompareHub services..."

# Check if docker is installed
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed"
    exit 1
}

# Check if docker-compose is installed
if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Docker Compose is not installed"
    exit 1
}

# Check if services are running
$services = docker-compose -f docker-compose.prod.yml ps
if ($services -match "Up") {
    Write-Host "All services are running"
} else {
    Write-Host "Some services are not running"
    Write-Host $services
    exit 1
}

# Check backend API
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
    if ($backend.StatusCode -eq 200) {
        Write-Host "Backend API is responding"
    } else {
        Write-Host "Backend API returned status code: $($backend.StatusCode)"
        exit 1
    }
} catch {
    Write-Host "Backend API is not responding"
    exit 1
}

# Check frontend
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing
    if ($frontend.StatusCode -eq 200) {
        Write-Host "Frontend is responding"
    } else {
        Write-Host "Frontend returned status code: $($frontend.StatusCode)"
        exit 1
    }
} catch {
    Write-Host "Frontend is not responding"
    exit 1
}

Write-Host "All checks passed!"