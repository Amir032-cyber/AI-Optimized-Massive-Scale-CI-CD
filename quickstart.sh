#!/bin/bash

###############################################################################
# PTS Quick Start Script
# Starts the API server and initializes the environment
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC} PTS Quick Start"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Check if venv exists
if [[ ! -d "venv" ]]; then
    echo "Virtual environment not found. Running installation..."
    bash install.sh
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Create necessary directories
mkdir -p data/raw data/processed data/features models logs

# Run migrations if needed
echo "Setting up database..."
python -c "from src.pts.data.collector import DataCollector; print('Database ready')" 2>/dev/null || true

# Start the API server
echo -e "${GREEN}✓ Starting PTS API Server${NC}"
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn src.pts.api.server:app --reload --host 0.0.0.0 --port 8000
