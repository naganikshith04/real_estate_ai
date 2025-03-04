#!/bin/bash

# Demo setup script for Real Estate AI
# This script prepares a complete demo environment with sample data and visualizations

# Print colored messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Real Estate AI Demo Environment${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install required packages
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Generate sample data
echo -e "${YELLOW}Generating sample data...${NC}"
python3 -c "from data_providers.sample_data import SampleDataProvider; SampleDataProvider().generate_all_sample_data()"

# Generate visualizations
echo -e "${YELLOW}Generating visualizations...${NC}"
python3 visualization_generator.py

echo -e "${GREEN}Demo setup complete!${NC}"
echo "You can now run the following commands:"
echo "1. Start the dashboard: streamlit run web_dashboard.py"
echo "2. View generated visualizations: ls -la data/analysis/visuals/"
echo "3. Run the full AI analysis (if you have API keys): python main.py"

# Add startup script for the dashboard
echo -e "${YELLOW}Creating dashboard startup script...${NC}"
cat > start_dashboard.sh << 'EOL'
#!/bin/bash
# Script to start the web dashboard
source venv/bin/activate
streamlit run web_dashboard.py
EOL

chmod +x start_dashboard.sh

echo -e "${GREEN}All done! Run ./start_dashboard.sh to launch the dashboard.${NC}"