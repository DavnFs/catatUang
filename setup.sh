#!/bin/bash

# CatatUang Auto Setup Script
# Jalankan script ini untuk setup project secara otomatis

echo "🚀 CatatUang Auto Setup Script"
echo "==============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
echo -e "\n${BLUE}📋 Checking Prerequisites...${NC}"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js found: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js first."
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python not found. Please install Python first."
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    print_status "Git found"
else
    print_error "Git not found. Please install Git first."
    exit 1
fi

# Install dependencies
echo -e "\n${BLUE}📦 Installing Dependencies...${NC}"

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_info "Installing Python packages..."
    pip install -r requirements.txt
    print_status "Python packages installed"
else
    print_warning "requirements.txt not found"
fi

# Install Node.js dependencies
if [ -f "package.json" ]; then
    print_info "Installing Node.js packages..."
    npm install
    print_status "Node.js packages installed"
else
    print_warning "package.json not found"
fi

# Install Vercel CLI
print_info "Installing Vercel CLI..."
npm install -g vercel
print_status "Vercel CLI installed"

# Environment setup
echo -e "\n${BLUE}⚙️  Environment Setup...${NC}"

if [ ! -f ".env.local" ]; then
    print_info "Creating .env.local from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        print_status ".env.local created from .env.example"
        print_warning "Please edit .env.local with your actual credentials"
    elif [ -f "examples/credentials.json.example" ]; then
        cp examples/credentials.json.example .env.local
        print_status ".env.local created from examples template"
        print_warning "Please edit .env.local with your actual credentials"
    else
        print_error "No template file found. Creating basic .env.local..."
        cat > .env.local << EOL
# Copy from .env.example and fill with your actual values
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_SERVICE_ACCOUNT_KEY=your_base64_encoded_service_account_key_here
WHATSAPP_VERIFY_TOKEN=catatuang_2025
EOL
        print_status ".env.local created with basic template"
    fi
else
    print_info ".env.local already exists"
fi

# Create .gitignore if not exists
if [ ! -f ".gitignore" ]; then
    print_info "Creating .gitignore..."
    cat > .gitignore << EOL
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
EOL
    print_status ".gitignore created"
fi

# Test local development
echo -e "\n${BLUE}🧪 Testing Local Setup...${NC}"

print_info "Testing Python imports..."
python3 -c "
try:
    import gspread
    import google.auth
    print('✅ Python dependencies OK')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
" 2>/dev/null

# Instructions
echo -e "\n${GREEN}🎉 Setup Complete!${NC}"
echo -e "\n${BLUE}📝 Next Steps:${NC}"
echo "1. Edit .env.local with your credentials:"
echo "   - GOOGLE_SERVICE_ACCOUNT_KEY (base64 encoded)"
echo "   - GOOGLE_SHEETS_ID"
echo "   - WHATSAPP_VERIFY_TOKEN"
echo ""
echo "2. Deploy to Vercel:"
echo "   vercel login"
echo "   vercel"
echo ""
echo "3. Set environment variables in Vercel Dashboard"
echo ""
echo "4. Test your deployment:"
echo "   curl https://your-app.vercel.app/api/report"
echo ""
echo -e "${YELLOW}📚 Documentation:${NC}"
echo "- Quick Start: QUICK_START.md"
echo "- Full Guide: SETUP_GUIDE.md"
echo "- API Docs: docs/api.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
