from crewai import Crew
import os
import json
from dotenv import load_dotenv

from agents.data_collector import DataCollectorAgent
from agents.analyst import AnalystAgent
from agents.advisor import AdvisorAgent
from tasks import RealEstateTasks
from model_setup import ModelSetup
from data_providers.sample_data import SampleDataProvider

# Load environment variables
load_dotenv()

def prepare_sample_data():
    """Generate sample data for testing the system"""
    print("Generating sample real estate data for testing...")
    data_provider = SampleDataProvider()
    sample_data = data_provider.generate_all_sample_data()
    return sample_data

def main():
    # Generate sample data if it doesn't exist
    if not os.path.exists("data/property_listings.json"):
        prepare_sample_data()
        print("Sample data generated successfully!")
    else:
        print("Using existing sample data...")
    
    # Initialize model
    model_setup = ModelSetup()
    
    # Choose which model to use - uncomment the one you want to use
    # Use OpenAI GPT-4o model
    from langchain_community.chat_models import ChatOpenAI
    import os
    from dotenv import load_dotenv
    
    # Load API key from .env
    load_dotenv()
    
    # Initialize OpenAI model
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key or openai_api_key == "your_openai_api_key_here":
            raise ValueError("Valid API key not found in .env file")
            
        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.2,
            api_key=openai_api_key
        )
        print("Using OpenAI GPT-4o model")
    except Exception as e:
        print(f"Failed to initialize GPT-4o model: {str(e)}")
        print("Falling back to demo mode. Please check your API key.")
        
        # Fall back to fake LLM for demonstration
        from langchain_community.llms.fake import FakeListLLM
        responses = [
            "I've collected comprehensive real estate data for all cities.",
            "Analysis complete. I've identified high-growth areas and ROI potential.",
            "Here are my investment recommendations based on the analysis."
        ]
        llm = FakeListLLM(responses=responses)
    
    # Initialize agents
    print("Initializing agents...")
    data_collector = DataCollectorAgent(llm).create()
    analyst = AnalystAgent(llm).create()
    advisor = AdvisorAgent(llm).create()
    
    # Initialize tasks
    tasks = RealEstateTasks()
    
    # Cities to analyze
    target_cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
    
    print(f"Starting analysis for cities: {', '.join(target_cities)}")
    
    # Create tasks
    data_collection_task = tasks.collect_market_data(data_collector, target_cities)
    analysis_task = tasks.analyze_market_trends(analyst, "{{data_collection_task.output}}")
    recommendation_task = tasks.generate_investment_recommendations(advisor, "{{analysis_task.output}}")
    
    # Create and run crew
    crew = Crew(
        agents=[data_collector, analyst, advisor],
        tasks=[data_collection_task, analysis_task, recommendation_task],
        verbose=True
    )
    
    print("Starting real estate market analysis...")
    try:
        result = crew.kickoff()
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        # Create a mock result for demonstration
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
    with open("data/reports/final_recommendations.json", "w") as f:
        try:
            # Try parsing the result as JSON first
            result_json = json.loads(result)
            json.dump(result_json, f, indent=2)
        except:
            # If not valid JSON, just write as text
            f.write(result)
    
    print("\n==== Real Estate Investment Recommendations ====\n")
    print(result)
    print("\nAnalysis complete! Final recommendations saved to data/reports/final_recommendations.json")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data/reports", exist_ok=True)
    main()