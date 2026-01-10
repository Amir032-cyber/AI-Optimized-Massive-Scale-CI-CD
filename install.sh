#!/bin/bash

###############################################################################
# PTS (Predictive Test Selection) - Installation Script
# Compatible with: Linux, Termux, macOS
# 
# Usage: bash install.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -qi termux /proc/version 2>/dev/null || [[ -d "$PREFIX" ]]; then
            echo "termux"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main installation
main() {
    print_header "PTS Installation"
    
    OS=$(detect_os)
    print_info "Detected OS: $OS"
    
    # Check Python
    print_header "Checking Python Installation"
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Installing..."
        
        case $OS in
            termux)
                apt update && apt install -y python
                ;;
            linux)
                if command_exists apt-get; then
                    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
                elif command_exists yum; then
                    sudo yum install -y python3 python3-pip
                elif command_exists pacman; then
                    sudo pacman -S python python-pip
                else
                    print_error "Unsupported package manager"
                    exit 1
                fi
                ;;
            macos)
                if command_exists brew; then
                    brew install python3
                else
                    print_error "Homebrew not found. Please install it first."
                    exit 1
                fi
                ;;
        esac
        print_success "Python installed"
    fi
    
    # Check Git
    print_header "Checking Git Installation"
    if command_exists git; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        print_success "Git $GIT_VERSION found"
    else
        print_error "Git not found. Installing..."
        
        case $OS in
            termux)
                apt install -y git
                ;;
            linux)
                if command_exists apt-get; then
                    sudo apt-get install -y git
                elif command_exists yum; then
                    sudo yum install -y git
                elif command_exists pacman; then
                    sudo pacman -S git
                fi
                ;;
            macos)
                if command_exists brew; then
                    brew install git
                fi
                ;;
        esac
        print_success "Git installed"
    fi
    
    # Install system dependencies
    print_header "Installing System Dependencies"
    
    case $OS in
        termux)
            print_info "Installing Termux dependencies..."
            apt update
            apt install -y build-essential clang python3-dev libffi-dev libssl-dev
            ;;
        linux)
            print_info "Installing Linux dependencies..."
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y build-essential python3-dev libffi-dev libssl-dev
            elif command_exists yum; then
                sudo yum groupinstall -y "Development Tools"
                sudo yum install -y python3-devel libffi-devel openssl-devel
            elif command_exists pacman; then
                sudo pacman -S base-devel
            fi
            ;;
        macos)
            print_info "Installing macOS dependencies..."
            if command_exists brew; then
                brew install libffi openssl
            fi
            ;;
    esac
    
    print_success "System dependencies installed"
    
    # Create virtual environment
    print_header "Creating Virtual Environment"
    
    if [[ -d "venv" ]]; then
        print_warning "Virtual environment already exists. Skipping..."
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_header "Upgrading pip"
    pip install --upgrade pip setuptools wheel
    print_success "pip upgraded"
    
    # Install Python dependencies
    print_header "Installing Python Dependencies"
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_success "Production dependencies installed"
    fi
    
    if [[ -f "requirements-dev.txt" ]]; then
        pip install -r requirements-dev.txt
        print_success "Development dependencies installed"
    fi
    
    # Run tests
    print_header "Running Tests"
    if command_exists pytest; then
        pytest tests/ -v --tb=short || print_warning "Some tests failed"
    else
        print_warning "pytest not found. Skipping tests."
    fi
    
    # Display next steps
    print_header "Installation Complete!"
    echo ""
    print_info "Next steps:"
    echo "  1. Activate the virtual environment:"
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. Run the API server:"
    echo "     python -m uvicorn src.pts.api.server:app --reload"
    echo ""
    echo "  3. Train a model:"
    echo "     python scripts/train_model.py"
    echo ""
    echo "  4. Make predictions:"
    echo "     python scripts/predict.py"
    echo ""
    print_success "Happy testing! 🚀"
}

# Run main function
main
