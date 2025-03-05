import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import logger, DATA_DIR, PROPERTY_LISTINGS_FILE, HISTORICAL_PRICES_FILE, INFRASTRUCTURE_PROJECTS_FILE, TARGET_CITIES

class SampleDataProvider:
    """
    Provides sample real estate data for testing the system
    """
    
    def __init__(self):
        """Initialize the sample data provider with cities and areas"""
        self.logger = logger.getChild("sample_data")
        self.logger.info("Initializing SampleDataProvider")
        
        self.cities = TARGET_CITIES
        self.areas = {
            "Mumbai": ["Andheri", "Bandra", "Worli", "Powai", "Juhu"],
            "Bangalore": ["Whitefield", "Electronic City", "Koramangala", "Indiranagar", "HSR Layout"],
            "Hyderabad": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills", "Madhapur"],
            "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Aundh"],
            "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad"]
        }
        
        # Ensure all directories exist
        os.makedirs(DATA_DIR, exist_ok=True)
        
    def generate_property_listings(self):
        """Generate sample property listings data"""
        property_types = ["Apartment", "House", "Villa", "Penthouse"]
        listings = []
        
        for city in self.cities:
            for area in self.areas[city]:
                # Generate 5-10 listings per area
                num_listings = np.random.randint(5, 11)
                for _ in range(num_listings):
                    # Generate property details
                    prop_type = np.random.choice(property_types)
                    sqft = np.random.randint(800, 3000)
                    price_per_sqft = np.random.randint(5000, 15000)
                    price = sqft * price_per_sqft
                    bedrooms = np.random.randint(1, 6)
                    
                    listing = {
                        "city": city,
                        "area": area,
                        "property_type": prop_type,
                        "bedrooms": bedrooms,
                        "sqft": sqft,
                        "price": price,
                        "price_per_sqft": price_per_sqft,
                        "listing_date": (datetime.now() - timedelta(days=np.random.randint(1, 60))).strftime("%Y-%m-%d")
                    }
                    listings.append(listing)
        
        try:
            # Save to JSON file
            with open(PROPERTY_LISTINGS_FILE, "w") as f:
                json.dump(listings, f, indent=2)
            self.logger.info(f"Generated and saved {len(listings)} property listings")
            return listings
        except Exception as e:
            self.logger.error(f"Error saving property listings: {str(e)}")
            return []
    
    def generate_historical_prices(self):
        """Generate sample historical price data for past 5 years"""
        historical_data = []
        
        # Generate monthly data for past 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)  # 5 years ago
        
        current_date = start_date
        while current_date <= end_date:
            month_year = current_date.strftime("%Y-%m")
            
            for city in self.cities:
                for area in self.areas[city]:
                    # Base price per sqft with some randomness
                    base_price = np.random.randint(4000, 10000)
                    
                    # Add growth trend over time
                    months_passed = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
                    growth_factor = 1 + (months_passed * 0.005)  # 0.5% monthly growth on average
                    
                    # Add area-specific growth factors (some areas grow faster)
                    area_growth_factor = 1 + (self.areas[city].index(area) * 0.001)
                    
                    # Add some random variation
                    random_factor = np.random.uniform(0.95, 1.05)
                    
                    price = int(base_price * growth_factor * area_growth_factor * random_factor)
                    
                    data_point = {
                        "city": city,
                        "area": area,
                        "month_year": month_year,
                        "avg_price_per_sqft": price
                    }
                    historical_data.append(data_point)
            
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        try:
            # Save to JSON file
            with open(HISTORICAL_PRICES_FILE, "w") as f:
                json.dump(historical_data, f, indent=2)
            self.logger.info(f"Generated and saved {len(historical_data)} historical price data points")
            return historical_data
        except Exception as e:
            self.logger.error(f"Error saving historical prices: {str(e)}")
            return []
    
    def generate_infrastructure_projects(self):
        """Generate sample infrastructure development data"""
        project_types = ["Metro", "Highway", "Airport", "IT Park", "Mall", "Hospital", "University"]
        statuses = ["Announced", "In Progress", "Completed"]
        
        projects = []
        
        for city in self.cities:
            # Generate 3-7 projects per city
            num_projects = np.random.randint(3, 8)
            for _ in range(num_projects):
                proj_type = np.random.choice(project_types)
                area = np.random.choice(self.areas[city])
                status = np.random.choice(statuses)
                
                # Completion dates
                if status == "Completed":
                    completion_date = (datetime.now() - timedelta(days=np.random.randint(30, 365))).strftime("%Y-%m-%d")
                elif status == "In Progress":
                    completion_date = (datetime.now() + timedelta(days=np.random.randint(30, 730))).strftime("%Y-%m-%d")
                else:  # Announced
                    completion_date = (datetime.now() + timedelta(days=np.random.randint(365, 1460))).strftime("%Y-%m-%d")
                
                project = {
                    "city": city,
                    "area": area,
                    "project_name": f"{city} {proj_type} Development",
                    "project_type": proj_type,
                    "status": status,
                    "announcement_date": (datetime.now() - timedelta(days=np.random.randint(30, 730))).strftime("%Y-%m-%d"),
                    "expected_completion_date": completion_date,
                    "impact_radius_km": np.random.randint(1, 10)
                }
                projects.append(project)
        
        try:
            # Save to JSON file
            with open(INFRASTRUCTURE_PROJECTS_FILE, "w") as f:
                json.dump(projects, f, indent=2)
            self.logger.info(f"Generated and saved {len(projects)} infrastructure projects")
            return projects
        except Exception as e:
            self.logger.error(f"Error saving infrastructure projects: {str(e)}")
            return []
    
    def generate_all_sample_data(self):
        """Generate all sample data files"""
        self.logger.info("Generating all sample data")
        
        property_listings = self.generate_property_listings()
        historical_prices = self.generate_historical_prices()
        infrastructure_projects = self.generate_infrastructure_projects()
        
        # Create ROI analysis sample
        try:
            sample_roi = {
                "top_investment_areas": [
                    ["Bangalore", "Whitefield", 38.5],
                    ["Pune", "Hinjewadi", 36.7],
                    ["Hyderabad", "HITEC City", 35.8],
                    ["Mumbai", "Powai", 33.2],
                    ["Bangalore", "Electronic City", 32.9],
                    ["Hyderabad", "Gachibowli", 32.5],
                    ["Pune", "Baner", 30.1],
                    ["Mumbai", "Bandra", 29.7],
                    ["Hyderabad", "Madhapur", 28.5],
                    ["Delhi-NCR", "Gurgaon", 27.8]
                ],
                "city_roi_analysis": {}
            }
            
            # Add city-specific ROI data
            for city in self.cities:
                areas_by_roi = []
                for area in self.areas[city]:
                    roi = np.random.uniform(15, 40)
                    area_data = {
                        "growth_factors": [
                            {"factor": "Infrastructure", "impact": np.random.uniform(3, 5)},
                            {"factor": "Job Growth", "impact": np.random.uniform(2, 5)},
                            {"factor": "Connectivity", "impact": np.random.uniform(2, 4)}
                        ],
                        "roi_projections": {
                            "3_year_roi_percent": roi * 0.6,
                            "5_year_roi_percent": roi,
                            "10_year_roi_percent": roi * 1.8,
                            "risk_score": np.random.uniform(2, 8)
                        }
                    }
                    areas_by_roi.append([area, roi, area_data])
                
                # Sort by ROI (descending)
                areas_by_roi.sort(key=lambda x: x[1], reverse=True)
                
                sample_roi["city_roi_analysis"][city] = {
                    "areas_by_roi": areas_by_roi,
                    "avg_roi": np.mean([a[1] for a in areas_by_roi])
                }
            
            # Save ROI analysis
            os.makedirs(os.path.dirname(os.path.join(DATA_DIR, "reports")), exist_ok=True)
            with open(os.path.join(DATA_DIR, "reports", "roi_analysis_sample.json"), "w") as f:
                json.dump(sample_roi, f, indent=2)
                
            self.logger.info("Generated and saved sample ROI analysis")
            
        except Exception as e:
            self.logger.error(f"Error saving ROI analysis sample: {str(e)}")
        
        self.logger.info(f"Successfully generated all sample data")
        
        return {
            "property_listings": property_listings,
            "historical_prices": historical_prices,
            "infrastructure_projects": infrastructure_projects
        }