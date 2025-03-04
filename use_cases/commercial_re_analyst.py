"""
Commercial real estate analysis module for Real Estate AI.
Focuses on business location factors, foot traffic, and zoning analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import folium
from streamlit_folium import st_folium
from data_providers.location_analyzer import LocationAnalyzer

class CommercialREAnalysis:
    """Commercial real estate specialized analysis and dashboard components."""
    
    def __init__(self, data, processed):
        """Initialize with loaded data."""
        self.data = data
        self.processed = processed
        self.location_analyzer = LocationAnalyzer()
    
    def analyze_business_district_proximity(self, city, area):
        """Analyze proximity to key business centers for a given area."""
        results = {
            "city": city,
            "area": area,
            "proximity_scores": {},
            "overall_proximity_score": 0
        }
        
        # Define key business districts by city
        business_districts = {
            "Mumbai": ["BKC", "Nariman Point", "Worli", "Andheri East", "Lower Parel"],
            "Bangalore": ["MG Road", "Electronic City", "Whitefield", "Outer Ring Road", "Koramangala"],
            "Hyderabad": ["HITEC City", "Gachibowli", "Banjara Hills", "Madhapur", "Jubilee Hills"],
            "Pune": ["Hinjewadi", "Kharadi", "Magarpatta", "Kalyani Nagar", "SB Road"],
            "Delhi-NCR": ["Connaught Place", "Cyber City Gurgaon", "Noida Expressway", "Aerocity", "Nehru Place"]
        }
        
        # Default districts if city not in the list
        if city not in business_districts:
            business_districts[city] = ["Central Business District", "Tech Park", "Financial District"]
        
        # Try to geocode the target area
        area_coords = self.location_analyzer.geocode_with_nominatim(f"{area}, {city}, India")
        
        if not area_coords:
            return self.generate_synthetic_proximity_data(city, area, business_districts[city])
        
        # Calculate distance to each business district
        total_proximity_score = 0
        count = 0
        
        for district in business_districts[city]:
            try:
                # Geocode the business district
                district_coords = self.location_analyzer.geocode_with_nominatim(f"{district}, {city}, India")
                
                if district_coords:
                    # Calculate route info using OSRM
                    route_info = self.location_analyzer.fetch_osm_distance(area_coords, district_coords)
                    
                    if route_info:
                        # Store distance and time
                        dist_km = route_info.get("distance_km", 0)
                        time_mins = route_info.get("time_mins", 0)
                        
                        # Calculate proximity score (0-10, inverse of distance)
                        # Closer districts get higher scores
                        proximity_score = max(0, 10 - (dist_km / 2))  # 20km or more = 0, 0km = 10
                        
                        results["proximity_scores"][district] = {
                            "distance_km": dist_km,
                            "travel_time_mins": time_mins,
                            "proximity_score": proximity_score
                        }
                        
                        total_proximity_score += proximity_score
                        count += 1
            except Exception as e:
                print(f"Error calculating proximity to {district}: {str(e)}")
        
        # Calculate overall score
        if count > 0:
            results["overall_proximity_score"] = round(total_proximity_score / count, 1)
        
        # If we couldn't calculate any real distances, use synthetic data
        if count == 0:
            return self.generate_synthetic_proximity_data(city, area, business_districts[city])
            
        return results
    
    def generate_synthetic_proximity_data(self, city, area, districts):
        """Generate synthetic data for business district proximity."""
        results = {
            "city": city,
            "area": area,
            "proximity_scores": {},
            "overall_proximity_score": 0,
            "is_synthetic": True
        }
        
        total_proximity_score = 0
        
        # Generate random but realistic proximity data for each district
        for district in districts:
            # Random distance between 2-25 km
            dist_km = round(np.random.uniform(2, 25), 1)
            
            # Calculate approximate travel time (assuming avg speed of 20-30 km/h in Indian cities)
            avg_speed = np.random.uniform(20, 30)  # km/h
            time_mins = round((dist_km / avg_speed) * 60, 1)
            
            # Calculate proximity score (0-10, inverse of distance)
            proximity_score = max(0, 10 - (dist_km / 2))
            
            results["proximity_scores"][district] = {
                "distance_km": dist_km,
                "travel_time_mins": time_mins,
                "proximity_score": proximity_score
            }
            
            total_proximity_score += proximity_score
        
        # Calculate overall score
        if districts:
            results["overall_proximity_score"] = round(total_proximity_score / len(districts), 1)
            
        return results
    
    def analyze_foot_traffic(self, city, area):
        """Analyze foot traffic potential using amenity density."""
        results = {
            "city": city,
            "area": area,
            "foot_traffic_score": 0,
            "amenity_counts": {},
            "traffic_generators": []
        }
        
        try:
            # Try to geocode the area
            area_coords = self.location_analyzer.geocode_with_nominatim(f"{area}, {city}, India")
            
            if not area_coords:
                return self.generate_synthetic_foot_traffic(city, area)
            
            # Amenities that generate foot traffic
            traffic_generators = [
                "restaurant", "cafe", "fast_food", "pub", "bar",  # Food & drink
                "supermarket", "mall", "marketplace", "department_store",  # Shopping
                "bank", "atm", "post_office",  # Services
                "cinema", "theatre", "arts_centre", "tourist_attraction",  # Entertainment
                "bus_station", "subway_station", "train_station"  # Transportation
            ]
            
            total_count = 0
            found_data = False
            
            # Search for each amenity type
            for amenity in traffic_generators:
                try:
                    # Query for amenities using OpenStreetMap
                    amenities = self.location_analyzer.query_osm_amenities(
                        area_coords["lat"], area_coords["lng"], amenity, radius=1000
                    )
                    
                    if amenities:
                        count = len(amenities)
                        results["amenity_counts"][amenity] = count
                        total_count += count
                        found_data = True
                        
                        # Add top traffic generators
                        if count >= 3:
                            results["traffic_generators"].append({
                                "type": amenity,
                                "count": count
                            })
                except Exception as e:
                    print(f"Error searching for {amenity}: {str(e)}")
            
            # If we couldn't find any real data, use synthetic data
            if not found_data:
                return self.generate_synthetic_foot_traffic(city, area)
            
            # Calculate foot traffic score (scale of 0-100)
            # Using a logarithmic scale to avoid outliers
            import math
            results["foot_traffic_score"] = min(100, round(20 * math.log10(total_count + 1), 0))
            
            # Sort traffic generators by count
            results["traffic_generators"].sort(key=lambda x: x["count"], reverse=True)
            
            # Calculate density (amenities per sq km)
            area_sqkm = 3.14  # π * radius² = π * 1² = 3.14 sq km
            results["amenity_density"] = round(total_count / area_sqkm, 1)
            
            return results
            
        except Exception as e:
            print(f"Error analyzing foot traffic: {str(e)}")
            return self.generate_synthetic_foot_traffic(city, area)
    
    def generate_synthetic_foot_traffic(self, city, area):
        """Generate synthetic foot traffic data."""
        results = {
            "city": city,
            "area": area,
            "foot_traffic_score": 0,
            "amenity_counts": {},
            "traffic_generators": [],
            "is_synthetic": True
        }
        
        # Define amenity types that generate foot traffic
        amenity_types = [
            "restaurant", "cafe", "fast_food", "pub", "bar",
            "supermarket", "mall", "marketplace", 
            "bank", "atm", "post_office",
            "cinema", "theatre", 
            "bus_station", "train_station"
        ]
        
        # City-based density factor
        density_factor = 1.0
        if city in ["Mumbai", "Delhi-NCR"]:
            density_factor = 1.5
        elif city in ["Bangalore", "Hyderabad", "Chennai"]:
            density_factor = 1.2
            
        # Area-based factor (assuming areas with certain names are busier)
        area_factor = 1.0
        busy_terms = ["central", "market", "mall", "plaza", "complex", "commercial", "main"]
        if any(term in area.lower() for term in busy_terms):
            area_factor = 1.3
            
        total_count = 0
        
        # Generate random counts for each amenity type
        for amenity in amenity_types:
            # Base count varies by amenity type
            if amenity in ["restaurant", "cafe", "fast_food"]:
                base_count = np.random.randint(3, 15)
            elif amenity in ["mall", "cinema", "theatre"]:
                base_count = np.random.randint(0, 3)
            elif amenity in ["bus_station", "train_station"]:
                base_count = np.random.randint(0, 2)
            else:
                base_count = np.random.randint(1, 8)
                
            # Apply factors
            count = int(base_count * density_factor * area_factor)
            
            results["amenity_counts"][amenity] = count
            total_count += count
            
            # Add significant traffic generators
            if count >= 3:
                results["traffic_generators"].append({
                    "type": amenity,
                    "count": count
                })
        
        # Calculate foot traffic score (scale of 0-100)
        import math
        results["foot_traffic_score"] = min(100, round(20 * math.log10(total_count + 1), 0))
        
        # Sort traffic generators by count
        results["traffic_generators"].sort(key=lambda x: x["count"], reverse=True)
        
        # Calculate density (amenities per sq km)
        area_sqkm = 3.14  # π * radius² = π * 1² = 3.14 sq km
        results["amenity_density"] = round(total_count / area_sqkm, 1)
        
        return results
    
    def analyze_zoning(self, city, area):
        """Analyze zoning and land use information for commercial potential."""
        zoning_info = {
            "city": city,
            "area": area,
            "zoning_type": "Unknown",
            "commercial_allowed": False,
            "max_fsi": 0,
            "zoning_details": {},
            "commercial_suitability_score": 0
        }
        
        # Since OpenStreetMap doesn't provide detailed zoning data,
        # we would normally need to integrate with a municipal data source
        # For this demo, we'll use predefined data for major areas
        
        # Define known zoning data for select areas
        zoning_database = {
            "Mumbai": {
                "BKC": {"zoning_type": "Commercial", "commercial_allowed": True, "max_fsi": 4.0},
                "Nariman Point": {"zoning_type": "Commercial", "commercial_allowed": True, "max_fsi": 3.5},
                "Andheri East": {"zoning_type": "Mixed-Use", "commercial_allowed": True, "max_fsi": 3.0},
                "Worli": {"zoning_type": "Mixed-Use", "commercial_allowed": True, "max_fsi": 3.5},
                "Powai": {"zoning_type": "Mixed-Use", "commercial_allowed": True, "max_fsi": 2.5},
            },
            "Bangalore": {
                "MG Road": {"zoning_type": "Commercial", "commercial_allowed": True, "max_fsi": 3.25},
                "Whitefield": {"zoning_type": "Mixed-Use", "commercial_allowed": True, "max_fsi": 2.5},
                "Electronic City": {"zoning_type": "Commercial", "commercial_allowed": True, "max_fsi": 3.0},
                "Koramangala": {"zoning_type": "Mixed-Use", "commercial_allowed": True, "max_fsi": 2.5},
                "Indiranagar": {"zoning_type": "Mixed-Use", "commercial_allowed": True, "max_fsi": 2.0},
            }
        }
        
        # Check if we have data for this city and area
        if city in zoning_database and area in zoning_database[city]:
            zoning_info.update(zoning_database[city][area])
            
            # Calculate commercial suitability score (scale of 0-100)
            if zoning_info["zoning_type"] == "Commercial":
                zoning_info["commercial_suitability_score"] = 90
            elif zoning_info["zoning_type"] == "Mixed-Use" and zoning_info["commercial_allowed"]:
                zoning_info["commercial_suitability_score"] = 70
            elif zoning_info["commercial_allowed"]:
                zoning_info["commercial_suitability_score"] = 50
            else:
                zoning_info["commercial_suitability_score"] = 10
                
            # Adjust based on FSI/FAR
            if zoning_info["max_fsi"] > 3.0:
                zoning_info["commercial_suitability_score"] += 10
            elif zoning_info["max_fsi"] < 2.0:
                zoning_info["commercial_suitability_score"] -= 10
            
            # Cap at 100
            zoning_info["commercial_suitability_score"] = min(100, zoning_info["commercial_suitability_score"])
            
            return zoning_info
        else:
            # Generate synthetic zoning data
            return self.generate_synthetic_zoning(city, area)
    
    def generate_synthetic_zoning(self, city, area):
        """Generate synthetic zoning data when real data is not available."""
        zoning_info = {
            "city": city,
            "area": area,
            "is_synthetic": True
        }
        
        # Generate zoning type based on area name
        commercial_terms = ["commercial", "business", "market", "mall", "plaza", "complex"]
        residential_terms = ["colony", "nagar", "residential", "garden", "villa", "house"]
        
        area_lower = area.lower()
        
        if any(term in area_lower for term in commercial_terms):
            zoning_type = "Commercial"
            commercial_allowed = True
            max_fsi = round(np.random.uniform(2.5, 4.0), 1)
        elif any(term in area_lower for term in residential_terms):
            zoning_type = "Residential"
            commercial_allowed = np.random.choice([True, False], p=[0.3, 0.7])
            max_fsi = round(np.random.uniform(1.5, 2.5), 1)
        else:
            zoning_type = "Mixed-Use"
            commercial_allowed = True
            max_fsi = round(np.random.uniform(2.0, 3.0), 1)
        
        # Additional zoning details
        zoning_details = {
            "height_restriction_meters": int(np.random.uniform(15, 45)),
            "parking_requirement": f"{np.random.randint(1, 3)} per {np.random.randint(50, 100)} sq.m",
            "setback_required_meters": round(np.random.uniform(3, 8), 1)
        }
        
        # Set values
        zoning_info["zoning_type"] = zoning_type
        zoning_info["commercial_allowed"] = commercial_allowed
        zoning_info["max_fsi"] = max_fsi
        zoning_info["zoning_details"] = zoning_details
        
        # Calculate commercial suitability score (scale of 0-100)
        if zoning_type == "Commercial":
            commercial_suitability = 90
        elif zoning_type == "Mixed-Use" and commercial_allowed:
            commercial_suitability = 70
        elif commercial_allowed:
            commercial_suitability = 40
        else:
            commercial_suitability = 10
            
        # Adjust based on FSI/FAR
        if max_fsi > 3.0:
            commercial_suitability += 10
        elif max_fsi < 2.0:
            commercial_suitability -= 10
        
        # Cap at 100
        zoning_info["commercial_suitability_score"] = min(100, commercial_suitability)
        
        return zoning_info
    
    def render_dashboard(self):
        """Render the commercial real estate dashboard."""
        st.title("🏢 Commercial Real Estate Analysis")
        st.write("Specialized tools for analyzing commercial real estate opportunities in the Indian market.")
        
        tab1, tab2, tab3 = st.tabs(["🗺️ Business District Proximity", "👥 Foot Traffic Analysis", "📋 Zoning Analysis"])
        
        # Common location selection UI
        st.sidebar.header("Location Selection")
        
        # City selection
        cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
        selected_city = st.sidebar.selectbox("Select City", cities, key="commercial_city_select")
        
        # Get areas for selected city
        areas = []
        if selected_city and self.processed["listings_df"] is not None and not self.processed["listings_df"].empty:
            city_data = self.processed["listings_df"][self.processed["listings_df"]["city"] == selected_city]
            areas = sorted(city_data["area"].unique().tolist())
        
        if not areas and selected_city:
            # Default areas if data is missing
            default_areas = {
                "Mumbai": ["BKC", "Andheri East", "Worli", "Nariman Point", "Powai"],
                "Bangalore": ["Whitefield", "Electronic City", "MG Road", "Koramangala", "Indiranagar"],
                "Hyderabad": ["HITEC City", "Gachibowli", "Banjara Hills", "Jubilee Hills", "Madhapur"],
                "Pune": ["Hinjewadi", "Kharadi", "SB Road", "Kalyani Nagar", "Viman Nagar"],
                "Delhi-NCR": ["Connaught Place", "Cyber City Gurgaon", "Noida Expressway", "Aerocity", "Nehru Place"]
            }
            areas = default_areas.get(selected_city, [])
        
        selected_area = st.sidebar.selectbox("Select Area", areas, key="commercial_area_select") if areas else None
        
        if not selected_area:
            st.warning("Please select a city and area from the sidebar.")
            return
        
        # Tab 1: Business District Proximity
        with tab1:
            st.header("Business District Proximity Analysis")
            st.write("Analyze the location's proximity to key business districts in the city.")
            
            if st.button("Analyze Business District Proximity"):
                with st.spinner(f"Analyzing proximity to business districts in {selected_city}..."):
                    proximity_data = self.analyze_business_district_proximity(selected_city, selected_area)
                    
                    if proximity_data.get("is_synthetic"):
                        st.info("Note: Using generated sample data for demonstration purposes.")
                    
                    # Display overall score
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        score = proximity_data.get("overall_proximity_score", 0)
                        st.metric("Business District Proximity Score", f"{score}/10")
                        
                        # Interpretation
                        if score >= 7:
                            st.success("Excellent proximity to business districts")
                        elif score >= 5:
                            st.info("Good proximity to business districts")
                        elif score >= 3:
                            st.warning("Average proximity to business districts")
                        else:
                            st.error("Poor proximity to business districts")
                    
                    with col2:
                        try:
                            # Generate map with business districts
                            area_coords = self.location_analyzer.geocode_with_nominatim(
                                f"{selected_area}, {selected_city}, India"
                            )
                            
                            if area_coords:
                                # Create map
                                bd_map = folium.Map(location=[area_coords["lat"], area_coords["lng"]], 
                                                   zoom_start=12, tiles='OpenStreetMap')
                                
                                # Add marker for selected area
                                folium.Marker(
                                    location=[area_coords["lat"], area_coords["lng"]],
                                    popup=selected_area,
                                    tooltip=f"{selected_area} (Your Location)",
                                    icon=folium.Icon(color='red', icon='building')
                                ).add_to(bd_map)
                                
                                # Add markers for business districts
                                for district, data in proximity_data["proximity_scores"].items():
                                    # For synthetic data, add random offset from center
                                    if proximity_data.get("is_synthetic", False):
                                        import random
                                        lat_offset = random.uniform(-0.05, 0.05)
                                        lng_offset = random.uniform(-0.05, 0.05)
                                        
                                        # Scale offset based on distance
                                        distance_factor = data["distance_km"] / 20  # Normalize to 0-1 range for typical distances
                                        lat_offset *= distance_factor
                                        lng_offset *= distance_factor
                                        
                                        district_lat = area_coords["lat"] + lat_offset
                                        district_lng = area_coords["lng"] + lng_offset
                                    else:
                                        # If we had real coordinates, we would use them here
                                        # For now, use the same approach as synthetic data
                                        import random
                                        lat_offset = random.uniform(-0.05, 0.05)
                                        lng_offset = random.uniform(-0.05, 0.05)
                                        
                                        distance_factor = data["distance_km"] / 20
                                        lat_offset *= distance_factor
                                        lng_offset *= distance_factor
                                        
                                        district_lat = area_coords["lat"] + lat_offset
                                        district_lng = area_coords["lng"] + lng_offset
                                    
                                    # Add district marker
                                    folium.Marker(
                                        location=[district_lat, district_lng],
                                        popup=f"{district}<br>Distance: {data['distance_km']} km<br>Travel Time: {data['travel_time_mins']} mins",
                                        tooltip=district,
                                        icon=folium.Icon(color='blue', icon='briefcase')
                                    ).add_to(bd_map)
                                    
                                    # Add line connecting location to district
                                    folium.PolyLine(
                                        locations=[[area_coords["lat"], area_coords["lng"]], 
                                                [district_lat, district_lng]],
                                        color='gray',
                                        weight=2,
                                        opacity=0.7,
                                        dash_array='5'
                                    ).add_to(bd_map)
                                
                                # Display map
                                st_folium(bd_map, width=700, height=400)
                            else:
                                st.error("Unable to generate map for this location.")
                        except Exception as e:
                            st.error(f"Error generating map: {str(e)}")
                    
                    # Display proximity details
                    st.subheader("Business District Distances")
                    
                    # Create dataframe for display
                    district_data = []
                    for district, data in proximity_data["proximity_scores"].items():
                        district_data.append({
                            "Business District": district,
                            "Distance (km)": data["distance_km"],
                            "Travel Time (mins)": data["travel_time_mins"],
                            "Proximity Score": f"{data['proximity_score']:.1f}/10"
                        })
                    
                    # Sort by distance
                    district_df = pd.DataFrame(district_data).sort_values("Distance (km)")
                    st.dataframe(district_df, hide_index=True, use_container_width=True)
                    
                    # Create distance visualization
                    st.subheader("Distance Comparison")
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    
                    # Extract data for plotting
                    districts = district_df["Business District"].tolist()
                    distances = district_df["Distance (km)"].tolist()
                    
                    # Define colors based on distance
                    colors = ['#1e88e5' if d < 5 else '#ffb300' if d < 10 else '#e53935' for d in distances]
                    
                    # Plot horizontal bars
                    bars = ax.barh(districts, distances, color=colors)
                    
                    # Add value labels
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                               f"{width:.1f} km", va='center')
                    
                    ax.set_xlabel("Distance (km)")
                    ax.set_title("Distance to Key Business Districts")
                    ax.set_xlim(0, max(distances) * 1.2)  # Add some padding
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Commercial potential assessment
                    st.subheader("Commercial Potential Assessment")
                    
                    nearest_district = district_df.iloc[0]["Business District"]
                    nearest_dist = district_df.iloc[0]["Distance (km)"]
                    
                    if nearest_dist < 5:
                        st.success(f"✅ **High Commercial Potential**: {selected_area} is only {nearest_dist:.1f} km from {nearest_district}, making it an excellent location for commercial space. Proximity to multiple business districts creates strong demand for office and retail space.")
                    elif nearest_dist < 10:
                        st.info(f"ℹ️ **Good Commercial Potential**: {selected_area} is {nearest_dist:.1f} km from {nearest_district}, providing reasonable access to business activity. The location should be attractive to businesses that don't require immediate proximity to business districts.")
                    else:
                        st.warning(f"⚠️ **Limited Commercial Potential**: {selected_area} is {nearest_dist:.1f} km from {nearest_district}, which may limit its appeal as a primary commercial location. Consider local amenities and foot traffic as alternative value drivers.")
        
        # Tab 2: Foot Traffic Analysis
        with tab2:
            st.header("Foot Traffic Analysis")
            st.write("Analyze potential foot traffic based on nearby amenities and attractors.")
            
            if st.button("Analyze Foot Traffic Potential"):
                with st.spinner(f"Analyzing foot traffic in {selected_area}, {selected_city}..."):
                    traffic_data = self.analyze_foot_traffic(selected_city, selected_area)
                    
                    if traffic_data.get("is_synthetic"):
                        st.info("Note: Using generated sample data for demonstration purposes.")
                    
                    # Display foot traffic score
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        score = traffic_data.get("foot_traffic_score", 0)
                        
                        # Create score gauge
                        fig, ax = plt.subplots(figsize=(8, 2))
                        
                        # Configure gauge chart
                        gauge_colors = ['#FF6B6B', '#FFD166', '#06D6A0']
                        score_color = gauge_colors[0] if score < 40 else gauge_colors[1] if score < 70 else gauge_colors[2]
                        
                        # Draw gauge bar
                        ax.barh([0], [100], color='#e6e6e6', height=0.5)
                        ax.barh([0], [score], color=score_color, height=0.5)
                        
                        # Add score text
                        ax.text(score, 0, f'{score}/100', ha='center', va='center', 
                               color='black', fontweight='bold')
                        
                        # Configure gauge chart appearance
                        ax.set_xlim(0, 100)
                        ax.set_ylim(-0.5, 0.5)
                        ax.set_yticks([])
                        ax.set_xticks([0, 25, 50, 75, 100])
                        ax.set_xticklabels(['0', 'Low', 'Moderate', 'High', 'Excellent'])
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        ax.spines['left'].set_visible(False)
                        
                        plt.title("Foot Traffic Potential Score", pad=10)
                        st.pyplot(fig)
                        
                        # Interpretation
                        st.metric("Amenity Density", f"{traffic_data.get('amenity_density', 0)} per km²")
                        
                        if score >= 75:
                            st.success("Excellent foot traffic potential")
                        elif score >= 50:
                            st.info("Good foot traffic potential")
                        elif score >= 30:
                            st.warning("Moderate foot traffic potential")
                        else:
                            st.error("Low foot traffic potential")
                    
                    with col2:
                        st.subheader("Top Foot Traffic Generators")
                        
                        if traffic_data.get("traffic_generators"):
                            # Create pie chart of traffic generators
                            generators = traffic_data["traffic_generators"][:5]  # Top 5
                            
                            if generators:
                                labels = [g["type"].replace("_", " ").title() for g in generators]
                                sizes = [g["count"] for g in generators]
                                
                                fig2, ax2 = plt.subplots(figsize=(8, 5))
                                ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                                      colors=plt.cm.tab10(range(len(generators))))
                                ax2.axis('equal')
                                plt.title("Traffic Generators by Type")
                                st.pyplot(fig2)
                        else:
                            st.write("No significant foot traffic generators found.")
                    
                    # Display amenity counts
                    st.subheader("Amenity Distribution")
                    
                    # Group amenities by category
                    categories = {
                        "Food & Dining": ["restaurant", "cafe", "fast_food", "pub", "bar"],
                        "Shopping": ["supermarket", "mall", "marketplace", "department_store"],
                        "Services": ["bank", "atm", "post_office"],
                        "Entertainment": ["cinema", "theatre", "arts_centre", "tourist_attraction"],
                        "Transportation": ["bus_station", "subway_station", "train_station"]
                    }
                    
                    amenity_counts = traffic_data.get("amenity_counts", {})
                    
                    # Calculate totals by category
                    category_totals = {}
                    for category, amenities in categories.items():
                        total = sum(amenity_counts.get(amenity, 0) for amenity in amenities)
                        category_totals[category] = total
                    
                    # Create bar chart of categories
                    fig3, ax3 = plt.subplots(figsize=(10, 5))
                    
                    categories_list = list(category_totals.keys())
                    totals = list(category_totals.values())
                    
                    bars = ax3.bar(categories_list, totals, color=plt.cm.Paired(range(len(categories_list))))
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1, 
                               str(int(height)), ha='center', va='bottom')
                    
                    ax3.set_ylabel("Number of Amenities")
                    ax3.set_title("Amenities by Category")
                    
                    plt.tight_layout()
                    st.pyplot(fig3)
                    
                    # Detailed amenity counts
                    amenity_data = []
                    for amenity, count in amenity_counts.items():
                        # Find category
                        category = next((cat for cat, amenities in categories.items() if amenity in amenities), "Other")
                        
                        amenity_data.append({
                            "Amenity": amenity.replace("_", " ").title(),
                            "Category": category,
                            "Count": count
                        })
                    
                    # Sort by count
                    amenity_df = pd.DataFrame(amenity_data).sort_values("Count", ascending=False)
                    st.dataframe(amenity_df, hide_index=True, use_container_width=True)
                    
                    # Commercial recommendation
                    st.subheader("Commercial Recommendation")
                    
                    score = traffic_data.get("foot_traffic_score", 0)
                    if score >= 75:
                        st.success(f"✅ **High Commercial Value**: {selected_area} has excellent foot traffic potential with a score of {score}/100. This location would be suitable for high-visibility retail, restaurants, or consumer services. The area has {traffic_data.get('amenity_density', 0)} amenities per km², creating a strong commercial ecosystem.")
                    elif score >= 50:
                        st.info(f"ℹ️ **Good Commercial Value**: {selected_area} has good foot traffic potential with a score of {score}/100. This location would be suitable for neighborhood retail, professional services, or specialty shops. Consider businesses that complement the existing {category_totals.get('Food & Dining', 0)} food & dining establishments and {category_totals.get('Shopping', 0)} shopping venues.")
                    elif score >= 30:
                        st.warning(f"⚠️ **Moderate Commercial Value**: {selected_area} has moderate foot traffic potential with a score of {score}/100. This location may be better suited for destination businesses, offices, or services that don't rely heavily on walk-in traffic.")
                    else:
                        st.error(f"❌ **Limited Commercial Value**: {selected_area} has low foot traffic potential with a score of {score}/100. This location would be challenging for retail or consumer services. Consider office space, warehousing, or other uses that don't depend on foot traffic.")
        
        # Tab 3: Zoning Analysis
        with tab3:
            st.header("Zoning and Land Use Analysis")
            st.write("Analyze zoning regulations and land use permissions for commercial development.")
            
            if st.button("Analyze Zoning Regulations"):
                with st.spinner(f"Retrieving zoning information for {selected_area}, {selected_city}..."):
                    zoning_data = self.analyze_zoning(selected_city, selected_area)
                    
                    if zoning_data.get("is_synthetic"):
                        st.info("Note: Using generated sample data for demonstration purposes. For accurate zoning information, please consult local municipal records.")
                    
                    # Display zoning status
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Zoning Classification")
                        
                        zoning_type = zoning_data.get("zoning_type", "Unknown")
                        commercial_allowed = zoning_data.get("commercial_allowed", False)
                        
                        # Colorful box displaying zoning type
                        if zoning_type == "Commercial":
                            box_color = "#1e88e5"  # Blue
                        elif zoning_type == "Mixed-Use":
                            box_color = "#7cb342"  # Green
                        elif zoning_type == "Residential":
                            box_color = "#fb8c00"  # Orange
                        else:
                            box_color = "#757575"  # Gray
                            
                        st.markdown(f"""
                        <div style="background-color:{box_color}; padding:10px; border-radius:5px; color:white;">
                        <h3 style="margin:0;">{zoning_type}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Commercial status
                        if commercial_allowed:
                            st.success("✅ Commercial use is permitted")
                        else:
                            st.error("❌ Commercial use is NOT permitted")
                            
                        # FSI/FAR
                        st.metric("Maximum FSI/FAR", zoning_data.get("max_fsi", "Unknown"))
                    
                    with col2:
                        st.subheader("Commercial Suitability")
                        
                        # Create commercial suitability gauge
                        score = zoning_data.get("commercial_suitability_score", 0)
                        fig, ax = plt.subplots(figsize=(8, 2))
                        
                        # Configure gauge colors
                        gauge_colors = ['#FF6B6B', '#FFD166', '#06D6A0']
                        score_color = gauge_colors[0] if score < 40 else gauge_colors[1] if score < 70 else gauge_colors[2]
                        
                        # Draw gauge bar
                        ax.barh([0], [100], color='#e6e6e6', height=0.5)
                        ax.barh([0], [score], color=score_color, height=0.5)
                        
                        # Add score text
                        ax.text(score, 0, f'{score}/100', ha='center', va='center', 
                               color='black', fontweight='bold')
                        
                        # Configure gauge appearance
                        ax.set_xlim(0, 100)
                        ax.set_ylim(-0.5, 0.5)
                        ax.set_yticks([])
                        ax.set_xticks([0, 25, 50, 75, 100])
                        ax.set_xticklabels(['0', 'Poor', 'Average', 'Good', 'Excellent'])
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        ax.spines['left'].set_visible(False)
                        
                        plt.title("Commercial Development Suitability", pad=10)
                        st.pyplot(fig)
                        
                        # Interpretation
                        if score >= 75:
                            st.success("Excellent suitability for commercial development")
                        elif score >= 50:
                            st.info("Good suitability for commercial development")
                        elif score >= 30:
                            st.warning("Average suitability for commercial development")
                        else:
                            st.error("Poor suitability for commercial development")
                    
                    # Display zoning details
                    st.subheader("Zoning Details")
                    
                    zoning_details = zoning_data.get("zoning_details", {})
                    if zoning_details:
                        details_data = [{"Parameter": k, "Value": v} for k, v in zoning_details.items()]
                        details_df = pd.DataFrame(details_data)
                        st.dataframe(details_df, hide_index=True, use_container_width=True)
                    else:
                        st.write("No detailed zoning information available.")
                    
                    # Development recommendation
                    st.subheader("Development Recommendation")
                    
                    score = zoning_data.get("commercial_suitability_score", 0)
                    zoning_type = zoning_data.get("zoning_type", "Unknown")
                    commercial_allowed = zoning_data.get("commercial_allowed", False)
                    max_fsi = zoning_data.get("max_fsi", 0)
                    
                    if score >= 75:
                        st.success(f"""
                        ✅ **Recommended for Commercial Development**: {selected_area} has excellent zoning conditions for commercial real estate with a suitability score of {score}/100.
                        
                        **Optimal Uses**: 
                        - Office buildings
                        - Retail centers
                        - Mixed-use developments with ground floor commercial
                        
                        **Key Advantages**:
                        - {zoning_type} zoning with commercial explicitly permitted
                        - High FSI/FAR allowance of {max_fsi}
                        - Favorable development conditions
                        """)
                    elif score >= 50 and commercial_allowed:
                        st.info(f"""
                        ℹ️ **Suitable for Commercial Development**: {selected_area} has good zoning conditions for commercial real estate with a suitability score of {score}/100.
                        
                        **Suitable Uses**: 
                        - Small to medium office spaces
                        - Neighborhood retail
                        - Professional services
                        
                        **Considerations**:
                        - {zoning_type} zoning with commercial permitted
                        - Moderate FSI/FAR allowance of {max_fsi}
                        - May require careful planning to maximize value
                        """)
                    elif commercial_allowed:
                        st.warning(f"""
                        ⚠️ **Limited Commercial Development Potential**: {selected_area} has limited zoning conditions for commercial real estate with a suitability score of {score}/100.
                        
                        **Possible Uses**: 
                        - Home offices
                        - Small professional services
                        - Limited retail/commercial
                        
                        **Challenges**:
                        - {zoning_type} zoning with restrictions on commercial use
                        - Lower FSI/FAR allowance of {max_fsi}
                        - May require zoning variances or special permissions
                        """)
                    else:
                        st.error(f"""
                        ❌ **Not Recommended for Commercial Development**: {selected_area} is not suitable for commercial real estate with a suitability score of {score}/100.
                        
                        **Key Issues**:
                        - {zoning_type} zoning does not permit commercial use
                        - Would require rezoning or special use permits
                        - Consider alternative locations or residential investment instead
                        """)
                    
                    # Additional information for investors
                    with st.expander("Commercial Property Investment Considerations"):
                        st.write("""
                        ### Key Factors for Commercial Property Investment
                        
                        1. **Zoning Classification**: Always verify the actual zoning classification with municipal authorities before investment.
                        
                        2. **Development Controls**:
                           - Floor Space Index (FSI) / Floor Area Ratio (FAR)
                           - Building height restrictions
                           - Setback requirements
                           - Parking requirements
                        
                        3. **Change of Use Permits**: If considering converting from one use to another, research the permissions required.
                        
                        4. **Future Development Plans**: Check municipal development plans for upcoming changes to zoning or infrastructure.
                        
                        5. **Environmental Clearances**: Commercial properties may require additional environmental approvals.
                        
                        6. **Infrastructure Assessment**: Verify adequate water supply, electricity capacity, and sewage connections for commercial needs.
                        
                        7. **Fire Safety Compliance**: Commercial properties have stricter fire safety requirements than residential.
                        
                        > **Disclaimer:** This analysis provides an overview based on available data. Professional legal and zoning consultation is recommended before making investment decisions.
                        """)
                        