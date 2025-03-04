from crewai import Task

class RealEstateTasks:
    def collect_market_data(self, agent, cities):
        return Task(
            description=f"""Collect comprehensive real estate market data for the following Indian cities: {cities}.
            
            For each city, you need to collect:
            1. Property listings data with current prices and location details
            2. Historical price trends (for the past 5 years)
            3. Infrastructure development projects
            
            Use the collect_property_listings, collect_historical_prices, and collect_infrastructure_data tools 
            to gather this information for each city. Process one city at a time.
            
            IMPORTANT:
            1. Store the data for each city separately.
            2. The data should be structured for easy analysis in the next step.
            3. Make sure to collect data for ALL cities in the list.
            
            Your final answer should be a comprehensive JSON object with all the data collected, 
            structured by city and data type.
            """,
            agent=agent,
            expected_output="JSON object with structured real estate data for all specified cities"
        )
    
    def analyze_market_trends(self, agent, input_data):
        return Task(
            description=f"""Analyze the collected real estate data to identify market trends, growth patterns, 
            rental yields, and investment opportunities.
            
            Conduct five specific analyses:
            
            1. Price Trend Analysis:
               - Use the analyze_price_trends tool
               - Identify areas with highest growth rates
               - Compare price trends across different cities
               - Generate visualizations of price trends where possible
            
            2. ROI Potential Assessment:
               - Use the assess_roi_potential tool
               - Calculate potential returns for different areas
               - Consider both short-term (3yr) and long-term (5-10yr) horizons
               - Factor in current prices and historical growth rates
            
            3. Growth Driver Analysis:
               - Use the analyze_growth_drivers tool
               - Identify factors contributing to price appreciation
               - Examine correlation between infrastructure and property values
               - Determine which areas have sustainable growth potential
            
            4. Rental Yield Analysis:
               - Use the analyze_rental_yields tool
               - Calculate rental yields for different areas
               - Identify areas with highest rental returns
               - Determine price-to-rent ratios across different locations
               - Generate visualizations of rental yield patterns
               
            5. Buy vs Rent Analysis:
               - Use the compare_buy_vs_rent tool
               - Compare financial benefits of buying versus renting
               - Calculate break-even points for different areas
               - Provide time-horizon based recommendations
               - Generate visualizations for buy vs rent comparisons
            
            Your final answer should include all five analyses in a structured JSON format
            that can be used by the investment advisor agent.
            """,
            agent=agent,
            expected_output="Comprehensive market analysis with price trends, ROI assessment, growth drivers, rental yields, and buy vs rent comparisons in JSON format"
        )
    
    def generate_investment_recommendations(self, agent, analysis_results):
        return Task(
            description=f"""Based on the market analysis, generate actionable investment recommendations for real estate
            in Indian cities.
            
            Create a comprehensive investment recommendation package with these components:
            
            1. Investment Recommendations Report:
               - Use the generate_investment_recommendations tool
               - Identify the top 3 areas for high-yield investments in each city
               - Provide specific reasoning for each recommendation
               - Include investment strategies tailored to each area
            
            2. Appreciation Forecast:
               - Use the predict_appreciation tool
               - Provide projected appreciation for recommended areas
               - Include 3, 5, and 10 year forecasts
               - Explain factors that will drive future appreciation
            
            3. Risk Assessment:
               - Use the evaluate_risk_factors tool
               - Conduct risk assessment for each recommended area
               - Identify specific risk factors and their potential impact
               - Provide risk mitigation strategies for investors
            
            Your final answer should be a well-structured investment recommendation package 
            that provides clear, actionable advice for real estate investors looking for 
            high-yield opportunities in the Indian market.
            """,
            agent=agent,
            expected_output="Comprehensive investment recommendation package with area recommendations, appreciation forecasts, and risk assessments"
        )