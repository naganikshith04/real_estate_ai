#!/bin/bash

# Run the full AI analysis with real language models

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running Real Estate AI Analysis with GPT-4o${NC}"

# Check if virtual environment exists
if [ -d "venv" ]; then
    # Activate virtual environment
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Check if API key is configured correctly
if grep -q "your_openai_api_key_here" .env; then
    echo -e "${RED}API key not found in .env file.${NC}"
    echo "Please add your OpenAI API key to the .env file first."
    exit 1
fi

# Generate sample data if it doesn't exist
if [ ! -d "data" ]; then
    echo -e "${YELLOW}Generating sample data...${NC}"
    python3 -c "from data_providers.sample_data import SampleDataProvider; SampleDataProvider().generate_all_sample_data()"
fi

# Run the analysis
echo -e "${GREEN}Starting AI analysis...${NC}"
echo -e "${YELLOW}This may take several minutes as the AI agents work on your data.${NC}"
echo "Press Ctrl+C at any time to cancel."
echo ""

python3 main.py

echo -e "\n${GREEN}Analysis complete!${NC}"
echo "You can now run the dashboard to explore the results:"
echo -e "${YELLOW}streamlit run web_dashboard.py${NC}"

# Deactivate virtual environment
deactivate