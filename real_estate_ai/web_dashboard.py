#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", 
                                      "💰 Investment Recommendations", 
                                      "📈 ROI Analysis", 
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
            selected_city = st.selectbox("Select City", cities)
            
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
    
    # Tab 4: Data Explorer
    with tab4:
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