from crewai import Agent
from langchain_core.tools import Tool
import pandas as pd
import json
import os

class DataCollectorAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create(self):
        return Agent(
            role="Real Estate Data Collector",
            goal="Collect comprehensive data about real estate markets in India",
            backstory="""You are an expert in gathering and organizing real estate data 
            from various sources. You have extensive knowledge of the Indian property market
            and know how to access and clean data from multiple sources.""",
            llm=self.llm,
            tools=[
                Tool(
                    name="collect_property_listings",
                    func=self.collect_property_listings,
                    description="Collects property listing data from APIs or websites"
                ),
                Tool(
                    name="collect_historical_prices",
                    func=self.collect_historical_prices,
                    description="Retrieves historical price trends for different areas"
                ),
                Tool(
                    name="collect_infrastructure_data",
                    func=self.collect_infrastructure_data,
                    description="Gathers information about infrastructure development projects"
                )
            ],
            verbose=True
        )
    
    def collect_property_listings(self, city):
        """
        Collect property listings for a specific city
        Uses locally stored sample data for demonstration
        """
        try:
            with open("data/property_listings.json", "r") as f:
                all_listings = json.load(f)
            
            # Filter listings for the requested city
            city_listings = [listing for listing in all_listings if listing["city"] == city]
            
            # Basic analysis
            total_listings = len(city_listings)
            avg_price = sum(listing["price"] for listing in city_listings) / total_listings if total_listings > 0 else 0
            avg_price_per_sqft = sum(listing["price_per_sqft"] for listing in city_listings) / total_listings if total_listings > 0 else 0
            
            # Area-wise breakdown
            areas = {}
            for listing in city_listings:
                area = listing["area"]
                if area not in areas:
                    areas[area] = {"count": 0, "total_price": 0, "total_sqft": 0}
                
                areas[area]["count"] += 1
                areas[area]["total_price"] += listing["price"]
                areas[area]["total_sqft"] += listing["sqft"]
            
            area_summary = {}
            for area, data in areas.items():
                if data["count"] > 0:
                    area_summary[area] = {
                        "listing_count": data["count"],
                        "avg_price": data["total_price"] / data["count"],
                        "avg_sqft": data["total_sqft"] / data["count"],
                        "avg_price_per_sqft": data["total_price"] / data["total_sqft"] if data["total_sqft"] > 0 else 0
                    }
            
            result = {
                "city": city,
                "total_listings": total_listings,
                "average_price": avg_price,
                "average_price_per_sqft": avg_price_per_sqft,
                "area_summary": area_summary,
                "sample_listings": city_listings[:5]  # Include a few sample listings
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error collecting property listings: {str(e)}"
    
    def collect_historical_prices(self, city):
        """
        Retrieve historical price data for a specific city
        Uses locally stored sample data for demonstration
        """
        try:
            with open("data/historical_prices.json", "r") as f:
                all_historical_data = json.load(f)
            
            # Filter data for the requested city
            city_data = [data for data in all_historical_data if data["city"] == city]
            
            # Organize by area and month
            area_data = {}
            for data_point in city_data:
                area = data_point["area"]
                month_year = data_point["month_year"]
                price = data_point["avg_price_per_sqft"]
                
                if area not in area_data:
                    area_data[area] = {}
                
                area_data[area][month_year] = price
            
            # Calculate growth rates
            growth_rates = {}
            for area, monthly_data in area_data.items():
                # Sort by month_year
                sorted_months = sorted(monthly_data.keys())
                if len(sorted_months) >= 12:  # Need at least 12 months for YoY calculation
                    # Calculate YoY growth for each area
                    earliest_price = monthly_data[sorted_months[0]]
                    latest_price = monthly_data[sorted_months[-1]]
                    
                    # Calculate monthly growth rate
                    months_between = len(sorted_months) - 1
                    if months_between > 0 and earliest_price > 0:
                        monthly_growth = (latest_price / earliest_price) ** (1/months_between) - 1
                        annual_growth = ((1 + monthly_growth) ** 12) - 1
                        growth_rates[area] = {
                            "earliest_month": sorted_months[0],
                            "latest_month": sorted_months[-1],
                            "earliest_price": earliest_price,
                            "latest_price": latest_price,
                            "monthly_growth_rate": monthly_growth,
                            "annualized_growth_rate": annual_growth
                        }
            
            result = {
                "city": city,
                "period_covered": f"{sorted_months[0]} to {sorted_months[-1]}" if 'sorted_months' in locals() and sorted_months else "N/A",
                "area_growth_rates": growth_rates,
                "area_data": area_data
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error collecting historical prices: {str(e)}"
    
    def collect_infrastructure_data(self, city):
        """
        Collect infrastructure development data for a specific city
        Uses locally stored sample data for demonstration
        """
        try:
            with open("data/infrastructure_projects.json", "r") as f:
                all_projects = json.load(f)
            
            # Filter projects for the requested city
            city_projects = [project for project in all_projects if project["city"] == city]
            
            # Organize by status and type
            projects_by_status = {
                "Announced": [],
                "In Progress": [],
                "Completed": []
            }
            
            projects_by_type = {}
            projects_by_area = {}
            
            for project in city_projects:
                status = project["status"]
                proj_type = project["project_type"]
                area = project["area"]
                
                projects_by_status[status].append(project)
                
                if proj_type not in projects_by_type:
                    projects_by_type[proj_type] = []
                projects_by_type[proj_type].append(project)
                
                if area not in projects_by_area:
                    projects_by_area[area] = []
                projects_by_area[area].append(project)
            
            # Calculate impact scores for each area (simple heuristic)
            impact_scores = {}
            for area, projects in projects_by_area.items():
                score = 0
                for project in projects:
                    # Weight by status
                    status_weight = 0.5 if project["status"] == "Announced" else 1.0 if project["status"] == "In Progress" else 1.5
                    
                    # Weight by type (simple weights)
                    type_weight = 1.5 if project["project_type"] in ["Metro", "Airport", "IT Park"] else 1.0
                    
                    # Weight by radius
                    radius_weight = project["impact_radius_km"] / 5.0  # Normalize by 5km
                    
                    project_score = status_weight * type_weight * radius_weight
                    score += project_score
                
                impact_scores[area] = score
            
            result = {
                "city": city,
                "total_projects": len(city_projects),
                "projects_by_status": {
                    status: len(projects) for status, projects in projects_by_status.items()
                },
                "projects_by_type": {
                    proj_type: len(projects) for proj_type, projects in projects_by_type.items()
                },
                "infrastructure_impact_scores": impact_scores,
                "projects": city_projects  # Include all project details
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error collecting infrastructure data: {str(e)}"