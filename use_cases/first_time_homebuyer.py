"""
First-time homebuyer module for Real Estate AI.
Focuses on buy vs. rent analysis, school districts, and long-term financial planning.
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

class FirstTimeHomebuyerAnalysis:
    """First-time homebuyer specialized analysis and dashboard components."""
    
    def __init__(self, data, processed):
        """Initialize with loaded data."""
        self.data = data
        self.processed = processed
        self.location_analyzer = LocationAnalyzer()
        
    def calculate_mortgage_details(self, property_price, down_payment_pct, interest_rate, years):
        """Calculate mortgage payments and amortization schedule."""
        loan_amount = property_price * (1 - down_payment_pct/100)
        monthly_rate = interest_rate / (12 * 100)
        num_payments = years * 12
        
        # Calculate monthly payment using the formula: M = P[r(1+r)^n]/[(1+r)^n-1]
        if monthly_rate == 0:
            monthly_payment = loan_amount / num_payments
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        
        # Generate amortization schedule
        schedule = []
        remaining_balance = loan_amount
        total_interest = 0
        
        for payment_num in range(1, num_payments + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment
            total_interest += interest_payment
            
            # Add to schedule (yearly)
            if payment_num % 12 == 0:
                year = payment_num // 12
                schedule.append({
                    'Year': year,
                    'Total Paid': year * 12 * monthly_payment,
                    'Principal Paid': loan_amount - remaining_balance,
                    'Interest Paid': total_interest,
                    'Remaining Balance': max(0, remaining_balance)
                })
        
        return {
            'monthly_payment': monthly_payment,
            'total_payment': monthly_payment * num_payments,
            'total_interest': total_interest,
            'schedule': schedule
        }
    
    def analyze_buy_vs_rent(self, purchase_price, monthly_rent, years, down_payment_pct=20, 
                          interest_rate=8.5, home_appreciation=5, rent_increase=7):
        """
        Compare buying vs renting over a given time period.
        
        Args:
            purchase_price: Home purchase price
            monthly_rent: Initial monthly rent
            years: Time period for analysis
            down_payment_pct: Down payment percentage
            interest_rate: Annual mortgage interest rate
            home_appreciation: Annual home value appreciation rate
            rent_increase: Annual rent increase rate
            
        Returns:
            dict: Analysis results
        """
        # Initial calculations
        down_payment = purchase_price * (down_payment_pct/100)
        monthly_mortgage = self.calculate_mortgage_details(
            purchase_price, down_payment_pct, interest_rate, years)['monthly_payment']
        
        # Include property tax, maintenance, insurance for buying scenario
        property_tax_rate = 1.5  # 1.5% of property value annually
        monthly_property_tax = (purchase_price * property_tax_rate/100) / 12
        monthly_maintenance = purchase_price * 0.01 / 12  # 1% of home value annually
        monthly_insurance = purchase_price * 0.005 / 12  # 0.5% of home value annually
        
        # Total monthly cost of buying initially
        monthly_cost_buying = monthly_mortgage + monthly_property_tax + monthly_maintenance + monthly_insurance
        
        # Projected costs over time
        buying_costs = []
        renting_costs = []
        home_values = []
        equity_values = []
        total_buying = down_payment
        total_renting = 0
        current_home_value = purchase_price
        current_rent = monthly_rent
        mortgage_balance = purchase_price - down_payment
        
        for year in range(1, years + 1):
            # Update home value and rent for this year
            current_home_value = current_home_value * (1 + home_appreciation/100)
            current_rent = current_rent * (1 + rent_increase/100)
            
            # Calculate buying costs for this year
            yearly_mortgage = monthly_mortgage * 12
            yearly_property_tax = monthly_property_tax * 12 * (1 + home_appreciation/200)  # Property tax increases with home value
            yearly_maintenance = monthly_maintenance * 12 * (1 + home_appreciation/200)  # Maintenance increases with home value
            yearly_insurance = monthly_insurance * 12 * (1 + home_appreciation/200)  # Insurance increases with home value
            
            yearly_buying_cost = yearly_mortgage + yearly_property_tax + yearly_maintenance + yearly_insurance
            total_buying += yearly_buying_cost
            
            # Calculate renting costs for this year
            yearly_renting_cost = current_rent * 12
            total_renting += yearly_renting_cost
            
            # Calculate mortgage balance and equity
            interest_paid = mortgage_balance * interest_rate/100
            principal_paid = yearly_mortgage - interest_paid
            mortgage_balance -= principal_paid
            mortgage_balance = max(0, mortgage_balance)
            equity = current_home_value - mortgage_balance
            
            # Store values for plotting
            buying_costs.append(total_buying)
            renting_costs.append(total_renting)
            home_values.append(current_home_value)
            equity_values.append(equity)
        
        # Determine break-even point
        break_even_year = None
        for i in range(len(buying_costs)):
            if equity_values[i] + (total_renting - buying_costs[i]) > 0:
                break_even_year = i + 1
                break
                
        # Net position after all years
        net_worth_buying = equity_values[-1] - (buying_costs[-1] - down_payment)
        net_worth_renting = -renting_costs[-1]
        
        return {
            'monthly_payment': monthly_mortgage,
            'monthly_cost_buying': monthly_cost_buying,
            'monthly_rent': monthly_rent,
            'break_even_year': break_even_year,
            'total_cost_buying': buying_costs[-1],
            'total_cost_renting': renting_costs[-1],
            'final_home_value': home_values[-1],
            'final_equity': equity_values[-1],
            'net_worth_buying': current_home_value - mortgage_balance,
            'net_worth_renting': -total_renting,
            'yearly_data': {
                'years': list(range(1, years + 1)),
                'buying_costs': buying_costs,
                'renting_costs': renting_costs,
                'home_values': home_values,
                'equity_values': equity_values
            }
        }
    
    def analyze_school_districts(self, city, area):
        """Analyze school districts and educational facilities near location."""
        schools_data = {
            "city": city,
            "area": area,
            "schools": [],
            "education_score": 0
        }
        
        try:
            # Try to geocode the area
            area_coords = self.location_analyzer.geocode_with_nominatim(f"{area}, {city}, India")
            
            if not area_coords:
                return self.generate_synthetic_school_data(city, area)
            
            # Use Overpass API to find schools in the area
            amenity_types = ["school", "college", "university"]
            total_schools = 0
            education_score = 0
            
            for amenity_type in amenity_types:
                schools = self.location_analyzer.query_osm_amenities(
                    area_coords["lat"], area_coords["lng"], amenity_type, radius=3000
                )
                
                if schools:
                    schools_data["schools"].extend([
                        {"name": school.get("name", f"{amenity_type.title()}"), 
                         "type": amenity_type} 
                        for school in schools
                    ])
                    
                    # Contribute to education score
                    count = len(schools)
                    total_schools += count
                    
                    # Weight different types of institutions
                    weight = 1.0 if amenity_type == "school" else 1.5 if amenity_type == "college" else 2.0
                    education_score += count * weight
            
            # Normalize score to 0-10 scale
            schools_data["education_score"] = min(10, round(education_score / 5, 1))
            schools_data["total_count"] = total_schools
            
            return schools_data
            
        except Exception as e:
            print(f"Error analyzing school districts: {str(e)}")
            return self.generate_synthetic_school_data(city, area)
    
    def generate_synthetic_school_data(self, city, area):
        """Generate synthetic school data when real data is not available."""
        schools_data = {
            "city": city,
            "area": area,
            "schools": [],
            "is_synthetic": True
        }
        
        # Generate different numbers of schools based on area profile
        major_cities = ["Mumbai", "Delhi-NCR", "Bangalore", "Hyderabad", "Chennai"]
        is_major_city = city in major_cities
        
        # Base counts for different school types
        school_count = np.random.randint(3, 12) if is_major_city else np.random.randint(1, 8)
        college_count = np.random.randint(1, 5) if is_major_city else np.random.randint(0, 3)
        university_count = np.random.randint(0, 2) if is_major_city else np.random.randint(0, 1)
        
        # Generate school names
        school_types = ["Public", "Private", "International", "CBSE", "ICSE", "State Board"]
        school_suffixes = ["School", "Academy", "High School", "Public School", "International School"]
        
        for i in range(school_count):
            school_type = np.random.choice(school_types)
            suffix = np.random.choice(school_suffixes)
            name = f"{area} {school_type} {suffix}"
            schools_data["schools"].append({"name": name, "type": "school"})
        
        # Generate college names
        college_types = ["Junior", "Degree", "Arts & Science", "Engineering", "Medical"]
        college_suffixes = ["College", "Institute", "College of Engineering", "College of Arts"]
        
        for i in range(college_count):
            college_type = np.random.choice(college_types)
            suffix = np.random.choice(college_suffixes)
            name = f"{area} {college_type} {suffix}"
            schools_data["schools"].append({"name": name, "type": "college"})
        
        # Generate university names
        for i in range(university_count):
            name = f"{city} University {i+1}" if i > 0 else f"{city} University"
            schools_data["schools"].append({"name": name, "type": "university"})
        
        # Calculate education score
        education_score = school_count * 1.0 + college_count * 1.5 + university_count * 2.0
        schools_data["education_score"] = min(10, round(education_score / 5, 1))
        schools_data["total_count"] = school_count + college_count + university_count
        
        return schools_data
    
    def render_dashboard(self):
        """Render the first-time homebuyer dashboard."""
        st.title("🏠 First-Time Homebuyer Analysis")
        st.write("Tools and analysis designed specifically for first-time homebuyers in the Indian market.")
        
        tab1, tab2, tab3 = st.tabs(["🔄 Buy vs. Rent Calculator", "🏫 School District Analysis", "💰 Mortgage Calculator"])
        
        # Tab 1: Buy vs. Rent Calculator
        with tab1:
            st.header("Buy vs. Rent Analysis")
            st.write("Compare the long-term financial implications of buying versus renting.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Property Details")
                purchase_price = st.number_input("Purchase Price (₹)", min_value=1000000, max_value=100000000, 
                                              value=5000000, step=500000, format="%d")
                monthly_rent = st.number_input("Equivalent Monthly Rent (₹)", min_value=5000, max_value=500000, 
                                            value=25000, step=1000, format="%d")
            
            with col2:
                st.subheader("Financial Parameters")
                down_payment_pct = st.slider("Down Payment (%)", min_value=10, max_value=50, value=20, step=5)
                interest_rate = st.slider("Interest Rate (%)", min_value=6.0, max_value=12.0, value=8.5, step=0.1)
                
            col3, col4 = st.columns([1, 1])
            
            with col3:
                st.subheader("Growth Assumptions")
                home_appreciation = st.slider("Annual Home Appreciation (%)", min_value=2.0, max_value=10.0, value=5.0, step=0.5)
                rent_increase = st.slider("Annual Rent Increase (%)", min_value=3.0, max_value=15.0, value=7.0, step=0.5)
            
            with col4:
                st.subheader("Time Horizon")
                years = st.slider("Analysis Period (Years)", min_value=5, max_value=30, value=15, step=1)
            
            # Perform the analysis
            if st.button("Calculate Buy vs. Rent Analysis"):
                with st.spinner("Calculating buy vs. rent comparison..."):
                    analysis = self.analyze_buy_vs_rent(
                        purchase_price=purchase_price,
                        monthly_rent=monthly_rent,
                        down_payment_pct=down_payment_pct,
                        interest_rate=interest_rate,
                        home_appreciation=home_appreciation,
                        rent_increase=rent_increase,
                        years=years
                    )
                    
                    # Show results
                    col_results1, col_results2 = st.columns([1, 1])
                    
                    with col_results1:
                        st.subheader("Monthly Costs")
                        monthly_data = pd.DataFrame({
                            "Category": ["Monthly Mortgage", "Total Monthly Cost (Buy)", "Monthly Rent"],
                            "Amount (₹)": [
                                f"₹{analysis['monthly_payment']:,.2f}",
                                f"₹{analysis['monthly_cost_buying']:,.2f}",
                                f"₹{analysis['monthly_rent']:,.2f}"
                            ]
                        })
                        st.dataframe(monthly_data, hide_index=True, use_container_width=True)
                        
                        if analysis['break_even_year']:
                            st.success(f"**Break-Even Point:** Year {analysis['break_even_year']}")
                        else:
                            st.warning("No break-even point found within the analysis period.")
                    
                    with col_results2:
                        st.subheader("After {years} Years")
                        final_data = pd.DataFrame({
                            "Category": ["Home Value", "Home Equity", "Total Cost (Buy)", "Total Cost (Rent)", "Net Position (Buy)"],
                            "Amount (₹)": [
                                f"₹{analysis['final_home_value']:,.2f}",
                                f"₹{analysis['final_equity']:,.2f}",
                                f"₹{analysis['total_cost_buying']:,.2f}",
                                f"₹{analysis['total_cost_renting']:,.2f}",
                                f"₹{analysis['net_worth_buying']:,.2f}"
                            ]
                        })
                        st.dataframe(final_data, hide_index=True, use_container_width=True)
                    
                    # Create visualization
                    st.subheader("Costs and Value Over Time")
                    
                    yearly_data = analysis['yearly_data']
                    fig, ax = plt.subplots(figsize=(12, 7))
                    
                    # Plot the data
                    ax.plot(yearly_data['years'], yearly_data['buying_costs'], label='Total Cost (Buy)', color='red')
                    ax.plot(yearly_data['years'], yearly_data['renting_costs'], label='Total Cost (Rent)', color='blue')
                    ax.plot(yearly_data['years'], yearly_data['home_values'], label='Home Value', color='green')
                    ax.plot(yearly_data['years'], yearly_data['equity_values'], label='Home Equity', color='purple')
                    
                    # Add break-even point if applicable
                    if analysis['break_even_year']:
                        ax.axvline(x=analysis['break_even_year'], color='orange', linestyle='--', alpha=0.7)
                        ax.text(analysis['break_even_year'] + 0.1, max(yearly_data['home_values'])*0.8, 
                              f"Break-even: Year {analysis['break_even_year']}", 
                              color='orange', fontweight='bold')
                    
                    ax.set_xlabel("Years")
                    ax.set_ylabel("Amount (₹)")
                    ax.set_title("Buy vs. Rent Financial Comparison")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Recommendation
                    st.subheader("Recommendation")
                    if analysis['break_even_year'] and analysis['break_even_year'] <= years/2:
                        st.success(f"✅ **Buy Recommendation**: The break-even point occurs in year {analysis['break_even_year']}, which is early in your time horizon. Buying appears to be the better financial option if you plan to stay in this home for at least {max(5, analysis['break_even_year'])} years.")
                    elif analysis['break_even_year'] and analysis['break_even_year'] > years/2:
                        st.warning(f"⚠️ **Conditional Recommendation**: The break-even point occurs in year {analysis['break_even_year']}, which is later in your time horizon. Buying makes financial sense only if you plan to stay in this home for more than {analysis['break_even_year']} years.")
                    else:
                        st.error(f"❌ **Rent Recommendation**: No break-even point was found within {years} years. Renting appears to be the better financial option under these parameters.")
        
        # Tab 2: School District Analysis  
        with tab2:
            st.header("School District Analysis")
            st.write("Analyze educational facilities near potential home locations.")
            
            # City and area selection
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # City selection
                cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
                selected_city = st.selectbox("Select City", cities, key="school_city_select")
            
            with col2:
                # Get areas for selected city
                areas = []
                if selected_city and self.processed["listings_df"] is not None and not self.processed["listings_df"].empty:
                    city_data = self.processed["listings_df"][self.processed["listings_df"]["city"] == selected_city]
                    areas = sorted(city_data["area"].unique().tolist())
                
                if not areas and selected_city:
                    # Default areas if data is missing
                    default_areas = {
                        "Mumbai": ["Andheri", "Bandra", "Worli", "Powai", "Juhu"],
                        "Bangalore": ["Whitefield", "Electronic City", "Koramangala", "Indiranagar", "HSR Layout"],
                        "Hyderabad": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills", "Madhapur"],
                        "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Aundh"],
                        "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad"]
                    }
                    areas = default_areas.get(selected_city, [])
                
                selected_area = st.selectbox("Select Area", areas, key="school_area_select") if areas else None
            
            if selected_city and selected_area:
                if st.button("Analyze Schools and Education"):
                    with st.spinner(f"Analyzing educational facilities in {selected_area}, {selected_city}..."):
                        schools_data = self.analyze_school_districts(selected_city, selected_area)
                        
                        # Display results
                        col_score, col_map = st.columns([1, 2])
                        
                        with col_score:
                            st.subheader("Education Rating")
                            
                            # Create education score gauge chart
                            score = schools_data.get("education_score", 0)
                            fig, ax = plt.subplots(figsize=(6, 1))
                            
                            # Configure gauge chart
                            gauge_colors = ['#FF6B6B', '#FFD166', '#06D6A0']
                            score_color = gauge_colors[0] if score < 3.5 else gauge_colors[1] if score < 7 else gauge_colors[2]
                            
                            # Draw gauge bar
                            ax.barh([0], [10], color='#e6e6e6', height=0.5)
                            ax.barh([0], [score], color=score_color, height=0.5)
                            
                            # Add score text
                            ax.text(score, 0, f'{score}/10', ha='center', va='center', 
                                   color='black', fontweight='bold')
                            
                            # Configure gauge chart appearance
                            ax.set_xlim(0, 10)
                            ax.set_ylim(-0.5, 0.5)
                            ax.set_yticks([])
                            ax.set_xticks([0, 2.5, 5, 7.5, 10])
                            ax.set_xticklabels(['0', 'Poor', 'Average', 'Good', 'Excellent'])
                            ax.spines['top'].set_visible(False)
                            ax.spines['right'].set_visible(False)
                            ax.spines['left'].set_visible(False)
                            
                            st.pyplot(fig)
                            
                            st.metric(
                                "Total Educational Institutions", 
                                schools_data.get("total_count", 0)
                            )
                            
                            # Education score interpretation
                            if score >= 7:
                                st.success("Excellent educational facilities with diverse options.")
                            elif score >= 5:
                                st.info("Good educational infrastructure with adequate schooling options.")
                            elif score >= 3:
                                st.warning("Average educational facilities available.")
                            else:
                                st.error("Limited educational options in this area.")
                        
                        with col_map:
                            st.subheader("Schools & Colleges Map")
                            try:
                                # Generate area map with schools highlighted
                                area_coords = self.location_analyzer.geocode_with_nominatim(f"{selected_area}, {selected_city}, India")
                                if area_coords:
                                    # Create map centered on area
                                    area_map = folium.Map(location=[area_coords["lat"], area_coords["lng"]], 
                                                        zoom_start=14, 
                                                        tiles='OpenStreetMap')
                                    
                                    # Add area marker
                                    folium.Marker(
                                        location=[area_coords["lat"], area_coords["lng"]],
                                        popup=selected_area,
                                        tooltip=f"{selected_area} (Center)",
                                        icon=folium.Icon(color='red', icon='home')
                                    ).add_to(area_map)
                                    
                                    # Add radius circle for 3km
                                    folium.Circle(
                                        location=[area_coords["lat"], area_coords["lng"]],
                                        radius=3000,  # 3km in meters
                                        color='blue',
                                        fill=True,
                                        fill_opacity=0.1
                                    ).add_to(area_map)
                                    
                                    # Add school markers
                                    for i, school in enumerate(schools_data.get("schools", [])):
                                        # Different icon based on institution type
                                        icon_color = 'green' if school['type'] == 'school' else 'purple' if school['type'] == 'college' else 'darkblue'
                                        icon_name = 'graduation-cap' if school['type'] in ['college', 'university'] else 'school'
                                        
                                        # Add random offset for synthetic data
                                        if schools_data.get("is_synthetic", False):
                                            import random
                                            lat_offset = random.uniform(-0.02, 0.02)
                                            lng_offset = random.uniform(-0.02, 0.02)
                                            school_lat = area_coords["lat"] + lat_offset
                                            school_lng = area_coords["lng"] + lng_offset
                                        else:
                                            school_lat = area_coords["lat"]
                                            school_lng = area_coords["lng"]
                                        
                                        folium.Marker(
                                            location=[school_lat, school_lng],
                                            popup=f"{school['name']} ({school['type'].title()})",
                                            tooltip=school['name'],
                                            icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
                                        ).add_to(area_map)
                                    
                                    # Display map
                                    st_folium(area_map, width=700, height=400)
                                else:
                                    st.error("Unable to generate map for this location.")
                            except Exception as e:
                                st.error(f"Error generating school map: {str(e)}")
                        
                        # Display schools list
                        st.subheader(f"Educational Institutions in {selected_area}")
                        
                        school_list = schools_data.get("schools", [])
                        if school_list:
                            # Group by type
                            schools = [s for s in school_list if s['type'] == 'school']
                            colleges = [s for s in school_list if s['type'] == 'college']
                            universities = [s for s in school_list if s['type'] == 'university']
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**Schools ({len(schools)})**")
                                for school in schools:
                                    st.write(f"- {school['name']}")
                            
                            with col2:
                                st.write(f"**Colleges ({len(colleges)})**")
                                for college in colleges:
                                    st.write(f"- {college['name']}")
                                    
                            with col3:
                                st.write(f"**Universities ({len(universities)})**")
                                for university in universities:
                                    st.write(f"- {university['name']}")
                        else:
                            st.info("No educational institutions found in this area.")
                        
                        # Show synthetic data notice if applicable
                        if schools_data.get("is_synthetic", False):
                            st.info("Note: Using generated sample data for educational institutions.")
        
        # Tab 3: Mortgage Calculator
        with tab3:
            st.header("Mortgage Calculator")
            st.write("Calculate mortgage payments and view amortization schedule.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Loan Details")
                loan_amount = st.number_input("Property Price (₹)", min_value=1000000, max_value=100000000, 
                                           value=5000000, step=500000, format="%d")
                down_payment_pct = st.slider("Down Payment (%)", min_value=10, max_value=50, value=20, step=5, 
                                          key="mortgage_down_payment")
            
            with col2:
                st.subheader("Loan Terms")
                interest_rate = st.slider("Interest Rate (%)", min_value=6.0, max_value=12.0, value=8.5, step=0.1, 
                                       key="mortgage_interest")
                years = st.slider("Loan Term (Years)", min_value=5, max_value=30, value=20, step=1, 
                               key="mortgage_years")
            
            if st.button("Calculate Mortgage"):
                with st.spinner("Calculating mortgage details..."):
                    mortgage_details = self.calculate_mortgage_details(
                        loan_amount, down_payment_pct, interest_rate, years
                    )
                    
                    # Display mortgage summary
                    col_results1, col_results2, col_results3 = st.columns(3)
                    
                    with col_results1:
                        st.metric("Monthly Payment", f"₹{mortgage_details['monthly_payment']:,.2f}")
                    
                    with col_results2:
                        st.metric("Total Payments", f"₹{mortgage_details['total_payment']:,.2f}")
                    
                    with col_results3:
                        st.metric("Total Interest", f"₹{mortgage_details['total_interest']:,.2f}")
                    
                    # Display amortization schedule
                    st.subheader("Amortization Schedule")
                    
                    schedule_df = pd.DataFrame(mortgage_details['schedule'])
                    schedule_df['Total Paid'] = schedule_df['Total Paid'].map(lambda x: f"₹{x:,.2f}")
                    schedule_df['Principal Paid'] = schedule_df['Principal Paid'].map(lambda x: f"₹{x:,.2f}")
                    schedule_df['Interest Paid'] = schedule_df['Interest Paid'].map(lambda x: f"₹{x:,.2f}")
                    schedule_df['Remaining Balance'] = schedule_df['Remaining Balance'].map(lambda x: f"₹{x:,.2f}")
                    
                    st.dataframe(schedule_df, hide_index=True, use_container_width=True)
                    
                    # Create visualization of amortization
                    st.subheader("Principal and Interest Over Time")
                    
                    # Extract data from schedule for plotting
                    principal_paid = [item['Principal Paid'] for item in mortgage_details['schedule']]
                    interest_paid = [item['Interest Paid'] for item in mortgage_details['schedule']]
                    chart_years = [item['Year'] for item in mortgage_details['schedule']]
                    
                    fig, ax = plt.subplots(figsize=(12, 7))
                    
                    ax.bar(chart_years, principal_paid, label='Principal Paid', color='green')
                    ax.bar(chart_years, interest_paid, bottom=principal_paid, label='Interest Paid', color='red')
                    
                    ax.set_xlabel('Year')
                    ax.set_ylabel('Amount (₹)')
                    ax.set_title('Mortgage Breakdown: Principal vs Interest')
                    ax.legend()
                    
                    # Format y-axis to show crores/lakhs
                    def crore_formatter(x, pos):
                        if x >= 10000000:
                            return f'{x/10000000:.1f}Cr'
                        elif x >= 100000:
                            return f'{x/100000:.1f}L'
                        else:
                            return f'{x:.0f}'
                    
                    ax.yaxis.set_major_formatter(plt.FuncFormatter(crore_formatter))
                    
                    plt.tight_layout()
                    st.pyplot(fig)