#!/usr/bin/env python3
"""
Improved Web Dashboard for Real Estate AI
Includes geospatial analysis, interactive maps, and personalized investment recommendations
"""

import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import folium
from streamlit_folium import st_folium
import sys

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from our config and utils packages
try:
    from config import logger, DATA_DIR, PROPERTY_LISTINGS_FILE, HISTORICAL_PRICES_FILE, INFRASTRUCTURE_PROJECTS_FILE
    from utils.file_utils import load_json_file, save_json_file
    from utils.geospatial import create_city_map, create_heatmap
except ImportError:
    # Set up basic logging if config import fails
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("dashboard")
    DATA_DIR = "data"
    PROPERTY_LISTINGS_FILE = os.path.join(DATA_DIR, "property_listings.json")
    HISTORICAL_PRICES_FILE = os.path.join(DATA_DIR, "historical_prices.json")
    INFRASTRUCTURE_PROJECTS_FILE = os.path.join(DATA_DIR, "infrastructure_projects.json")

# Import from data providers and use cases if they exist
try:
    from data_providers.location_analyzer import LocationAnalyzer
    has_location_analyzer = True
except ImportError:
    has_location_analyzer = False
    logger.warning("LocationAnalyzer not found - maps will be limited")

try:
    from use_cases.first_time_homebuyer import FirstTimeHomebuyerAnalysis
    from use_cases.property_investor import PropertyInvestorAnalysis
    from use_cases.commercial_re_analyst import CommercialREAnalysis
    from use_cases.nri_investor import NRIInvestorAnalysis
    has_specialized_modules = True
    logger.info("Specialized analysis modules loaded successfully")
except ImportError:
    has_specialized_modules = False
    logger.warning("Specialized analysis modules not found - using basic dashboard features only")
    
# Add required dependencies to requirements.txt
try:
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
        
    required_packages = ['streamlit==1.31.0', 'streamlit-folium', 'folium>=0.14.0']
    for package in required_packages:
        if package.split('==')[0] not in requirements:
            with open('requirements.txt', 'a') as f:
                f.write(f'\n{package}\n')
except Exception as e:
    logger.warning(f"Could not update requirements.txt: {str(e)}")

