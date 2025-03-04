#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import folium
import folium.plugins
from streamlit_folium import st_folium
from data_providers.location_analyzer import LocationAnalyzer

# Add Streamlit to requirements
with open('requirements.txt', 'r') as f:
    requirements = f.read()
if 'streamlit' not in requirements:
    with open('requirements.txt', 'a') as f:
        f.write('\nstreamlit==1.31.0\n')

def load_data():
    """Load all necessary data files"""
    data = {}
    
    # Load property listings
    try:
        if os.path.exists("data/property_listings.json"):
            with open("data/property_listings.json", "r") as f:
                data["property_listings"] = json.load(f)
        else:
            data["property_listings"] = []
    except Exception as e:
        st.error(f"Error loading property listings: {str(e)}")
        data["property_listings"] = []
    
    # Load historical prices
    try:
        if os.path.exists("data/historical_prices.json"):
            with open("data/historical_prices.json", "r") as f:
                data["historical_prices"] = json.load(f)
        else:
            data["historical_prices"] = []
    except Exception as e:
        st.error(f"Error loading historical prices: {str(e)}")
        data["historical_prices"] = []
    
    # Load infrastructure projects
    try:
        if os.path.exists("data/infrastructure_projects.json"):
            with open("data/infrastructure_projects.json", "r") as f:
                data["infrastructure_projects"] = json.load(f)
        else:
            data["infrastructure_projects"] = []
    except Exception as e:
        st.error(f"Error loading infrastructure projects: {str(e)}")
        data["infrastructure_projects"] = []
    
    # Load ROI analysis
    try:
        if os.path.exists("data/reports/roi_analysis_sample.json"):
            with open("data/reports/roi_analysis_sample.json", "r") as f:
                data["roi_analysis"] = json.load(f)
        else:
            data["roi_analysis"] = {}
    except Exception as e:
        st.error(f"Error loading ROI analysis: {str(e)}")
        data["roi_analysis"] = {}
    
    # Load recommendations
    try:
        if os.path.exists("data/reports/final_recommendations.json"):
            with open("data/reports/final_recommendations.json", "r") as f:
                data["recommendations"] = json.load(f)
        else:
            data["recommendations"] = {}
    except Exception as e:
        st.error(f"Error loading recommendations: {str(e)}")
        data["recommendations"] = {}
    
    return data

def process_data(data):
    """Process raw data into usable DataFrames"""
    processed = {}
    
    # Process property listings
    if data["property_listings"]:
        processed["listings_df"] = pd.DataFrame(data["property_listings"])
    else:
        processed["listings_df"] = pd.DataFrame()
    
    # Process historical prices
    if data["historical_prices"]:
        processed["historical_df"] = pd.DataFrame(data["historical_prices"])
    else:
        processed["historical_df"] = pd.DataFrame()
    
    # Process infrastructure projects
    if data["infrastructure_projects"]:
        processed["infra_df"] = pd.DataFrame(data["infrastructure_projects"])
    else:
        processed["infra_df"] = pd.DataFrame()
    
    return processed

