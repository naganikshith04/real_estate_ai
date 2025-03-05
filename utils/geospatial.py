"""
Geospatial utilities for Real Estate AI
Provides map generation, distance calculations, and location scoring
"""

import folium
import numpy as np
from typing import List, Dict, Any, Tuple
from config import logger

def create_city_map(city_name: str, areas: List[Dict[str, Any]]) -> folium.Map:
    """
    Create a folium map for a city with areas marked
    
    Args:
        city_name: Name of the city
        areas: List of area dictionaries with lat/lng coordinates
        
    Returns:
        folium.Map: Interactive map object
    """
    logger.info(f"Creating map for {city_name} with {len(areas)} areas")
    
    # Default center coordinates by city
    city_centers = {
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Hyderabad": (17.3850, 78.4867),
        "Pune": (18.5204, 73.8567),
        "Delhi-NCR": (28.7041, 77.1025)
    }
    
    # Get city center, default to center of India
    center = city_centers.get(city_name, (20.5937, 78.9629))
    
    # Create map
    city_map = folium.Map(
        location=center,
        zoom_start=11,
        tiles='CartoDB positron'  # Use a clean map style
    )
    
    # Add a title
    title_html = f'''
         <h3 align="center" style="font-size:16px"><b>{city_name} - Real Estate Investment Areas</b></h3>
         '''
    city_map.get_root().html.add_child(folium.Element(title_html))
    
    # Add areas to map
    for area in areas:
        # Skip if missing coordinates
        if 'latitude' not in area or 'longitude' not in area:
            continue
        
        # Get ROI for color (default to 0 if not present)
        roi = area.get('roi', 0)
        
        # Calculate color based on ROI (green = high, yellow = medium, red = low)
        if roi >= 30:
            color = 'green'
            fill_color = '#76b852'
        elif roi >= 20:
            color = 'orange'
            fill_color = '#f9a825'
        else:
            color = 'red'
            fill_color = '#e53935'
            
        # Create popup with area details
        popup_html = f"""
        <div style="width:200px">
            <h4>{area.get('name', 'Area')}</h4>
            <p><b>5-Year ROI:</b> {roi:.1f}%</p>
            <p><b>Avg Price:</b> ₹{area.get('price_per_sqft', 0):,.0f}/sqft</p>
            <p><b>Risk Score:</b> {area.get('risk_score', 5)}/10</p>
        </div>
        """
        
        # Add marker
        folium.CircleMarker(
            location=(area['latitude'], area['longitude']),
            radius=8,
            color=color,
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=area.get('name', 'Area')
        ).add_to(city_map)
    
    return city_map

def create_heatmap(city_name: str, areas: List[Dict[str, Any]], value_field: str = 'roi') -> folium.Map:
    """
    Create a heatmap for a city based on a value field
    
    Args:
        city_name: Name of the city
        areas: List of area dictionaries with lat/lng coordinates
        value_field: Field to use for heatmap intensity
        
    Returns:
        folium.Map: Interactive map with heatmap
    """
    from folium.plugins import HeatMap
    
    logger.info(f"Creating heatmap for {city_name} with {len(areas)} areas")
    
    # Default center coordinates by city
    city_centers = {
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Hyderabad": (17.3850, 78.4867),
        "Pune": (18.5204, 73.8567),
        "Delhi-NCR": (28.7041, 77.1025)
    }
    
    # Get city center, default to center of India
    center = city_centers.get(city_name, (20.5937, 78.9629))
    
    # Create map
    city_map = folium.Map(
        location=center,
        zoom_start=11,
        tiles='CartoDB dark_matter'  # Dark background for heatmap
    )
    
    # Add a title
    title_html = f'''
         <h3 align="center" style="font-size:16px; color:white;"><b>{city_name} - {value_field.upper()} Heatmap</b></h3>
         '''
    city_map.get_root().html.add_child(folium.Element(title_html))
    
    # Prepare heatmap data
    heatmap_data = []
    for area in areas:
        # Skip if missing coordinates or value
        if 'latitude' not in area or 'longitude' not in area or value_field not in area:
            continue
            
        # Add data point [lat, lng, intensity]
        heatmap_data.append([area['latitude'], area['longitude'], area[value_field]])
    
    # Add heatmap layer
    HeatMap(heatmap_data, radius=15, gradient={0.2: 'blue', 0.5: 'lime', 0.8: 'yellow', 1.0: 'red'}).add_to(city_map)
    
    return city_map

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the Earth's surface
    using the Haversine formula
    
    Args:
        lat1: Latitude of point 1 in degrees
        lon1: Longitude of point 1 in degrees
        lat2: Latitude of point 2 in degrees
        lon2: Longitude of point 2 in degrees
        
    Returns:
        float: Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c
    
    return distance

def create_property_clusters(properties: List[Dict[str, Any]], max_distance_km: float = 2.0) -> List[List[Dict[str, Any]]]:
    """
    Group nearby properties into clusters
    
    Args:
        properties: List of property dictionaries with lat/lng coordinates
        max_distance_km: Maximum distance between properties in a cluster
        
    Returns:
        List of property clusters
    """
    # Filter properties with coordinates
    valid_properties = [p for p in properties if 'latitude' in p and 'longitude' in p]
    
    if not valid_properties:
        return []
        
    # Initialize clusters
    clusters = []
    unclustered = valid_properties.copy()
    
    while unclustered:
        # Start a new cluster with the first property
        current_cluster = [unclustered.pop(0)]
        
        # Find all properties within max_distance of any property in the cluster
        i = 0
        while i < len(unclustered):
            for cluster_property in current_cluster:
                distance = calculate_haversine_distance(
                    cluster_property['latitude'], cluster_property['longitude'],
                    unclustered[i]['latitude'], unclustered[i]['longitude']
                )
                
                if distance <= max_distance_km:
                    # Add to cluster and remove from unclustered
                    current_cluster.append(unclustered.pop(i))
                    i -= 1  # Adjust index after removal
                    break
            i += 1
            
        # Add the completed cluster
        clusters.append(current_cluster)
        
    return clusters