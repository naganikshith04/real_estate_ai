#!/bin/bash

# Start the Streamlit dashboard
echo "Starting Real Estate AI Dashboard..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Launch the Streamlit dashboard
echo "Launching dashboard..."
streamlit run web_dashboard.py

# Deactivate virtual environment when done
deactivate