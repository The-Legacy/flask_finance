@echo off
echo 🚀 Building Flask Finance executable locally...

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Create the executable
echo 📦 Creating executable...
pyinstaller --onefile --name flask-finance ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import flask ^
  --hidden-import flask.templating ^
  --hidden-import flask.json.tag ^
  --hidden-import sqlalchemy ^
  --hidden-import sqlalchemy.ext.baked ^
  --hidden-import werkzeug ^
  --hidden-import werkzeug.security ^
  --hidden-import jinja2 ^
  --hidden-import click ^
  --hidden-import itsdangerous ^
  --hidden-import markupsafe ^
  --hidden-import flask_sqlalchemy ^
  --hidden-import models.transaction ^
  --hidden-import models.loan ^
  --hidden-import models.investment ^
  --hidden-import models.account ^
  --hidden-import models.budget ^
  --hidden-import database ^
  --hidden-import utils.tax_calculator ^
  app.py

if %errorlevel% equ 0 (
    echo ✅ Build successful!
    echo 📁 Executable created at: dist\flask-finance.exe
    echo.
    echo To test the executable:
    echo   cd dist
    echo   flask-finance.exe
    echo   Then open http://localhost:5000 in your browser
    echo.
    echo To create a release on GitHub:
    echo   1. Commit and push your changes
    echo   2. Create and push a tag: git tag v1.0.0 ^&^& git push origin v1.0.0
    echo   3. The GitHub Action will automatically build and create a release
) else (
    echo ❌ Build failed!
    exit /b 1
)

pause
