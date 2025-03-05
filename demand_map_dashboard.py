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
from data_providers.location_analyzer import LocationAnalyzer
import random

# Setup page configuration
st.set_page_config(
    page_title="Real Estate Demand Map - India",
    page_icon="🏢",
    layout="wide"
)

# Load data
def load_data():
    """Load necessary data files"""
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
    
    return processed

def get_demand_data(city, area=None):
    """Get demand data for a city or area"""
    # This would normally pull from a demand prediction model
    # For now, we'll generate synthetic data
    
    # Base demand is higher in major cities
    base_demand = {
        "Mumbai": 85,
        "Bangalore": 82,
        "Hyderabad": 78,
        "Pune": 72,
        "Delhi-NCR": 80
    }.get(city, 70)
    
    # If we're looking at a specific area, adjust the demand
    if area:
        # Add some variability for areas
        demand = base_demand + random.randint(-15, 15)
        # Keep demand between 0-100
        demand = max(0, min(100, demand))
        
        return {
            "current_demand": demand,
            "trend": random.choice(["increasing", "stable", "decreasing"]),
            "future_potential": random.randint(1, 10)
        }
    else:
        return base_demand

def get_area_details(city, area):
    """Get detailed information about an area"""
    # In a real application, this would pull from a database or API
    # For now, we'll generate synthetic data
    
    demand_data = get_demand_data(city, area)
    
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

def get_high_potential_areas(city, current_location=None, count=5):
    """Find nearby areas with high potential"""
    # This would normally use a geographic distance model and prediction algorithm
    # For now, we'll generate synthetic data
    
    # Define city areas (subset of actual areas)
    city_areas = {
        "Mumbai": ["Andheri", "Bandra", "Worli", "Powai", "Juhu", "Malad", "Goregaon", "Thane", "Navi Mumbai"],
        "Bangalore": ["Whitefield", "Electronic City", "Koramangala", "Indiranagar", "HSR Layout", "Jayanagar", "JP Nagar"],
        "Hyderabad": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills", "Madhapur", "Kukatpally", "Miyapur"],
        "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Aundh", "Wakad", "Kalyani Nagar"],
        "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad", "Ghaziabad", "Vasant Kunj"]
    }.get(city, [])
    
    # If we have a current location, remove it from the list
    if current_location and current_location in city_areas:
        city_areas.remove(current_location)
    
    # Select random areas (or all if we have less than count)
    selected_areas = random.sample(city_areas, min(count, len(city_areas)))
    
    # Generate data for each area
    area_data = []
    for area in selected_areas:
        demand = get_demand_data(city, area)
        
        # Calculate distance (random for now)
        distance = random.uniform(3, 20)
        
        area_data.append({
            "name": area,
            "current_demand": demand["current_demand"],
            "future_potential": demand["future_potential"],
            "distance_km": round(distance, 1)
        })
    
    # Sort by future potential (descending)
    area_data.sort(key=lambda x: x["future_potential"], reverse=True)
    
    return area_data