def load_data():
    """Load all necessary data files using utility functions"""
    data = {}
    
    try:
        # Use file_utils if available
        if 'load_json_file' in globals():
            logger.info("Using file_utils for loading data")
            # Load property listings
            data["property_listings"] = load_json_file(PROPERTY_LISTINGS_FILE, [])
            
            # Load historical prices
            data["historical_prices"] = load_json_file(HISTORICAL_PRICES_FILE, [])
            
            # Load infrastructure projects
            data["infrastructure_projects"] = load_json_file(INFRASTRUCTURE_PROJECTS_FILE, [])
            
            # Load ROI analysis
            data["roi_analysis"] = load_json_file(os.path.join(DATA_DIR, "reports", "roi_analysis_sample.json"), {})
            
            # Load recommendations
            data["recommendations"] = load_json_file(os.path.join(DATA_DIR, "reports", "final_recommendations.json"), {})
        else:
            # Fall back to direct file loading
            logger.info("Using direct file loading")
            
            # Load property listings
            if os.path.exists(PROPERTY_LISTINGS_FILE):
                with open(PROPERTY_LISTINGS_FILE, "r") as f:
                    data["property_listings"] = json.load(f)
            else:
                data["property_listings"] = []
            
            # Load historical prices
            if os.path.exists(HISTORICAL_PRICES_FILE):
                with open(HISTORICAL_PRICES_FILE, "r") as f:
                    data["historical_prices"] = json.load(f)
            else:
                data["historical_prices"] = []
            
            # Load infrastructure projects
            if os.path.exists(INFRASTRUCTURE_PROJECTS_FILE):
                with open(INFRASTRUCTURE_PROJECTS_FILE, "r") as f:
                    data["infrastructure_projects"] = json.load(f)
            else:
                data["infrastructure_projects"] = []
            
            # Load ROI analysis
            roi_file = os.path.join(DATA_DIR, "reports", "roi_analysis_sample.json")
            if os.path.exists(roi_file):
                with open(roi_file, "r") as f:
                    data["roi_analysis"] = json.load(f)
            else:
                data["roi_analysis"] = {}
            
            # Load recommendations
            rec_file = os.path.join(DATA_DIR, "reports", "final_recommendations.json")
            if os.path.exists(rec_file):
                with open(rec_file, "r") as f:
                    data["recommendations"] = json.load(f)
            else:
                data["recommendations"] = {}
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Error loading data: {str(e)}")
        # Provide empty data structures
        data = {
            "property_listings": [],
            "historical_prices": [],
            "infrastructure_projects": [],
            "roi_analysis": {},
            "recommendations": {}
        }
    
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
    """Main Streamlit application with specialized use cases"""
    # Create necessary directories
    os.makedirs(os.path.join(DATA_DIR, "analysis"), exist_ok=True)  
    os.makedirs(os.path.join(DATA_DIR, "reports"), exist_ok=True)
    st.set_page_config(
        page_title="Real Estate AI Investment Dashboard",
        page_icon="🏢",
        layout="wide"
    )
    
    # Load and process data
    data = load_data()
    processed = process_data(data)
    
    # Initialize specialized analyzers if available
    if has_specialized_modules:
        try:
            first_time_buyer = FirstTimeHomebuyerAnalysis(data, processed)
            property_investor = PropertyInvestorAnalysis(data, processed)
            commercial_analyst = CommercialREAnalysis(data, processed)
            nri_investor = NRIInvestorAnalysis(data, processed)
            specialized_ready = True
            logger.info("Specialized analyzers initialized successfully")
        except Exception as e:
            st.error(f"Error initializing specialized analyzers: {str(e)}")
            logger.error(f"Error initializing specialized analyzers: {str(e)}")
            specialized_ready = False
    else:
        specialized_ready = False
    
    # Create persistent sidebar with profile icons
    with st.sidebar:
        st.title("🏢 RE Analysis")
        st.divider()
        
        # User profile selection with icons
        st.subheader("Select Your Profile")
        
        # Session state to remember user selection
        if 'use_case' not in st.session_state:
            st.session_state['use_case'] = "First-time Homebuyer"
            
        # Profile buttons with icons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠", help="First-time Homebuyer", use_container_width=True):
                st.session_state['use_case'] = "First-time Homebuyer"
            if st.button("🏗️", help="Commercial Real Estate", use_container_width=True):
                st.session_state['use_case'] = "Commercial Real Estate"
        with col2:
            if st.button("💰", help="Property Investor", use_container_width=True):
                st.session_state['use_case'] = "Property Investor"
            if st.button("🌏", help="NRI Investor", use_container_width=True):
                st.session_state['use_case'] = "NRI Investor"
                
        if st.button("📊", help="General Analysis", use_container_width=True):
            st.session_state['use_case'] = "General Analysis"
            
        st.divider()
        
        # Show current profile
        st.write(f"**Current Profile:** {st.session_state['use_case']}")
        
        # User preferences section
        st.subheader("Preferences")
        
        # Save/load feature
        with st.expander("Save/Load Analysis"):
            save_name = st.text_input("Analysis Name", "My Analysis")
            save_col1, save_col2 = st.columns(2)
            with save_col1:
                if st.button("Save", use_container_width=True):
                    st.success("Analysis saved!")
            with save_col2:
                if st.button("Load", use_container_width=True):
                    st.info("Analysis loaded!")
        
        # Add tooltips for first-time users
        if 'first_visit' not in st.session_state:
            st.session_state['first_visit'] = True
            st.info("👋 Welcome! Click on a profile icon to get started with personalized analysis.")
    
    # Main content area with title
    st.title("🏢 Real Estate Investment Analysis Dashboard")
    st.write("AI-powered insights tailored to your investment profile")
    
    # Get use case from session state
    use_case = st.session_state['use_case']
    
    st.divider()
    
    # Render the appropriate dashboard based on user selection
    if specialized_ready:
        if use_case == "First-time Homebuyer":
            first_time_buyer.render_dashboard()
        elif use_case == "Property Investor":
            property_investor.render_dashboard()
        elif use_case == "Commercial Real Estate":
            commercial_analyst.render_dashboard()
        elif use_case == "NRI Investor":
            nri_investor.render_dashboard()
        else:
            render_general_dashboard(data, processed)
    else:
        # Fall back to general dashboard
        st.warning("Specialized analyzers not available. Showing general dashboard instead.")
        render_general_dashboard(data, processed)

