import matplotlib.pyplot as plt
import numpy as np
import os
import json
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

class ROIVisualizer:
    """Generate visualizations for ROI and investment potential"""
    
    def __init__(self, output_dir="data/analysis/visuals"):
        """Initialize the visualizer with output directory"""
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_roi_heatmap(self, roi_data, save=True):
        """Generate heatmap showing ROI potential across different areas
        
        Args:
            roi_data (dict): Dict with cities as keys and areas with ROI values as values
            save (bool): Whether to save the chart to file
            
        Returns:
            str: Path to saved chart or None if not saved
        """
        try:
            # Prepare data for heatmap
            cities = []
            areas = []
            roi_values = []
            
            for city, city_data in roi_data.items():
                for area, area_data in city_data.items():
                    if "5_year_roi_percent" in area_data:
                        cities.append(city)
                        areas.append(area)
                        roi_values.append(area_data["5_year_roi_percent"])
            
            # Create DataFrame for heatmap
            data = pd.DataFrame({
                'City': cities,
                'Area': areas,
                'ROI': roi_values
            })
            
            # Pivot data for heatmap format
            pivot_data = data.pivot_table(values='ROI', index='City', columns='Area', fill_value=0)
            
            # Create custom colormap from red to green
            colors = ['#FF0000', '#FFFF00', '#00FF00']  # Red to Yellow to Green
            cmap = LinearSegmentedColormap.from_list('roi_cmap', colors, N=100)
            
            # Create figure
            plt.figure(figsize=(14, 10))
            sns.heatmap(pivot_data, annot=True, cmap=cmap, fmt=".1f", 
                        linewidths=0.5, cbar_kws={'label': 'ROI (%)'})
            
            plt.title('5-Year ROI Potential by City and Area')
            plt.tight_layout()
            
            if save:
                filepath = os.path.join(self.output_dir, "roi_heatmap.png")
                plt.savefig(filepath)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return None
        except Exception as e:
            print(f"Error generating ROI heatmap: {str(e)}")
            plt.close()
            return None
    
    def generate_risk_reward_scatter(self, investment_data, save=True):
        """Generate risk-reward scatter plot
        
        Args:
            investment_data (dict): Dict with areas as keys and risk/reward metrics as values
            save (bool): Whether to save the chart to file
            
        Returns:
            str: Path to saved chart or None if not saved
        """
        try:
            areas = []
            roi_values = []
            risk_scores = []
            cities = []
            
            for city, city_data in investment_data.items():
                for area, data in city_data.items():
                    if "roi_projections" in data and "risk_score" in data["roi_projections"]:
                        areas.append(area)
                        roi_values.append(data["roi_projections"]["5_year_roi_percent"])
                        risk_scores.append(data["roi_projections"]["risk_score"])
                        cities.append(city)
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Create scatter plot with city-based colors
            unique_cities = list(set(cities))
            colors = plt.cm.tab10(np.linspace(0, 1, len(unique_cities)))
            
            for i, city in enumerate(unique_cities):
                indices = [idx for idx, c in enumerate(cities) if c == city]
                city_areas = [areas[idx] for idx in indices]
                city_roi = [roi_values[idx] for idx in indices]
                city_risk = [risk_scores[idx] for idx in indices]
                
                plt.scatter(city_risk, city_roi, label=city, color=colors[i], s=80, alpha=0.7)
                
                # Add area labels
                for j, area in enumerate(city_areas):
                    plt.annotate(area, (city_risk[j], city_roi[j]), 
                                fontsize=9, ha='center', va='bottom')
            
            # Add quadrant lines and labels
            plt.axhline(y=25, color='gray', linestyle='--', alpha=0.5)
            plt.axvline(x=5, color='gray', linestyle='--', alpha=0.5)
            
            # Add quadrant labels
            plt.text(2.5, 37.5, "High Return\nLow Risk", ha='center', fontsize=12, alpha=0.7,
                    bbox=dict(facecolor='white', alpha=0.5))
            plt.text(7.5, 37.5, "High Return\nHigh Risk", ha='center', fontsize=12, alpha=0.7,
                    bbox=dict(facecolor='white', alpha=0.5))
            plt.text(2.5, 12.5, "Low Return\nLow Risk", ha='center', fontsize=12, alpha=0.7,
                    bbox=dict(facecolor='white', alpha=0.5))
            plt.text(7.5, 12.5, "Low Return\nHigh Risk", ha='center', fontsize=12, alpha=0.7,
                    bbox=dict(facecolor='white', alpha=0.5))
            
            plt.xlabel('Risk Score (1-10)')
            plt.ylabel('5-Year ROI Potential (%)')
            plt.title('Risk-Reward Analysis of Investment Areas')
            plt.grid(True, linestyle='--', alpha=0.3)
            plt.legend(title="City", loc="upper right")
            plt.tight_layout()
            
            if save:
                filepath = os.path.join(self.output_dir, "risk_reward_scatter.png")
                plt.savefig(filepath)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return None
        except Exception as e:
            print(f"Error generating risk-reward scatter: {str(e)}")
            plt.close()
            return None
    
    def generate_investment_horizon_chart(self, roi_data, save=True):
        """Generate chart showing ROI across different investment horizons
        
        Args:
            roi_data (dict): Dictionary with area names and ROI projections
            save (bool): Whether to save the chart to file
            
        Returns:
            str: Path to saved chart or None if not saved
        """
        try:
            areas = []
            roi_3yr = []
            roi_5yr = []
            roi_10yr = []
            
            for area, data in roi_data.items():
                if "roi_projections" in data:
                    projections = data["roi_projections"]
                    areas.append(area)
                    roi_3yr.append(projections.get("3_year_roi_percent", 0))
                    roi_5yr.append(projections.get("5_year_roi_percent", 0))
                    roi_10yr.append(projections.get("10_year_roi_percent", 0))
            
            # Sort areas by 5-year ROI
            sort_idx = np.argsort(roi_5yr)[::-1]
            areas = [areas[i] for i in sort_idx]
            roi_3yr = [roi_3yr[i] for i in sort_idx]
            roi_5yr = [roi_5yr[i] for i in sort_idx]
            roi_10yr = [roi_10yr[i] for i in sort_idx]
            
            # Create figure
            plt.figure(figsize=(14, 10))
            
            # Create bar positions
            x = np.arange(len(areas))
            width = 0.25
            
            plt.bar(x - width, roi_3yr, width, label='3-Year ROI', color='skyblue')
            plt.bar(x, roi_5yr, width, label='5-Year ROI', color='orange')
            plt.bar(x + width, roi_10yr, width, label='10-Year ROI', color='green')
            
            plt.xlabel('Investment Area')
            plt.ylabel('ROI (%)')
            plt.title('ROI Potential Across Different Investment Horizons')
            plt.xticks(x, areas, rotation=45, ha='right')
            plt.legend()
            plt.grid(True, axis='y', linestyle='--', alpha=0.3)
            plt.tight_layout()
            
            if save:
                filepath = os.path.join(self.output_dir, "investment_horizon_comparison.png")
                plt.savefig(filepath)
                plt.close()
                return filepath
            else:
                plt.show()
                plt.close()
                return None
        except Exception as e:
            print(f"Error generating investment horizon chart: {str(e)}")
            plt.close()
            return None
    
    def visualize_roi_data(self, roi_data_path):
        """Visualize ROI data from JSON file
        
        Args:
            roi_data_path (str): Path to ROI data JSON file
            
        Returns:
            list: Paths to generated visualization files
        """
        try:
            # Load ROI data
            with open(roi_data_path, 'r') as f:
                data = json.load(f)
            
            # Generate visualizations
            generated_files = []
            
            # Extract ROI data structure
            if "city_roi_analysis" in data:
                # Structure for ROI heatmap
                roi_heatmap_data = {}
                for city, city_data in data["city_roi_analysis"].items():
                    if "areas_by_roi" in city_data and city_data["areas_by_roi"]:
                        roi_heatmap_data[city] = {}
                        for area, roi, area_data in city_data["areas_by_roi"]:
                            roi_heatmap_data[city][area] = {"5_year_roi_percent": roi}
                
                # Generate ROI heatmap
                heatmap_path = self.generate_roi_heatmap(roi_heatmap_data)
                if heatmap_path:
                    generated_files.append(heatmap_path)
                
                # Generate risk-reward scatter
                risk_reward_data = {}
                for city, city_data in data["city_roi_analysis"].items():
                    risk_reward_data[city] = {}
                    if "areas_by_roi" in city_data:
                        for area, roi, area_data in city_data["areas_by_roi"]:
                            risk_reward_data[city][area] = area_data
                
                scatter_path = self.generate_risk_reward_scatter(risk_reward_data)
                if scatter_path:
                    generated_files.append(scatter_path)
                
                # Generate investment horizon chart for top areas
                if "top_investment_areas" in data:
                    top_areas = {}
                    for city, area, roi in data["top_investment_areas"][:10]:  # Top 10 areas
                        for city_name, city_data in risk_reward_data.items():
                            if city_name == city and area in city_data:
                                top_areas[f"{city} - {area}"] = city_data[area]
                    
                    horizon_path = self.generate_investment_horizon_chart(top_areas)
                    if horizon_path:
                        generated_files.append(horizon_path)
            
            return generated_files
        except Exception as e:
            print(f"Error visualizing ROI data: {str(e)}")
            return []