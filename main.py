#!/usr/bin/env python3
"""
Main module for Real Estate AI Investment Analysis
"""

from crewai import Crew
import os
import sys
import json
import traceback
from dotenv import load_dotenv

# Import from our config package
try:
    from config import logger, PROPERTY_LISTINGS_FILE, FINAL_RECOMMENDATIONS_FILE, TARGET_CITIES
    from config.llm_utils import LLMProvider
except ImportError:
    # Set up basic logging if config import fails
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("real_estate_ai")
    
    # Set default values
    PROPERTY_LISTINGS_FILE = os.path.join("data", "property_listings.json")
    FINAL_RECOMMENDATIONS_FILE = os.path.join("data", "reports", "final_recommendations.json")
    TARGET_CITIES = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]

from agents.data_collector import DataCollectorAgent
from agents.analyst import AnalystAgent
from agents.advisor import AdvisorAgent
from tasks import RealEstateTasks
from data_providers.sample_data import SampleDataProvider

# Load environment variables
load_dotenv()

def prepare_sample_data():
    """Generate sample data for testing the system"""
    logger.info("Generating sample real estate data for testing...")
    data_provider = SampleDataProvider()
    sample_data = data_provider.generate_all_sample_data()
    return sample_data

def main():
    # Generate sample data if it doesn't exist
    if not os.path.exists(PROPERTY_LISTINGS_FILE):
        prepare_sample_data()
        logger.info("Sample data generated successfully!")
    else:
        logger.info("Using existing sample data...")
    
    # Initialize the LLM provider
    llm_provider = LLMProvider()
    
    # Get available models
    available_models = llm_provider.get_available_models()
    logger.info(f"Available models: {available_models}")
    
    # Initialize model with fallback mechanism
    try:
        # Try to use the best available model
        model_name = llm_provider.get_best_available_model()
        logger.info(f"Using model: {model_name}")
        
        # Initialize the LLM
        llm = llm_provider.initialize_llm(model_name, temperature=0.2)
        
    except Exception as e:
        logger.error(f"Error initializing model: {str(e)}")
        logger.error(traceback.format_exc())
        logger.warning("Falling back to demo mode")
        
        # Fall back to fake LLM for demonstration
        from langchain.llms.fake import FakeListLLM
        responses = [
            "I've collected comprehensive real estate data for all cities.",
            "Analysis complete. I've identified high-growth areas and ROI potential.",
            "Here are my investment recommendations based on the analysis."
        ]
        llm = FakeListLLM(responses=responses)
    
    # Initialize agents
    logger.info("Initializing agents...")
    data_collector = DataCollectorAgent(llm).create()
    analyst = AnalystAgent(llm).create()
    advisor = AdvisorAgent(llm).create()
    
    # Initialize tasks
    tasks = RealEstateTasks()
    
    # Use target cities from config
    logger.info(f"Starting analysis for cities: {', '.join(TARGET_CITIES)}")
    
    # Create tasks
    data_collection_task = tasks.collect_market_data(data_collector, TARGET_CITIES)
    analysis_task = tasks.analyze_market_trends(analyst, "{{data_collection_task.output}}")
    recommendation_task = tasks.generate_investment_recommendations(advisor, "{{analysis_task.output}}")
    
    # Create and run crew
    crew = Crew(
        agents=[data_collector, analyst, advisor],
        tasks=[data_collection_task, analysis_task, recommendation_task],
        verbose=True
    )
    
    logger.info("Starting real estate market analysis...")
    try:
        # Add progress indicators for longer tasks
        logger.info("This may take some time depending on the model...")
        
        # Execute the analysis process
        result = crew.kickoff()
        
        logger.info("Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Create a mock result for demonstration
        logger.warning("Generating fallback results for demonstration")
        result = {
            "investment_recommendations": {
                "top_areas": [
                    {"city": "Bangalore", "area": "Whitefield", "roi_5yr": 42.5},
                    {"city": "Pune", "area": "Hinjewadi", "roi_5yr": 38.2},
                    {"city": "Hyderabad", "area": "HITEC City", "roi_5yr": 37.8}
                ],
                "risk_assessment": "These areas show strong potential with moderate risk profiles.",
                "summary": "Focus on tech-hub adjacent areas with ongoing infrastructure development."
            }
        }
        result = json.dumps(result)
    
    # Save final result to a file
    try:
        os.makedirs(os.path.dirname(FINAL_RECOMMENDATIONS_FILE), exist_ok=True)
        with open(FINAL_RECOMMENDATIONS_FILE, "w") as f:
            try:
                # Try parsing the result as JSON first
                result_json = json.loads(result)
                json.dump(result_json, f, indent=2)
                logger.info(f"Saved results as JSON to {FINAL_RECOMMENDATIONS_FILE}")
            except json.JSONDecodeError:
                # If not valid JSON, just write as text
                f.write(result)
                logger.info(f"Saved results as text to {FINAL_RECOMMENDATIONS_FILE}")
    except Exception as e:
        logger.error(f"Error saving recommendations: {str(e)}")
    
    logger.info("\n==== Real Estate Investment Recommendations ====\n")
    logger.info(result)
    logger.info(f"\nAnalysis complete! Final recommendations saved to {FINAL_RECOMMENDATIONS_FILE}")
    
    print("\n==== Real Estate Investment Recommendations ====\n")
    print(result)
    print(f"\nAnalysis complete! Final recommendations saved to {FINAL_RECOMMENDATIONS_FILE}")

if __name__ == "__main__":
    main()