.PHONY: all setup install run clean \
        api-root api-health api-convert api-summary api-graph api-matrix api-traffic api-all

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

BASE_URL := http://localhost:8000

all: setup install run

# Create virtual environment
setup:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Virtual environment created."

# Install dependencies
install: setup
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r retrofit_framework/requirements.txt
	@echo "Dependencies installed."

# Run the FastAPI server
run:
	@echo "Starting FastAPI server..."
	cd retrofit_framework && ../$(UVICORN) main:app --host 0.0.0.0 --port 8000 --reload

# Clean up virtual environment
clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Cleaned."

# ============================================================
# API Commands (requires server running on port 8000)
# ============================================================

# Hit the root endpoint - API info and documentation links
api-root:
	@echo "=== API Root Endpoint ==="
	@curl -s $(BASE_URL)/ | python3 -m json.tool

# Health check endpoint
api-health:
	@echo "=== Health Check ==="
	@curl -s $(BASE_URL)/health | python3 -m json.tool

# Full warehouse conversion - returns complete retrofit data
api-convert:
	@echo "=== Full Warehouse Conversion (Layout A) ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -m json.tool

# Get only the conversion summary (nodes, edges, feasibility score, recommendations)
api-summary:
	@echo "=== Conversion Summary ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['summary'], indent=2))"

# Get only the navigation graph (nodes and edges)
api-graph:
	@echo "=== Navigation Graph ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['navigation_graph'], indent=2))"

# Get only the distance matrix
api-matrix:
	@echo "=== Distance Matrix ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -c "import sys,json; d=json.load(sys.stdin); print('Node IDs:', [n['id'] for n in d['navigation_graph']['nodes']]); print('Matrix size:', len(d['distance_matrix']), 'x', len(d['distance_matrix'][0]) if d['distance_matrix'] else 0)"

# Get only the traffic rules
api-traffic:
	@echo "=== Traffic Rules ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['traffic_rules'], indent=2))"

# Get original warehouse specification
api-original:
	@echo "=== Original Warehouse Specification ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['original_warehouse'], indent=2))"

# Get robotic warehouse specification (with charging stations)
api-robotic:
	@echo "=== Robotic Warehouse Specification ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['robotic_warehouse'], indent=2))"

# Get charging station locations
api-charging:
	@echo "=== Charging Stations ==="
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['robotic_warehouse']['charging_stations'], indent=2))"

# Save full conversion to JSON file
api-save:
	@echo "=== Saving Conversion to output/conversion_result.json ==="
	@mkdir -p output
	@curl -s $(BASE_URL)/api/v1/convert/layouta | python3 -m json.tool > output/conversion_result.json
	@echo "Saved to output/conversion_result.json"

# Run all API tests
api-all: api-root api-health api-summary api-graph api-traffic api-charging
	@echo ""
	@echo "=== All API tests completed ==="

# Quick test - health + summary only
api-test:
	@echo "=== Quick API Test ==="
	@curl -s -o /dev/null -w "Root: %{http_code}\n" $(BASE_URL)/
	@curl -s -o /dev/null -w "Health: %{http_code}\n" $(BASE_URL)/health
	@curl -s -o /dev/null -w "Convert: %{http_code}\n" $(BASE_URL)/api/v1/convert/layouta
	@echo "All endpoints responding!"