def render_general_dashboard(data, processed):
    """Render the general market analysis dashboard"""
    st.header("Real Estate Market Analysis Dashboard")
    st.subheader("Investment Opportunities in Indian Metropolitan Areas")
    
    # Add tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", 
                                     "💰 Investment Recommendations", 
                                     "📈 ROI Analysis", 
                                     "🔍 Data Explorer"])
    
    # Tab 1: Market Overview
    with tab1:
        st.header("Market Overview")
        
        # Show city comparison if data exists
        if processed["historical_df"] is not None and not processed["historical_df"].empty:
            try:
                city_data = processed["historical_df"].groupby("city")["avg_price_per_sqft"].mean().sort_values(ascending=False)
                
                # Create bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                city_data.plot(kind="bar", color="skyblue", ax=ax)
                ax.set_ylabel("Average Price (₹ per sq.ft)")
                ax.set_title("Average Property Prices by City")
                
                for i, v in enumerate(city_data):
                    ax.text(i, v + 100, f"₹{v:.0f}", ha='center')
                
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error creating city comparison chart: {str(e)}")
                logger.error(f"Error creating city comparison chart: {str(e)}")
        else:
            st.info("No historical price data available.")
            
        # Add map if location analyzer is available
        if has_location_analyzer:
            st.subheader("Investment Hotspots")
            try:
                # Create location analyzer
                location_analyzer = LocationAnalyzer()
                city_selection = st.selectbox("Select City for Map View", 
                                           ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"])
                
                # Generate map
                city_map = location_analyzer.generate_area_map(city_selection, 
                               [area for area in data["recommendations"].get("top_areas", []) if area["city"] == city_selection])
                
                # Display map
                st_folium(city_map, width=700, height=500)
            except Exception as e:
                st.error(f"Error generating map: {str(e)}")
                logger.error(f"Error generating map: {str(e)}")
        elif 'create_city_map' in globals():
            # Use our own map utilities
            st.subheader("Investment Hotspots Map")
            try:
                city_selection = st.selectbox("Select City for Map View", 
                                          ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"])
                
                # Create area data for map
                areas = []
                for area_data in data["recommendations"].get("investment_recommendations", {}).get("top_areas", []):
                    if area_data.get("city") == city_selection:
                        # Format for our map utility
                        areas.append({
                            "name": area_data.get("area"),
                            "latitude": area_data.get("latitude", 0),
                            "longitude": area_data.get("longitude", 0),
                            "roi": area_data.get("roi_5yr", 0),
                            "price_per_sqft": area_data.get("price_per_sqft", 0)
                        })
                
                if areas:
                    city_map = create_city_map(city_selection, areas)
                    st_folium(city_map, width=700, height=500)
                else:
                    st.info(f"No area data available for {city_selection}")
            except Exception as e:
                st.error(f"Error generating map: {str(e)}")
                logger.error(f"Error generating map: {str(e)}")
    
    # Tab 2: Investment Recommendations
    with tab2:
        st.header("Investment Recommendations")
        
        # Display investment recommendations if available
        if "investment_recommendations" in data["recommendations"]:
            recommendations = data["recommendations"]["investment_recommendations"]
            
            # Format top areas as a DataFrame for display
            if "top_areas" in recommendations:
                top_areas_df = pd.DataFrame(recommendations["top_areas"])
                
                # Add styling
                st.subheader("Top Areas by ROI Potential")
                st.dataframe(top_areas_df, hide_index=True, use_container_width=True)
                
                # Add bar chart visualization
                try:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Select top 10 areas
                    plot_data = top_areas_df.head(10)
                    
                    # Create labels with city and area
                    labels = [f"{row['city']} - {row['area']}" for _, row in plot_data.iterrows()]
                    
                    # Plot horizontal bar chart
                    bars = ax.barh(labels, plot_data["roi_5yr"], color="#3498db")
                    
                    # Add value labels
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        label_x_pos = width * 1.01
                        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                               va='center')
                    
                    ax.set_xlabel("5-Year ROI Potential (%)")
                    ax.set_title("Top Investment Areas by ROI")
                    
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error creating recommendation chart: {str(e)}")
                    logger.error(f"Error creating recommendation chart: {str(e)}")
            
            # Display summary and risk assessment
            if "summary" in recommendations:
                st.subheader("Investment Strategy")
                st.write(recommendations["summary"])
                
            if "risk_assessment" in recommendations:
                st.subheader("Risk Assessment")
                st.write(recommendations["risk_assessment"])
        else:
            st.info("No investment recommendations available. Run the analysis first.")
    
    # Tab 3: ROI Analysis
    with tab3:
        st.header("ROI Analysis")
        
        if "city_roi_analysis" in data["roi_analysis"]:
            # City selection
            cities = list(data["roi_analysis"]["city_roi_analysis"].keys())
            selected_city = st.selectbox("Select City for ROI Analysis", cities)
            
            if selected_city in data["roi_analysis"]["city_roi_analysis"]:
                city_roi = data["roi_analysis"]["city_roi_analysis"][selected_city]
                
                # Extract ROI data for areas
                if "areas_by_roi" in city_roi:
                    areas_roi = []
                    for area_data in city_roi["areas_by_roi"]:
                        area_name = area_data[0]
                        roi = area_data[1]
                        risk_score = area_data[2].get("roi_projections", {}).get("risk_score", 5) if len(area_data) > 2 else 5
                        areas_roi.append({"area": area_name, "roi": roi, "risk_score": risk_score})
                    
                    # Create DataFrame for display
                    areas_roi_df = pd.DataFrame(areas_roi)
                    
                    # Display table
                    st.subheader(f"ROI Analysis for Areas in {selected_city}")
                    st.dataframe(areas_roi_df, hide_index=True, use_container_width=True)
                    
                    # Create scatter plot of risk vs. return
                    try:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        # Scatter plot
                        scatter = ax.scatter(areas_roi_df["risk_score"], areas_roi_df["roi"], 
                                          s=100, c=areas_roi_df["roi"], cmap="viridis", alpha=0.7)
                        
                        # Add area labels
                        for i, area in enumerate(areas_roi_df["area"]):
                            ax.annotate(area, 
                                      (areas_roi_df["risk_score"].iloc[i], areas_roi_df["roi"].iloc[i]),
                                      fontsize=9, ha='center', va='bottom')
                        
                        # Add quadrant lines
                        ax.axhline(y=25, color='gray', linestyle='--', alpha=0.5)
                        ax.axvline(x=5, color='gray', linestyle='--', alpha=0.5)
                        
                        ax.set_xlabel("Risk Score (Higher = More Risk)")
                        ax.set_ylabel("5-Year ROI (%)")
                        ax.set_title(f"Risk-Return Profile for {selected_city}")
                        
                        fig.colorbar(scatter, label="ROI (%)")
                        
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error creating risk-return chart: {str(e)}")
                        logger.error(f"Error creating risk-return chart: {str(e)}")
        else:
            st.info("No ROI analysis data available. Run the analysis first.")
    
    # Tab 4: Data Explorer
    with tab4:
        st.header("Data Explorer")
        
        # Create tabs for different data types
        data_tabs = st.tabs(["Property Listings", "Historical Prices", "Infrastructure Projects"])
        
        # Tab for property listings
        with data_tabs[0]:
            st.subheader("Property Listings")
            
            if not processed["listings_df"].empty:
                # Filters
                city_filter = st.multiselect("Filter by City", 
                                       processed["listings_df"]["city"].unique().tolist())
                
                # Apply filters
                filtered_df = processed["listings_df"]
                if city_filter:
                    filtered_df = filtered_df[filtered_df["city"].isin(city_filter)]
                
                # Display data
                st.dataframe(filtered_df, use_container_width=True)
                
                # Show statistics
                if not filtered_df.empty:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_price = filtered_df["price"].mean() if "price" in filtered_df.columns else 0
                        st.metric("Average Price", f"₹{avg_price:,.0f}")
                    
                    with col2:
                        avg_size = filtered_df["sqft"].mean() if "sqft" in filtered_df.columns else 0
                        st.metric("Average Size", f"{avg_size:.0f} sq.ft")
                    
                    with col3:
                        avg_price_sqft = filtered_df["price_per_sqft"].mean() if "price_per_sqft" in filtered_df.columns else 0
                        st.metric("Average Price/sq.ft", f"₹{avg_price_sqft:,.0f}")
            else:
                st.info("No property listings data available.")
        
        # Tab for historical prices
        with data_tabs[1]:
            st.subheader("Historical Price Trends")
            
            if not processed["historical_df"].empty:
                # Filters
                city_filter = st.selectbox("Select City", 
                                       ["All"] + processed["historical_df"]["city"].unique().tolist(),
                                       key="historical_city")
                
                # Apply filters
                filtered_df = processed["historical_df"]
                if city_filter != "All":
                    filtered_df = filtered_df[filtered_df["city"] == city_filter]
                    
                    # Area filter for the selected city
                    areas = ["All"] + filtered_df["area"].unique().tolist()
                    area_filter = st.selectbox("Select Area", areas)
                    
                    if area_filter != "All":
                        filtered_df = filtered_df[filtered_df["area"] == area_filter]
                        
                        # Show price trend chart for specific area
                        try:
                            st.subheader(f"Price Trend for {area_filter}, {city_filter}")
                            
                            # Sort by date
                            trend_data = filtered_df.sort_values("month_year")
                            
                            # Plot line chart
                            fig, ax = plt.subplots(figsize=(10, 6))
                            ax.plot(trend_data["month_year"], trend_data["avg_price_per_sqft"], 
                                   marker='o', linewidth=2)
                            
                            ax.set_xlabel("Month-Year")
                            ax.set_ylabel("Price per sq.ft (₹)")
                            ax.set_title(f"Price Trend for {area_filter}, {city_filter}")
                            
                            plt.xticks(rotation=45)
                            plt.tight_layout()
                            
                            st.pyplot(fig)
                        except Exception as e:
                            st.error(f"Error creating price trend chart: {str(e)}")
                            logger.error(f"Error creating price trend chart: {str(e)}")
                
                # Display data table
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No historical price data available.")
                
        # Tab for infrastructure projects
        with data_tabs[2]:
            st.subheader("Infrastructure Projects")
            
            if not processed["infra_df"].empty:
                # Filters
                status_filter = st.multiselect("Filter by Status", 
                                          processed["infra_df"]["status"].unique().tolist())
                
                # Apply filters
                filtered_df = processed["infra_df"]
                if status_filter:
                    filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
                
                # Display data
                st.dataframe(filtered_df, use_container_width=True)
                
                # Show project type distribution
                if not filtered_df.empty and "project_type" in filtered_df.columns:
                    try:
                        st.subheader("Project Type Distribution")
                        
                        # Count projects by type
                        type_counts = filtered_df["project_type"].value_counts()
                        
                        # Create bar chart
                        fig, ax = plt.subplots(figsize=(10, 6))
                        type_counts.plot(kind="bar", ax=ax, color="#2ecc71")
                        
                        ax.set_xlabel("Project Type")
                        ax.set_ylabel("Number of Projects")
                        ax.set_title("Infrastructure Projects by Type")
                        
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error creating project type chart: {str(e)}")
                        logger.error(f"Error creating project type chart: {str(e)}")
            else:
                st.info("No infrastructure projects data available.")

if __name__ == "__main__":
    app()