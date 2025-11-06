#!/bin/bash
# Build script: Format, lint, test, and generate coverage

set -e  # Exit on error

echo "=== Running Black (formatter) ==="
python -m black ready_to_start/ tests/

echo ""
echo "=== Running Ruff (linter) ==="
python -m ruff check ready_to_start/ tests/ --fix

echo ""
echo "=== Running pytest with coverage ==="
python -m pytest tests/ --cov=ready_to_start --cov-report=html --cov-report=term

echo ""
echo "=== Build completed successfully! ==="
echo "Coverage report available at: htmlcov/index.html"
