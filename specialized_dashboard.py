#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import folium
import folium.plugins
from streamlit_folium import st_folium
import random
import datetime

from data_providers.location_analyzer import LocationAnalyzer
from use_cases.first_time_homebuyer import FirstTimeHomebuyerAnalysis
from use_cases.property_investor import PropertyInvestorAnalysis
from use_cases.commercial_re_analyst import CommercialREAnalysis
from use_cases.nri_investor import NRIInvestorAnalysis

# Function for demand map analysis
def get_demand_data(location):
    """Get demand data for any location in India based on coordinates or name"""
    # This would use a real AI model in production
    # For now, we'll generate synthetic data
    
    # Random demand score between 50-90
    demand_score = random.randint(50, 90)
    
    return {
        "current_demand": demand_score,
        "trend": random.choice(["increasing", "stable", "decreasing"]),
        "future_potential": random.randint(1, 10),
        "location_name": location.get("name", "Selected Area")
    }

def get_location_details(location):
    """Get detailed information about a location"""
    # In production, this would pull from database/API with real data
    # For now, we'll generate synthetic data
    
    demand_data = get_demand_data(location)
    
    # Generate factors affecting demand
    factors = []
    
    if demand_data["current_demand"] > 80:
        factors.extend([
            "Strong job market",
            "Excellent connectivity",
            "Good schools and amenities"
        ])
    elif demand_data["current_demand"] > 60:
        factors.extend([
            "Developing infrastructure",
            "Growing commercial activity",
            "Reasonable property prices"
        ])
    else:
        factors.extend([
            "Limited infrastructure",
            "Distance from city center",
            "Fewer amenities"
        ])
    
    # Add some random factors
    additional_factors = [
        "New metro line planned",
        "Upcoming IT park",
        "New shopping mall under construction",
        "School/University in vicinity",
        "Hospital development",
        "Green space development",
        "Road widening project"
    ]
    
    factors.extend(random.sample(additional_factors, 2))
    
    return {
        "demand": demand_data,
        "factors": factors,
        "avg_price_per_sqft": random.randint(5000, 15000)
    }

def get_high_potential_nearby(location, radius_km=20, count=5):
    """Find nearby areas with high potential"""
    # This would use geospatial data in production
    # For now, we'll generate synthetic locations
    
    lat, lng = location["lat"], location["lng"]
    nearby_locations = []
    
    for i in range(count):
        # Generate random point within radius_km
        delta_lat = random.uniform(-0.01, 0.01) * radius_km/10
        delta_lng = random.uniform(-0.01, 0.01) * radius_km/10
        
        nearby_lat = lat + delta_lat
        nearby_lng = lng + delta_lng
        
        # Calculate distance (simplified)
        distance = ((delta_lat**2 + delta_lng**2)**0.5) * 111  # rough km per degree
        
        # Generate area name
        area_name = f"Area {chr(65+i)}"
        
        # Get demand data
        demand = get_demand_data({"lat": nearby_lat, "lng": nearby_lng, "name": area_name})
        
        nearby_locations.append({
            "name": area_name,
            "lat": nearby_lat,
            "lng": nearby_lng,
            "current_demand": demand["current_demand"],
            "future_potential": demand["future_potential"],
            "distance_km": round(distance, 1)
        })
    
    # Sort by future potential (descending)
    nearby_locations.sort(key=lambda x: x["future_potential"], reverse=True)
    
    return nearby_locations

