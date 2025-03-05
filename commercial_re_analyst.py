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
    
    def render_dashboard(self):
        """Render the commercial real estate dashboard."""
        st.title("🏢 Commercial Real Estate Analysis")
        st.write("Specialized tools for analyzing commercial real estate opportunities in the Indian market.")
        
        # Use a more mobile-friendly tab layout
        tab1, tab2, tab3 = st.tabs(["🗺️ Business Districts", "👥 Foot Traffic", "📋 Zoning"])
        
        # Common location selection UI
        st.sidebar.header("Location Selection")
        
        # City selection
        cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
        selected_city = st.sidebar.selectbox("Select City", cities, key="commercial_city_select")
        
        # Default areas for each city
        default_areas = {
            "Mumbai": ["BKC", "Andheri East", "Worli", "Nariman Point", "Powai"],
            "Bangalore": ["Whitefield", "Electronic City", "MG Road", "Koramangala", "Indiranagar"],
            "Hyderabad": ["HITEC City", "Gachibowli", "Banjara Hills", "Jubilee Hills", "Madhapur"],
            "Pune": ["Hinjewadi", "Kharadi", "SB Road", "Kalyani Nagar", "Viman Nagar"],
            "Delhi-NCR": ["Connaught Place", "Cyber City Gurgaon", "Noida Expressway", "Aerocity", "Nehru Place"]
        }
        
        # Get areas for selected city
        areas = default_areas.get(selected_city, [])
        selected_area = st.sidebar.selectbox("Select Area", areas, key="commercial_area_select") if areas else None
        
        if not selected_area:
            st.warning("Please select a city and area from the sidebar.")
            return
        
        # Tab 1: Business District Proximity Analysis
        with tab1:
            st.header("Business District Proximity Analysis")
            st.write("Analyze the location's proximity to key business districts in the city.")
            
            # Display example note
            st.info("Showing example data for demonstration purposes.")
            
            # Create example data for business district proximity
            districts = default_areas.get(selected_city, [])[:3]  # Take up to 3 districts
            distances = [round(np.random.uniform(2, 15), 1) for _ in range(len(districts))]
            travel_times = [round(d * 3, 1) for d in distances]  # Assume 20 km/h average speed
            proximity_scores = [max(0, round(10 - (d / 2), 1)) for d in distances]
            
            # Display overall score - average of individual scores
            overall_score = round(sum(proximity_scores) / len(proximity_scores), 1) if proximity_scores else 0
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Business District Proximity Score", f"{overall_score}/10")
                
                # Interpretation
                if overall_score >= 7:
                    st.success("Excellent proximity to business districts")
                elif overall_score >= 5:
                    st.info("Good proximity to business districts")
                elif overall_score >= 3:
                    st.warning("Average proximity to business districts")
                else:
                    st.error("Poor proximity to business districts")
            
            with col2:
                # Create a simple map
                m = folium.Map(location=[19.076, 72.8777], zoom_start=12)  # Default to Mumbai
                
                # Add marker for selected area
                folium.Marker(
                    location=[19.076, 72.8777],
                    popup=selected_area,
                    tooltip=selected_area,
                    icon=folium.Icon(color='red', icon='building')
                ).add_to(m)
                
                # Add markers for business districts
                for i, district in enumerate(districts):
                    # Add some random offset to create visual separation
                    lat_offset = np.random.uniform(-0.02, 0.02)
                    lng_offset = np.random.uniform(-0.02, 0.02)
                    
                    folium.Marker(
                        location=[19.076 + lat_offset, 72.8777 + lng_offset],
                        popup=district,
                        tooltip=district,
                        icon=folium.Icon(color='blue', icon='briefcase')
                    ).add_to(m)
                
                # Display map
                st_folium(m, width="100%", height=300)
            
            # Display proximity details
            st.subheader("Business District Distances")
            
            # Create dataframe for display
            data = {
                "Business District": districts,
                "Distance (km)": distances,
                "Travel Time (mins)": travel_times,
                "Proximity Score": [f"{score}/10" for score in proximity_scores]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, hide_index=True, use_container_width=True)
            
            # Create a simple bar chart
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = ['#1e88e5' if d < 5 else '#ffb300' if d < 10 else '#e53935' for d in distances]
            bars = ax.barh(districts, distances, color=colors)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                       f"{width:.1f} km", va='center')
            
            ax.set_xlabel("Distance (km)")
            ax.set_title("Distance to Key Business Districts")
            plt.tight_layout()
            st.pyplot(fig)
            
            # Commercial potential assessment
            st.subheader("Commercial Potential Assessment")
            
            nearest_district = districts[distances.index(min(distances))]
            nearest_dist = min(distances)
            
            if nearest_dist < 5:
                st.success(f"✅ **High Commercial Potential**: {selected_area} is only {nearest_dist:.1f} km from {nearest_district}, making it an excellent location for commercial space.")
            elif nearest_dist < 10:
                st.info(f"ℹ️ **Good Commercial Potential**: {selected_area} is {nearest_dist:.1f} km from {nearest_district}, providing reasonable access to business activity.")
            else:
                st.warning(f"⚠️ **Limited Commercial Potential**: {selected_area} is {nearest_dist:.1f} km from {nearest_district}, which may limit its appeal as a primary commercial location.")
        
        # Tab 2: Foot Traffic Analysis
        with tab2:
            st.header("Foot Traffic Analysis")
            st.write("Analyze potential foot traffic based on nearby amenities and attractors.")
            
            # Display example note
            st.info("Showing example data for demonstration purposes.")
            
            # Create example foot traffic data
            foot_traffic_score = np.random.randint(30, 90)
            amenity_density = round(np.random.uniform(10, 50), 1)
            
            # Create example amenity data
            amenity_categories = {
                "Food & Dining": np.random.randint(5, 20),
                "Shopping": np.random.randint(3, 15),
                "Services": np.random.randint(2, 10),
                "Entertainment": np.random.randint(1, 5),
                "Transportation": np.random.randint(1, 3)
            }
            
            # Display foot traffic score
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Create score display
                fig, ax = plt.subplots(figsize=(8, 2))
                
                # Configure gauge colors
                score_color = '#FF6B6B' if foot_traffic_score < 40 else '#FFD166' if foot_traffic_score < 70 else '#06D6A0'
                
                # Draw gauge bar
                ax.barh([0], [100], color='#e6e6e6', height=0.5)
                ax.barh([0], [foot_traffic_score], color=score_color, height=0.5)
                
                # Add score text
                ax.text(foot_traffic_score, 0, f'{foot_traffic_score}/100', ha='center', va='center', 
                       color='black', fontweight='bold')
                
                # Configure gauge appearance
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
                
                # Display density metric
                st.metric("Amenity Density", f"{amenity_density} per km²")
                
                # Interpretation
                if foot_traffic_score >= 75:
                    st.success("Excellent foot traffic potential")
                elif foot_traffic_score >= 50:
                    st.info("Good foot traffic potential")
                elif foot_traffic_score >= 30:
                    st.warning("Moderate foot traffic potential")
                else:
                    st.error("Low foot traffic potential")
            
            with col2:
                # Create pie chart of traffic generators
                labels = list(amenity_categories.keys())
                sizes = list(amenity_categories.values())
                
                fig2, ax2 = plt.subplots(figsize=(8, 8))
                ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                      colors=plt.cm.tab10(range(len(labels))))
                ax2.axis('equal')
                plt.title("Amenities by Category")
                st.pyplot(fig2)
            
            # Display amenity breakdown
            st.subheader("Amenity Distribution")
            
            # Create bar chart
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            
            categories = list(amenity_categories.keys())
            counts = list(amenity_categories.values())
            
            bars = ax3.bar(categories, counts, color=plt.cm.Paired(range(len(categories))))
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1, 
                       str(int(height)), ha='center', va='bottom')
            
            ax3.set_ylabel("Number of Amenities")
            ax3.set_title("Amenities by Category")
            
            plt.tight_layout()
            st.pyplot(fig3)
            
            # Commercial recommendation
            st.subheader("Commercial Recommendation")
            
            if foot_traffic_score >= 75:
                st.success(f"✅ **High Commercial Value**: {selected_area} has excellent foot traffic potential with a score of {foot_traffic_score}/100. This location would be suitable for high-visibility retail, restaurants, or consumer services.")
            elif foot_traffic_score >= 50:
                st.info(f"ℹ️ **Good Commercial Value**: {selected_area} has good foot traffic potential with a score of {foot_traffic_score}/100. This location would be suitable for neighborhood retail, professional services, or specialty shops.")
            elif foot_traffic_score >= 30:
                st.warning(f"⚠️ **Moderate Commercial Value**: {selected_area} has moderate foot traffic potential with a score of {foot_traffic_score}/100. This location may be better suited for destination businesses or offices.")
            else:
                st.error(f"❌ **Limited Commercial Value**: {selected_area} has low foot traffic potential with a score of {foot_traffic_score}/100. This location would be challenging for retail or consumer services.")
        
        # Tab 3: Zoning Analysis
        with tab3:
            st.header("Zoning and Land Use Analysis")
            st.write("Analyze zoning regulations and land use permissions for commercial development.")
            
            # Display example note
            st.info("Showing example zoning data for demonstration purposes. For accurate information, please consult local municipal records.")
            
            # Create example zoning data
            zoning_types = ["Commercial", "Mixed-Use", "Residential"]
            weights = [0.4, 0.4, 0.2]
            zoning_type = np.random.choice(zoning_types, p=weights)
            
            commercial_allowed = True if zoning_type in ["Commercial", "Mixed-Use"] else np.random.choice([True, False], p=[0.3, 0.7])
            max_fsi = round(np.random.uniform(1.5, 4.0), 1)
            
            # Calculate commercial suitability score
            if zoning_type == "Commercial":
                suitability_score = 90
            elif zoning_type == "Mixed-Use" and commercial_allowed:
                suitability_score = 70
            elif commercial_allowed:
                suitability_score = 40
            else:
                suitability_score = 10
                
            # Adjust based on FSI
            if max_fsi > 3.0:
                suitability_score += 10
            elif max_fsi < 2.0:
                suitability_score -= 10
                
            # Cap at 100
            suitability_score = min(100, suitability_score)
            
            # Display zoning status
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Zoning Classification")
                
                # Colorful box displaying zoning type
                if zoning_type == "Commercial":
                    box_color = "#1e88e5"  # Blue
                elif zoning_type == "Mixed-Use":
                    box_color = "#7cb342"  # Green
                else:
                    box_color = "#fb8c00"  # Orange
                    
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
                st.metric("Maximum FSI/FAR", max_fsi)
            
            with col2:
                st.subheader("Commercial Suitability")
                
                # Create gauge chart for suitability score
                fig, ax = plt.subplots(figsize=(8, 2))
                
                # Configure gauge colors
                score_color = '#FF6B6B' if suitability_score < 40 else '#FFD166' if suitability_score < 70 else '#06D6A0'
                
                # Draw gauge bar
                ax.barh([0], [100], color='#e6e6e6', height=0.5)
                ax.barh([0], [suitability_score], color=score_color, height=0.5)
                
                # Add score text
                ax.text(suitability_score, 0, f'{suitability_score}/100', ha='center', va='center', 
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
                if suitability_score >= 75:
                    st.success("Excellent suitability for commercial development")
                elif suitability_score >= 50:
                    st.info("Good suitability for commercial development")
                elif suitability_score >= 30:
                    st.warning("Average suitability for commercial development")
                else:
                    st.error("Poor suitability for commercial development")
            
            # Display zoning details
            st.subheader("Zoning Details")
            
            # Example zoning details
            zoning_details = {
                "Height Restriction (meters)": int(np.random.uniform(15, 45)),
                "Parking Requirement": f"{np.random.randint(1, 3)} per {np.random.randint(50, 100)} sq.m",
                "Setback Required (meters)": round(np.random.uniform(3, 8), 1)
            }
            
            # Display as table
            details_data = [{"Parameter": k, "Value": v} for k, v in zoning_details.items()]
            details_df = pd.DataFrame(details_data)
            st.dataframe(details_df, hide_index=True, use_container_width=True)
            
            # Development recommendation
            st.subheader("Development Recommendation")
            
            if suitability_score >= 75:
                st.success(f"""
                ✅ **Recommended for Commercial Development**: {selected_area} has excellent zoning conditions for commercial real estate with a suitability score of {suitability_score}/100.
                
                **Optimal Uses**: 
                - Office buildings
                - Retail centers
                - Mixed-use developments with ground floor commercial
                
                **Key Advantages**:
                - {zoning_type} zoning with commercial explicitly permitted
                - High FSI/FAR allowance of {max_fsi}
                - Favorable development conditions
                """)
            elif suitability_score >= 50 and commercial_allowed:
                st.info(f"""
                ℹ️ **Suitable for Commercial Development**: {selected_area} has good zoning conditions for commercial real estate with a suitability score of {suitability_score}/100.
                
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
                ⚠️ **Limited Commercial Development Potential**: {selected_area} has limited zoning conditions for commercial real estate with a suitability score of {suitability_score}/100.
                
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
                ❌ **Not Recommended for Commercial Development**: {selected_area} is not suitable for commercial real estate with a suitability score of {suitability_score}/100.
                
                **Key Issues**:
                - {zoning_type} zoning does not permit commercial use
                - Would require rezoning or special use permits
                - Consider alternative locations or residential investment instead
                """)
