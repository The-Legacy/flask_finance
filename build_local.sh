#!/bin/bash

# Local build script for testing PyInstaller packaging
# This script helps you test the executable creation locally before pushing to GitHub

echo "🚀 Building Flask Finance executable locally..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Create the executable
echo "📦 Creating executable..."
pyinstaller --onefile --name flask-finance \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import flask \
  --hidden-import flask.templating \
  --hidden-import flask.json.tag \
  --hidden-import sqlalchemy \
  --hidden-import sqlalchemy.ext.baked \
  --hidden-import werkzeug \
  --hidden-import werkzeug.security \
  --hidden-import jinja2 \
  --hidden-import click \
  --hidden-import itsdangerous \
  --hidden-import markupsafe \
  --hidden-import flask_sqlalchemy \
  --hidden-import models.transaction \
  --hidden-import models.loan \
  --hidden-import models.investment \
  --hidden-import models.account \
  --hidden-import models.budget \
  --hidden-import database \
  --hidden-import utils.tax_calculator \
  app.py

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Executable created at: dist/flask-finance"
    echo ""
    echo "To test the executable:"
    echo "  cd dist"
    echo "  ./flask-finance"
    echo "  Then open http://localhost:5000 in your browser"
    echo ""
    echo "To create a release on GitHub:"
    echo "  1. Commit and push your changes"
    echo "  2. Create and push a tag: git tag v1.0.0 && git push origin v1.0.0"
    echo "  3. The GitHub Action will automatically build and create a release"
else
    echo "❌ Build failed!"
    exit 1
fi
