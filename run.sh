#!/bin/bash

# Setup script for running the Real Estate AI analysis system

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.8 or newer."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if API keys are configured
if grep -q "your_openai_api_key_here\|your_anthropic_api_key_here" .env; then
    echo "===================================================="
    echo "WARNING: API keys not configured in .env file."
    echo "Before running the analysis, please edit the .env file"
    echo "and add your OpenAI, Anthropic, or AWS Bedrock credentials."
    echo "===================================================="
else
    echo "API keys appear to be configured."
fi

# Run the analysis
echo "Starting Real Estate AI analysis..."
python main.py

# Deactivate virtual environment
deactivate

echo "Analysis complete!"