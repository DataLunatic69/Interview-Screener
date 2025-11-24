#!/bin/bash

# Setup script for AI Interview Screener

echo "🚀 Setting up AI Interview Screener..."

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Create virtual environment (optional but recommended)
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GROQ_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GROQ_API_KEY (get it from https://console.groq.com)"
echo "2. Start Redis (docker run -d -p 6379:6379 redis:7-alpine)"
echo "3. Run the app: python main.py"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""

