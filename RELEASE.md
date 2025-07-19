# GitHub Release Automation

This repository is configured with GitHub Actions to automatically build and release executables for Windows, Linux, and macOS whenever you create a new version tag.

## How to Create a Release

### Method 1: Create a Tag (Automatic Release)

1. **Make sure your code is ready for release**
   ```bash
   git add .
   git commit -m "Prepare for release v1.0.0"
   git push origin main
   ```

2. **Create and push a version tag**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Wait for the build to complete**
   - GitHub Actions will automatically:
     - Build executables for Windows, Linux, and macOS
     - Create a new release on GitHub
     - Upload the executables as release assets

### Method 2: Manual Trigger

You can also manually trigger the build workflow from the GitHub Actions tab in your repository.

## Testing Locally

Before creating a release, you can test the executable creation locally:

### On Linux/macOS:
```bash
./build_local.sh
```

### On Windows:
```batch
build_local.bat
```

This will create an executable in the `dist/` directory that you can test.

## Release Files

Each release will include three executable files:

- **`flask-finance-windows-x64.exe`** - For Windows (64-bit)
- **`flask-finance-linux-x64`** - For Linux (64-bit)
- **`flask-finance-macos-x64`** - For macOS (64-bit)

## How Users Run the Executables

### Windows:
1. Download `flask-finance-windows-x64.exe`
2. Double-click to run
3. Open browser to `http://localhost:5000`

### Linux:
1. Download `flask-finance-linux-x64`
2. Make executable: `chmod +x flask-finance-linux-x64`
3. Run: `./flask-finance-linux-x64`
4. Open browser to `http://localhost:5000`

### macOS:
1. Download `flask-finance-macos-x64`
2. Make executable: `chmod +x flask-finance-macos-x64`
3. Run: `./flask-finance-macos-x64`
4. Open browser to `http://localhost:5000`

## Troubleshooting

### If the build fails:

1. **Check the GitHub Actions logs** in the "Actions" tab of your repository
2. **Test locally first** using the build scripts
3. **Make sure all dependencies are in requirements.txt**
4. **Verify that all imports work correctly**

### Common issues:

- **Missing dependencies**: Add them to `requirements.txt`
- **Import errors**: Add hidden imports to the PyInstaller spec file
- **File not found errors**: Make sure template and static files are included in the build

## Customization

### To modify the build process:

1. **Edit `.github/workflows/release.yml`** to change the workflow
2. **Edit `flask-finance.spec`** to modify PyInstaller settings
3. **Update build scripts** (`build_local.sh` and `build_local.bat`) for local testing

### To change the release description:

Edit the `body` section in `.github/workflows/release.yml` under the "Create Release" step.

## Version Naming

Use semantic versioning for your tags:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

The GitHub Action will automatically use the tag name in the release title and description.
