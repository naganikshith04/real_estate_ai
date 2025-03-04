#!/bin/bash

# Run the Real Estate AI system with specialized use cases

echo -e "\033[0;32mStarting Real Estate AI with OSM Integration and Specialized Use Cases\033[0m"

# First, make sure we have sample data
echo -e "\033[1;33mEnsuring sample data is ready...\033[0m"
if [ ! -f "data/property_listings.json" ]; then
    ./demo_setup.sh
else
    echo "Sample data already exists"
fi

# Activate the virtual environment
echo -e "\033[1;33mActivating virtual environment...\033[0m"
source venv/bin/activate

# Start the dashboard
echo -e "\033[1;33mLaunching specialized dashboard with OpenStreetMap integration...\033[0m"
echo "Access the dashboard at http://localhost:8501 when it starts"
echo -e "\033[0;32mPress Ctrl+C to stop the dashboard when finished\033[0m"
streamlit run specialized_dashboard.py