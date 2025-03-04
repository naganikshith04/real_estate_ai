import os
import json
import requests
import folium
import time
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LocationAnalyzer:
    """
    Integration with OpenStreetMap and other free location-based services for real estate analysis.
    Provides geospatial analysis of real estate areas.
    """
    
    def __init__(self):
        """Initialize the location analyzer with OpenStreetMap services"""
        # Define the Nominatim API endpoint (for geocoding)
        self.nominatim_endpoint = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "real_estate_ai/1.0"  # Required for Nominatim API
        
        # Default coordinates for Indian cities
        self.city_coordinates = {
            "Mumbai": {"lat": 19.0760, "lng": 72.8777},
            "Bangalore": {"lat": 12.9716, "lng": 77.5946},
            "Hyderabad": {"lat": 17.3850, "lng": 78.4867},
            "Pune": {"lat": 18.5204, "lng": 73.8567},
            "Delhi-NCR": {"lat": 28.7041, "lng": 77.1025}
        }
        
        # POI data for cities (to avoid too many API calls)
        self.poi_cache = {}
        
    def has_api_key(self):
        """Compatibility method - always returns True since we're using free services"""
        return True
        
    def geocode_with_nominatim(self, query):
        """
        Use OpenStreetMap's Nominatim service to geocode an address
        
        Args:
            query (str): The address or location to geocode
            
        Returns:
            dict: Latitude and longitude, or None if not found
        """
        try:
            # Build the Nominatim API query
            params = {
                "q": query,
                "format": "json",
                "limit": 1
            }
            
            # Add user agent (required by Nominatim's ToS)
            headers = {"User-Agent": self.user_agent}
            
            # Make the request
            response = requests.get(self.nominatim_endpoint, params=params, headers=headers)
            
            # Respect Nominatim's usage policy (1 request per second)
            time.sleep(1)
            
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    return {
                        "lat": float(results[0]["lat"]), 
                        "lng": float(results[0]["lon"])
                    }
            
            return None
        except Exception as e:
            print(f"Error in geocoding: {str(e)}")
            return None
    
    def generate_area_map(self, city, areas):
        """
        Generate a map for a city showing various areas of interest using OpenStreetMap
        
        Args:
            city (str): City name
            areas (list): List of area names in the city
            
        Returns:
            folium.Map: Interactive map object
        """
        # Get city coordinates
        city_coord = self.city_coordinates.get(city, {"lat": 20.5937, "lng": 78.9629})  # Default to India center
        
        # Create map centered on city using OpenStreetMap
        city_map = folium.Map(location=[city_coord["lat"], city_coord["lng"]], 
                             zoom_start=11, 
                             tiles='OpenStreetMap')
        
        # Add a title
        title_html = f'''
             <h3 align="center" style="font-size:16px"><b>{city} - Real Estate Analysis Areas</b></h3>
             '''
        city_map.get_root().html.add_child(folium.Element(title_html))
        
        # Try to geocode each area with Nominatim
        for area in areas:
            try:
                # First check if we've already geocoded this area
                cache_key = f"{area}_{city}_India"
                
                if cache_key in self.poi_cache:
                    # Use cached coordinates
                    location = self.poi_cache[cache_key]
                else:
                    # Geocode the area within the city
                    location = self.geocode_with_nominatim(f"{area}, {city}, India")
                    
                    # Cache the result if found
                    if location:
                        self.poi_cache[cache_key] = location
                
                if location:
                    # Add marker to map
                    folium.Marker(
                        location=[location["lat"], location["lng"]],
                        popup=area,
                        tooltip=area,
                        icon=folium.Icon(color='blue', icon='home')
                    ).add_to(city_map)
                else:
                    # If geocoding fails, place marker with random offset from city center
                    import random
                    lat_offset = random.uniform(-0.05, 0.05)
                    lng_offset = random.uniform(-0.05, 0.05)
                    
                    folium.Marker(
                        location=[city_coord["lat"] + lat_offset, city_coord["lng"] + lng_offset],
                        popup=f"{area} (approximate location)",
                        tooltip=area,
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(city_map)
            except Exception as e:
                print(f"Error adding marker for {area} in {city}: {str(e)}")
                
        # Add scale control
        folium.LayerControl().add_to(city_map)
                
        return city_map
    
    def fetch_osm_distance(self, origin, destination):
        """
        Use the OSRM API to get distance and time between two locations
        
        Args:
            origin (dict): Origin coordinates (lat, lng)
            destination (dict): Destination coordinates (lat, lng)
            
        Returns:
            dict: Distance and duration information
        """
        try:
            # Use the OSRM public API for routing
            osrm_endpoint = "https://router.project-osrm.org/route/v1/driving"
            
            # Format coordinates as required by OSRM
            coords = f"{origin['lng']},{origin['lat']};{destination['lng']},{destination['lat']}"
            url = f"{osrm_endpoint}/{coords}"
            
            # Make the request
            response = requests.get(url)
            
            # Respect rate limits
            time.sleep(1)
            
            if response.status_code == 200:
                data = response.json()
                if data["code"] == "Ok" and len(data["routes"]) > 0:
                    # Get the distance (in meters) and duration (in seconds)
                    route = data["routes"][0]
                    distance_km = route["distance"] / 1000  # Convert to km
                    duration_mins = route["duration"] / 60  # Convert to minutes
                    
                    return {
                        "distance_km": round(distance_km, 1),
                        "time_mins": round(duration_mins, 1)
                    }
            
            # Fall back to approximate calculation if OSRM fails
            import math
            # Calculate rough distance using Haversine formula
            R = 6371  # Earth radius in km
            lat1, lon1 = math.radians(origin["lat"]), math.radians(origin["lng"])
            lat2, lon2 = math.radians(destination["lat"]), math.radians(destination["lng"])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            # Assume average speed of 20 km/h in Indian cities
            duration = distance / 20 * 60  # Convert to minutes
            
            return {
                "distance_km": round(distance, 1),
                "time_mins": round(duration, 1),
                "estimated": True
            }
            
        except Exception as e:
            print(f"Error calculating distance: {str(e)}")
            return None
    
    def analyze_commute_times(self, city, area, destination_type="business_district"):
        """
        Analyze commute times from an area to key locations using OpenStreetMap's OSRM
        
        Args:
            city (str): City name
            area (str): Area name
            destination_type (str): Type of destination (business_district, tech_park, etc.)
            
        Returns:
            dict: Commute time information
        """
        results = {
            "city": city,
            "area": area,
            "commute_times": {},
            "avg_commute_time": None
        }
        
        # Define key destinations based on city
        destinations = {}
        
        if city == "Mumbai":
            destinations = {
                "business_district": ["Nariman Point", "BKC", "Worli"],
                "airport": ["Mumbai International Airport"]
            }
        elif city == "Bangalore":
            destinations = {
                "business_district": ["MG Road", "UB City"],
                "tech_park": ["Electronic City", "Whitefield", "Manyata Tech Park"]
            }
        elif city == "Hyderabad":
            destinations = {
                "business_district": ["Banjara Hills"],
                "tech_park": ["HITEC City", "Gachibowli"]
            }
        elif city == "Pune":
            destinations = {
                "business_district": ["Koregaon Park", "Camp"],
                "tech_park": ["Hinjewadi", "Magarpatta"]
            }
        elif city == "Delhi-NCR":
            destinations = {
                "business_district": ["Connaught Place", "Nehru Place"],
                "airport": ["Indira Gandhi International Airport"]
            }
        else:
            # Default destinations for other cities
            destinations = {
                "business_district": ["Central Business District", "Downtown"],
                "tech_park": ["IT Park", "Tech Hub"],
                "shopping_mall": ["City Mall", "Shopping Center"],
                "airport": ["International Airport"]
            }
        
        # Try to geocode the origin (area)
        origin_coords = self.geocode_with_nominatim(f"{area}, {city}, India")
        
        # If we can't geocode the origin, fall back to synthetic data
        if not origin_coords:
            return self.generate_synthetic_commute_data(city, area)
        
        commute_times = []
        
        for dest_category, locations in destinations.items():
            for dest in locations:
                try:
                    # Check if we have this destination in cache
                    dest_key = f"{dest}_{city}_India"
                    
                    if dest_key in self.poi_cache:
                        dest_coords = self.poi_cache[dest_key]
                    else:
                        # Geocode the destination
                        dest_coords = self.geocode_with_nominatim(f"{dest}, {city}, India")
                        
                        # Cache the result if found
                        if dest_coords:
                            self.poi_cache[dest_key] = dest_coords
                    
                    # If we have coordinates for both origin and destination, calculate distance and time
                    if dest_coords:
                        route_info = self.fetch_osm_distance(origin_coords, dest_coords)
                        
                        if route_info:
                            results["commute_times"][f"{dest} ({dest_category})"] = {
                                "distance_km": route_info["distance_km"],
                                "time_mins": route_info["time_mins"],
                                "estimated": route_info.get("estimated", False),
                                "mode": "driving"
                            }
                            
                            commute_times.append(route_info["time_mins"])
                except Exception as e:
                    print(f"Error calculating commute to {dest}: {str(e)}")
            
        # If we couldn't calculate any real commute times, fall back to synthetic data
        if not commute_times:
            return self.generate_synthetic_commute_data(city, area)
        
        # Calculate average commute time
        if commute_times:
            results["avg_commute_time"] = round(sum(commute_times) / len(commute_times), 1)
        
        return results
    
    def generate_synthetic_commute_data(self, city, area):
        """
        Generate synthetic commute data when real data cannot be retrieved
        
        Args:
            city (str): City name
            area (str): Area name
            
        Returns:
            dict: Synthetic commute time information
        """
        results = {
            "city": city,
            "area": area,
            "commute_times": {},
            "avg_commute_time": None,
            "is_synthetic": True
        }
        
        destinations = {
            "business_district": ["Central Business District", "Downtown", "Financial Center"],
            "tech_park": ["IT Park", "Tech Hub", "Software Technology Park"],
            "shopping_mall": ["City Mall", "Shopping Center", "Main Market"],
            "airport": ["International Airport", "Domestic Airport"]
        }
        
        commute_times = []
        for dest_category, locations in destinations.items():
            for dest in locations:
                # Generate random commute times based on city and area
                base_time = np.random.randint(15, 60)  # Base commute time between 15-60 minutes
                
                # Adjust based on city (Mumbai/Delhi typically have higher commute times)
                if city in ["Mumbai", "Delhi-NCR"]:
                    base_time += np.random.randint(10, 30)
                    
                results["commute_times"][f"{dest} ({dest_category})"] = {
                    "distance_km": round(base_time/3 * np.random.uniform(0.8, 1.2), 1),  # ~20km/hr average speed in Indian cities
                    "time_mins": base_time,
                    "mode": np.random.choice(["driving", "transit"]),
                    "estimated": True
                }
                commute_times.append(base_time)
        
        # Calculate average commute time
        if commute_times:
            results["avg_commute_time"] = round(sum(commute_times) / len(commute_times), 1)
            
        return results
    
    def query_osm_amenities(self, lat, lng, amenity_type, radius=2000):
        """
        Query OpenStreetMap Overpass API for amenities near a location
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            amenity_type (str): Type of amenity to search for
            radius (int): Search radius in meters
            
        Returns:
            list: List of amenities found
        """
        try:
            # Use Overpass API to query for amenities
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Convert OSM amenity types
            osm_type_mapping = {
                "school": "amenity=school",
                "hospital": "amenity=hospital",
                "restaurant": "amenity=restaurant",
                "shopping_mall": "shop=mall",
                "supermarket": "shop=supermarket",
                "bank": "amenity=bank",
                "park": "leisure=park",
                "gym": "leisure=fitness_centre"
            }
            
            # Get OSM search query
            osm_type = osm_type_mapping.get(amenity_type, f"amenity={amenity_type}")
            
            # Build the Overpass query
            overpass_query = f"""
            [out:json];
            (
              node[{osm_type}](around:{radius},{lat},{lng});
              way[{osm_type}](around:{radius},{lat},{lng});
              relation[{osm_type}](around:{radius},{lat},{lng});
            );
            out center;
            """
            
            # Make the request
            response = requests.post(overpass_url, data={"data": overpass_query})
            
            # Respect rate limits
            time.sleep(2)
            
            if response.status_code == 200:
                data = response.json()
                
                if "elements" in data:
                    # Extract amenity information
                    amenities = []
                    
                    for element in data["elements"]:
                        name = element.get("tags", {}).get("name", f"{amenity_type.title()}")
                        if name:
                            amenities.append({"name": name})
                    
                    return amenities
            
            return []
            
        except Exception as e:
            print(f"Error querying OSM for amenities: {str(e)}")
            return []
    
    def analyze_nearby_amenities(self, city, area):
        """
        Analyze amenities near a specific area using OpenStreetMap
        
        Args:
            city (str): City name
            area (str): Area name
            
        Returns:
            dict: Information about nearby amenities
        """
        results = {
            "city": city,
            "area": area,
            "amenities": {},
            "amenity_scores": {}
        }
        
        # List of amenity types to check
        amenity_types = [
            "school", "hospital", "restaurant", "shopping_mall", 
            "park", "gym", "supermarket", "bank"
        ]
        
        # Try to geocode the area
        area_coords = self.geocode_with_nominatim(f"{area}, {city}, India")
        
        # If we can't geocode the area, fall back to synthetic data
        if not area_coords:
            return self.generate_synthetic_amenity_data(city, area, amenity_types)
        
        found_real_data = False
        
        # Search for amenities using OpenStreetMap Overpass API
        for amenity in amenity_types:
            try:
                # Query for amenities
                amenities = self.query_osm_amenities(
                    area_coords["lat"], 
                    area_coords["lng"], 
                    amenity
                )
                
                if amenities:
                    count = len(amenities)
                    names = [item["name"] for item in amenities[:5]]  # List up to 5 examples
                    
                    results["amenities"][amenity] = {
                        "count": count,
                        "names": names
                    }
                    
                    # Generate a score based on count (0-10 scale)
                    base_score = min(10, count * 0.5)  # Adjusted for real data
                    results["amenity_scores"][amenity] = round(base_score, 1)
                    
                    found_real_data = True
                else:
                    # If no amenities found, use placeholder
                    results["amenities"][amenity] = {
                        "count": 0,
                        "names": []
                    }
                    results["amenity_scores"][amenity] = 0
                
            except Exception as e:
                print(f"Error searching for {amenity} in {area}: {str(e)}")
                # Skip this amenity type
        
        # If we couldn't find any real data, fall back to synthetic data
        if not found_real_data:
            return self.generate_synthetic_amenity_data(city, area, amenity_types)
        
        # Calculate overall amenity score
        if results["amenity_scores"]:
            results["overall_amenity_score"] = round(
                sum(results["amenity_scores"].values()) / len(results["amenity_scores"]), 1
            )
        
        return results
        
    def generate_synthetic_amenity_data(self, city, area, amenity_types):
        """
        Generate synthetic amenity data when real data cannot be retrieved
        
        Args:
            city (str): City name
            area (str): Area name
            amenity_types (list): Types of amenities to generate data for
            
        Returns:
            dict: Synthetic amenity information
        """
        results = {
            "city": city,
            "area": area,
            "amenities": {},
            "amenity_scores": {},
            "is_synthetic": True
        }
        
        for amenity in amenity_types:
            # Random number of each amenity type (more in bigger cities)
            count_multiplier = 1.5 if city in ["Mumbai", "Delhi-NCR", "Bangalore"] else 1.0
            count = int(np.random.randint(1, 10) * count_multiplier)
            
            results["amenities"][amenity] = {
                "count": count,
                "names": [f"{amenity.title()} {i+1}" for i in range(min(count, 5))]  # List up to 5 examples
            }
            
            # Generate a score based on count (0-10 scale)
            base_score = min(10, count * 1.2)
            results["amenity_scores"][amenity] = round(base_score, 1)
        
        # Calculate overall amenity score
        results["overall_amenity_score"] = round(
            sum(results["amenity_scores"].values()) / len(results["amenity_scores"]), 1
        )
        
        return results
    
    def generate_location_report(self, city, areas):
        """
        Generate a comprehensive location report for selected areas
        
        Args:
            city (str): City name
            areas (list): List of area names
            
        Returns:
            dict: Comprehensive location data
        """
        report = {
            "city": city,
            "areas": [],
            "map_available": False
        }
        
        # Generate map
        try:
            city_map = self.generate_area_map(city, areas)
            report["map_available"] = True
            report["map"] = city_map
        except Exception as e:
            print(f"Error generating map: {str(e)}")
        
        # Analyze each area
        for area in areas:
            area_data = {
                "name": area,
                "commute_analysis": self.analyze_commute_times(city, area),
                "amenity_analysis": self.analyze_nearby_amenities(city, area)
            }
            
            # Calculate location score (0-100)
            location_score = 0
            
            # Commute score (lower is better)
            avg_commute = area_data["commute_analysis"].get("avg_commute_time", 45)
            commute_score = max(0, 50 - (avg_commute - 15))  # 15 mins = 35 points, 45 mins = 5 points
            location_score += commute_score
            
            # Amenity score
            amenity_score = area_data["amenity_analysis"].get("overall_amenity_score", 5) * 5  # 0-10 scale to 0-50 scale
            location_score += amenity_score
            
            area_data["location_score"] = min(100, int(location_score))
            report["areas"].append(area_data)
        
        # Sort areas by location score
        report["areas"].sort(key=lambda x: x["location_score"], reverse=True)
        
        return report