from crewai import Agent
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
import json
import os

class AdvisorAgent:
    def __init__(self, llm):
        self.llm = llm
        # Create output directory for reports if it doesn't exist
        os.makedirs("data/reports", exist_ok=True)
        
    def create(self):
        return Agent(
            role="Real Estate Investment Advisor",
            goal="Provide actionable real estate investment recommendations",
            backstory="""You are a trusted real estate investment advisor with years of 
            experience in the Indian market. You combine analytical insights with deep market 
            knowledge to provide tailored investment recommendations that maximize returns.""",
            llm=self.llm,
            tools=[
                Tool(
                    name="generate_investment_recommendations",
                    func=self.generate_investment_recommendations,
                    description="Creates personalized investment recommendations based on analysis"
                ),
                Tool(
                    name="predict_appreciation",
                    func=self.predict_appreciation,
                    description="Predicts potential appreciation for specific areas"
                ),
                Tool(
                    name="evaluate_risk_factors",
                    func=self.evaluate_risk_factors,
                    description="Evaluates risk factors associated with investments in specific areas"
                )
            ],
            verbose=True
        )
    
    def generate_investment_recommendations(self, analysis_results):
        """
        Generate investment recommendations based on analysis results
        """
        try:
            # Parse the input data
            results = json.loads(analysis_results)
            
            # Extract key insights from analysis
            price_trend_analysis = json.loads(results.get("price_trend_analysis", "{}"))
            roi_analysis = json.loads(results.get("roi_analysis", "{}"))
            growth_driver_analysis = json.loads(results.get("growth_driver_analysis", "{}"))
            rental_yield_analysis = json.loads(results.get("rental_yield_analysis", "{}"))
            buy_vs_rent_analysis = json.loads(results.get("buy_vs_rent_analysis", "{}"))
            
            # Create recommendations based on ROI and rental yield analysis
            top_investment_areas = []
            top_rental_areas = []
            
            if "top_investment_areas" in roi_analysis:
                top_investment_areas = roi_analysis["top_investment_areas"]
                
            if "top_rental_yield_areas" in rental_yield_analysis:
                top_rental_areas = rental_yield_analysis["top_rental_yield_areas"]
            
            # Create city-specific recommendations
            city_recommendations = {}
            all_cities = set()
            
            # Collect all cities from ROI and rental yield analysis
            if "city_roi_analysis" in roi_analysis:
                all_cities.update(roi_analysis["city_roi_analysis"].keys())
                
            if "city_rental_analysis" in rental_yield_analysis:
                all_cities.update(rental_yield_analysis["city_rental_analysis"].keys())
                
            for city in all_cities:
                city_recommendations[city] = {
                    "recommended_areas": [],
                    "rental_yield_areas": [],
                    "investment_strategies": []
                }
            
            # Process ROI analysis data
            if "city_roi_analysis" in roi_analysis:
                for city, analysis in roi_analysis["city_roi_analysis"].items():
                    if "areas_by_roi" in analysis and analysis["areas_by_roi"]:
                        # Get top 3 areas by ROI for this city
                        top_areas = analysis["areas_by_roi"][:3]
                        
                        city_recommendations[city]["recommended_areas"] = [
                            {
                                "area": area,
                                "roi_5yr": roi,
                                "risk_score": area_data["roi_projections"]["risk_score"] if "roi_projections" in area_data else "N/A"
                            } 
                            for area, roi, area_data in top_areas
                        ]
            
            # Process rental yield analysis data
            if "city_rental_analysis" in rental_yield_analysis:
                for city, analysis in rental_yield_analysis["city_rental_analysis"].items():
                    if "areas_by_yield" in analysis and analysis["areas_by_yield"]:
                        # Get top 3 areas by rental yield for this city
                        top_yield_areas = analysis["areas_by_yield"][:3]
                        
                        city_recommendations[city]["rental_yield_areas"] = [
                            {
                                "area": area,
                                "annual_yield_percent": yield_pct,
                                "price_to_rent_ratio": area_data.get("price_to_rent_ratio", "N/A")
                            } 
                            for area, yield_pct, area_data in top_yield_areas
                        ]
            
            # Add growth drivers to each recommended area
            if "growth_driver_analysis" in growth_driver_analysis:
                for city, city_data in growth_driver_analysis["growth_driver_analysis"].items():
                    if city in city_recommendations:
                        for recommended_area in city_recommendations[city]["recommended_areas"]:
                            area_name = recommended_area["area"]
                            if "area_growth_drivers" in city_data and area_name in city_data["area_growth_drivers"]:
                                drivers = city_data["area_growth_drivers"][area_name]
                                recommended_area["growth_drivers"] = drivers.get("primary_drivers", [])
            
            # Add buy vs rent recommendations
            if "buy_vs_rent_analysis" in buy_vs_rent_analysis:
                for city, city_data in buy_vs_rent_analysis["buy_vs_rent_analysis"].items():
                    if city in city_recommendations and "city_summary" in city_data:
                        if "buy_favored_areas" in city_data["city_summary"]:
                            city_recommendations[city]["buy_favored_areas"] = city_data["city_summary"]["buy_favored_areas"]
                        if "rent_favored_areas" in city_data["city_summary"]:
                            city_recommendations[city]["rent_favored_areas"] = city_data["city_summary"]["rent_favored_areas"]
            
            # Generate investment strategies for each city
            for city, recommendations in city_recommendations.items():
                top_areas = recommendations["recommended_areas"]
                top_rental_areas = recommendations.get("rental_yield_areas", [])
                
                # Combine ROI areas and rental yield areas to create comprehensive strategies
                all_areas = set()
                area_data = {}
                
                # Process ROI areas
                for area_info in top_areas:
                    area_name = area_info["area"]
                    all_areas.add(area_name)
                    area_data[area_name] = {
                        "roi_5yr": area_info["roi_5yr"],
                        "risk_score": area_info["risk_score"]
                    }
                
                # Add rental yield data
                for area_info in top_rental_areas:
                    area_name = area_info["area"]
                    all_areas.add(area_name)
                    if area_name not in area_data:
                        area_data[area_name] = {}
                    
                    area_data[area_name]["annual_yield_percent"] = area_info["annual_yield_percent"]
                    area_data[area_name]["price_to_rent_ratio"] = area_info["price_to_rent_ratio"]
                
                # Generate strategies based on combined data
                for area in all_areas:
                    data = area_data[area]
                    
                    # Default values if data is missing
                    roi = data.get("roi_5yr", 20)
                    risk = data.get("risk_score", 5)
                    rental_yield = data.get("annual_yield_percent", 3)
                    price_to_rent = data.get("price_to_rent_ratio", 30)
                    
                    # Buy favored?
                    buy_favored = area in recommendations.get("buy_favored_areas", [])
                    
                    # Determine strategy based on ROI, risk, rental yield
                    if isinstance(rental_yield, (int, float)) and rental_yield > 4.5:
                        # High rental yield strategy
                        strategy = "Rental Income Investment"
                        description = f"Buy recommendation for {area} for strong rental income. With a {rental_yield:.1f}% annual yield, this area offers excellent cash flow potential."
                    elif isinstance(risk, (int, float)) and isinstance(roi, (int, float)):
                        if roi > 40 and risk < 5:  # High ROI, low risk
                            strategy = "High-potential Core Investment"
                            description = f"Strong buy recommendation for {area}. Low risk with high potential returns makes this an ideal core investment."
                        elif roi > 40:  # High ROI, higher risk
                            strategy = "Growth-focused Investment"
                            description = f"Buy recommendation for {area} for investors with higher risk tolerance. High potential returns with moderate risk."
                        elif roi > 25 and risk < 4:  # Moderate ROI, very low risk
                            strategy = "Stable Core Investment"
                            description = f"Buy recommendation for {area} as a stable, lower-risk investment with good appreciation potential."
                        elif roi > 15 and rental_yield > 3.5:  # Lower ROI but decent rental yield
                            strategy = "Balanced Income-Growth Investment"
                            description = f"Consider {area} for balanced rental income and appreciation potential."
                        else:
                            strategy = "Hold / Monitor"
                            description = f"Monitor {area} for future potential but limited current investment opportunity."
                    else:
                        strategy = "Opportunistic Investment"
                        description = f"Consider {area} as an emerging opportunity, but conduct further research on risk factors."
                    
                    # Adjust recommendation based on buy vs rent analysis
                    if buy_favored:
                        description += " Buy vs rent analysis indicates favorable conditions for purchase over renting."
                    
                    recommendations["investment_strategies"].append({
                        "area": area,
                        "strategy": strategy,
                        "description": description,
                        "metrics": {
                            "roi_5yr": data.get("roi_5yr", "N/A"),
                            "annual_rental_yield": data.get("annual_yield_percent", "N/A"),
                            "risk_score": data.get("risk_score", "N/A"),
                            "price_to_rent_ratio": data.get("price_to_rent_ratio", "N/A")
                        }
                    })
            
            # Generate overall market recommendation
            overall_recommendation = {
                "top_cities": [],
                "top_growth_areas": top_investment_areas[:3] if top_investment_areas else [],
                "top_rental_yield_areas": top_rental_areas[:3] if top_rental_areas else [],
                "market_outlook": "Positive" if top_investment_areas and top_investment_areas[0][2] > 25 else "Moderate",
                "investment_horizon": "Long-term (5-10 years) investments are recommended in the current market conditions."
            }
            
            # Determine top cities based on combined ROI and rental yield
            city_scores = {}
            for city, recommendations in city_recommendations.items():
                score = 0
                count = 0
                
                # Average ROI contribution
                if recommendations["recommended_areas"]:
                    rois = [area_info["roi_5yr"] for area_info in recommendations["recommended_areas"]]
                    avg_roi = sum(rois) / len(rois)
                    score += avg_roi / 10  # Normalize to roughly 0-10 scale
                    count += 1
                
                # Average rental yield contribution
                if recommendations.get("rental_yield_areas", []):
                    yields = [area_info["annual_yield_percent"] for area_info in recommendations["rental_yield_areas"]]
                    avg_yield = sum(yields) / len(yields)
                    score += avg_yield * 2  # Weight rental yield
                    count += 1
                
                if count > 0:
                    city_scores[city] = score / count
            
            sorted_cities = sorted(city_scores.items(), key=lambda x: x[1], reverse=True)
            overall_recommendation["top_cities"] = sorted_cities
            
            # Create final recommendation report with enhanced rental focus
            recommendation_report = {
                "overall_market_recommendation": overall_recommendation,
                "city_specific_recommendations": city_recommendations,
                "investment_strategies": {
                    "high_growth": "Focus on areas with infrastructure development, especially metro connectivity and IT parks.",
                    "rental_yield": "Prioritize areas with strong rental demand and favorable price-to-rent ratios for steady income.",
                    "balanced_approach": "Target areas offering moderate appreciation with above-average rental yields for optimal cash flow and growth.",
                    "stable_income": "Established areas with consistent rental demand offer stable income opportunities.",
                    "emerging_areas": "Areas with high organic growth and upcoming infrastructure projects offer early-entry advantages."
                },
                "risk_factors": {
                    "market_volatility": "The Indian real estate market can be volatile in the short term, so invest with a 5+ year horizon.",
                    "rental_vacancy": "Consider vacancy risks in areas with oversupply or seasonal rental markets.",
                    "regulatory_changes": "Stay updated on regulatory changes in different cities that may impact property values and rental laws.",
                    "infrastructure_delays": "Infrastructure project delays can significantly impact expected appreciation timelines."
                }
            }
            
            # Save recommendation report to file
            with open("data/reports/investment_recommendations.json", "w") as f:
                json.dump(recommendation_report, f, indent=2)
            
            return json.dumps(recommendation_report, indent=2)
        except Exception as e:
            return f"Error generating investment recommendations: {str(e)}"
    
    def predict_appreciation(self, area_data):
        """
        Predict potential appreciation for specific areas
        """
        try:
            # Parse input data
            data = json.loads(area_data)
            
            roi_analysis = data.get("roi_analysis", {})
            price_trends = data.get("price_trends", {})
            
            # Extract top areas with highest projected growth
            top_areas = []
            
            if "city_roi_analysis" in roi_analysis:
                for city, city_analysis in roi_analysis["city_roi_analysis"].items():
                    if "areas_by_roi" in city_analysis:
                        for area, roi, details in city_analysis["areas_by_roi"]:
                            if "roi_projections" in details and "projected_annual_growth" in details["roi_projections"]:
                                projected_growth = details["roi_projections"]["projected_annual_growth"]
                                
                                # Calculate compound appreciation
                                current_price = details.get("current_price_per_sqft", 0)
                                
                                year1 = current_price * (1 + projected_growth)
                                year3 = current_price * (1 + projected_growth) ** 3
                                year5 = current_price * (1 + projected_growth) ** 5
                                year10 = current_price * (1 + projected_growth) ** 10
                                
                                top_areas.append({
                                    "city": city,
                                    "area": area,
                                    "current_price_per_sqft": current_price,
                                    "projected_annual_growth_rate": projected_growth,
                                    "projected_prices": {
                                        "year1": year1,
                                        "year3": year3,
                                        "year5": year5,
                                        "year10": year10
                                    },
                                    "appreciation_percentage": {
                                        "year1": ((year1 / current_price) - 1) * 100 if current_price > 0 else 0,
                                        "year3": ((year3 / current_price) - 1) * 100 if current_price > 0 else 0,
                                        "year5": ((year5 / current_price) - 1) * 100 if current_price > 0 else 0,
                                        "year10": ((year10 / current_price) - 1) * 100 if current_price > 0 else 0
                                    }
                                })
            
            # Sort areas by 5-year appreciation
            top_areas.sort(key=lambda x: x["appreciation_percentage"]["year5"], reverse=True)
            
            # Create appreciation forecast report
            appreciation_forecast = {
                "top_areas_by_appreciation": top_areas[:10],  # Top 10 areas
                "market_trends": {
                    "short_term": "The market shows positive momentum in the short term, particularly in areas with completed infrastructure projects.",
                    "medium_term": "Medium-term outlook (3-5 years) is strong for areas with ongoing infrastructure development.",
                    "long_term": "Long-term appreciation potential is highest in emerging areas with planned major infrastructure."
                },
                "appreciation_drivers": {
                    "infrastructure": "Infrastructure development continues to be the primary driver of real estate appreciation.",
                    "employment": "Areas with growing employment opportunities show stronger price appreciation.",
                    "urbanization": "The ongoing trend of urbanization supports sustained long-term appreciation in major cities."
                }
            }
            
            # Save appreciation forecast to file
            with open("data/reports/appreciation_forecast.json", "w") as f:
                json.dump(appreciation_forecast, f, indent=2)
            
            return json.dumps(appreciation_forecast, indent=2)
        except Exception as e:
            return f"Error predicting appreciation: {str(e)}"
    
    def evaluate_risk_factors(self, analysis_data):
        """
        Evaluate risk factors for investments in specific areas
        """
        try:
            # Parse input data
            data = json.loads(analysis_data)
            
            roi_analysis = data.get("roi_analysis", {})
            growth_drivers = data.get("growth_drivers", {})
            
            # Compile risk assessments for areas
            area_risk_factors = []
            
            if "city_roi_analysis" in roi_analysis:
                for city, city_analysis in roi_analysis["city_roi_analysis"].items():
                    if "areas_by_roi" in city_analysis:
                        for area, roi, details in city_analysis["areas_by_roi"]:
                            risk_score = details.get("roi_projections", {}).get("risk_score", 5)
                            
                            # Determine specific risk factors
                            risk_factors = []
                            
                            # Price volatility risk
                            if details.get("current_price_per_sqft", 0) > 12000:
                                risk_factors.append({
                                    "factor": "High Price Point",
                                    "description": "Current high prices may limit future appreciation potential.",
                                    "severity": "Medium"
                                })
                            
                            # Growth rate risk
                            if details.get("historical_growth", 0) > 0.12:
                                risk_factors.append({
                                    "factor": "Unsustainable Growth Rate",
                                    "description": "Current growth rate may be unsustainable long-term, leading to potential correction.",
                                    "severity": "High"
                                })
                            
                            # Infrastructure dependency risk
                            infrastructure_impact = details.get("infrastructure_impact", 0)
                            if infrastructure_impact > 3:
                                risk_factors.append({
                                    "factor": "Infrastructure Execution Risk",
                                    "description": "High dependency on future infrastructure projects that may face delays.",
                                    "severity": "Medium"
                                })
                            
                            # Add city-specific risks
                            if city == "Mumbai":
                                risk_factors.append({
                                    "factor": "Space Constraints",
                                    "description": "Limited land availability may impact future development potential.",
                                    "severity": "Medium"
                                })
                            elif city == "Bangalore":
                                risk_factors.append({
                                    "factor": "Traffic Infrastructure",
                                    "description": "Growing traffic congestion may impact property desirability in some areas.",
                                    "severity": "Medium"
                                })
                            elif city == "Delhi-NCR":
                                risk_factors.append({
                                    "factor": "Regulatory Uncertainty",
                                    "description": "Complex multi-jurisdictional regulatory environment creates policy risk.",
                                    "severity": "Medium"
                                })
                            
                            # General risk assessment
                            risk_assessment = "Low Risk"
                            if risk_score > 7:
                                risk_assessment = "High Risk"
                            elif risk_score > 4:
                                risk_assessment = "Medium Risk"
                            
                            area_risk_factors.append({
                                "city": city,
                                "area": area,
                                "risk_score": risk_score,
                                "risk_assessment": risk_assessment,
                                "specific_risk_factors": risk_factors,
                                "mitigation_strategies": [
                                    "Phase investments to manage exposure",
                                    "Focus on properties with rental income potential to offset risks",
                                    "Verify infrastructure project timelines before investing"
                                ]
                            })
            
            # Sort areas by risk score (low to high)
            area_risk_factors.sort(key=lambda x: x["risk_score"])
            
            # Create risk evaluation report
            risk_evaluation = {
                "area_risk_assessments": area_risk_factors,
                "market_risk_factors": {
                    "economic": "Economic slowdown could impact demand and appreciation in the short term.",
                    "interest_rates": "Rising interest rates may impact affordability and demand.",
                    "policy_changes": "Regulatory changes in real estate sector could impact investment returns."
                },
                "lowest_risk_investments": area_risk_factors[:3],
                "risk_mitigation_recommendations": {
                    "diversification": "Diversify investments across multiple cities and property types.",
                    "due_diligence": "Conduct thorough research on local market dynamics and infrastructure timelines.",
                    "phased_investment": "Consider phased investments to manage exposure to higher-risk areas."
                }
            }
            
            # Save risk evaluation to file
            with open("data/reports/risk_evaluation.json", "w") as f:
                json.dump(risk_evaluation, f, indent=2)
            
            return json.dumps(risk_evaluation, indent=2)
        except Exception as e:
            return f"Error evaluating risk factors: {str(e)}"