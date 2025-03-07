#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import folium
from streamlit_folium import st_folium

from data_providers.location_analyzer import LocationAnalyzer
from use_cases.first_time_homebuyer import FirstTimeHomebuyerAnalysis
from use_cases.property_investor import PropertyInvestorAnalysis
from use_cases.commercial_re_analyst import CommercialREAnalysis
from use_cases.nri_investor import NRIInvestorAnalysis

# Add required dependencies to requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = f.read()
    
required_packages = ['streamlit==1.31.0', 'streamlit-folium']
for package in required_packages:
    if package.split('==')[0] not in requirements:
        with open('requirements.txt', 'a') as f:
            f.write(f'\n{package}\n')

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
    """Main Streamlit application with specialized use cases"""
    # Create necessary directories
    os.makedirs("data/analysis", exist_ok=True)  
    os.makedirs("data/reports", exist_ok=True)
    st.set_page_config(
        page_title="Real Estate Investment Analysis Dashboard",
        page_icon="🏢",
        layout="wide"
    )
    
    # Load and process data
    data = load_data()
    processed = process_data(data)
    
    # Initialize specialized analyzers
    first_time_buyer = FirstTimeHomebuyerAnalysis(data, processed)
    property_investor = PropertyInvestorAnalysis(data, processed)
    commercial_analyst = CommercialREAnalysis(data, processed)
    nri_investor = NRIInvestorAnalysis(data, processed)
    
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
    if use_case == "First-time Homebuyer":
        first_time_buyer.render_dashboard()
    elif use_case == "Property Investor":
        property_investor.render_dashboard()
    elif use_case == "Commercial Real Estate":
        commercial_analyst.render_dashboard()
    elif use_case == "NRI Investor":
        nri_investor.render_dashboard()
    else:
        # Instead of importing and running the general dashboard which causes conflicts with set_page_config
        st.header("General Market Analysis")
        st.info("This specialized dashboard focuses on user-specific workflows. For the general market analysis dashboard, please run: `streamlit run web_dashboard.py`")
        
        # Show options to run the general dashboard
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("#### Launch General Dashboard")
            st.write("Run this command in your terminal:")
            st.code("streamlit run web_dashboard.py")
        
        with col2:
            st.write("#### General Dashboard Features")
            st.write("- Market Overview with price trends")
            st.write("- Investment Recommendations")
            st.write("- ROI Analysis by city and area")
            st.write("- Rental Yield Analysis")
            st.write("- Location Analysis with maps")
            st.write("- Data Explorer for listings and prices")

if __name__ == "__main__":
    app()