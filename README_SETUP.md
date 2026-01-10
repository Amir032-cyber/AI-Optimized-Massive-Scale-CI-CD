# PTS Installation & Setup Guide

Complete guide for installing and running Predictive Test Selection on Linux, Termux, and other Unix-like systems.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Platform-Specific Guides](#platform-specific-guides)
- [Troubleshooting](#troubleshooting)
- [Development Setup](#development-setup)

## 🚀 Quick Start

### One-Line Installation (Recommended)

```bash
git clone https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD.git
cd AI-Optimized-Massive-Scale-CI-CD
bash install.sh
source venv/bin/activate
bash quickstart.sh
```

The API will be available at `http://localhost:8000`

## 📦 System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB for installation + dependencies
- **OS**: Linux, Termux, macOS, or Windows (WSL2)

### Required System Packages

The installation script will automatically install these, but you can pre-install them:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv build-essential git
```

**Termux:**
```bash
apt update
apt install -y python git build-essential clang
```

**Fedora/RHEL:**
```bash
sudo yum install -y python3 python3-pip python3-devel gcc git
```

**macOS:**
```bash
brew install python3 git
```

## 🔧 Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
bash install.sh
```

This script will:
- Detect your operating system
- Install required system dependencies
- Create a Python virtual environment
- Install all Python packages
- Run tests to verify installation

### Method 2: Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Method 3: Docker Installation

```bash
docker build -t pts:latest .
docker run -p 8000:8000 pts:latest
```

## 🖥️ Platform-Specific Guides

### Linux (Ubuntu/Debian)

```bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git build-essential

# 2. Clone repository
git clone https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD.git
cd AI-Optimized-Massive-Scale-CI-CD

# 3. Run installation
bash install.sh

# 4. Activate environment and start
source venv/bin/activate
bash quickstart.sh
```

### Termux (Android)

```bash
# 1. Update package manager
apt update && apt upgrade -y

# 2. Install dependencies
apt install -y python git build-essential clang libffi-dev libssl-dev

# 3. Clone repository
git clone https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD.git
cd AI-Optimized-Massive-Scale-CI-CD

# 4. Run installation
bash install.sh

# 5. Start the server
source venv/bin/activate
bash quickstart.sh
```

**Note for Termux users**: The server will run on `http://localhost:8000` but you can access it from your browser using your device's local IP address.

### macOS

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies
brew install python3 git

# 3. Clone repository
git clone https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD.git
cd AI-Optimized-Massive-Scale-CI-CD

# 4. Run installation
bash install.sh

# 5. Start the server
source venv/bin/activate
bash quickstart.sh
```

### Windows (WSL2)

```bash
# 1. Open WSL2 terminal
# 2. Update package manager
sudo apt-get update

# 3. Follow Ubuntu/Debian guide above
```

## 🚀 Running the Application

### Start the API Server

```bash
source venv/bin/activate
bash quickstart.sh
```

Or manually:

```bash
python -m uvicorn src.pts.api.server:app --reload --host 0.0.0.0 --port 8000
```

### Access the API

- **API Base URL**: `http://localhost:8000`
- **Interactive Docs (Swagger)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`

### Example API Call

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "commit_hash": "abc123def456",
    "repository_url": "https://github.com/user/repo",
    "changed_files": ["src/main.py", "tests/test_main.py"]
  }'
```

## 🧪 Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_core.py -v

# Run with coverage
pytest tests/ --cov=src/pts --cov-report=html
```

## 📊 Training a Model

```bash
source venv/bin/activate
python scripts/train_model.py
```

## 🔍 Making Predictions

```bash
source venv/bin/activate
python scripts/predict.py
```

## 🐛 Troubleshooting

### Issue: "Python 3 not found"

**Solution**: Install Python 3
```bash
# Ubuntu/Debian
sudo apt-get install -y python3

# Termux
apt install -y python

# macOS
brew install python3
```

### Issue: "Permission denied" when running scripts

**Solution**: Make scripts executable
```bash
chmod +x install.sh quickstart.sh
```

### Issue: "ModuleNotFoundError" when running Python

**Solution**: Activate virtual environment
```bash
source venv/bin/activate
```

### Issue: Port 8000 already in use

**Solution**: Use a different port
```bash
python -m uvicorn src.pts.api.server:app --port 8001
```

### Issue: "libssl.so.1.1: cannot open shared object file" (Termux)

**Solution**: Install OpenSSL
```bash
apt install -y openssl libssl-dev
```

### Issue: Installation fails on Termux

**Solution**: Update packages and try again
```bash
apt update
apt upgrade -y
apt install -y build-essential clang python3-dev libffi-dev libssl-dev
```

## 🔨 Development Setup

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Check code style
pylint src/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 📚 Project Structure

```
.
├── src/pts/                 # Main package
│   ├── api/                 # FastAPI application
│   ├── core/                # Core ML components
│   ├── data/                # Data processing
│   ├── features/            # Feature engineering
│   ├── integrations/        # CI/CD integrations
│   └── utils/               # Utilities
├── scripts/                 # Standalone scripts
├── tests/                   # Test suite
├── configs/                 # Configuration files
├── data/                    # Data directory
├── models/                  # Trained models
├── install.sh              # Installation script
├── quickstart.sh           # Quick start script
└── requirements.txt        # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD/discussions)

## 🎯 Next Steps

After installation:

1. Read the [API Documentation](README.md#api-documentation)
2. Try the [Quick Examples](README.md#quick-examples)
3. Explore the [Integration Guides](README.md#integration-guides)
4. Join our community on GitHub Discussions

---

**Happy Testing! 🚀**
