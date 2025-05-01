#!/bin/bash
# Script to generate integration documentation

echo "Setting up environment..."

# Check if Jinja2 is installed
if ! python -c "import jinja2" &> /dev/null; then
    echo "Installing Jinja2..."
    pip install jinja2
fi

# Run the setup script to check Python path
echo "Setting up Python path..."
python scripts/setup_env.py

echo "Generating integration documentation..."

# Generate integration decision matrix
echo "Generating integration decision matrix for Open WebUI MCP..."
python scripts/generate_integration_matrix.py

# Generate proof-of-concept integration plan
echo "Generating proof-of-concept integration plan..."
python scripts/generate_poc_integration_plan.py

echo "Documentation generation complete!"
echo "Generated files:"
echo "- docs/integration/open-webui-mcp-decision-matrix.md"
echo "- docs/integration/poc-integration-plan-generated.md"

echo "You can view these files in your editor or browser."