def generate_demand_map(location_analyzer, city, selected_area=None):
    """Generate a map showing demand heatmap for a city"""
    
    # Get city coordinates
    city_coord = location_analyzer.city_coordinates.get(city, {"lat": 20.5937, "lng": 78.9629})
    
    # Create base map
    m = folium.Map(
        location=[city_coord["lat"], city_coord["lng"]],
        zoom_start=11,
        tiles="CartoDB positron"
    )
    
    # Add city areas
    city_areas = {
        "Mumbai": ["Andheri", "Bandra", "Worli", "Powai", "Juhu", "Malad", "Goregaon", "Thane", "Navi Mumbai"],
        "Bangalore": ["Whitefield", "Electronic City", "Koramangala", "Indiranagar", "HSR Layout", "Jayanagar", "JP Nagar"],
        "Hyderabad": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills", "Madhapur", "Kukatpally", "Miyapur"],
        "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Aundh", "Wakad", "Kalyani Nagar"],
        "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad", "Ghaziabad", "Vasant Kunj"]
    }.get(city, [])
    
    # Points for heatmap (lat, lng, intensity)
    heat_data = []
    
    # Add markers for each area
    for area in city_areas:
        # Try to geocode the area
        cache_key = f"{area}_{city}_India"
        
        if cache_key in location_analyzer.poi_cache:
            location = location_analyzer.poi_cache[cache_key]
        else:
            location = location_analyzer.geocode_with_nominatim(f"{area}, {city}, India")
            
            if location:
                location_analyzer.poi_cache[cache_key] = location
        
        if not location:
            # If geocoding fails, place marker with random offset from city center
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            location = {
                "lat": city_coord["lat"] + lat_offset,
                "lng": city_coord["lng"] + lng_offset
            }
        
        # Get demand data for the area
        demand_data = get_demand_data(city, area)
        
        # Add marker
        color = "green" if demand_data["current_demand"] > 80 else "orange" if demand_data["current_demand"] > 60 else "red"
        selected = area == selected_area
        icon = folium.Icon(color=color, icon="star" if selected else "home", prefix="fa")
        
        popup_html = f"""
        <div style="width:200px">
            <h4>{area}</h4>
            <p><b>Current Demand:</b> {demand_data["current_demand"]}/100</p>
            <p><b>Trend:</b> {demand_data.get("trend", "stable")}</p>
            <p><b>Future Potential:</b> {demand_data.get("future_potential", 5)}/10</p>
            <p><b>Click for details</b></p>
        </div>
        """
        
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=area,
            icon=icon
        ).add_to(m)
        
        # Add to heatmap data with intensity based on demand
        if isinstance(demand_data, dict):
            intensity = demand_data.get("current_demand", 50) / 20
        else:
            intensity = demand_data / 20
        heat_data.append([location["lat"], location["lng"], intensity])
    
    # Add heatmap layer
    folium.plugins.HeatMap(
        heat_data,
        radius=20,
        blur=15,
        gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1: 'red'},
        min_opacity=0.5
    ).add_to(m)
    
    # Add title
    title_html = f"""
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 500px; height: 40px; 
                background-color: white; border-radius: 5px;
                z-index:9999; font-size: 18px; font-weight: bold;
                padding: 10px; text-align: center;">
        Real Estate Demand Map - {city}
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))
    
    return m

def app():
    """Main application"""
    st.title("🏢 Real Estate Demand Map - India")
    st.write("Explore real estate demand across cities in India and discover high-potential areas")
    
    # Initialize location analyzer
    location_analyzer = LocationAnalyzer()
    
    # Load data
    data = load_data()
    processed = process_data(data)
    
    # City selection
    cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
    selected_city = st.selectbox("Select City", cities)
    
    # Get areas for the selected city
    city_areas = {
        "Mumbai": ["Andheri", "Bandra", "Worli", "Powai", "Juhu", "Malad", "Goregaon", "Thane", "Navi Mumbai"],
        "Bangalore": ["Whitefield", "Electronic City", "Koramangala", "Indiranagar", "HSR Layout", "Jayanagar", "JP Nagar"],
        "Hyderabad": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills", "Madhapur", "Kukatpally", "Miyapur"],
        "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Aundh", "Wakad", "Kalyani Nagar"],
        "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad", "Ghaziabad", "Vasant Kunj"]
    }.get(selected_city, [])
    
    # Area selection
    selected_area = st.selectbox("Select Area", ["None"] + city_areas)
    
    if selected_area == "None":
        selected_area = None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Real Estate Demand Map")
        st.write("Click on an area to view details. The heatmap shows current demand intensity.")
        
        with st.spinner("Generating demand map..."):
            # Generate the map
            demand_map = generate_demand_map(location_analyzer, selected_city, selected_area)
            
            # Display the map
            map_data = st_folium(demand_map, width=700, height=500)
        
        # Detect map click - Extract clicked location from map_data
        clicked_location = None
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data["last_clicked"]["lat"]
            clicked_lng = map_data["last_clicked"]["lng"]
            
            # Find the nearest area to the clicked point
            min_distance = float("inf")
            for area in city_areas:
                cache_key = f"{area}_{selected_city}_India"
                if cache_key in location_analyzer.poi_cache:
                    location = location_analyzer.poi_cache[cache_key]
                    dist = ((location["lat"] - clicked_lat)**2 + (location["lng"] - clicked_lng)**2)**0.5
                    if dist < min_distance:
                        min_distance = dist
                        clicked_location = area
    
    with col2:
        # Show area details if an area is selected or clicked
        display_area = selected_area if selected_area else clicked_location
        
        if display_area:
            st.subheader(f"{display_area}, {selected_city}")
            
            # Get area details
            details = get_area_details(selected_city, display_area)
            
            # Display current demand
            demand = details["demand"]["current_demand"]
            demand_color = "green" if demand > 80 else "orange" if demand > 60 else "red"
            st.markdown(f"#### Current Demand: <span style='color:{demand_color};'>{demand}/100</span>", unsafe_allow_html=True)
            
            # Display trend
            trend = details["demand"]["trend"]
            trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
            st.write(f"**Trend:** {trend_emoji} {trend.capitalize()}")
            
            # Display future potential
            future = details["demand"]["future_potential"]
            st.write(f"**Future Potential:** {'⭐' * future} ({future}/10)")
            
            # Display average price
            st.write(f"**Average Price:** ₹{details['avg_price_per_sqft']}/sq.ft")
            
            # Display factors affecting demand
            st.subheader("Key Factors")
            for factor in details["factors"]:
                st.write(f"• {factor}")
        else:
            st.info("👆 Select an area or click on the map to view details")
    
    # Recommended areas section
    st.subheader("High Potential Areas Nearby")
    
    if selected_area:
        high_potential_areas = get_high_potential_areas(selected_city, selected_area)
        
        # Create columns for each high potential area
        cols = st.columns(len(high_potential_areas))
        
        for i, area in enumerate(high_potential_areas):
            with cols[i]:
                st.write(f"**{area['name']}**")
                
                # Create a small gauge/chart for demand
                demand_fig, ax = plt.subplots(figsize=(3, 0.5))
                ax.barh([0], [area['current_demand']], height=0.3, color=plt.cm.RdYlGn(area['current_demand']/100))
                ax.set_xlim(0, 100)
                ax.set_ylim(-0.5, 0.5)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.text(area['current_demand']/2, 0, f"{area['current_demand']}/100", 
                        ha='center', va='center', fontsize=8, color='white', fontweight='bold')
                
                st.pyplot(demand_fig)
                
                # Show future potential
                st.write(f"**Future Potential:** {'⭐' * area['future_potential']}")
                st.write(f"**Distance:** {area['distance_km']} km")
    else:
        st.info("Select an area to see high potential nearby locations")
    
    # Add some context about the data
    st.markdown("---")
    st.caption("Note: This dashboard uses simulated demand data for demonstration purposes. In a production environment, it would use real-time data from market analysis and AI predictions.")

if __name__ == "__main__":
    app()