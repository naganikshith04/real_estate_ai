# Real Estate AI - Investment Analysis for Indian Market

An AI-powered system that analyzes the Indian real estate market to predict high-yield investment areas using CrewAI, LangChain, and advanced language models.

![Dashboard Preview](https://i.imgur.com/xoULT8N.png)

## Overview

This project creates a team of AI agents that work together to:

1. Collect real estate market data from various sources
2. Analyze market trends and identify growth patterns
3. Generate investment recommendations for high-yield areas

The system uses multiple AI models (GPT-4o, Claude, Llama) through direct APIs and Amazon Bedrock to power specialized agents that perform different tasks in the analysis pipeline.

## Features

- Multi-agent system with specialized roles (data collector, analyst, advisor)
- Support for multiple AI models (OpenAI, Anthropic, Llama via AWS Bedrock)
- Data collection from various sources (property listings, historical prices, infrastructure projects)
- Price trend analysis and ROI assessment
- Investment recommendations with risk evaluation
- Interactive web dashboard for exploring insights
- Data visualizations including price trends, ROI projections, and risk analysis

## Quick Setup (Demo Mode)

For a quick demonstration with sample data:

1. Clone the repository
2. Run the demo setup script:
   ```
   ./demo_setup.sh
   ```
3. Start the web dashboard:
   ```
   ./start_dashboard.sh
   ```

This will set up a complete demo environment with sample data and visualizations.

## Full Setup (with AI Analysis)

For the complete AI analysis pipeline:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys:
   ```
   cp .env.example .env
   ```
4. Edit `.env` with your API keys for OpenAI, Anthropic, or AWS Bedrock
5. Run the analysis script:
   ```
   python main.py
   ```

## Web Dashboard

The project includes an interactive web dashboard built with Streamlit:

- Market overview with price trends and infrastructure distribution
- Investment recommendations with ROI projections
- ROI analysis with risk-reward visualization
- Data explorer for property listings, historical prices, and infrastructure projects

To launch the dashboard:
```
streamlit run web_dashboard.py
```

## Visualizations

The system generates several visualizations to help analyze the real estate market:

- Price trend charts for different areas
- City comparison charts
- ROI heatmaps
- Risk-reward scatter plots
- Investment horizon comparisons

Generate visualizations from sample data:
```
python visualization_generator.py
```

## Customization

You can modify:
- Target cities in `main.py`
- Analysis parameters in the task descriptions
- LLM selection in `main.py`
- Visualization settings in the visualizers directory

## Directory Structure

```
real_estate_ai/
├── agents/               # AI agent definitions
├── data/                 # Sample and generated data
│   ├── analysis/         # Analysis output and visualizations
│   └── reports/          # Generated reports
├── data_providers/       # Data source connectors
├── visualizers/          # Visualization components
├── main.py               # Main analysis script
├── web_dashboard.py      # Interactive web dashboard
└── visualization_generator.py  # Data visualization script
```

## Future Improvements

- Add real data connectors for property websites (MagicBricks, 99acres, Housing.com)
- Implement geospatial analysis with interactive maps
- Add user authentication and personalized recommendations
- Create mobile app for on-the-go investment insights
- Implement scheduled market monitoring and alerts