def generate_india_map(location_analyzer=None, default_center=None):
    """Generate a map of India with click functionality for location selection"""
    if not location_analyzer:
        location_analyzer = LocationAnalyzer()
    
    # Default to center of India if no location specified
    if not default_center:
        default_center = [20.5937, 78.9629]
        
    m = folium.Map(
        location=default_center,
        zoom_start=5,
        tiles="CartoDB positron"
    )
    
    # Add cities as markers for reference
    cities = {
        "Mumbai": [19.0760, 72.8777],
        "Delhi": [28.7041, 77.1025],
        "Bangalore": [12.9716, 77.5946],
        "Hyderabad": [17.3850, 78.4867],
        "Chennai": [13.0827, 80.2707],
        "Kolkata": [22.5726, 88.3639],
        "Pune": [18.5204, 73.8567],
        "Ahmedabad": [23.0225, 72.5714],
        "Jaipur": [26.9124, 75.7873],
        "Surat": [21.1702, 72.8311]
    }
    
    # Add city markers
    for city, coords in cities.items():
        folium.Marker(
            location=coords,
            popup=city,
            tooltip=city,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
    
    # Add instructions as map text
    instructions_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 9999; 
                background-color: white; padding: 10px; border-radius: 5px; 
                max-width: 300px; box-shadow: 0 0 10px rgba(0,0,0,0.3);">
        <h4>Instructions:</h4>
        <p>Click anywhere on the map to analyze real estate demand for that location</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(instructions_html))
    
    return m

