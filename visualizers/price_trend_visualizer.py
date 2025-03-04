import matplotlib.pyplot as plt
import numpy as np
import os
import json
from pathlib import Path

class PriceTrendVisualizer:
    """Generate visualizations for real estate price trends"""
    
    def __init__(self, output_dir="data/analysis/visuals"):
        """Initialize the visualizer with output directory"""
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_area_price_trend_chart(self, city, area, area_data, save=True):
        """Generate price trend chart for a specific area
        
        Args:
            city (str): City name
            area_data (dict): Dictionary with month_year as keys and prices as values
            save (bool): Whether to save the chart to file
            
        Returns:
            str: Path to saved chart or None if not saved
        """
        try:
            # Sort data by month
            months = sorted(area_data.keys())
            prices = [area_data[month] for month in months]
            
            # Create figure
            plt.figure(figsize=(12, 6))
            plt.plot(months, prices, marker='o', linestyle='-', linewidth=2)
            
            # Handle potentially long x-axis by showing only some labels
            if len(months) > 12:
                # Show only every n-th month to avoid overcrowding
                n = max(1, len(months) // 12)
                plt.xticks(range(0, len(months), n), [months[i] for i in range(0, len(months), n)], rotation=45)
            else:
                plt.xticks(rotation=45)
            
            plt.title(f'Price Trend for {area} in {city}')
            plt.xlabel('Month/Year')
            plt.ylabel('Price per sq.ft (₹)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            if save:
                # Safe filename creation
                safe_area = "".join([c if c.isalnum() else "_" for c in area])
                filename = f"{city}_{safe_area}_price_trend.png"
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return None
        except Exception as e:
            print(f"Error generating area price trend chart: {str(e)}")
            plt.close()
            return None
    
    def generate_city_comparison_chart(self, city_data, save=True):
        """Generate chart comparing average price trends across cities
        
        Args:
            city_data (dict): Dictionary with city names as keys and yearly average prices as values
            save (bool): Whether to save the chart to file
            
        Returns:
            str: Path to saved chart or None if not saved
        """
        try:
            cities = list(city_data.keys())
            years = list(city_data[cities[0]].keys()) if cities else []
            
            if not cities or not years:
                return None
            
            # Setup figure
            plt.figure(figsize=(12, 8))
            
            # Plot each city with a different color
            for city in cities:
                yearly_prices = [city_data[city].get(year, 0) for year in years]
                plt.plot(years, yearly_prices, marker='o', linewidth=2, label=city)
            
            plt.title('Average Property Prices by City (₹ per sq.ft)')
            plt.xlabel('Year')
            plt.ylabel('Average Price per sq.ft (₹)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(loc='upper left')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if save:
                filepath = os.path.join(self.output_dir, "city_price_comparison.png")
                plt.savefig(filepath)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return None
        except Exception as e:
            print(f"Error generating city comparison chart: {str(e)}")
            plt.close()
            return None
    
    def generate_growth_rate_chart(self, growth_rates, save=True):
        """Generate bar chart showing annualized growth rates by area
        
        Args:
            growth_rates (dict): Dictionary with area names as keys and growth rates as values
            save (bool): Whether to save the chart to file
            
        Returns:
            str: Path to saved chart or None if not saved
        """
        try:
            # Sort areas by growth rate
            sorted_areas = sorted(growth_rates.items(), key=lambda x: x[1], reverse=True)
            areas = [area for area, _ in sorted_areas]
            rates = [rate * 100 for _, rate in sorted_areas]  # Convert to percentage
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(areas, rates, color='skyblue')
            
            # Add value labels on top of each bar
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                        f"{height:.1f}%", ha='center', va='bottom', rotation=0)
            
            plt.title('Annualized Growth Rate by Area (%)')
            plt.xlabel('Area')
            plt.ylabel('Growth Rate (%)')
            plt.grid(True, linestyle='--', alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if save:
                filepath = os.path.join(self.output_dir, "area_growth_rates.png")
                plt.savefig(filepath)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return None
        except Exception as e:
            print(f"Error generating growth rate chart: {str(e)}")
            plt.close()
            return None
    
    def generate_roi_comparison_chart(self, roi_data, save=True):
        """Generate chart comparing ROI across different areas
        
        Args:
            roi_data (dict): Dictionary with area names as keys and ROI projections as values
            save (bool): Whether to save the chart to file
            
        Returns:
            str: Path to saved chart or None if not saved
        """
        try:
            areas = list(roi_data.keys())
            three_yr = [roi_data[area].get("3_year_roi_percent", 0) for area in areas]
            five_yr = [roi_data[area].get("5_year_roi_percent", 0) for area in areas]
            ten_yr = [roi_data[area].get("10_year_roi_percent", 0) for area in areas]
            
            x = np.arange(len(areas))  # X-axis positions
            width = 0.25  # Bar width
            
            plt.figure(figsize=(14, 8))
            plt.bar(x - width, three_yr, width, label='3-Year ROI')
            plt.bar(x, five_yr, width, label='5-Year ROI')
            plt.bar(x + width, ten_yr, width, label='10-Year ROI')
            
            plt.title('ROI Projections by Area')
            plt.xlabel('Area')
            plt.ylabel('ROI (%)')
            plt.xticks(x, areas, rotation=45, ha='right')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.3, axis='y')
            plt.tight_layout()
            
            if save:
                filepath = os.path.join(self.output_dir, "roi_comparison.png")
                plt.savefig(filepath)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return None
        except Exception as e:
            print(f"Error generating ROI comparison chart: {str(e)}")
            plt.close()
            return None
    
    def visualize_historical_data(self, historical_data_path):
        """Visualize historical price data from JSON file
        
        Args:
            historical_data_path (str): Path to historical price data JSON file
            
        Returns:
            list: Paths to generated visualization files
        """
        try:
            # Load historical data
            with open(historical_data_path, 'r') as f:
                data = json.load(f)
            
            # Group data by city and area
            city_area_data = {}
            city_year_data = {}  # For city comparison
            
            for entry in data:
                city = entry["city"]
                area = entry["area"]
                month_year = entry["month_year"]
                price = entry["avg_price_per_sqft"]
                
                # Extract year for city comparison
                year = month_year.split('-')[0]
                
                # Group by city and area
                if city not in city_area_data:
                    city_area_data[city] = {}
                
                if area not in city_area_data[city]:
                    city_area_data[city][area] = {}
                
                city_area_data[city][area][month_year] = price
                
                # Group by city and year for comparison
                if city not in city_year_data:
                    city_year_data[city] = {}
                
                if year not in city_year_data[city]:
                    city_year_data[city][year] = []
                
                city_year_data[city][year].append(price)
            
            # Calculate yearly averages for cities
            for city in city_year_data:
                for year in city_year_data[city]:
                    city_year_data[city][year] = sum(city_year_data[city][year]) / len(city_year_data[city][year])
            
            # Generate visualizations
            generated_files = []
            
            # Generate city comparison chart
            city_chart = self.generate_city_comparison_chart(city_year_data)
            if city_chart:
                generated_files.append(city_chart)
            
            # Generate area price trend charts for each city and area
            for city, areas in city_area_data.items():
                for area, month_data in areas.items():
                    if len(month_data) >= 12:  # Only generate if we have at least 12 months of data
                        try:
                            area_chart = self.generate_area_price_trend_chart(city, area, month_data)
                            if area_chart:
                                generated_files.append(area_chart)
                        except Exception as e:
                            print(f"Error generating chart for {city} - {area}: {str(e)}")
            
            return generated_files
        except Exception as e:
            print(f"Error visualizing historical data: {str(e)}")
            return []