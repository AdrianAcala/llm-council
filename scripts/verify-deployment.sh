#!/bin/bash
# Verify LLM Council deployment is working properly

set -e

echo "=== LLM Council Deployment Verification ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if containers are running
echo "Checking Docker containers..."
if ! docker compose ps | grep -q "llm-council-backend.*Up"; then
    echo -e "${RED}ERROR: Backend container is not running${NC}"
    exit 1
fi

if ! docker compose ps | grep -q "llm-council-frontend.*Up"; then
    echo -e "${RED}ERROR: Frontend container is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Both containers are running${NC}"
echo ""

# Check port mappings
echo "Checking port mappings..."
BACKEND_PORTS=$(docker port llm-council-backend-1 2>/dev/null || echo "")
FRONTEND_PORTS=$(docker port llm-council-frontend-1 2>/dev/null || echo "")

if [ -z "$BACKEND_PORTS" ]; then
    echo -e "${RED}ERROR: Backend port not mapped${NC}"
    echo "  Fix: docker compose rm -f backend && docker compose up -d backend"
    exit 1
fi

if [ -z "$FRONTEND_PORTS" ]; then
    echo -e "${RED}ERROR: Frontend port not mapped${NC}"
    echo "  Fix: docker compose rm -f frontend && docker compose up -d frontend"
    exit 1
fi

echo -e "${GREEN}✓ Backend ports: $BACKEND_PORTS${NC}"
echo -e "${GREEN}✓ Frontend ports: $FRONTEND_PORTS${NC}"
echo ""

# Check if services are responding
echo "Checking service health..."

if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✓ Backend responding on port 8001${NC}"
else
    echo -e "${RED}ERROR: Backend not responding on port 8001${NC}"
    exit 1
fi

if curl -s http://localhost:5173/ > /dev/null; then
    echo -e "${GREEN}✓ Frontend responding on port 5173${NC}"
else
    echo -e "${RED}ERROR: Frontend not responding on port 5173${NC}"
    exit 1
fi
echo ""

# Check API endpoints
echo "Checking API endpoints..."
if curl -s http://localhost:8001/api/conversations > /dev/null; then
    echo -e "${GREEN}✓ /api/conversations endpoint working${NC}"
else
    echo -e "${RED}ERROR: /api/conversations endpoint failed${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}=== All checks passed! Deployment is working properly ===${NC}"
echo ""
echo "Frontend: http://localhost:5173/"
echo "Backend:  http://localhost:8001/"
