# CatatUang Auto Setup Script for Windows
# Jalankan: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "🚀 CatatUang Auto Setup Script" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

# Check prerequisites
Write-Host "`n📋 Checking Prerequisites..." -ForegroundColor Blue

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Success "Node.js found: $nodeVersion"
} catch {
    Write-Error "Node.js not found. Please install Node.js first."
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version 2>$null
    if (-not $pythonVersion) {
        $pythonVersion = python3 --version
    }
    Write-Success "Python found: $pythonVersion"
} catch {
    Write-Error "Python not found. Please install Python first."
    Write-Host "Download from: https://python.org/" -ForegroundColor Yellow
    exit 1
}

# Check Git
try {
    git --version | Out-Null
    Write-Success "Git found"
} catch {
    Write-Error "Git not found. Please install Git first."
    Write-Host "Download from: https://git-scm.com/" -ForegroundColor Yellow
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing Dependencies..." -ForegroundColor Blue

# Install Python dependencies
if (Test-Path "requirements.txt") {
    Write-Info "Installing Python packages..."
    try {
        pip install -r requirements.txt
        Write-Success "Python packages installed"
    } catch {
        Write-Warning "Some Python packages may have failed to install"
    }
} else {
    Write-Warning "requirements.txt not found"
}

# Install Node.js dependencies
if (Test-Path "package.json") {
    Write-Info "Installing Node.js packages..."
    try {
        npm install
        Write-Success "Node.js packages installed"
    } catch {
        Write-Warning "Some Node.js packages may have failed to install"
    }
} else {
    Write-Warning "package.json not found"
}

# Install Vercel CLI
Write-Info "Installing Vercel CLI..."
try {
    npm install -g vercel
    Write-Success "Vercel CLI installed"
} catch {
    Write-Warning "Vercel CLI installation may have failed"
}

# Environment setup
Write-Host "`n⚙️  Environment Setup..." -ForegroundColor Blue

if (-not (Test-Path ".env.local")) {
    Write-Info "Creating .env.local from template..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env.local"
        Write-Success ".env.local created from .env.example"
        Write-Warning "Please edit .env.local with your actual credentials"
    } elseif (Test-Path "examples\credentials.json.example") {
        Copy-Item "examples\credentials.json.example" ".env.local"
        Write-Success ".env.local created from examples template"
        Write-Warning "Please edit .env.local with your actual credentials"
    } else {
        Write-Error "No template file found. Creating basic .env.local..."
        $envContent = @"
# Copy from .env.example and fill with your actual values
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_SERVICE_ACCOUNT_KEY=your_base64_encoded_service_account_key_here
WHATSAPP_VERIFY_TOKEN=catatuang_2025
"@
        $envContent | Out-File -FilePath ".env.local" -Encoding utf8
        Write-Success ".env.local created with basic template"
    }
} else {
    Write-Info ".env.local already exists"
}

# Create .gitignore if not exists
if (-not (Test-Path ".gitignore")) {
    Write-Info "Creating .gitignore..."
    $gitignoreContent = @"
# Environment
.env*
!.env.example

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Node.js
node_modules/
.npm

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary
*.tmp
.temp/
"@
    $gitignoreContent | Out-File -FilePath ".gitignore" -Encoding utf8
    Write-Success ".gitignore created"
}

# Test local development
Write-Host "`n🧪 Testing Local Setup..." -ForegroundColor Blue

Write-Info "Testing Python imports..."
try {
    $testScript = @"
try:
    import gspread
    import google.auth
    print('✅ Python dependencies OK')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
"@
    python -c $testScript
} catch {
    Write-Warning "Could not test Python dependencies"
}

# Create batch file for easy deployment
Write-Info "Creating deployment helper..."
$deployScript = @"
@echo off
echo 🚀 Deploying CatatUang to Vercel...
echo.
echo Make sure you have:
echo 1. Edited .env.local with your credentials
echo 2. Logged in to Vercel (vercel login)
echo.
pause
vercel --prod
echo.
echo ✅ Deployment complete!
echo Check your Vercel dashboard for the URL.
pause
"@
$deployScript | Out-File -FilePath "deploy.bat" -Encoding ascii
Write-Success "deploy.bat created for easy deployment"

# Instructions
Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Blue
Write-Host "1. Edit .env.local with your credentials:"
Write-Host "   - GOOGLE_SERVICE_ACCOUNT_KEY (base64 encoded)"
Write-Host "   - GOOGLE_SHEETS_ID"
Write-Host "   - WHATSAPP_VERIFY_TOKEN"
Write-Host ""
Write-Host "2. Deploy to Vercel:"
Write-Host "   vercel login"
Write-Host "   vercel"
Write-Host "   Or run: deploy.bat"
Write-Host ""
Write-Host "3. Set environment variables in Vercel Dashboard"
Write-Host ""
Write-Host "4. Test your deployment:"
Write-Host "   curl https://your-app.vercel.app/api/report"
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "- Quick Start: QUICK_START.md"
Write-Host "- Full Guide: SETUP_GUIDE.md"
Write-Host "- API Docs: docs\api.md"
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green

# Ask if user wants to open documentation
$openDocs = Read-Host "`nOpen QUICK_START.md now? (y/n)"
if ($openDocs -eq 'y' -or $openDocs -eq 'Y') {
    try {
        Start-Process "QUICK_START.md"
    } catch {
        Write-Info "Please open QUICK_START.md manually"
    }
}
