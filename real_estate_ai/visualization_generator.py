#!/usr/bin/env python3

import os
import json
from visualizers.price_trend_visualizer import PriceTrendVisualizer
from visualizers.roi_visualizer import ROIVisualizer

def main():
    """
    Generate visualizations from sample data
    """
    print("Generating visualizations from sample data...")
    
    # Ensure output directory exists
    os.makedirs("data/analysis/visuals", exist_ok=True)
    
    # Create visualizers
    price_visualizer = PriceTrendVisualizer()
    roi_visualizer = ROIVisualizer()
    
    # Generate visualizations from historical data
    print("Generating price trend visualizations...")
    try:
        historical_data_path = "data/historical_prices.json"
        if os.path.exists(historical_data_path):
            price_charts = price_visualizer.visualize_historical_data(historical_data_path)
            print(f"Generated {len(price_charts)} price trend charts")
            
            # Create sample ROI data for visualization
            print("Generating ROI visualizations from mock data...")
            create_sample_roi_data()
            
            # Generate ROI visualizations
            roi_data_path = "data/reports/roi_analysis_sample.json"
            if os.path.exists(roi_data_path):
                roi_charts = roi_visualizer.visualize_roi_data(roi_data_path)
                print(f"Generated {len(roi_charts)} ROI visualizations")
            else:
                print("ROI data file not found.")
        else:
            print("Historical price data file not found.")
    except Exception as e:
        print(f"Error generating visualizations: {str(e)}")
    
    print("Visualization generation complete.")

def create_sample_roi_data():
    """
    Create sample ROI analysis data for visualization purposes
    """
    try:
        # Create a structure similar to what our ROI analysis would produce
        cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
        areas = {
            "Mumbai": ["Andheri", "Bandra", "Worli", "Powai", "Juhu"],
            "Bangalore": ["Whitefield", "Electronic City", "Koramangala", "Indiranagar", "HSR Layout"],
            "Hyderabad": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills", "Madhapur"],
            "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Aundh"],
            "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad"]
        }
        
        # Sample ROI analysis
        roi_analysis = {
            "city_roi_analysis": {}
        }
        
        top_areas = []
        
        import random
        import numpy as np
        
        for city in cities:
            roi_analysis["city_roi_analysis"][city] = {
                "areas_by_roi": []
            }
            
            for area in areas[city]:
                # Create realistic but random ROI projections
                base_growth = random.uniform(0.05, 0.12)  # 5-12% base growth
                risk_modifier = random.uniform(0.7, 1.3)  # Risk modifier
                
                # Some areas in tech hubs get higher ROI
                tech_hub_bonus = 0
                if city in ["Bangalore", "Hyderabad", "Pune"] and "Tech" in area or "Electronic" in area or "Whitefield" in area or "Hinjewadi" in area:
                    tech_hub_bonus = random.uniform(0.02, 0.04)  # 2-4% bonus for tech hubs
                
                # Add infrastructure bonus for some areas
                infra_bonus = 0
                if "Bandra" in area or "Gachibowli" in area or "Greater Noida" in area:
                    infra_bonus = random.uniform(0.01, 0.03)  # 1-3% bonus for good infrastructure
                
                growth_rate = base_growth + tech_hub_bonus + infra_bonus
                
                # Calculate ROI projections
                roi_3yr = ((1 + growth_rate) ** 3 - 1) * 100
                roi_5yr = ((1 + growth_rate) ** 5 - 1) * 100
                roi_10yr = ((1 + growth_rate) ** 10 - 1) * 100
                
                # Risk score (1-10, 10 being highest risk)
                risk_score = random.uniform(2, 8)
                
                # Higher risk for Mumbai and Delhi-NCR due to saturation
                if city in ["Mumbai", "Delhi-NCR"]:
                    risk_score += random.uniform(0.5, 1.5)
                    risk_score = min(10, risk_score)  # Cap at 10
                
                # Sample current price per sqft (higher for Mumbai, Delhi)
                price_multiplier = 1.0
                if city == "Mumbai":
                    price_multiplier = 2.0
                elif city == "Delhi-NCR":
                    price_multiplier = 1.7
                elif city == "Bangalore":
                    price_multiplier = 1.5
                    
                current_price_per_sqft = random.uniform(5000, 9000) * price_multiplier
                
                # Create area analysis data
                area_data = {
                    "current_price_per_sqft": current_price_per_sqft,
                    "historical_growth": growth_rate,
                    "infrastructure_impact": random.uniform(0.5, 4.0),
                    "roi_projections": {
                        "projected_annual_growth": growth_rate,
                        "3_year_roi_percent": roi_3yr,
                        "5_year_roi_percent": roi_5yr,
                        "10_year_roi_percent": roi_10yr,
                        "risk_score": risk_score
                    }
                }
                
                # Add to city analysis
                roi_analysis["city_roi_analysis"][city]["areas_by_roi"].append((area, roi_5yr, area_data))
                
                # Track for top areas
                top_areas.append((city, area, roi_5yr))
        
        # Sort areas by 5-year ROI for each city
        for city in roi_analysis["city_roi_analysis"]:
            roi_analysis["city_roi_analysis"][city]["areas_by_roi"].sort(key=lambda x: x[1], reverse=True)
        
        # Sort top areas by 5-year ROI
        top_areas.sort(key=lambda x: x[2], reverse=True)
        
        # Add top areas to ROI analysis
        roi_analysis["top_investment_areas"] = top_areas
        
        # Save to JSON file
        os.makedirs("data/reports", exist_ok=True)
        with open("data/reports/roi_analysis_sample.json", "w") as f:
            json.dump(roi_analysis, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error creating sample ROI data: {str(e)}")
        return False

if __name__ == "__main__":
    main()