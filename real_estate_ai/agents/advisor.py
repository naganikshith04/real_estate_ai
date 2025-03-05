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
            
            # Create recommendations based on ROI analysis
            top_investment_areas = []
            if "top_investment_areas" in roi_analysis:
                top_investment_areas = roi_analysis["top_investment_areas"]
            
            # Create city-specific recommendations
            city_recommendations = {}
            for city in set([area[0] for area in top_investment_areas]):
                city_recommendations[city] = {
                    "recommended_areas": [],
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
            
            # Add growth drivers to each recommended area
            if "growth_driver_analysis" in growth_driver_analysis:
                for city, city_data in growth_driver_analysis["growth_driver_analysis"].items():
                    if city in city_recommendations:
                        for recommended_area in city_recommendations[city]["recommended_areas"]:
                            area_name = recommended_area["area"]
                            if "area_growth_drivers" in city_data and area_name in city_data["area_growth_drivers"]:
                                drivers = city_data["area_growth_drivers"][area_name]
                                recommended_area["growth_drivers"] = drivers.get("primary_drivers", [])
            
            # Generate investment strategies for each city
            for city, recommendations in city_recommendations.items():
                top_areas = recommendations["recommended_areas"]
                
                for area_info in top_areas:
                    area = area_info["area"]
                    roi = area_info["roi_5yr"]
                    risk = area_info["risk_score"]
                    
                    # Determine strategy based on ROI and risk
                    if isinstance(risk, (int, float)):
                        if roi > 40 and risk < 5:  # High ROI, low risk
                            strategy = "High-potential Core Investment"
                            description = f"Strong buy recommendation for {area}. Low risk with high potential returns makes this an ideal core investment."
                        elif roi > 40:  # High ROI, higher risk
                            strategy = "Growth-focused Investment"
                            description = f"Buy recommendation for {area} for investors with higher risk tolerance. High potential returns with moderate risk."
                        elif roi > 25 and risk < 4:  # Moderate ROI, very low risk
                            strategy = "Stable Core Investment"
                            description = f"Buy recommendation for {area} as a stable, lower-risk investment with good appreciation potential."
                        elif roi > 15:  # Lower ROI
                            strategy = "Income-focused Investment"
                            description = f"Consider {area} for rental income potential rather than pure appreciation."
                        else:
                            strategy = "Hold / Monitor"
                            description = f"Monitor {area} for future potential but limited current investment opportunity."
                    else:
                        strategy = "Opportunistic Investment"
                        description = f"Consider {area} as an emerging opportunity, but conduct further research on risk factors."
                    
                    recommendations["investment_strategies"].append({
                        "area": area,
                        "strategy": strategy,
                        "description": description
                    })
            
            # Generate overall market recommendation
            overall_recommendation = {
                "top_cities": [],
                "top_areas_overall": top_investment_areas[:3],
                "market_outlook": "Positive" if top_investment_areas and top_investment_areas[0][2] > 25 else "Moderate",
                "investment_horizon": "Long-term (5-10 years) investments are recommended in the current market conditions."
            }
            
            # Determine top cities based on average ROI of top areas
            city_avg_roi = {}
            for city, recommendations in city_recommendations.items():
                if recommendations["recommended_areas"]:
                    rois = [area_info["roi_5yr"] for area_info in recommendations["recommended_areas"]]
                    city_avg_roi[city] = sum(rois) / len(rois)
            
            sorted_cities = sorted(city_avg_roi.items(), key=lambda x: x[1], reverse=True)
            overall_recommendation["top_cities"] = sorted_cities
            
            # Create final recommendation report
            recommendation_report = {
                "overall_market_recommendation": overall_recommendation,
                "city_specific_recommendations": city_recommendations,
                "investment_strategies": {
                    "high_growth": "Focus on areas with infrastructure development, especially metro connectivity and IT parks.",
                    "stable_income": "Established areas with consistent rental demand offer stable income opportunities.",
                    "emerging_areas": "Areas with high organic growth and upcoming infrastructure projects offer early-entry advantages."
                },
                "risk_factors": {
                    "market_volatility": "The Indian real estate market can be volatile in the short term, so invest with a 5+ year horizon.",
                    "regulatory_changes": "Stay updated on regulatory changes in different cities that may impact property values.",
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