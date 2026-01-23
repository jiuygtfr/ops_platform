Write-Host "Starting Ops Platform locally..."

# Check Python
$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Error "Python not found. Please install Python 3.9+."
    exit 1
}

# Check Node
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Error "Node.js not found. Please install Node.js 16+."
    exit 1
}

# Start Backend in a new process
Write-Host "Starting Backend..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; pip install -r requirements.txt; uvicorn app.main:app --reload"

# Start Frontend in a new process
Write-Host "Starting Frontend..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm run dev"

Write-Host "Services started in separate windows."