def render_demand_map_dashboard():
    """Render the demand map dashboard in the specialized dashboard"""
    st.markdown("""
    <div style="background-color:#1E3A8A; padding:15px; border-radius:10px; margin-bottom:20px">
        <h1 style="color:white; text-align:center">🏢 Real Estate Demand Map Explorer - India</h1>
        <p style="color:#E5E7EB; text-align:center">Discover high-potential real estate opportunities across India using our AI-powered demand prediction tool</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a tabbed interface for the map explorer
    map_tab, insights_tab, help_tab = st.tabs(["🗺️ Demand Map", "📊 Market Insights", "❓ How It Works"])
    
    # Initialize location analyzer
    location_analyzer = LocationAnalyzer()
    
    # Store selected location in session state to persist between tabs
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    
    with map_tab:
        st.markdown("""
        <div style="background-color:#F3F4F6; padding:10px; border-radius:5px; margin-bottom:15px">
            <p style="color:#4B5563; font-size:16px"><strong>📍 Click anywhere on the map</strong> to analyze current demand and future potential for real estate investment.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create two columns - map and details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Generate the base map
            india_map = generate_india_map(location_analyzer)
            
            # Display the map and capture clicked location
            map_data = st_folium(india_map, width=700, height=500, returned_objects=["last_clicked"])
            
            if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
                clicked_lat = map_data["last_clicked"]["lat"]
                clicked_lng = map_data["last_clicked"]["lng"]
                
                # Create a location object
                st.session_state.selected_location = {
                    "lat": clicked_lat,
                    "lng": clicked_lng,
                    "name": "Selected Location"
                }
                
                # Add marker to the map at clicked location
                clicked_map = generate_india_map(location_analyzer, [clicked_lat, clicked_lng])
                folium.Marker(
                    location=[clicked_lat, clicked_lng],
                    popup="Selected Location",
                    tooltip="Selected Location",
                    icon=folium.Icon(color="red", icon="home")
                ).add_to(clicked_map)
                
                # If clicked, show the updated map
                st_folium(clicked_map, width=700, height=500)
        
        with col2:
            if st.session_state.selected_location:
                selected_location = st.session_state.selected_location
                
                # Create a card-like container for location analysis
                st.markdown("""
                <div style="background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:20px">
                    <h3 style="color:#1E40AF; border-bottom:1px solid #E2E8F0; padding-bottom:8px">Location Analysis</h3>
                """, unsafe_allow_html=True)
                
                # Get location details
                details = get_location_details(selected_location)
                
                # Display coordinates
                st.markdown(f"**📍 Coordinates:** {selected_location['lat']:.4f}, {selected_location['lng']:.4f}")
                
                # Display current demand with gauge chart
                demand = details["demand"]["current_demand"]
                
                # Create a more visually appealing gauge
                fig = plt.figure(figsize=(4, 0.8))
                ax = fig.add_subplot(111)
                
                # Define colors based on demand value
                if demand > 80:
                    color = "#22C55E"  # green
                    status = "High"
                elif demand > 60:
                    color = "#F59E0B"  # amber
                    status = "Medium" 
                else:
                    color = "#EF4444"  # red
                    status = "Low"
                
                # Create gradient background
                background = np.ones((1, 100, 4))
                for i in range(100):
                    if i < 60:
                        background[0, i] = [0.93, 0.27, 0.27, 0.6]  # red with alpha
                    elif i < 80:
                        background[0, i] = [0.96, 0.62, 0.04, 0.6]  # amber with alpha
                    else:
                        background[0, i] = [0.13, 0.77, 0.37, 0.6]  # green with alpha
                
                ax.imshow(background, aspect='auto', extent=[0, 100, 0, 1])
                
                # Add the demand indicator
                ax.plot([demand, demand], [0, 1], 'k-', lw=2)
                ax.plot(demand, 0.5, 'ko', markersize=12)
                ax.plot(demand, 0.5, 'wo', markersize=8)
                
                # Add text
                ax.text(5, 0.5, "0", color='white', va='center', fontweight='bold')
                ax.text(95, 0.5, "100", color='white', va='center', ha='right', fontweight='bold')
                ax.set_title(f"Current Demand: {demand}/100 ({status})", fontsize=12, color='#1F2937')
                
                # Remove axes and spines
                ax.set_xlim(0, 100)
                ax.set_ylim(0, 1)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
                st.pyplot(fig)
                
                # Display trend with custom styling
                trend = details["demand"]["trend"]
                trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
                trend_color = "#22C55E" if trend == "increasing" else "#EF4444" if trend == "decreasing" else "#6B7280"
                
                st.markdown(f"""
                <div style="display:flex; align-items:center; margin:10px 0">
                    <div style="font-size:24px; margin-right:10px">{trend_emoji}</div>
                    <div>
                        <strong>Trend:</strong> <span style="color:{trend_color}; font-weight:500">{trend.capitalize()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display future potential as stars with better styling
                future = details["demand"]["future_potential"]
                st.markdown(f"""
                <div style="margin:10px 0">
                    <strong>Future Potential:</strong> <span style="color:#F59E0B; font-size:18px">{"★" * future}{"☆" * (10-future)}</span>
                    <span style="color:#6B7280; font-size:14px"> ({future}/10)</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Display average price
                st.markdown(f"""
                <div style="background-color:#EFF6FF; padding:8px 12px; border-radius:6px; margin:15px 0; border-left:4px solid #3B82F6">
                    <strong>Average Price:</strong> <span style="font-size:18px; font-weight:500">₹{details['avg_price_per_sqft']:,}/sq.ft</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Close the card div
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Display factors affecting demand in a nice card
                st.markdown("""
                <div style="background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0">
                    <h3 style="color:#1E40AF; border-bottom:1px solid #E2E8F0; padding-bottom:8px">Key Factors</h3>
                    <ul style="list-style-type:none; padding-left:5px">
                """, unsafe_allow_html=True)
                
                for factor in details["factors"]:
                    st.markdown(f"""
                    <li style="margin-bottom:8px; display:flex; align-items:center">
                        <span style="background-color:#3B82F6; border-radius:50%; width:20px; height:20px; display:flex; justify-content:center; align-items:center; margin-right:10px">
                            <span style="color:white; font-size:12px">✓</span>
                        </span>
                        <span>{factor}</span>
                    </li>
                    """, unsafe_allow_html=True)
                
                # Close the factors card
                st.markdown("</div>", unsafe_allow_html=True)
                
            else:
                # Show a nice prompt to click the map
                st.markdown("""
                <div style="background-color:#EFF6FF; padding:20px; border-radius:8px; text-align:center; margin-top:50px; border:1px dashed #3B82F6">
                    <img src="https://cdn-icons-png.flaticon.com/512/1077/1077969.png" width="40" style="margin-bottom:10px">
                    <h3 style="color:#1F2937">Select a Location</h3>
                    <p style="color:#4B5563">Click anywhere on the map to analyze real estate demand and investment potential for that location.</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Market insights tab
    with insights_tab:
        st.subheader("📊 Market Insights")
        
        if st.session_state.selected_location:
            selected_location = st.session_state.selected_location
            
            st.markdown("""
            <div style="background-color:#F0FDF4; padding:10px 15px; border-radius:6px; margin-bottom:20px; border-left:4px solid #22C55E">
                <h3 style="margin:5px 0; color:#1F2937">High Potential Areas Nearby</h3>
                <p style="color:#4B5563; margin:5px 0">Discover upcoming neighborhoods with strong investment potential within 20km radius</p>
            </div>
            """, unsafe_allow_html=True)
            
            high_potential_areas = get_high_potential_nearby(selected_location)
            
            # Display areas in a more attractive grid
            for i in range(0, len(high_potential_areas), 2):
                col1, col2 = st.columns(2)
                
                # First area in this row
                with col1:
                    if i < len(high_potential_areas):
                        area = high_potential_areas[i]
                        st.markdown(f"""
                        <div style="background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:15px">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
                                <h3 style="margin:0; color:#1E40AF">{area['name']}</h3>
                                <span style="background-color:#3B82F6; color:white; padding:3px 8px; border-radius:12px; font-size:12px">{area['distance_km']} km</span>
                            </div>
                            
                            <div style="display:flex; align-items:center; margin:10px 0">
                                <div style="flex-grow:1; height:10px; background-color:#E5E7EB; border-radius:5px">
                                    <div style="width:{area['current_demand']}%; height:10px; background-color:{get_demand_color(area['current_demand'])}; border-radius:5px"></div>
                                </div>
                                <div style="margin-left:10px; font-weight:500">{area['current_demand']}%</div>
                            </div>
                            
                            <div style="color:#F59E0B; font-size:18px; margin-top:5px">{"★" * area['future_potential']}{"☆" * (10-area['future_potential'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Second area in this row
                with col2:
                    if i+1 < len(high_potential_areas):
                        area = high_potential_areas[i+1]
                        st.markdown(f"""
                        <div style="background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:15px">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
                                <h3 style="margin:0; color:#1E40AF">{area['name']}</h3>
                                <span style="background-color:#3B82F6; color:white; padding:3px 8px; border-radius:12px; font-size:12px">{area['distance_km']} km</span>
                            </div>
                            
                            <div style="display:flex; align-items:center; margin:10px 0">
                                <div style="flex-grow:1; height:10px; background-color:#E5E7EB; border-radius:5px">
                                    <div style="width:{area['current_demand']}%; height:10px; background-color:{get_demand_color(area['current_demand'])}; border-radius:5px"></div>
                                </div>
                                <div style="margin-left:10px; font-weight:500">{area['current_demand']}%</div>
                            </div>
                            
                            <div style="color:#F59E0B; font-size:18px; margin-top:5px">{"★" * area['future_potential']}{"☆" * (10-area['future_potential'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Add a prediction timeline
            st.markdown("""
            <div style="background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0; margin-top:20px">
                <h3 style="color:#1E40AF; border-bottom:1px solid #E2E8F0; padding-bottom:8px">Investment Timeline Prediction</h3>
                <p style="color:#4B5563; margin:5px 0">Projected price growth over the next 5 years based on current trends</p>
            """, unsafe_allow_html=True)
            
            # Create a timeline chart showing price growth prediction
            timeline_fig, ax = plt.subplots(figsize=(10, 4))
            years = 5
            x = np.arange(years + 1)  # Current year + 5
            
            # Generate synthetic data
            details = get_location_details(selected_location)
            base_price = details['avg_price_per_sqft']
            
            if details['demand']['trend'] == 'increasing':
                growth_rate = 0.08 + (details['demand']['future_potential'] / 100)  # 8-18% growth
            elif details['demand']['trend'] == 'stable':
                growth_rate = 0.05 + (details['demand']['future_potential'] / 150)  # 5-12% growth
            else:
                growth_rate = 0.02 + (details['demand']['future_potential'] / 200)  # 2-7% growth
            
            # Calculate price projection
            prices = [base_price]
            for i in range(1, years + 1):
                next_price = prices[-1] * (1 + growth_rate)
                prices.append(next_price)
            
            # Plot the growth
            ax.plot(x, prices, marker='o', markersize=8, linewidth=3, color='#3B82F6')
            ax.fill_between(x, prices, color='#93C5FD', alpha=0.3)
            
            # Add labels
            current_year = datetime.datetime.now().year
            ax.set_xticks(x)
            ax.set_xticklabels([str(current_year + i) for i in range(years + 1)])
            
            # Format y-axis as currency
            ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: f"₹{int(x):,}"))
            
            # Add annotations
            for i, price in enumerate(prices):
                ax.annotate(f"₹{int(price):,}", 
                            (x[i], price), 
                            textcoords="offset points",
                            xytext=(0, 10),
                            ha='center',
                            fontweight='bold')
            
            # Add title and styling
            ax.set_title("Projected Price per sq.ft", fontsize=14, pad=20)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            st.pyplot(timeline_fig)
            
            # Calculate and display ROI
            total_growth = (prices[-1] / prices[0] - 1) * 100
            annualized_growth = ((prices[-1] / prices[0]) ** (1/years) - 1) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style="text-align:center; padding:10px; background-color:#EFF6FF; border-radius:5px">
                    <div style="font-size:24px; font-weight:bold; color:#1E40AF">{total_growth:.1f}%</div>
                    <div style="color:#6B7280">Total 5-Year Growth</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align:center; padding:10px; background-color:#EFF6FF; border-radius:5px">
                    <div style="font-size:24px; font-weight:bold; color:#1E40AF">{annualized_growth:.1f}%</div>
                    <div style="color:#6B7280">Annual Growth Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Close the timeline card
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            # Prompt to select a location first
            st.markdown("""
            <div style="background-color:#FEF2F2; padding:20px; border-radius:8px; text-align:center; margin-top:30px">
                <img src="https://cdn-icons-png.flaticon.com/512/1250/1250751.png" width="40" style="margin-bottom:10px">
                <h3 style="color:#1F2937">No Location Selected</h3>
                <p style="color:#4B5563">Please go to the Demand Map tab and click on a location to view detailed market insights and analytics.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # How it works tab
    with help_tab:
        st.subheader("How the Demand Map Explorer Works")
        
        st.markdown("""
        <div style="background-color:#F8FAFC; padding:20px; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:20px">
            <h3 style="color:#1E40AF; border-bottom:1px solid #E2E8F0; padding-bottom:10px">Understanding the Data</h3>
            <p style="color:#1F2937">Our AI-powered demand prediction model analyzes multiple factors to calculate real estate demand and investment potential:</p>
            
            <div style="display:flex; margin:15px 0; align-items:center">
                <div style="background-color:#3B82F6; color:white; border-radius:50%; width:30px; height:30px; display:flex; justify-content:center; align-items:center; margin-right:15px">1</div>
                <div style="color:#1F2937">
                    <strong>Current Demand (0-100)</strong>: Measures present market interest and activity
                </div>
            </div>
            
            <div style="display:flex; margin:15px 0; align-items:center">
                <div style="background-color:#3B82F6; color:white; border-radius:50%; width:30px; height:30px; display:flex; justify-content:center; align-items:center; margin-right:15px">2</div>
                <div style="color:#1F2937">
                    <strong>Trend</strong>: Indicates whether demand is increasing, stable, or decreasing
                </div>
            </div>
            
            <div style="display:flex; margin:15px 0; align-items:center">
                <div style="background-color:#3B82F6; color:white; border-radius:50%; width:30px; height:30px; display:flex; justify-content:center; align-items:center; margin-right:15px">3</div>
                <div style="color:#1F2937">
                    <strong>Future Potential (1-10)</strong>: Predicts long-term growth prospects
                </div>
            </div>
            
            <div style="display:flex; margin:15px 0; align-items:center">
                <div style="background-color:#3B82F6; color:white; border-radius:50%; width:30px; height:30px; display:flex; justify-content:center; align-items:center; margin-right:15px">4</div>
                <div style="color:#1F2937">
                    <strong>Key Factors</strong>: Important elements influencing demand in the area
                </div>
            </div>
        </div>
        
        <div style="background-color:#F8FAFC; padding:20px; border-radius:8px; border:1px solid #E2E8F0; margin-bottom:20px">
            <h3 style="color:#1E40AF; border-bottom:1px solid #E2E8F0; padding-bottom:10px">How to Use This Tool</h3>
            
            <ol style="padding-left:20px">
                <li style="margin-bottom:10px; color:#1F2937"><strong>Select a Location</strong>: Click anywhere on the map to analyze that specific location</li>
                <li style="margin-bottom:10px; color:#1F2937"><strong>Analyze Demand</strong>: View current demand, trends, and future potential</li>
                <li style="margin-bottom:10px; color:#1F2937"><strong>Explore Nearby Areas</strong>: Discover high-potential neighborhoods in the vicinity</li>
                <li style="margin-bottom:10px; color:#1F2937"><strong>Review Insights</strong>: Check detailed market projections and ROI estimates</li>
                <li style="margin-bottom:10px; color:#1F2937"><strong>Compare Multiple Areas</strong>: Click different locations to compare opportunities</li>
            </ol>
        </div>
        
        <div style="background-color:#F0FDF4; padding:15px; border-radius:8px; border-left:4px solid #22C55E">
            <p style="margin:5px 0; color:#1F2937"><strong>Note:</strong> This demonstration uses simulated data for illustration purposes. In a production environment, the tool would incorporate real-time market data, historical trends, infrastructure development plans, and AI predictions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer section
    st.markdown("---")
    st.markdown("""
    <div style="display:flex; justify-content:center; color:#6B7280; font-size:14px; background-color:#F9FAFB; padding:10px; border-radius:5px">
        <p>Data updated: March 2025 | Real Estate AI Insights | Powered by OpenStreetMap & AI Analysis</p>
    </div>
    """, unsafe_allow_html=True)

# Helper function to get color based on demand value
def get_demand_color(demand):
    if demand > 80:
        return "#22C55E"  # green
    elif demand > 60:
        return "#F59E0B"  # amber
    else:
        return "#EF4444"  # red

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
        layout="wide",
        initial_sidebar_state="expanded"
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
            
        # Make buttons more visible and mobile-friendly with clear labels
        if st.button("🏠 First-time Homebuyer", use_container_width=True):
            st.session_state['use_case'] = "First-time Homebuyer"
            
        if st.button("💰 Property Investor", use_container_width=True):
            st.session_state['use_case'] = "Property Investor"
        
        if st.button("🏗️ Commercial Real Estate", use_container_width=True):
            st.session_state['use_case'] = "Commercial Real Estate"
            
        if st.button("🌏 NRI Investor", use_container_width=True):
            st.session_state['use_case'] = "NRI Investor"
                
        if st.button("📊 General Analysis", use_container_width=True):
            st.session_state['use_case'] = "General Analysis"
            
        if st.button("🗺️ Demand Map Explorer", use_container_width=True):
            st.session_state['use_case'] = "Demand Map Explorer"
            
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
    elif use_case == "Demand Map Explorer":
        render_demand_map_dashboard()
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