def app():
    """Main Streamlit application"""
    # Create necessary directories
    os.makedirs("data/analysis", exist_ok=True)  
    os.makedirs("data/reports", exist_ok=True)
    st.set_page_config(
        page_title="Real Estate Investment Analysis Dashboard",
        page_icon="🏢",
        layout="wide"
    )
    
    st.title("🏢 Real Estate Investment Analysis Dashboard")
    st.write("AI-powered insights for high-yield property investments in the Indian market")
    
    # Load and process data
    data = load_data()
    processed = process_data(data)
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Market Overview", 
                                      "💰 Investment Recommendations", 
                                      "📈 ROI Analysis",
                                      "🏠 Rental Yield Analysis",
                                      "🗺️ Location Analysis", 
                                      "🔍 Data Explorer"])
    
    # Tab 1: Market Overview
    with tab1:
        st.header("Real Estate Market Overview")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Price Trends by City")
            if not processed["historical_df"].empty:
                # Calculate average prices by city
                city_avg = processed["historical_df"].groupby("city")["avg_price_per_sqft"].mean().sort_values(ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                city_avg.plot(kind="bar", color="skyblue", ax=ax)
                ax.set_ylabel("Average Price (₹ per sq.ft)")
                ax.set_title("Average Property Prices by City")
                
                for i, v in enumerate(city_avg):
                    ax.text(i, v + 100, f"₹{v:.0f}", ha='center')
                
                st.pyplot(fig)
            else:
                st.info("No historical price data available.")
        
        with col2:
            st.subheader("Infrastructure Projects by City")
            if not processed["infra_df"].empty:
                infra_count = processed["infra_df"]["city"].value_counts()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                infra_count.plot(kind="pie", autopct='%1.1f%%', ax=ax)
                ax.set_title("Infrastructure Projects Distribution")
                ax.set_ylabel("")
                
                st.pyplot(fig)
            else:
                st.info("No infrastructure project data available.")
        
        # Popular areas by city
        st.subheader("Top Areas by Property Listings")
        if not processed["listings_df"].empty:
            # Group by city and area, count listings
            area_counts = processed["listings_df"].groupby(["city", "area"]).size().reset_index(name="listings")
            
            # Sort by count and get top 3 areas per city
            top_areas_by_city = {}
            for city in area_counts["city"].unique():
                city_areas = area_counts[area_counts["city"] == city].sort_values("listings", ascending=False).head(3)
                top_areas_by_city[city] = city_areas
            
            cols = st.columns(len(top_areas_by_city))
            
            for i, (city, df) in enumerate(top_areas_by_city.items()):
                with cols[i]:
                    st.write(f"**{city}**")
                    for _, row in df.iterrows():
                        st.write(f"{row['area']}: {row['listings']} listings")
        else:
            st.info("No property listing data available.")
    
    # Tab 2: Investment Recommendations
    with tab2:
        st.header("Investment Recommendations")
        
        if "top_investment_areas" in data["roi_analysis"]:
            top_areas = data["roi_analysis"]["top_investment_areas"][:10]  # Get top 10
            
            # Create DataFrame for display
            top_df = pd.DataFrame(top_areas, columns=["City", "Area", "5-Year ROI (%)"])
            
            # Round ROI to 2 decimal places
            top_df["5-Year ROI (%)"] = top_df["5-Year ROI (%)"].round(2)
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("Top 10 Areas by ROI Potential")
                st.dataframe(top_df, hide_index=True, use_container_width=True)
                
                # Create bar chart
                fig, ax = plt.subplots(figsize=(10, 8))
                colors = plt.cm.viridis(np.linspace(0, 1, len(top_df)))
                bars = ax.barh(top_df["City"] + " - " + top_df["Area"], top_df["5-Year ROI (%)"], color=colors)
                
                # Add value labels
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", 
                            ha='left', va='center')
                
                ax.set_xlabel("5-Year ROI (%)")
                ax.set_title("Top 10 Areas by ROI Potential")
                
                st.pyplot(fig)
            
            with col2:
                st.subheader("Investment Strategies")
                
                strategies = {
                    "High Growth": "Focus on areas with significant infrastructure development and tech sector presence, particularly in Bangalore, Hyderabad, and Pune.",
                    "Stable Income": "Consider established areas in Mumbai and Delhi-NCR for steady rental income with moderate appreciation.",
                    "Emerging Opportunities": "Look for areas adjacent to tech corridors with upcoming infrastructure projects for early entry advantage."
                }
                
                for strategy, desc in strategies.items():
                    st.write(f"**{strategy}:** {desc}")
                
                st.write("---")
                st.subheader("Risk Considerations")
                
                risks = {
                    "Price Volatility": "High-priced areas in Mumbai may face limited appreciation potential.",
                    "Infrastructure Delays": "ROI projections dependent on infrastructure completion timelines.",
                    "Market Saturation": "Some popular areas may face oversupply risks."
                }
                
                for risk, desc in risks.items():
                    st.write(f"**{risk}:** {desc}")
        else:
            st.info("Investment recommendation data not available. Run the analysis pipeline first.")
    
    # Tab 3: ROI Analysis
    with tab3:
        st.header("ROI Analysis Dashboard")
        
        if "city_roi_analysis" in data["roi_analysis"]:
            # City selection
            cities = list(data["roi_analysis"]["city_roi_analysis"].keys())
            selected_city = st.selectbox("Select City for ROI Analysis", cities, key="roi_city_select")
            
            if selected_city:
                city_data = data["roi_analysis"]["city_roi_analysis"][selected_city]
                
                if "areas_by_roi" in city_data and city_data["areas_by_roi"]:
                    # Extract area data
                    areas = []
                    roi_values = []
                    risk_scores = []
                    
                    for area, roi, area_data in city_data["areas_by_roi"]:
                        areas.append(area)
                        roi_values.append(roi)
                        risk_score = area_data.get("roi_projections", {}).get("risk_score", 5)
                        risk_scores.append(risk_score)
                    
                    # Create DataFrame for display
                    area_df = pd.DataFrame({
                        "Area": areas,
                        "5-Year ROI (%)": [round(r, 2) for r in roi_values],
                        "Risk Score (1-10)": [round(r, 1) for r in risk_scores]
                    })
                    
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.subheader(f"Areas in {selected_city} by ROI")
                        st.dataframe(area_df, hide_index=True, use_container_width=True)
                    
                    with col2:
                        st.subheader("Risk vs. Return Analysis")
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        scatter = ax.scatter(risk_scores, roi_values, s=100, c=roi_values, cmap="viridis", alpha=0.7)
                        
                        # Add area labels
                        for i, area in enumerate(areas):
                            ax.annotate(area, (risk_scores[i], roi_values[i]), 
                                      fontsize=9, ha='center', va='bottom')
                        
                        # Add quadrant lines
                        ax.axhline(y=25, color='gray', linestyle='--', alpha=0.5)
                        ax.axvline(x=5, color='gray', linestyle='--', alpha=0.5)
                        
                        ax.set_xlabel("Risk Score")
                        ax.set_ylabel("5-Year ROI (%)")
                        ax.set_title(f"Risk-Return Profile for {selected_city}")
                        fig.colorbar(scatter, label="ROI (%)")
                        
                        st.pyplot(fig)
                    
                    # ROI over time horizons
                    st.subheader("ROI Across Different Investment Horizons")
                    
                    # Extract top 5 areas
                    top_areas = areas[:5]
                    area_data_list = [d for _, _, d in city_data["areas_by_roi"][:5]]
                    
                    # Extract ROI projections
                    roi_3yr = []
                    roi_5yr = []
                    roi_10yr = []
                    
                    for data in area_data_list:
                        projections = data.get("roi_projections", {})
                        roi_3yr.append(projections.get("3_year_roi_percent", 0))
                        roi_5yr.append(projections.get("5_year_roi_percent", 0))
                        roi_10yr.append(projections.get("10_year_roi_percent", 0))
                    
                    # Create grouped bar chart
                    fig, ax = plt.subplots(figsize=(12, 7))
                    x = np.arange(len(top_areas))
                    width = 0.25
                    
                    ax.bar(x - width, roi_3yr, width, label='3-Year', color='skyblue')
                    ax.bar(x, roi_5yr, width, label='5-Year', color='orange')
                    ax.bar(x + width, roi_10yr, width, label='10-Year', color='green')
                    
                    ax.set_xticks(x)
                    ax.set_xticklabels(top_areas, rotation=45, ha='right')
                    ax.set_ylabel('ROI (%)')
                    ax.set_title(f"ROI Projections for Top Areas in {selected_city}")
                    ax.legend()
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                else:
                    st.info(f"No area ROI analysis available for {selected_city}.")
        else:
            st.info("ROI analysis data not available. Run the analysis pipeline first.")
            
    # Tab 4: Rental Yield Analysis
    with tab4:
        st.header("Rental Yield Analysis Dashboard")
        
        # Try to load rental yield analysis data
        rental_analysis_path = "data/reports/rental_yield_analysis.json"
        rental_analysis = {}
        
        try:
            if os.path.exists(rental_analysis_path):
                with open(rental_analysis_path, "r") as f:
                    rental_analysis = json.load(f)
            # For demo purposes, if file doesn't exist but we have ROI data,
            # we'll generate some synthetic rental data
            elif "roi_analysis" in data and "city_roi_analysis" in data["roi_analysis"]:
                st.info("Generating sample rental yield data for demonstration purposes...")
                rental_analysis = {"city_rental_analysis": {}}
                
                for city, city_data in data["roi_analysis"]["city_roi_analysis"].items():
                    if "areas_by_roi" in city_data and city_data["areas_by_roi"]:
                        areas_data = []
                        
                        for area, roi, area_details in city_data["areas_by_roi"]:
                            # Generate synthetic rental yield (2-5% range)
                            # Higher ROI areas generally have lower rental yields in Indian market
                            base_yield = 5.5 - (roi / 25)  # Inverse relationship with ROI
                            yield_pct = max(2.0, min(5.0, base_yield + np.random.uniform(-0.5, 0.5)))
                            
                            price = area_details.get("current_price_per_sqft", 8000) * 1000  # Assuming 1000 sqft property
                            monthly_rental = price * (yield_pct / 100) / 12
                            
                            areas_data.append((area, yield_pct, {
                                "current_avg_price": price,
                                "estimated_monthly_rental": monthly_rental,
                                "annual_rental_yield_percent": yield_pct,
                                "price_to_rent_ratio": price / (monthly_rental * 12) if monthly_rental > 0 else 0
                            }))
                        
                        # Sort by yield
                        areas_data.sort(key=lambda x: x[1], reverse=True)
                        
                        rental_analysis["city_rental_analysis"][city] = {
                            "areas_by_yield": areas_data,
                            "top_yield_area": areas_data[0][0] if areas_data else None,
                            "top_yield_percentage": areas_data[0][1] if areas_data else 0
                        }
                
                # Find top rental yield areas across all cities
                all_areas = []
                for city, analysis in rental_analysis["city_rental_analysis"].items():
                    for area, yield_pct, details in analysis["areas_by_yield"]:
                        all_areas.append((city, area, yield_pct))
                
                all_areas.sort(key=lambda x: x[2], reverse=True)
                rental_analysis["top_rental_yield_areas"] = all_areas[:10]
        except Exception as e:
            st.error(f"Error loading rental yield analysis: {str(e)}")
        
        if rental_analysis and "city_rental_analysis" in rental_analysis:
            # Show top rental yield areas overall
            st.subheader("Top Areas by Rental Yield")
            if "top_rental_yield_areas" in rental_analysis:
                top_areas = rental_analysis["top_rental_yield_areas"][:10]
                
                # Create DataFrame for display
                top_df = pd.DataFrame(top_areas, columns=["City", "Area", "Annual Yield (%)"])
                
                # Round yields to 2 decimal places
                top_df["Annual Yield (%)"] = top_df["Annual Yield (%)"].round(2)
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.dataframe(top_df, hide_index=True, use_container_width=True)
                    
                with col2:
                    # Create bar chart of top yields
                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = plt.cm.Greens(np.linspace(0.5, 0.9, len(top_df)))
                    bars = ax.barh(top_df["City"] + " - " + top_df["Area"], top_df["Annual Yield (%)"], color=colors)
                    
                    # Add value labels
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f"{width:.2f}%", 
                                ha='left', va='center')
                    
                    ax.set_xlabel("Annual Rental Yield (%)")
                    ax.set_title("Top Areas by Rental Yield")
                    
                    st.pyplot(fig)
            
            # City-specific rental yield analysis
            cities = list(rental_analysis["city_rental_analysis"].keys())
            selected_city = st.selectbox("Select City for Rental Analysis", cities, key="rental_city_select")
            
            if selected_city:
                city_data = rental_analysis["city_rental_analysis"][selected_city]
                
                if "areas_by_yield" in city_data and city_data["areas_by_yield"]:
                    # Extract area data
                    areas = []
                    yield_values = []
                    price_to_rent_ratios = []
                    monthly_rentals = []
                    
                    for area, yield_pct, area_data in city_data["areas_by_yield"]:
                        areas.append(area)
                        yield_values.append(yield_pct)
                        price_to_rent_ratio = area_data.get("price_to_rent_ratio", 25)
                        price_to_rent_ratios.append(price_to_rent_ratio)
                        monthly_rentals.append(area_data.get("estimated_monthly_rental", 0))
                    
                    # Create DataFrame for display
                    area_df = pd.DataFrame({
                        "Area": areas,
                        "Annual Yield (%)": [round(y, 2) for y in yield_values],
                        "Monthly Rental (₹)": [f"₹{int(r):,}" for r in monthly_rentals],
                        "Price-to-Rent Ratio": [round(r, 1) for r in price_to_rent_ratios]
                    })
                    
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.subheader(f"Rental Yields in {selected_city}")
                        st.dataframe(area_df, hide_index=True, use_container_width=True)
                        
                        st.write("**Understanding Price-to-Rent Ratio:**")
                        st.write("- Below 15: Potentially excellent rental investment")
                        st.write("- 16-20: Generally good for rental returns")
                        st.write("- 21-25: Moderate rental returns")
                        st.write("- Above 25: Better for long-term appreciation than rental income")
                    
                    with col2:
                        st.subheader("Rental Yield Analysis")
                        
                        # Create scatter plot of yield vs price-to-rent ratio
                        fig, ax = plt.subplots(figsize=(10, 6))
                        scatter = ax.scatter(price_to_rent_ratios, yield_values, s=100, 
                                           c=price_to_rent_ratios, cmap="RdYlGn_r", alpha=0.7)
                        
                        # Add area labels
                        for i, area in enumerate(areas):
                            ax.annotate(area, (price_to_rent_ratios[i], yield_values[i]), 
                                      fontsize=9, ha='center', va='bottom')
                        
                        # Add reference line
                        ax.axhline(y=3.5, color='gray', linestyle='--', alpha=0.5)
                        ax.axvline(x=20, color='gray', linestyle='--', alpha=0.5)
                        
                        ax.set_xlabel("Price-to-Rent Ratio")
                        ax.set_ylabel("Annual Rental Yield (%)")
                        ax.set_title(f"Rental Yield vs Price-to-Rent Ratio in {selected_city}")
                        fig.colorbar(scatter, label="Price-to-Rent Ratio")
                        
                        st.pyplot(fig)
                    
                    # Buy vs Rent Analysis if available
                    buy_vs_rent_data_path = "data/reports/buy_vs_rent_analysis.json"
                    if os.path.exists(buy_vs_rent_data_path):
                        try:
                            with open(buy_vs_rent_data_path, "r") as f:
                                buy_vs_rent_data = json.load(f)
                                
                            if "buy_vs_rent_analysis" in buy_vs_rent_data and selected_city in buy_vs_rent_data["buy_vs_rent_analysis"]:
                                city_bvr_data = buy_vs_rent_data["buy_vs_rent_analysis"][selected_city]
                                
                                st.subheader("Buy vs. Rent Break-even Analysis")
                                
                                if "area_comparisons" in city_bvr_data:
                                    break_even_data = []
                                    
                                    for area, area_data in city_bvr_data["area_comparisons"].items():
                                        if area in areas[:10]:  # Only include areas we already displayed
                                            break_even_year = area_data.get("break_even_year", "Beyond 15 years")
                                            recommendation = area_data.get("long_term_recommendation", "")
                                            
                                            break_even_data.append({
                                                "Area": area,
                                                "Break-even Year": break_even_year if isinstance(break_even_year, (int, float)) else 15,
                                                "Recommendation": recommendation,
                                                "Is Numeric": isinstance(break_even_year, (int, float))
                                            })
                                    
                                    if break_even_data:
                                        # Sort by break-even year (numeric first, then non-numeric)
                                        break_even_data.sort(key=lambda x: (not x["Is Numeric"], x["Break-even Year"]))
                                        
                                        # Create dataframe for display
                                        be_df = pd.DataFrame([{
                                            "Area": d["Area"], 
                                            "Break-even Year": d["Break-even Year"] if d["Is Numeric"] else "Beyond 15 years",
                                            "Recommendation": d["Recommendation"]
                                        } for d in break_even_data])
                                        
                                        st.dataframe(be_df, hide_index=True, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading buy vs rent analysis: {str(e)}")
                else:
                    st.info(f"No rental yield analysis available for {selected_city}.")
        else:
            st.info("Rental yield analysis data not available. Run the full analysis pipeline to generate this data.")
    
    # Tab 5: Location Analysis
    with tab5:
        st.header("Location Analysis Dashboard")
        
        # Initialize location analyzer
        location_analyzer = LocationAnalyzer()
        
        # Show API key status
        api_key_status = "✅ Google Maps API key configured" if location_analyzer.has_api_key() else "❌ Google Maps API key not found (using synthetic data)"
        st.info(api_key_status)
        
        # City selection
        cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
        selected_city = st.selectbox("Select City for Location Analysis", cities, key="location_city_select")
        
        # Get areas for selected city
        areas = []
        if selected_city and processed["listings_df"] is not None and not processed["listings_df"].empty:
            city_data = processed["listings_df"][processed["listings_df"]["city"] == selected_city]
            areas = sorted(city_data["area"].unique().tolist())
        
        if not areas and selected_city:
            # Default areas if data is missing
            default_areas = {
                "Mumbai": ["Andheri", "Bandra", "Worli", "Powai", "Juhu"],
                "Bangalore": ["Whitefield", "Electronic City", "Koramangala", "Indiranagar", "HSR Layout"],
                "Hyderabad": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills", "Madhapur"],
                "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Aundh"],
                "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad"]
            }
            areas = default_areas.get(selected_city, [])
        
        # Area selection
        selected_areas = st.multiselect(
            "Select Areas to Analyze (max 5)", 
            options=areas, 
            default=areas[:min(3, len(areas))],
            max_selections=5
        )
        
        if selected_areas:
            with st.spinner(f"Analyzing locations in {selected_city}..."):
                # Generate location report
                location_report = location_analyzer.generate_location_report(selected_city, selected_areas)
                
                # Display map if available
                if location_report.get("map_available", False):
                    st.subheader("Area Map")
                    city_map = location_report.get("map")
                    st_folium(city_map, width=800, height=500)
                
                # Display location scores
                st.subheader("Location Scores")
                location_scores = []
                
                for area_data in location_report.get("areas", []):
                    location_scores.append({
                        "Area": area_data["name"],
                        "Location Score": area_data["location_score"],
                        "Avg. Commute Time (mins)": area_data["commute_analysis"].get("avg_commute_time", "N/A"),
                        "Amenity Score": area_data["amenity_analysis"].get("overall_amenity_score", "N/A")
                    })
                
                if location_scores:
                    score_df = pd.DataFrame(location_scores)
                    
                    # Create bar chart of location scores
                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(score_df)))
                    bars = ax.barh(score_df["Area"], score_df["Location Score"], color=colors)
                    
                    # Add value labels
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(width + 2, bar.get_y() + bar.get_height()/2, f"{width:.0f}", 
                                ha='left', va='center')
                    
                    ax.set_xlabel("Location Score (0-100)")
                    ax.set_title("Area Location Scores")
                    ax.set_xlim(0, 105)  # Leave room for labels
                    
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        st.pyplot(fig)
                    
                    with col2:
                        st.dataframe(score_df, hide_index=True, use_container_width=True)
                
                # Area details
                if location_report.get("areas"):
                    st.subheader("Area Details")
                    
                    # Area selection for detailed view
                    detail_area = st.selectbox(
                        "Select Area for Detailed Analysis",
                        options=[area["name"] for area in location_report["areas"]],
                        key="detail_area_select"
                    )
                    
                    # Find selected area data
                    area_details = next((area for area in location_report["areas"] if area["name"] == detail_area), None)
                    
                    if area_details:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Commute Analysis")
                            
                            commute_data = area_details["commute_analysis"]
                            st.write(f"**Average Commute Time:** {commute_data.get('avg_commute_time', 'N/A')} minutes")
                            
                            # Show commute times to key destinations
                            if commute_data.get("commute_times"):
                                commute_times_data = []
                                
                                for dest, details in commute_data["commute_times"].items():
                                    commute_times_data.append({
                                        "Destination": dest,
                                        "Distance": details.get("distance_km", details.get("distance", "N/A")),
                                        "Travel Time": f"{details.get('time_mins', 'N/A')} mins"
                                    })
                                
                                st.dataframe(pd.DataFrame(commute_times_data), hide_index=True, use_container_width=True)
                        
                        with col2:
                            st.subheader("Amenity Analysis")
                            
                            amenity_data = area_details["amenity_analysis"]
                            overall_score = amenity_data.get("overall_amenity_score", "N/A")
                            st.write(f"**Overall Amenity Score:** {overall_score}/10")
                            
                            # Show amenity scores
                            if amenity_data.get("amenity_scores"):
                                amenity_scores_data = []
                                
                                for amenity, score in amenity_data["amenity_scores"].items():
                                    count = amenity_data.get("amenities", {}).get(amenity, {}).get("count", 0)
                                    amenity_scores_data.append({
                                        "Amenity Type": amenity.replace("_", " ").title(),
                                        "Count": count,
                                        "Score": f"{score}/10"
                                    })
                                
                                # Create amenity score chart
                                amenity_df = pd.DataFrame(amenity_scores_data)
                                
                                fig, ax = plt.subplots(figsize=(10, 6))
                                amenity_colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(amenity_df)))
                                ax.barh(amenity_df["Amenity Type"], 
                                      [float(score.split("/")[0]) for score in amenity_df["Score"]], 
                                      color=amenity_colors)
                                
                                ax.set_xlabel("Score (0-10)")
                                ax.set_title(f"Amenity Scores for {detail_area}")
                                ax.set_xlim(0, 11)  # 0-10 scale with room for labels
                                
                                st.pyplot(fig)
                                st.dataframe(amenity_df, hide_index=True, use_container_width=True)
                    
                        # Investment Recommendation
                        st.subheader("Location-based Investment Insight")
                        
                        location_score = area_details.get("location_score", 0)
                        commute_score = 50 - (area_details["commute_analysis"].get("avg_commute_time", 45) - 15)
                        amenity_score = area_details["amenity_analysis"].get("overall_amenity_score", 5) * 5
                        
                        if location_score > 80:
                            st.success(f"**Prime Location (Score: {location_score}/100)**: {detail_area} offers excellent accessibility and amenities, making it ideal for both primary residence and rental investment. Properties here typically command premium prices but offer strong appreciation potential.")
                        elif location_score > 65:
                            st.info(f"**Very Good Location (Score: {location_score}/100)**: {detail_area} offers good connectivity and sufficient amenities, making it suitable for long-term investments. Good balance of price and lifestyle quality.")
                        elif location_score > 50:
                            st.warning(f"**Average Location (Score: {location_score}/100)**: {detail_area} has moderate accessibility and basic amenities. Consider for mid-term investment if there are upcoming infrastructure projects that could improve its score.")
                        else:
                            st.error(f"**Below Average Location (Score: {location_score}/100)**: {detail_area} has limited accessibility and amenities. Only consider for long-term speculative investment if there are significant development plans.")
                        
                        # Rental potential based on location
                        rental_potential = "High" if amenity_score > 30 else "Medium" if amenity_score > 20 else "Low"
                        st.write(f"**Rental Potential**: {rental_potential}")
                        
                        if commute_score < 10:
                            st.write("⚠️ **Long commute times may limit rental demand from working professionals.**")
        else:
            st.info("Please select at least one area to analyze.")

    # Tab 6: Data Explorer
    with tab6:
        st.header("Data Explorer")
        
        data_type = st.radio("Select Data to Explore", 
                           ["Property Listings", "Historical Prices", "Infrastructure Projects"])
        
        if data_type == "Property Listings" and not processed["listings_df"].empty:
            st.subheader("Property Listings Data")
            
            # Filters
            city_filter = st.multiselect("Filter by City", 
                                      processed["listings_df"]["city"].unique().tolist())
            
            filtered_df = processed["listings_df"]
            if city_filter:
                filtered_df = filtered_df[filtered_df["city"].isin(city_filter)]
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_price = filtered_df["price"].mean()
                st.metric("Average Price", f"₹{avg_price:,.0f}")
            
            with col2:
                avg_size = filtered_df["sqft"].mean()
                st.metric("Average Size", f"{avg_size:.0f} sq.ft")
            
            with col3:
                avg_price_sqft = filtered_df["price_per_sqft"].mean()
                st.metric("Average Price/sq.ft", f"₹{avg_price_sqft:,.0f}")
            
        elif data_type == "Historical Prices" and not processed["historical_df"].empty:
            st.subheader("Historical Price Data")
            
            # Filters
            city_filter = st.selectbox("Select City", 
                                     ["All"] + processed["historical_df"]["city"].unique().tolist())
            
            filtered_df = processed["historical_df"]
            if city_filter != "All":
                filtered_df = filtered_df[filtered_df["city"] == city_filter]
                
                # Area filter becomes available when city is selected
                areas = ["All"] + filtered_df["area"].unique().tolist()
                area_filter = st.selectbox("Select Area", areas)
                
                if area_filter != "All":
                    filtered_df = filtered_df[filtered_df["area"] == area_filter]
                    
                    # If specific area selected, show price trend
                    st.subheader(f"Price Trend for {area_filter}, {city_filter}")
                    
                    # Group by month_year and calculate average price
                    trend_data = filtered_df.sort_values("month_year")
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(trend_data["month_year"], trend_data["avg_price_per_sqft"], marker='o')
                    ax.set_xlabel("Month-Year")
                    ax.set_ylabel("Price per sq.ft (₹)")
                    ax.set_title(f"Price Trend for {area_filter}, {city_filter}")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
        elif data_type == "Infrastructure Projects" and not processed["infra_df"].empty:
            st.subheader("Infrastructure Projects Data")
            
            # Filters
            status_filter = st.multiselect("Filter by Status", 
                                        processed["infra_df"]["status"].unique().tolist())
            
            filtered_df = processed["infra_df"]
            if status_filter:
                filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Project type distribution
            st.subheader("Project Type Distribution")
            
            if not filtered_df.empty:
                type_counts = filtered_df["project_type"].value_counts()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                type_counts.plot(kind="bar", ax=ax)
                ax.set_xlabel("Project Type")
                ax.set_ylabel("Number of Projects")
                ax.set_title("Infrastructure Projects by Type")
                
                st.pyplot(fig)
        else:
            st.info(f"No {data_type.lower()} data available.")

if __name__ == "__main__":
    app()