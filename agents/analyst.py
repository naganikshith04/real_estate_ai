from crewai import Agent
from langchain_core.tools import Tool
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import os
from io import StringIO

class AnalystAgent:
    def __init__(self, llm):
        self.llm = llm
        # Create output directory for graphs if it doesn't exist
        os.makedirs("data/analysis", exist_ok=True)
        
    def create(self):
        return Agent(
            role="Real Estate Market Analyst",
            goal="Analyze real estate data to identify high-yield investment opportunities with focus on rental yields",
            backstory="""You are a seasoned real estate analyst with expertise in identifying 
            emerging high-yield areas. You have deep knowledge of market trends, price movements, 
            and factors that drive property appreciation and rental yields in Indian real estate markets.""",
            llm=self.llm,
            tools=[
                Tool(
                    name="analyze_price_trends",
                    func=self.analyze_price_trends,
                    description="Analyzes historical price trends to identify growth patterns"
                ),
                Tool(
                    name="assess_roi_potential",
                    func=self.assess_roi_potential,
                    description="Evaluates potential return on investment for different areas"
                ),
                Tool(
                    name="analyze_growth_drivers",
                    func=self.analyze_growth_drivers,
                    description="Identifies key factors driving real estate growth in an area"
                ),
                Tool(
                    name="analyze_rental_yields",
                    func=self.analyze_rental_yields,
                    description="Analyzes rental yields potential across different areas"
                ),
                Tool(
                    name="compare_buy_vs_rent",
                    func=self.compare_buy_vs_rent,
                    description="Compares financial benefits of buying versus renting properties"
                )
            ],
            verbose=True
        )
    
    def analyze_price_trends(self, data):
        """
        Analyze historical price data to identify trends
        """
        try:
            # Parse the input data
            input_data = json.loads(data)
            cities_data = {}
            
            # For each city, extract and analyze price trend data
            for city, city_data in input_data.items():
                if "historical_prices" not in city_data:
                    continue
                
                historical_data = json.loads(city_data["historical_prices"])
                
                if "area_growth_rates" not in historical_data:
                    continue
                    
                growth_rates = historical_data["area_growth_rates"]
                
                # Extract growth rates for each area
                area_growth = {}
                for area, details in growth_rates.items():
                    if "annualized_growth_rate" in details:
                        area_growth[area] = details["annualized_growth_rate"]
                
                # Sort areas by growth rate
                sorted_areas = sorted(area_growth.items(), key=lambda x: x[1], reverse=True)
                
                # Categorize areas by growth potential
                high_growth = [(area, rate) for area, rate in sorted_areas if rate > 0.08]  # >8% annual growth
                moderate_growth = [(area, rate) for area, rate in sorted_areas if 0.05 <= rate <= 0.08]  # 5-8% annual growth
                stable_growth = [(area, rate) for area, rate in sorted_areas if 0.03 <= rate < 0.05]  # 3-5% annual growth
                low_growth = [(area, rate) for area, rate in sorted_areas if rate < 0.03]  # <3% annual growth
                
                # Create price trend summary
                trend_summary = {
                    "high_growth_areas": high_growth,
                    "moderate_growth_areas": moderate_growth,
                    "stable_growth_areas": stable_growth,
                    "low_growth_areas": low_growth,
                    "top_performing_area": sorted_areas[0] if sorted_areas else None,
                    "average_growth_rate": sum(area_growth.values()) / len(area_growth) if area_growth else 0
                }
                
                cities_data[city] = {
                    "trend_summary": trend_summary,
                    "area_growth_rates": growth_rates
                }
                
                # Generate a simple bar chart of growth rates (if matplotlib is available)
                try:
                    if sorted_areas:
                        areas = [area for area, _ in sorted_areas[:5]]  # Top 5 areas
                        rates = [rate * 100 for _, rate in sorted_areas[:5]]  # Convert to percentage
                        
                        plt.figure(figsize=(10, 6))
                        plt.bar(areas, rates, color='skyblue')
                        plt.xlabel('Area')
                        plt.ylabel('Annual Growth Rate (%)')
                        plt.title(f'Top 5 Areas by Price Growth Rate in {city}')
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        
                        chart_path = f"data/analysis/{city}_growth_rates.png"
                        plt.savefig(chart_path)
                        plt.close()
                        
                        cities_data[city]["chart_path"] = chart_path
                except Exception as chart_error:
                    print(f"Error generating chart: {str(chart_error)}")
            
            # Compare cities and identify the best performing ones
            city_rankings = []
            for city, data in cities_data.items():
                if "trend_summary" in data and "average_growth_rate" in data["trend_summary"]:
                    city_rankings.append((city, data["trend_summary"]["average_growth_rate"]))
            
            city_rankings.sort(key=lambda x: x[1], reverse=True)
            
            result = {
                "city_price_trends": cities_data,
                "city_rankings": city_rankings,
                "best_performing_city": city_rankings[0][0] if city_rankings else None,
                "analysis_summary": "Price trend analysis has identified areas with high growth potential based on historical data."
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error analyzing price trends: {str(e)}"
    
    def assess_roi_potential(self, data):
        """
        Calculate potential ROI for investments in different areas
        """
        try:
            # Parse the input data
            input_data = json.loads(data)
            roi_analysis = {}
            
            for city, city_data in input_data.items():
                property_data = json.loads(city_data.get("property_listings", "{}"))
                historical_data = json.loads(city_data.get("historical_prices", "{}"))
                infrastructure_data = json.loads(city_data.get("infrastructure_data", "{}"))
                
                # Skip cities with incomplete data
                if not property_data or not historical_data or not infrastructure_data:
                    continue
                
                area_analysis = {}
                
                # Get area property details
                if "area_summary" in property_data:
                    for area, details in property_data["area_summary"].items():
                        area_analysis[area] = {
                            "current_price_per_sqft": details.get("avg_price_per_sqft", 0),
                            "current_avg_price": details.get("avg_price", 0)
                        }
                
                # Get historical growth rates
                if "area_growth_rates" in historical_data:
                    for area, growth_details in historical_data["area_growth_rates"].items():
                        if area in area_analysis:
                            area_analysis[area]["historical_growth"] = growth_details.get("annualized_growth_rate", 0)
                
                # Get infrastructure impact
                if "infrastructure_impact_scores" in infrastructure_data:
                    for area, impact_score in infrastructure_data["infrastructure_impact_scores"].items():
                        if area in area_analysis:
                            area_analysis[area]["infrastructure_impact"] = impact_score
                
                # Calculate potential ROI for each area
                for area, analysis in area_analysis.items():
                    if "historical_growth" in analysis and "infrastructure_impact" in analysis:
                        # Basic ROI calculation (simple model for demonstration)
                        historical_growth = analysis["historical_growth"]
                        infra_impact = analysis["infrastructure_impact"]
                        
                        # Normalize infrastructure impact (0-1 scale)
                        max_impact = max(area_analysis[a].get("infrastructure_impact", 0) for a in area_analysis)
                        normalized_impact = infra_impact / max_impact if max_impact > 0 else 0
                        
                        # Weight historical growth more heavily (70%) than infrastructure (30%)
                        projected_growth = (historical_growth * 0.7) + (normalized_impact * 0.1)
                        
                        # Calculate projected values for different time horizons
                        current_price = analysis["current_price_per_sqft"]
                        year3_price = current_price * (1 + projected_growth) ** 3
                        year5_price = current_price * (1 + projected_growth) ** 5
                        year10_price = current_price * (1 + projected_growth) ** 10
                        
                        # Calculate ROI percentages
                        roi_3yr = ((year3_price / current_price) - 1) * 100
                        roi_5yr = ((year5_price / current_price) - 1) * 100
                        roi_10yr = ((year10_price / current_price) - 1) * 100
                        
                        # Calculate risk score (simple model)
                        # Lower is better: high growth with low price is less risky
                        risk_score = (analysis["current_price_per_sqft"] / 10000) / (historical_growth * 10 + 0.5)
                        
                        # Map risk score to a 1-10 scale (10 being highest risk)
                        normalized_risk = min(10, max(1, risk_score * 5))
                        
                        analysis["roi_projections"] = {
                            "projected_annual_growth": projected_growth,
                            "3_year_roi_percent": roi_3yr,
                            "5_year_roi_percent": roi_5yr,
                            "10_year_roi_percent": roi_10yr,
                            "risk_score": normalized_risk  # 1-10 scale
                        }
                
                # Sort areas by 5-year ROI
                sorted_areas = []
                for area, analysis in area_analysis.items():
                    if "roi_projections" in analysis:
                        sorted_areas.append((area, analysis["roi_projections"]["5_year_roi_percent"], analysis))
                
                sorted_areas.sort(key=lambda x: x[1], reverse=True)
                
                roi_analysis[city] = {
                    "areas_by_roi": [(area, roi, analysis) for area, roi, analysis in sorted_areas],
                    "top_roi_area": sorted_areas[0][0] if sorted_areas else None,
                    "top_roi_percentage": sorted_areas[0][1] if sorted_areas else 0
                }
            
            # Find the overall best investment areas across all cities
            all_areas = []
            for city, analysis in roi_analysis.items():
                for area, roi, details in analysis["areas_by_roi"]:
                    all_areas.append((city, area, roi, details))
            
            all_areas.sort(key=lambda x: x[2], reverse=True)
            top_areas = all_areas[:5]  # Top 5 areas overall
            
            result = {
                "city_roi_analysis": roi_analysis,
                "top_investment_areas": [(item[0], item[1], item[2]) for item in top_areas],
                "analysis_summary": "ROI potential assessment has identified the most promising investment areas based on historical growth, current prices, and infrastructure development."
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error assessing ROI potential: {str(e)}"
    
    def analyze_growth_drivers(self, data):
        """
        Identify key factors driving real estate growth in cities/areas
        """
        try:
            # Parse the input data
            input_data = json.loads(data)
            growth_analysis = {}
            
            for city, city_data in input_data.items():
                property_data = json.loads(city_data.get("property_listings", "{}"))
                historical_data = json.loads(city_data.get("historical_prices", "{}"))
                infrastructure_data = json.loads(city_data.get("infrastructure_data", "{}"))
                
                # Skip cities with incomplete data
                if not property_data or not historical_data or not infrastructure_data:
                    continue
                
                # Extract infrastructure projects by area
                area_projects = {}
                if "projects" in infrastructure_data:
                    for project in infrastructure_data["projects"]:
                        area = project["area"]
                        if area not in area_projects:
                            area_projects[area] = []
                        area_projects[area].append(project)
                
                # Extract historical growth by area
                area_growth = {}
                if "area_growth_rates" in historical_data:
                    for area, details in historical_data["area_growth_rates"].items():
                        if "annualized_growth_rate" in details:
                            area_growth[area] = details["annualized_growth_rate"]
                
                # Identify correlation between infrastructure and growth
                growth_drivers = {}
                for area, projects in area_projects.items():
                    if area in area_growth:
                        growth_rate = area_growth[area]
                        
                        # Count projects by type
                        project_types = {}
                        for project in projects:
                            proj_type = project["project_type"]
                            if proj_type not in project_types:
                                project_types[proj_type] = 0
                            project_types[proj_type] += 1
                        
                        # Identify primary growth drivers for this area
                        primary_drivers = []
                        
                        # High impact infrastructure types
                        high_impact_types = ["Metro", "IT Park", "Airport"]
                        for proj_type in high_impact_types:
                            if proj_type in project_types and project_types[proj_type] > 0:
                                primary_drivers.append(f"{proj_type} Development")
                        
                        # Check for multiple projects of other types
                        other_types = [t for t in project_types if t not in high_impact_types]
                        for proj_type in other_types:
                            if project_types[proj_type] >= 2:  # Multiple projects of same type
                                primary_drivers.append(f"Multiple {proj_type} Developments")
                        
                        # Check if area has high growth without many infrastructure projects
                        if growth_rate > 0.08 and len(primary_drivers) == 0:
                            primary_drivers.append("Organic Demand Growth")
                        
                        # Add to analysis
                        growth_drivers[area] = {
                            "growth_rate": growth_rate,
                            "infrastructure_projects": project_types,
                            "primary_drivers": primary_drivers,
                            "secondary_factors": ["Proximity to business districts" if "IT Park" in project_types else "Residential demand"]
                        }
                
                # Find areas with highest growth-to-infrastructure ratio
                # These areas might be growing organically without much infrastructure support
                growth_to_infra_ratio = []
                for area in growth_drivers:
                    if area in infrastructure_data.get("infrastructure_impact_scores", {}):
                        infra_score = infrastructure_data["infrastructure_impact_scores"][area]
                        growth = growth_drivers[area]["growth_rate"]
                        if infra_score > 0:
                            ratio = growth / infra_score
                            growth_to_infra_ratio.append((area, ratio))
                
                growth_to_infra_ratio.sort(key=lambda x: x[1], reverse=True)
                
                # Compile city analysis
                growth_analysis[city] = {
                    "area_growth_drivers": growth_drivers,
                    "high_organic_growth_areas": growth_to_infra_ratio[:3] if growth_to_infra_ratio else [],
                    "infrastructure_driven_growth": [(a, growth_drivers[a]["growth_rate"]) for a in growth_drivers 
                                                   if len(growth_drivers[a]["primary_drivers"]) > 0 
                                                   and "Organic Demand Growth" not in growth_drivers[a]["primary_drivers"]]
                }
            
            result = {
                "growth_driver_analysis": growth_analysis,
                "analysis_summary": "Growth driver analysis has identified key factors contributing to real estate appreciation in different areas, including infrastructure developments and organic demand."
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error analyzing growth drivers: {str(e)}"
            
    def analyze_rental_yields(self, data):
        """
        Analyze rental yield potential across different areas
        """
        try:
            # Parse the input data
            input_data = json.loads(data)
            rental_analysis = {}
            
            for city, city_data in input_data.items():
                property_data = json.loads(city_data.get("property_listings", "{}"))
                
                # Skip cities with incomplete data
                if not property_data:
                    continue
                
                # Add rental yield data (if it exists in the dataset)
                # In a real implementation, we would have actual rental data
                # For demo purposes, we'll generate synthetic rental data based on property values
                
                area_analysis = {}
                
                # Get area property details
                if "area_summary" in property_data:
                    for area, details in property_data["area_summary"].items():
                        current_price = details.get("avg_price", 0)
                        
                        # Generate synthetic rental data
                        # Rental yield typically ranges from 2-5% annually in Indian metro cities
                        # Higher-end properties typically have lower yields
                        base_yield = np.random.uniform(2.0, 5.0)
                        
                        # Adjust yield based on property price (higher prices = lower yields)
                        price_factor = min(1.0, 10000000 / max(current_price, 1))
                        adjusted_yield = base_yield * price_factor
                        
                        # Calculate monthly rental
                        annual_rental = current_price * (adjusted_yield / 100)
                        monthly_rental = annual_rental / 12
                        
                        area_analysis[area] = {
                            "current_avg_price": current_price,
                            "estimated_monthly_rental": monthly_rental,
                            "annual_rental_yield_percent": adjusted_yield,
                            "price_to_rent_ratio": current_price / (monthly_rental * 12) if monthly_rental > 0 else 0
                        }
                
                # Sort areas by rental yield
                sorted_areas = [(area, data["annual_rental_yield_percent"], data) 
                               for area, data in area_analysis.items()]
                sorted_areas.sort(key=lambda x: x[1], reverse=True)
                
                rental_analysis[city] = {
                    "areas_by_yield": sorted_areas,
                    "top_yield_area": sorted_areas[0][0] if sorted_areas else None,
                    "top_yield_percentage": sorted_areas[0][1] if sorted_areas else 0
                }
                
                # Generate a simple bar chart of rental yields
                try:
                    if sorted_areas:
                        areas = [area for area, _, _ in sorted_areas[:5]]  # Top 5 areas
                        yields = [yield_pct for _, yield_pct, _ in sorted_areas[:5]]
                        
                        plt.figure(figsize=(10, 6))
                        plt.bar(areas, yields, color='green')
                        plt.xlabel('Area')
                        plt.ylabel('Annual Rental Yield (%)')
                        plt.title(f'Top 5 Areas by Rental Yield in {city}')
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        
                        chart_path = f"data/analysis/{city}_rental_yields.png"
                        plt.savefig(chart_path)
                        plt.close()
                        
                        rental_analysis[city]["chart_path"] = chart_path
                except Exception as chart_error:
                    print(f"Error generating rental yield chart: {str(chart_error)}")
            
            # Find the overall best rental yield areas across all cities
            all_areas = []
            for city, analysis in rental_analysis.items():
                for area, yield_pct, details in analysis["areas_by_yield"]:
                    all_areas.append((city, area, yield_pct, details))
            
            all_areas.sort(key=lambda x: x[2], reverse=True)
            top_yield_areas = all_areas[:5]  # Top 5 areas overall
            
            result = {
                "city_rental_analysis": rental_analysis,
                "top_rental_yield_areas": [(item[0], item[1], item[2]) for item in top_yield_areas],
                "analysis_summary": "Rental yield analysis has identified areas offering the highest rental returns based on property value and estimated rental income."
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error analyzing rental yields: {str(e)}"
    
    def compare_buy_vs_rent(self, data):
        """
        Compare financial benefits of buying versus renting properties
        """
        try:
            # Parse the input data
            input_data = json.loads(data)
            comparison_analysis = {}
            
            for city, city_data in input_data.items():
                property_data = json.loads(city_data.get("property_listings", "{}"))
                historical_data = json.loads(city_data.get("historical_prices", "{}"))
                
                # Skip cities with incomplete data
                if not property_data or not historical_data:
                    continue
                
                area_analysis = {}
                
                # Get area property details
                if "area_summary" in property_data:
                    for area, details in property_data["area_summary"].items():
                        current_price = details.get("avg_price", 0)
                        
                        # Generate synthetic rental data
                        base_yield = np.random.uniform(2.0, 5.0)
                        price_factor = min(1.0, 10000000 / max(current_price, 1))
                        adjusted_yield = base_yield * price_factor
                        annual_rental = current_price * (adjusted_yield / 100)
                        monthly_rental = annual_rental / 12
                        
                        # Get historical growth rate if available
                        historical_growth = 0.07  # Default annual appreciation (7%)
                        if "area_growth_rates" in historical_data:
                            for area_name, growth_details in historical_data["area_growth_rates"].items():
                                if area_name == area and "annualized_growth_rate" in growth_details:
                                    historical_growth = growth_details["annualized_growth_rate"]
                        
                        # Calculate buy vs rent over different time horizons
                        horizons = [3, 5, 10, 15]
                        time_analysis = {}
                        
                        for years in horizons:
                            # Buying scenario assumptions
                            down_payment_percent = 20
                            loan_term_years = 20
                            loan_interest_rate = 7.5  # 7.5% annual interest
                            
                            down_payment = current_price * (down_payment_percent / 100)
                            loan_amount = current_price - down_payment
                            
                            # Calculate EMI (Equated Monthly Installment)
                            monthly_interest_rate = loan_interest_rate / 12 / 100
                            loan_term_months = loan_term_years * 12
                            emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**loan_term_months / ((1 + monthly_interest_rate)**loan_term_months - 1)
                            
                            total_buying_cost = down_payment + (emi * 12 * years)
                            
                            # Property appreciation
                            future_value = current_price * (1 + historical_growth)**years
                            equity_value = future_value - (loan_amount - (years * 12 * emi * 0.7))  # Approximately 70% of EMI goes to principal
                            
                            # Renting scenario
                            monthly_rent_increase = 0.05  # 5% annual rent increase
                            total_rent = 0
                            
                            for y in range(years):
                                annual_rent = monthly_rental * 12 * (1 + monthly_rent_increase)**y
                                total_rent += annual_rent
                            
                            # Investment scenario (if amount used for down payment was invested instead)
                            investment_return_rate = 0.08  # 8% annual return
                            investment_value = down_payment * (1 + investment_return_rate)**years
                            
                            # Final comparison
                            buy_scenario_value = equity_value - total_buying_cost
                            rent_scenario_value = investment_value - total_rent
                            
                            buy_advantage = buy_scenario_value - rent_scenario_value
                            
                            time_analysis[str(years)] = {
                                "years": years,
                                "total_buying_cost": total_buying_cost,
                                "equity_value": equity_value,
                                "total_rent_paid": total_rent,
                                "investment_value": investment_value,
                                "buy_advantage": buy_advantage,
                                "recommendation": "Buy" if buy_advantage > 0 else "Rent",
                                "break_even_year": years if buy_advantage > 0 else "Beyond horizon"
                            }
                        
                        # Find break-even point
                        break_even_found = False
                        break_even_year = "Beyond 15 years"
                        
                        for years in horizons:
                            if time_analysis[str(years)]["buy_advantage"] > 0 and not break_even_found:
                                break_even_year = years
                                break_even_found = True
                                break
                        
                        area_analysis[area] = {
                            "current_price": current_price,
                            "monthly_rental": monthly_rental,
                            "annual_appreciation": historical_growth * 100,  # Convert to percentage
                            "price_to_rent_ratio": current_price / (monthly_rental * 12) if monthly_rental > 0 else 0,
                            "time_horizon_analysis": time_analysis,
                            "break_even_year": break_even_year,
                            "long_term_recommendation": "Buy" if break_even_found else "Rent"
                        }
                
                comparison_analysis[city] = {
                    "area_comparisons": area_analysis,
                    "city_summary": {
                        "avg_break_even": np.mean([area_data["break_even_year"] for area, area_data in area_analysis.items() if area_data["break_even_year"] != "Beyond 15 years"]) if area_analysis else 0,
                        "buy_favored_areas": [area for area, area_data in area_analysis.items() if area_data["long_term_recommendation"] == "Buy"],
                        "rent_favored_areas": [area for area, area_data in area_analysis.items() if area_data["long_term_recommendation"] == "Rent"]
                    }
                }
                
                # Generate visualization: Break-even years by area
                try:
                    if area_analysis:
                        areas = []
                        break_evens = []
                        
                        for area, data in area_analysis.items():
                            if data["break_even_year"] != "Beyond 15 years":
                                areas.append(area)
                                break_evens.append(data["break_even_year"])
                        
                        if areas and break_evens:
                            plt.figure(figsize=(10, 6))
                            plt.bar(areas, break_evens, color='purple')
                            plt.xlabel('Area')
                            plt.ylabel('Break-even Year')
                            plt.title(f'Buy vs Rent Break-even Years in {city}')
                            plt.xticks(rotation=45, ha='right')
                            plt.tight_layout()
                            
                            chart_path = f"data/analysis/{city}_buy_vs_rent.png"
                            plt.savefig(chart_path)
                            plt.close()
                            
                            comparison_analysis[city]["chart_path"] = chart_path
                except Exception as chart_error:
                    print(f"Error generating buy vs rent chart: {str(chart_error)}")
            
            result = {
                "buy_vs_rent_analysis": comparison_analysis,
                "analysis_summary": "Buy vs Rent analysis has identified areas where buying is financially advantageous over renting in the long term, as well as areas where renting may be more financially prudent."
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in buy vs rent comparison: {str(e)}"