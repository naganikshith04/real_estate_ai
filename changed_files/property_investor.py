"""
Property investor module for Real Estate AI.
Focuses on rental yield, portfolio tracking, and tax optimization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import folium
from streamlit_folium import st_folium
from data_providers.location_analyzer import LocationAnalyzer

class PropertyInvestorAnalysis:
    """Property investor specialized analysis and dashboard components."""
    
    def __init__(self, data, processed):
        """Initialize with loaded data."""
        self.data = data
        self.processed = processed
        self.location_analyzer = LocationAnalyzer()
    
    def analyze_rental_yield(self, property_price, monthly_rent, occupancy_rate=95, 
                           maintenance_pct=1.0, property_tax_pct=1.5):
        """
        Analyze rental yield for a property.
        
        Args:
            property_price: Property price
            monthly_rent: Monthly rental income
            occupancy_rate: Expected occupancy rate percentage
            maintenance_pct: Annual maintenance cost as percentage of property value
            property_tax_pct: Annual property tax as percentage of property value
            
        Returns:
            dict: Rental yield analysis
        """
        # Calculate annual income
        annual_rent = monthly_rent * 12
        effective_annual_rent = annual_rent * (occupancy_rate / 100)
        
        # Calculate expenses
        annual_maintenance = property_price * (maintenance_pct / 100)
        annual_property_tax = property_price * (property_tax_pct / 100)
        annual_expenses = annual_maintenance + annual_property_tax
        
        # Calculate net income and yield
        net_annual_income = effective_annual_rent - annual_expenses
        gross_yield = (annual_rent / property_price) * 100
        net_yield = (net_annual_income / property_price) * 100
        
        # Price-to-rent ratio (common metric for rental investments)
        price_to_rent_ratio = property_price / annual_rent
        
        # Capital appreciation (assuming 5% annual appreciation over 5 years)
        appreciation_rate = 5  # 5% annual appreciation
        future_value_5yr = property_price * ((1 + (appreciation_rate/100)) ** 5)
        
        # Tax analysis (simplified)
        # Assuming 30% tax bracket for rental income in India
        tax_rate = 30
        taxable_income = net_annual_income * 0.7  # 30% standard deduction in India
        tax_amount = taxable_income * (tax_rate / 100)
        after_tax_yield = ((net_annual_income - tax_amount) / property_price) * 100
        
        return {
            'property_price': property_price,
            'monthly_rent': monthly_rent,
            'annual_rent': annual_rent,
            'effective_annual_rent': effective_annual_rent,
            'annual_expenses': annual_expenses,
            'net_annual_income': net_annual_income,
            'gross_yield': gross_yield,
            'net_yield': net_yield,
            'after_tax_yield': after_tax_yield,
            'price_to_rent_ratio': price_to_rent_ratio,
            'future_value_5yr': future_value_5yr,
            'potential_appreciation': future_value_5yr - property_price,
            'occupancy_rate': occupancy_rate,
            'tax_amount': tax_amount
        }
    
    def analyze_portfolio(self, properties):
        """
        Analyze a portfolio of properties.
        
        Args:
            properties: List of property dictionaries with price, rent, location info
            
        Returns:
            dict: Portfolio analysis
        """
        if not properties:
            return {
                'total_value': 0,
                'total_monthly_income': 0,
                'total_annual_income': 0,
                'average_yield': 0,
                'properties': []
            }
        
        total_value = sum(p['price'] for p in properties)
        total_monthly_income = sum(p['monthly_rent'] for p in properties)
        total_annual_income = total_monthly_income * 12
        
        # Calculate yields for each property
        for prop in properties:
            analysis = self.analyze_rental_yield(
                prop['price'], prop['monthly_rent'], 
                prop.get('occupancy_rate', 95)
            )
            prop['gross_yield'] = analysis['gross_yield']
            prop['net_yield'] = analysis['net_yield']
            prop['annual_expenses'] = analysis['annual_expenses']
        
        # Calculate portfolio average yield (weighted by property value)
        if total_value > 0:
            weighted_yields = sum(p['price'] * p['net_yield'] for p in properties)
            average_yield = weighted_yields / total_value
        else:
            average_yield = 0
            
        # Calculate diversification metrics
        city_distribution = {}
        type_distribution = {}
        
        for prop in properties:
            # City distribution
            city = prop.get('city', 'Unknown')
            city_distribution[city] = city_distribution.get(city, 0) + prop['price']
            
            # Property type distribution
            prop_type = prop.get('type', 'Residential')
            type_distribution[prop_type] = type_distribution.get(prop_type, 0) + prop['price']
        
        # Convert absolute values to percentages
        for city in city_distribution:
            city_distribution[city] = (city_distribution[city] / total_value) * 100
            
        for prop_type in type_distribution:
            type_distribution[prop_type] = (type_distribution[prop_type] / total_value) * 100
        
        return {
            'total_value': total_value,
            'total_monthly_income': total_monthly_income,
            'total_annual_income': total_annual_income,
            'average_yield': average_yield,
            'city_distribution': city_distribution,
            'type_distribution': type_distribution,
            'properties': properties
        }
    
    def run_monte_carlo_simulation(self, property_price, monthly_rent, years=10, simulations=1000,
                              appreciation_mean=5, appreciation_std=3, occupancy_mean=95, occupancy_std=5,
                              rent_increase_mean=5, rent_increase_std=2, interest_rate=8.5, loan_percentage=80):
        """
        Run a Monte Carlo simulation to analyze risk and return profiles for a property investment.
        
        Args:
            property_price: Initial property price
            monthly_rent: Initial monthly rental income
            years: Time horizon for simulation
            simulations: Number of simulations to run
            appreciation_mean: Mean annual property appreciation rate (%)
            appreciation_std: Standard deviation for appreciation rate (%)
            occupancy_mean: Mean occupancy rate (%)
            occupancy_std: Standard deviation for occupancy rate (%)
            rent_increase_mean: Mean annual rent increase rate (%)
            rent_increase_std: Standard deviation for rent increase rate (%)
            interest_rate: Loan interest rate (if applicable)
            loan_percentage: Loan as percentage of property value
            
        Returns:
            dict: Monte Carlo simulation results
        """
        # Initialize results arrays
        final_property_values = []
        cumulative_cash_flows = []
        total_returns = []
        rois = []
        annual_returns = []
        yearly_property_values = np.zeros((simulations, years))
        yearly_cash_flows = np.zeros((simulations, years))
        
        # Calculate initial investment (down payment)
        down_payment = property_price * (1 - loan_percentage/100)
        loan_amount = property_price * (loan_percentage/100)
        
        # Calculate monthly mortgage payment (if using leverage)
        if loan_percentage > 0:
            monthly_rate = interest_rate / (12 * 100)
            num_payments = 30 * 12  # Assume 30-year mortgage
            monthly_mortgage = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        else:
            monthly_mortgage = 0
        
        # Property tax and maintenance costs
        annual_property_tax_rate = 1.5  # 1.5% of property value
        annual_maintenance_rate = 1.0  # 1% of property value
        
        # Run simulations
        for sim in range(simulations):
            # Initialize values for this simulation
            current_property_value = property_price
            current_monthly_rent = monthly_rent
            cumulative_cash_flow = -down_payment  # Start with down payment as negative cash flow
            
            for year in range(years):
                # Generate random values for this year
                appreciation_rate = np.random.normal(appreciation_mean, appreciation_std)
                occupancy_rate = min(100, max(0, np.random.normal(occupancy_mean, occupancy_std)))
                rent_increase_rate = np.random.normal(rent_increase_mean, rent_increase_std)
                
                # Update property value and rent for this year
                current_property_value *= (1 + appreciation_rate/100)
                current_monthly_rent *= (1 + rent_increase_rate/100)
                
                # Calculate income and expenses
                annual_rental_income = current_monthly_rent * 12 * (occupancy_rate/100)
                annual_property_tax = current_property_value * (annual_property_tax_rate/100)
                annual_maintenance = current_property_value * (annual_maintenance_rate/100)
                annual_mortgage = monthly_mortgage * 12
                
                # Calculate cash flow for the year
                annual_cash_flow = annual_rental_income - annual_property_tax - annual_maintenance - annual_mortgage
                
                # Store values
                yearly_property_values[sim, year] = current_property_value
                yearly_cash_flows[sim, year] = annual_cash_flow
                cumulative_cash_flow += annual_cash_flow
            
            # Store final results for this simulation
            final_property_values.append(current_property_value)
            cumulative_cash_flows.append(cumulative_cash_flow)
            
            # Total return includes property value plus cumulative cash flow minus initial investment
            total_return = current_property_value + cumulative_cash_flow - property_price
            total_returns.append(total_return)
            
            # ROI = (total_return / initial_investment) * 100
            roi = (total_return / down_payment) * 100
            rois.append(roi)
            
            # Annualized return calculation
            annual_return = ((1 + roi/100) ** (1/years) - 1) * 100
            annual_returns.append(annual_return)
        
        # Calculate statistics
        mean_final_value = np.mean(final_property_values)
        median_final_value = np.median(final_property_values)
        p10_final_value = np.percentile(final_property_values, 10)
        p90_final_value = np.percentile(final_property_values, 90)
        
        mean_roi = np.mean(rois)
        median_roi = np.median(rois)
        p10_roi = np.percentile(rois, 10)
        p90_roi = np.percentile(rois, 90)
        
        mean_annual_return = np.mean(annual_returns)
        
        # Value at Risk (VaR) calculation - the maximum loss at 95% confidence level
        var_95 = np.percentile(rois, 5)
        
        # Calculate probability of loss
        loss_probability = sum(1 for r in rois if r < 0) / len(rois) * 100
        
        # Calculate probability of achieving different ROI levels
        prob_roi_above_20 = sum(1 for r in rois if r >= 20) / len(rois) * 100
        prob_roi_above_50 = sum(1 for r in rois if r >= 50) / len(rois) * 100
        prob_roi_above_100 = sum(1 for r in rois if r >= 100) / len(rois) * 100
        
        # Calculate yearly averages for property values and cash flows
        mean_yearly_property_values = np.mean(yearly_property_values, axis=0)
        mean_yearly_cash_flows = np.mean(yearly_cash_flows, axis=0)
        
        return {
            'initial_investment': down_payment,
            'total_property_cost': property_price,
            'loan_amount': loan_amount,
            'mean_final_property_value': mean_final_value,
            'median_final_property_value': median_final_value,
            'p10_final_property_value': p10_final_value,
            'p90_final_property_value': p90_final_value,
            'mean_roi': mean_roi,
            'median_roi': median_roi,
            'p10_roi': p10_roi,
            'p90_roi': p90_roi,
            'mean_annual_return': mean_annual_return,
            'var_95': var_95,
            'loss_probability': loss_probability,
            'prob_roi_above_20': prob_roi_above_20,
            'prob_roi_above_50': prob_roi_above_50,
            'prob_roi_above_100': prob_roi_above_100,
            'mean_yearly_property_values': mean_yearly_property_values.tolist(),
            'mean_yearly_cash_flows': mean_yearly_cash_flows.tolist(),
            'all_rois': rois,
            'years': years
        }
        
    def calculate_tax_optimization(self, property_price, monthly_rent, interest_rate=8.5, 
                                loan_percentage=80, loan_term=20):
        """
        Calculate tax optimization strategies for rental property investment.
        
        Args:
            property_price: Property price
            monthly_rent: Monthly rental income
            interest_rate: Loan interest rate
            loan_percentage: Loan as percentage of property value
            loan_term: Loan term in years
            
        Returns:
            dict: Tax optimization analysis
        """
        # Calculate loan amount and EMI
        loan_amount = property_price * (loan_percentage / 100)
        monthly_rate = interest_rate / (12 * 100)
        num_payments = loan_term * 12
        
        if monthly_rate == 0:
            emi = loan_amount / num_payments
        else:
            emi = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        
        # Calculate annual interest payment (simplified, first year)
        annual_interest = loan_amount * (interest_rate / 100)
        
        # Calculate rental income
        annual_rent = monthly_rent * 12
        standard_deduction = annual_rent * 0.3  # 30% standard deduction for maintenance
        
        # Calculate property tax and insurance costs
        property_tax = property_price * 0.015  # Assuming 1.5% property tax
        insurance = property_price * 0.005  # Assuming 0.5% insurance cost
        
        # Calculate taxable rental income
        taxable_rental_income_without_loan = max(0, annual_rent - standard_deduction - property_tax - insurance)
        taxable_rental_income_with_loan = max(0, annual_rent - standard_deduction - property_tax - insurance - annual_interest)
        
        # Calculate tax for different scenarios (assuming 30% tax bracket)
        tax_rate = 30
        tax_without_loan = taxable_rental_income_without_loan * (tax_rate / 100)
        tax_with_loan = taxable_rental_income_with_loan * (tax_rate / 100)
        
        # Calculate tax savings
        tax_savings = tax_without_loan - tax_with_loan
        
        # Calculate ROI impact
        net_income_without_loan = annual_rent - standard_deduction - property_tax - insurance - tax_without_loan
        net_income_with_loan = annual_rent - standard_deduction - property_tax - insurance - annual_interest - tax_with_loan
        
        roi_without_loan = (net_income_without_loan / property_price) * 100
        roi_with_loan = (net_income_with_loan / (property_price - loan_amount)) * 100
        
        return {
            'property_price': property_price,
            'loan_amount': loan_amount,
            'emi': emi,
            'annual_interest': annual_interest,
            'annual_rent': annual_rent,
            'standard_deduction': standard_deduction,
            'property_tax': property_tax,
            'insurance': insurance,
            'taxable_income_without_loan': taxable_rental_income_without_loan,
            'taxable_income_with_loan': taxable_rental_income_with_loan,
            'tax_without_loan': tax_without_loan,
            'tax_with_loan': tax_with_loan,
            'tax_savings': tax_savings,
            'net_income_without_loan': net_income_without_loan,
            'net_income_with_loan': net_income_with_loan,
            'roi_without_loan': roi_without_loan,
            'roi_with_loan': roi_with_loan
        }
    
    def render_dashboard(self):
        """Render the property investor dashboard."""
        st.title("💰 Property Investor Dashboard")
        st.write("Advanced tools for real estate investors focusing on rental yield and portfolio optimization.")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Rental Yield Analyzer", "📈 Risk Analysis", "📁 Portfolio Tracker", "💸 Tax Optimization"])
        
        # Tab 1: Rental Yield Analyzer
        with tab1:
            st.header("Rental Yield Analysis")
            st.write("Analyze rental yield and return on investment for a property.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Property Details")
                property_price = st.number_input("Property Price (₹)", min_value=1000000, max_value=100000000, 
                                              value=7500000, step=500000, format="%d")
                monthly_rent = st.number_input("Monthly Rent (₹)", min_value=5000, max_value=1000000, 
                                            value=35000, step=1000, format="%d")
            
            with col2:
                st.subheader("Cost Factors")
                occupancy_rate = st.slider("Expected Occupancy Rate (%)", min_value=70, max_value=100, value=95, step=1)
                maintenance_pct = st.slider("Annual Maintenance (%)", min_value=0.5, max_value=3.0, value=1.0, step=0.1)
                property_tax_pct = st.slider("Annual Property Tax (%)", min_value=0.5, max_value=3.0, value=1.5, step=0.1)
                
            # First-time user help tooltip
            if 'rental_yield_tooltip' not in st.session_state:
                st.session_state.rental_yield_tooltip = True
                st.info("ℹ️ **Tip:** The rental yield is the annual rental income as a percentage of the property value. Higher is better!")
            
            if st.button("Calculate Rental Yield"):
                with st.spinner("Analyzing rental yield..."):
                    analysis = self.analyze_rental_yield(
                        property_price=property_price,
                        monthly_rent=monthly_rent,
                        occupancy_rate=occupancy_rate,
                        maintenance_pct=maintenance_pct,
                        property_tax_pct=property_tax_pct
                    )
                    
                    # Display results
                    col_yield1, col_yield2, col_yield3 = st.columns(3)
                    
                    with col_yield1:
                        gross_yield = analysis["gross_yield"]
                        st.metric("Gross Rental Yield", f"{gross_yield:.2f}%")
                        
                        # Color-coded interpretation
                        if gross_yield >= 8:
                            st.success("Excellent yield")
                        elif gross_yield >= 6:
                            st.info("Good yield")
                        elif gross_yield >= 4:
                            st.warning("Average yield")
                        else:
                            st.error("Below average yield")
                    
                    with col_yield2:
                        net_yield = analysis["net_yield"]
                        st.metric("Net Rental Yield", f"{net_yield:.2f}%")
                    
                    with col_yield3:
                        after_tax_yield = analysis["after_tax_yield"]
                        st.metric("After-Tax Yield", f"{after_tax_yield:.2f}%")
                    
                    # Financial breakdown
                    st.subheader("Financial Breakdown")
                    
                    col_details1, col_details2 = st.columns([1, 1])
                    
                    with col_details1:
                        st.write("**Income**")
                        income_data = pd.DataFrame({
                            "Item": ["Monthly Rent", "Annual Rent (100% Occupancy)", "Effective Annual Rent"],
                            "Amount": [
                                f"₹{analysis['monthly_rent']:,.2f}",
                                f"₹{analysis['annual_rent']:,.2f}",
                                f"₹{analysis['effective_annual_rent']:,.2f}"
                            ]
                        })
                        st.dataframe(income_data, hide_index=True, use_container_width=True)
                    
                    with col_details2:
                        st.write("**Expenses & Taxes**")
                        expense_data = pd.DataFrame({
                            "Item": ["Annual Maintenance", "Property Tax", "Total Annual Expenses", "Income Tax"],
                            "Amount": [
                                f"₹{property_price * maintenance_pct/100:,.2f}",
                                f"₹{property_price * property_tax_pct/100:,.2f}",
                                f"₹{analysis['annual_expenses']:,.2f}",
                                f"₹{analysis['tax_amount']:,.2f}"
                            ]
                        })
                        st.dataframe(expense_data, hide_index=True, use_container_width=True)
                    
                    # ROI visualization
                    st.subheader("5-Year Return Projection")
                    
                    # Create stacked bar for 5-year projection
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Calculate 5-year values
                    rental_income_5yr = analysis['net_annual_income'] * 5
                    appreciation_5yr = analysis['potential_appreciation']
                    total_return_5yr = rental_income_5yr + appreciation_5yr
                    roi_percentage = (total_return_5yr / property_price) * 100
                    
                    # Create data
                    categories = ['Initial Investment', 'Total 5-Year Return']
                    values = [property_price, property_price + total_return_5yr]
                    colors = ['#8f97de', '#6eb57e']
                    
                    # Plot bars
                    ax.bar(categories, values, color=colors, width=0.4)
                    
                    # Add value labels
                    for i, v in enumerate(values):
                        ax.text(i, v * 1.01, f"₹{v:,.0f}", ha='center')
                    
                    # Add components to the second bar
                    ax.text(1, property_price * 0.5, f"Initial: ₹{property_price:,.0f}", ha='center')
                    ax.text(1, property_price + rental_income_5yr * 0.5, f"Rental: ₹{rental_income_5yr:,.0f}", ha='center')
                    ax.text(1, property_price + rental_income_5yr + appreciation_5yr * 0.5, 
                          f"Appreciation: ₹{appreciation_5yr:,.0f}", ha='center')
                    
                    ax.set_ylabel("Amount (₹)")
                    ax.set_title(f"5-Year Investment Return (ROI: {roi_percentage:.2f}%)")
                    
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
                    
                    # Investment metrics
                    st.subheader("Investment Metrics")
                    
                    metrics_data = pd.DataFrame({
                        "Metric": ["Price-to-Rent Ratio", "Monthly ROI", "5-Year Total ROI", "Projected Value in 5 Years"],
                        "Value": [
                            f"{analysis['price_to_rent_ratio']:.2f}",
                            f"{(analysis['net_annual_income']/12) / property_price * 100:.2f}%",
                            f"{roi_percentage:.2f}%",
                            f"₹{analysis['future_value_5yr']:,.2f}"
                        ]
                    })
                    st.dataframe(metrics_data, hide_index=True, use_container_width=True)
                    
                    # Interpretation
                    st.subheader("Analysis")
                    
                    price_rent_ratio = analysis['price_to_rent_ratio']
                    if price_rent_ratio < 15:
                        st.success(f"✅ With a price-to-rent ratio of {price_rent_ratio:.1f}, this property is an **excellent rental investment**. Properties with ratios below 15 typically generate strong cash flow.")
                    elif price_rent_ratio < 20:
                        st.info(f"ℹ️ With a price-to-rent ratio of {price_rent_ratio:.1f}, this property is a **good rental investment**. Properties with ratios between 15-20 typically generate decent cash flow.")
                    elif price_rent_ratio < 25:
                        st.warning(f"⚠️ With a price-to-rent ratio of {price_rent_ratio:.1f}, this property is a **moderate rental investment**. Cash flow may be limited and you'll rely more on appreciation for returns.")
                    else:
                        st.error(f"❌ With a price-to-rent ratio of {price_rent_ratio:.1f}, this property is **not ideal for rental income**. Cash flow will be minimal or negative, and you'll be heavily dependent on appreciation.")
                    
                    # Recommendation based on yield
                    if analysis['net_yield'] > 7:
                        st.success(f"With a net yield of {analysis['net_yield']:.2f}%, this property offers excellent rental returns compared to the Indian market average of 3-4%.")
                    elif analysis['net_yield'] > 5:
                        st.info(f"With a net yield of {analysis['net_yield']:.2f}%, this property offers above-average rental returns compared to the Indian market average of 3-4%.")
                    elif analysis['net_yield'] > 3:
                        st.warning(f"With a net yield of {analysis['net_yield']:.2f}%, this property offers average rental returns for the Indian market.")
                    else:
                        st.error(f"With a net yield of {analysis['net_yield']:.2f}%, this property offers below-average rental returns. Consider negotiating the purchase price or finding ways to increase rental income.")
        
        # Tab 2: Portfolio Tracker
        with tab2:
            st.header("Real Estate Portfolio Tracker")
            st.write("Track and analyze your entire real estate investment portfolio.")
            
            # Initialize session state for portfolio if it doesn't exist
            if 'portfolio' not in st.session_state:
                st.session_state.portfolio = []
            
            # Portfolio summary
            if st.session_state.portfolio:
                portfolio_analysis = self.analyze_portfolio(st.session_state.portfolio)
                
                # Portfolio metrics
                col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
                
                with col_metrics1:
                    st.metric("Total Value", f"₹{portfolio_analysis['total_value']:,.0f}")
                
                with col_metrics2:
                    st.metric("Monthly Income", f"₹{portfolio_analysis['total_monthly_income']:,.0f}")
                
                with col_metrics3:
                    st.metric("Annual Income", f"₹{portfolio_analysis['total_annual_income']:,.0f}")
                
                with col_metrics4:
                    st.metric("Average Yield", f"{portfolio_analysis['average_yield']:.2f}%")
                
                # Portfolio visualization
                st.subheader("Portfolio Distribution")
                
                col_chart1, col_chart2 = st.columns([1, 1])
                
                with col_chart1:
                    # City distribution pie chart
                    city_dist = portfolio_analysis['city_distribution']
                    if city_dist:
                        fig1, ax1 = plt.subplots(figsize=(8, 5))
                        ax1.pie(city_dist.values(), labels=city_dist.keys(), autopct='%1.1f%%',
                              startangle=90, colors=plt.cm.Paired(np.linspace(0, 1, len(city_dist))))
                        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                        ax1.set_title('Portfolio Distribution by City')
                        st.pyplot(fig1)
                
                with col_chart2:
                    # Property type distribution pie chart
                    type_dist = portfolio_analysis['type_distribution']
                    if type_dist:
                        fig2, ax2 = plt.subplots(figsize=(8, 5))
                        ax2.pie(type_dist.values(), labels=type_dist.keys(), autopct='%1.1f%%',
                              startangle=90, colors=plt.cm.Set3(np.linspace(0, 1, len(type_dist))))
                        ax2.axis('equal')
                        ax2.set_title('Portfolio Distribution by Property Type')
                        st.pyplot(fig2)
                
                # Properties table
                st.subheader("Your Properties")
                
                property_data = []
                for i, prop in enumerate(st.session_state.portfolio):
                    property_data.append({
                        "ID": i+1,
                        "Name": prop.get('name', f"Property {i+1}"),
                        "Type": prop.get('type', 'Residential'),
                        "Location": f"{prop.get('area', '')}, {prop.get('city', '')}",
                        "Value": f"₹{prop['price']:,.0f}",
                        "Monthly Rent": f"₹{prop['monthly_rent']:,.0f}",
                        "Net Yield": f"{prop.get('net_yield', 0):.2f}%",
                        "Annual Expenses": f"₹{prop.get('annual_expenses', 0):,.0f}"
                    })
                
                property_df = pd.DataFrame(property_data)
                st.dataframe(property_df, hide_index=True, use_container_width=True)
                
                # Delete property option
                col_delete1, col_delete2 = st.columns([1, 3])
                with col_delete1:
                    delete_id = st.number_input("Property ID to remove", min_value=1, 
                                             max_value=len(st.session_state.portfolio), step=1)
                with col_delete2:
                    if st.button("Remove Property"):
                        if 1 <= delete_id <= len(st.session_state.portfolio):
                            st.session_state.portfolio.pop(delete_id - 1)
                            st.success(f"Property {delete_id} removed from portfolio.")
                            st.experimental_rerun()
            
            # Add new property form
            st.subheader("Add New Property")
            
            with st.expander("Add new property to portfolio"):
                col_new1, col_new2 = st.columns([1, 1])
                
                with col_new1:
                    new_name = st.text_input("Property Name", value="New Property")
                    new_type = st.selectbox("Property Type", 
                                         ["Residential", "Commercial", "Land", "Industrial", "Mixed-Use"])
                    new_price = st.number_input("Purchase Price (₹)", min_value=100000, value=5000000, step=100000)
                    new_monthly_rent = st.number_input("Monthly Rent (₹)", min_value=0, value=25000, step=1000)
                
                with col_new2:
                    new_city = st.selectbox("City", 
                                         ["Mumbai", "Bangalore", "Hyderabad", "Delhi-NCR", "Pune", "Chennai", "Kolkata", "Other"])
                    new_area = st.text_input("Area/Locality", value="")
                    new_size = st.number_input("Size (sq.ft)", min_value=1, value=1200)
                    new_occupancy = st.slider("Expected Occupancy (%)", min_value=70, max_value=100, value=95)
                
                if st.button("Add to Portfolio"):
                    new_property = {
                        'name': new_name,
                        'type': new_type,
                        'price': new_price,
                        'monthly_rent': new_monthly_rent,
                        'city': new_city,
                        'area': new_area,
                        'size': new_size,
                        'occupancy_rate': new_occupancy
                    }
                    
                    st.session_state.portfolio.append(new_property)
                    st.success(f"Added {new_name} to your portfolio!")
                    st.experimental_rerun()
            
            # Clear portfolio option
            if st.session_state.portfolio and st.button("Clear Entire Portfolio"):
                st.session_state.portfolio = []
                st.warning("Portfolio cleared.")
                st.experimental_rerun()
            
            # Sample portfolio option
            if not st.session_state.portfolio and st.button("Load Sample Portfolio"):
                sample_portfolio = [
                    {
                        'name': 'Garden Apartment',
                        'type': 'Residential',
                        'price': 7500000,
                        'monthly_rent': 35000,
                        'city': 'Bangalore',
                        'area': 'HSR Layout',
                        'size': 1250,
                        'occupancy_rate': 95
                    },
                    {
                        'name': 'Office Space',
                        'type': 'Commercial',
                        'price': 12000000,
                        'monthly_rent': 80000,
                        'city': 'Mumbai',
                        'area': 'Andheri East',
                        'size': 800,
                        'occupancy_rate': 90
                    },
                    {
                        'name': 'Luxury Villa',
                        'type': 'Residential',
                        'price': 20000000,
                        'monthly_rent': 90000,
                        'city': 'Hyderabad',
                        'area': 'Banjara Hills',
                        'size': 3200,
                        'occupancy_rate': 85
                    }
                ]
                st.session_state.portfolio = sample_portfolio
                st.success("Sample portfolio loaded!")
                st.experimental_rerun()
                
        # Tab 2: Risk Analysis with Monte Carlo Simulation
        with tab2:
            st.header("Monte Carlo Investment Risk Analysis")
            st.write("Simulate thousands of possible investment outcomes to understand risk and potential returns.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Property Details")
                mc_property_price = st.number_input("Property Price (₹)", min_value=1000000, max_value=100000000, 
                                              value=7500000, step=500000, format="%d", key="mc_price")
                mc_monthly_rent = st.number_input("Monthly Rent (₹)", min_value=5000, max_value=1000000, 
                                            value=35000, step=1000, format="%d", key="mc_rent")
                mc_loan_percentage = st.slider("Loan Percentage (%)", min_value=0, max_value=90, value=80, step=5, key="mc_loan")
                mc_interest_rate = st.slider("Loan Interest Rate (%)", min_value=6.0, max_value=12.0, value=8.5, step=0.1, key="mc_interest")
            
            with col2:
                st.subheader("Simulation Parameters")
                mc_years = st.slider("Investment Horizon (Years)", min_value=5, max_value=30, value=10, step=1)
                mc_simulations = st.select_slider("Number of Simulations", options=[100, 500, 1000, 2000, 5000], value=1000)
                
                st.subheader("Market Variables")
                mc_appreciation_mean = st.slider("Avg. Annual Appreciation (%)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
                mc_appreciation_std = st.slider("Appreciation Volatility (%)", min_value=1.0, max_value=8.0, value=3.0, step=0.5)
            
            # First-time user help tooltip
            if 'monte_carlo_tooltip' not in st.session_state:
                st.session_state.monte_carlo_tooltip = True
                st.info("ℹ️ **What is Monte Carlo analysis?** This simulation runs thousands of scenarios with different random variables to help you understand the range of possible investment outcomes and assess risk.")
            
            if st.button("Run Monte Carlo Simulation"):
                with st.spinner(f"Running {mc_simulations} simulations over {mc_years} years..."):
                    # Run the simulation
                    simulation_results = self.run_monte_carlo_simulation(
                        property_price=mc_property_price,
                        monthly_rent=mc_monthly_rent,
                        years=mc_years,
                        simulations=mc_simulations,
                        appreciation_mean=mc_appreciation_mean,
                        appreciation_std=mc_appreciation_std,
                        interest_rate=mc_interest_rate,
                        loan_percentage=mc_loan_percentage
                    )
                    
                    # Display key metrics
                    st.subheader("Simulation Results")
                    
                    col_results1, col_results2, col_results3, col_results4 = st.columns(4)
                    
                    with col_results1:
                        st.metric(
                            "Median ROI", 
                            f"{simulation_results['median_roi']:.1f}%",
                            help="Median return on investment after the specified time period"
                        )
                    
                    with col_results2:
                        st.metric(
                            "Mean Annual Return", 
                            f"{simulation_results['mean_annual_return']:.1f}%", 
                            help="Average annualized return on investment"
                        )
                    
                    with col_results3:
                        st.metric(
                            "Loss Probability", 
                            f"{simulation_results['loss_probability']:.1f}%",
                            help="Probability of a negative return on investment"
                        )
                    
                    with col_results4:
                        st.metric(
                            "Value at Risk (95%)", 
                            f"{abs(simulation_results['var_95']):.1f}%",
                            help="Maximum expected loss at 95% confidence level"
                        )
                    
                    # ROI Distribution Histogram
                    st.subheader("Return on Investment Distribution")
                    
                    # Create ROI histogram
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Plot histogram with KDE
                    sns.histplot(simulation_results['all_rois'], bins=30, kde=True, ax=ax, color='skyblue')
                    
                    # Add vertical lines for key statistics
                    ax.axvline(x=simulation_results['median_roi'], color='red', linestyle='-', label=f"Median ROI: {simulation_results['median_roi']:.1f}%")
                    ax.axvline(x=simulation_results['p10_roi'], color='orange', linestyle='--', label=f"10th Percentile: {simulation_results['p10_roi']:.1f}%")
                    ax.axvline(x=simulation_results['p90_roi'], color='green', linestyle='--', label=f"90th Percentile: {simulation_results['p90_roi']:.1f}%")
                    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
                    
                    ax.set_xlabel('Return on Investment (%)')
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'Distribution of ROI after {mc_years} Years ({mc_simulations} Simulations)')
                    ax.legend()
                    
                    st.pyplot(fig)
                    
                    # Property value and cash flow projections
                    st.subheader("Investment Projections Over Time")
                    
                    col_charts1, col_charts2 = st.columns([1, 1])
                    
                    with col_charts1:
                        # Property value projection
                        fig2, ax2 = plt.subplots(figsize=(8, 5))
                        
                        years_range = list(range(1, mc_years + 1))
                        property_values = simulation_results['mean_yearly_property_values']
                        
                        ax2.plot(years_range, property_values, marker='o', linewidth=2, color='#6eb57e')
                        ax2.fill_between(
                            years_range, 
                            [mc_property_price * (1 + simulation_results['p10_roi']/100/mc_years * y) for y in years_range],
                            [mc_property_price * (1 + simulation_results['p90_roi']/100/mc_years * y) for y in years_range],
                            alpha=0.2, color='#6eb57e'
                        )
                        
                        # Format y-axis to show in lakhs/crores
                        def lakh_crore_formatter(x, pos):
                            if x >= 10000000:
                                return f'₹{x/10000000:.1f}Cr'
                            elif x >= 100000:
                                return f'₹{x/100000:.1f}L'
                            else:
                                return f'₹{x:.0f}'
                                
                        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lakh_crore_formatter))
                        
                        ax2.set_xlabel('Year')
                        ax2.set_ylabel('Property Value')
                        ax2.set_title('Projected Property Value Growth')
                        ax2.grid(alpha=0.3)
                        
                        st.pyplot(fig2)
                        
                    with col_charts2:
                        # Annual cash flow projection
                        fig3, ax3 = plt.subplots(figsize=(8, 5))
                        
                        cash_flows = simulation_results['mean_yearly_cash_flows']
                        
                        # Plot the line chart with markers
                        ax3.plot(years_range, cash_flows, marker='o', linewidth=2, color='#428bca')
                        
                        # Fill between to indicate variability
                        ax3.fill_between(
                            years_range, 
                            [cf * 0.7 for cf in cash_flows], 
                            [cf * 1.3 for cf in cash_flows], 
                            alpha=0.2, color='#428bca'
                        )
                        
                        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lakh_crore_formatter))
                        
                        ax3.set_xlabel('Year')
                        ax3.set_ylabel('Annual Cash Flow')
                        ax3.set_title('Projected Annual Cash Flow')
                        ax3.grid(alpha=0.3)
                        
                        st.pyplot(fig3)
                    
                    # Probability metrics
                    st.subheader("Achievement Probabilities")
                    
                    col_prob1, col_prob2, col_prob3 = st.columns(3)
                    
                    with col_prob1:
                        st.metric(
                            "Probability of >20% ROI", 
                            f"{simulation_results['prob_roi_above_20']:.1f}%"
                        )
                        
                    with col_prob2:
                        st.metric(
                            "Probability of >50% ROI", 
                            f"{simulation_results['prob_roi_above_50']:.1f}%"
                        )
                        
                    with col_prob3:
                        st.metric(
                            "Probability of >100% ROI", 
                            f"{simulation_results['prob_roi_above_100']:.1f}%"
                        )
                    
                    # Risk assessment
                    st.subheader("Risk Assessment")
                    
                    # Determine risk level based on simulation results
                    loss_prob = simulation_results['loss_probability']
                    roi_vol = (simulation_results['p90_roi'] - simulation_results['p10_roi']) / simulation_results['median_roi'] * 100 if simulation_results['median_roi'] != 0 else 0
                    
                    if loss_prob < 5 and roi_vol < 50:
                        risk_level = "Low"
                        risk_color = "green"
                    elif loss_prob < 15 and roi_vol < 100:
                        risk_level = "Medium"
                        risk_color = "orange"
                    else:
                        risk_level = "High"
                        risk_color = "red"
                    
                    st.markdown(f"<h3 style='color:{risk_color}'>Risk Level: {risk_level}</h3>", unsafe_allow_html=True)
                    
                    # Risk factors explanation
                    st.markdown(f"""
                    **Key Risk Factors:**
                    - **Volatility:** The spread between best and worst outcomes is {roi_vol:.1f}% of the median return
                    - **Loss Probability:** {loss_prob:.1f}% chance of negative returns
                    - **Value at Risk:** You could lose up to {abs(simulation_results['var_95']):.1f}% of your investment in adverse scenarios
                    """)
                    
                    # Risk mitigation recommendations
                    with st.expander("Risk Mitigation Strategies"):
                        st.write("""
                        ### Strategies to Mitigate Investment Risk
                        
                        #### For High Risk Investments:
                        - **Extend Investment Horizon:** Longer holding periods typically reduce volatility
                        - **Income Focus:** Place greater emphasis on rental income rather than appreciation
                        - **Diversification:** Consider investing in multiple smaller properties across different locations
                        - **Professional Management:** Hire professional property management to ensure consistent occupancy
                        - **Insurance:** Ensure comprehensive insurance coverage for property and rent loss
                        
                        #### For Medium Risk Investments:
                        - **Regular Reviews:** Conduct annual performance reviews and market assessments
                        - **Capital Improvements:** Strategic renovations to boost rental income
                        - **Fixed-Rate Financing:** Consider fixed-rate loans to protect against interest rate fluctuations
                        - **Tenant Quality:** Focus on high-quality tenant screening to reduce vacancy risk
                        
                        #### For Low Risk Investments:
                        - **Performance Optimization:** Focus on minimizing costs and maximizing rent
                        - **Reinvestment:** Consider reinvesting a portion of rental income into property improvements
                        - **Long-Term Leases:** Secure longer lease terms with reliable tenants
                        """)
                    
                    # Investment confidence score
                    confidence_score = 0
                    # Calculate based on simulation results (higher is better)
                    confidence_score += (100 - loss_prob) * 0.4  # Lower loss probability is better
                    confidence_score += min(simulation_results['median_roi'], 100) * 0.3  # Higher median ROI is better (capped at 100)
                    confidence_score -= min(abs(simulation_results['var_95']), 50) * 0.3  # Lower VaR is better
                    confidence_score = max(0, min(100, confidence_score))  # Clamp between 0-100
                    
                    # Display confidence score gauge
                    st.subheader("Investment Confidence Score")
                    
                    # Create gauge figure
                    fig4, ax4 = plt.subplots(figsize=(10, 2))
                    
                    # Determine color based on score
                    if confidence_score >= 70:
                        gauge_color = '#5cb85c'  # Green
                    elif confidence_score >= 40:
                        gauge_color = '#f0ad4e'  # Orange
                    else:
                        gauge_color = '#d9534f'  # Red
                        
                    # Draw gauge
                    ax4.barh(0, 100, color='#e6e6e6', height=0.6)
                    ax4.barh(0, confidence_score, color=gauge_color, height=0.6)
                    
                    # Add score text
                    ax4.text(confidence_score, 0, f'{confidence_score:.0f}', ha='center', va='center', fontweight='bold')
                    
                    # Configure gauge chart appearance
                    ax4.set_xlim(0, 100)
                    ax4.set_ylim(-0.5, 0.5)
                    ax4.set_yticks([])
                    ax4.set_xticks([0, 25, 50, 75, 100])
                    ax4.set_xticklabels(['0', 'Low', 'Medium', 'Good', 'Excellent'])
                    ax4.spines['top'].set_visible(False)
                    ax4.spines['right'].set_visible(False)
                    ax4.spines['left'].set_visible(False)
                    
                    st.pyplot(fig4)
        
        # Tab 3: Review & Sentiment Analysis (new feature)
        with tab3:
            st.header("Area Review Sentiment Analysis")
            st.write("Analyze sentiment in property reviews and area feedback to identify promising locations.")
            
            # Show sample data selection
            analysis_type = st.radio(
                "Select analysis type:",
                ["Pre-analyzed Data", "Real-time Analysis"],
                horizontal=True
            )
            
            if analysis_type == "Pre-analyzed Data":
                # City selection for pre-analyzed data
                cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]
                selected_city = st.selectbox("Select City", cities, key="sentiment_city")
                
                # Show pre-computed sentiment analysis results by area
                st.subheader(f"Review Sentiment Analysis for {selected_city}")
                
                # Create sample sentiment data based on the selected city
                sentiment_data = []
                
                if selected_city == "Mumbai":
                    sentiment_data = [
                        {"area": "Bandra", "positive": 85, "neutral": 10, "negative": 5, "avg_rating": 4.6},
                        {"area": "Andheri", "positive": 68, "neutral": 22, "negative": 10, "avg_rating": 4.1},
                        {"area": "Worli", "positive": 82, "neutral": 12, "negative": 6, "avg_rating": 4.5},
                        {"area": "Powai", "positive": 75, "neutral": 15, "negative": 10, "avg_rating": 4.3},
                        {"area": "Juhu", "positive": 80, "neutral": 12, "negative": 8, "avg_rating": 4.4}
                    ]
                elif selected_city == "Bangalore":
                    sentiment_data = [
                        {"area": "Whitefield", "positive": 72, "neutral": 18, "negative": 10, "avg_rating": 4.2},
                        {"area": "Electronic City", "positive": 65, "neutral": 25, "negative": 10, "avg_rating": 4.0},
                        {"area": "Koramangala", "positive": 88, "neutral": 7, "negative": 5, "avg_rating": 4.7},
                        {"area": "Indiranagar", "positive": 85, "neutral": 10, "negative": 5, "avg_rating": 4.6},
                        {"area": "HSR Layout", "positive": 82, "neutral": 12, "negative": 6, "avg_rating": 4.5}
                    ]
                elif selected_city == "Hyderabad":
                    sentiment_data = [
                        {"area": "Gachibowli", "positive": 78, "neutral": 12, "negative": 10, "avg_rating": 4.4},
                        {"area": "HITEC City", "positive": 75, "neutral": 15, "negative": 10, "avg_rating": 4.3},
                        {"area": "Banjara Hills", "positive": 90, "neutral": 7, "negative": 3, "avg_rating": 4.8},
                        {"area": "Jubilee Hills", "positive": 88, "neutral": 8, "negative": 4, "avg_rating": 4.7},
                        {"area": "Madhapur", "positive": 70, "neutral": 18, "negative": 12, "avg_rating": 4.1}
                    ]
                elif selected_city == "Pune":
                    sentiment_data = [
                        {"area": "Kothrud", "positive": 80, "neutral": 12, "negative": 8, "avg_rating": 4.4},
                        {"area": "Hinjewadi", "positive": 68, "neutral": 20, "negative": 12, "avg_rating": 4.0},
                        {"area": "Viman Nagar", "positive": 75, "neutral": 15, "negative": 10, "avg_rating": 4.3},
                        {"area": "Baner", "positive": 78, "neutral": 14, "negative": 8, "avg_rating": 4.4},
                        {"area": "Aundh", "positive": 82, "neutral": 12, "negative": 6, "avg_rating": 4.5}
                    ]
                else:  # Delhi-NCR
                    sentiment_data = [
                        {"area": "Gurgaon", "positive": 75, "neutral": 15, "negative": 10, "avg_rating": 4.3},
                        {"area": "Noida", "positive": 72, "neutral": 18, "negative": 10, "avg_rating": 4.2},
                        {"area": "Greater Noida", "positive": 65, "neutral": 20, "negative": 15, "avg_rating": 3.9},
                        {"area": "Dwarka", "positive": 78, "neutral": 12, "negative": 10, "avg_rating": 4.4},
                        {"area": "Faridabad", "positive": 60, "neutral": 25, "negative": 15, "avg_rating": 3.8}
                    ]
                
                # Display sentiment analysis in a table
                sentiment_df = pd.DataFrame(sentiment_data)
                
                # Calculate sentiment score (scale of 0-10)
                sentiment_df["sentiment_score"] = (sentiment_df["positive"] * 0.1 + 
                                               sentiment_df["avg_rating"] * 1.5).round(1)
                
                # Sort by sentiment score
                sentiment_df = sentiment_df.sort_values("sentiment_score", ascending=False)
                
                # Format for display
                display_df = sentiment_df.copy()
                display_df["positive"] = display_df["positive"].apply(lambda x: f"{x}%")
                display_df["neutral"] = display_df["neutral"].apply(lambda x: f"{x}%")
                display_df["negative"] = display_df["negative"].apply(lambda x: f"{x}%")
                
                # Display table
                st.dataframe(
                    display_df.rename(columns={
                        "area": "Area", 
                        "positive": "Positive", 
                        "neutral": "Neutral", 
                        "negative": "Negative", 
                        "avg_rating": "Avg. Rating (1-5)", 
                        "sentiment_score": "Sentiment Score (0-10)"
                    }), 
                    hide_index=True
                )
                
                # Visualize sentiment comparison
                st.subheader("Sentiment Comparison by Area")
                
                # Create comparison chart
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Bar chart data
                areas = sentiment_df["area"].tolist()
                x = range(len(areas))
                width = 0.25
                
                # Create grouped bars
                ax.bar(x, sentiment_df["positive"], width, label='Positive', color='#5cb85c')
                ax.bar([i + width for i in x], sentiment_df["neutral"], width, label='Neutral', color='#f0ad4e')
                ax.bar([i + width*2 for i in x], sentiment_df["negative"], width, label='Negative', color='#d9534f')
                
                # Configure chart
                ax.set_xticks([i + width for i in x])
                ax.set_xticklabels(areas)
                ax.set_ylabel('Percentage (%)')
                ax.set_title(f'Review Sentiment Analysis by Area in {selected_city}')
                ax.legend()
                
                plt.tight_layout()
                st.pyplot(fig)
                
                # Key insights based on sentiment analysis
                st.subheader("Key Insights")
                
                top_area = sentiment_df.iloc[0]["area"]
                bottom_area = sentiment_df.iloc[-1]["area"]
                
                st.markdown(f"""
                **Investment Recommendations Based on Sentiment Analysis:**
                
                - **{top_area}** shows the highest positive sentiment ({sentiment_df.iloc[0]['positive']}%), making it an attractive investment area.
                - **{bottom_area}** has comparatively lower positive sentiment, indicating potential issues to investigate.
                - Areas with high positive sentiment typically correlate with better tenant demand and price appreciation.
                
                **Common Positive Themes:**
                - Connectivity and accessibility
                - Social infrastructure (schools, hospitals, markets)
                - Security and safety
                - Green spaces and parks
                
                **Common Negative Themes:**
                - Traffic congestion
                - Noise pollution
                - Construction activity
                - Water supply issues
                """)
                
                # Review examples with sentiment
                with st.expander("Sample Reviews with Sentiment"):
                    # Display sample reviews for the top area
                    st.markdown(f"### Sample Reviews for {top_area}")
                    
                    # Generate synthetic positive reviews
                    positive_reviews = [
                        {"text": f"Absolutely love living in {top_area}. Great connectivity, excellent amenities, and very safe environment for families.", "sentiment": "Positive"},
                        {"text": f"Best decision to buy property in {top_area}. Property values have consistently increased over the last 3 years.", "sentiment": "Positive"},
                        {"text": f"{top_area} has fantastic schools and hospitals nearby. No need to travel far for essentials.", "sentiment": "Positive"}
                    ]
                    
                    # Generate some neutral/negative reviews
                    mixed_reviews = [
                        {"text": f"{top_area} is good but traffic during peak hours can be a problem. Still better than most areas though.", "sentiment": "Neutral"},
                        {"text": f"Water supply issues in parts of {top_area} during summer months, but overall a decent place to live.", "sentiment": "Mixed"}
                    ]
                    
                    # Display reviews with sentiment color coding
                    for review in positive_reviews + mixed_reviews:
                        if review["sentiment"] == "Positive":
                            st.markdown(f"<div style='padding:10px; border-left:3px solid green; margin-bottom:10px;'>{review['text']} <br/><small><b style='color:green;'>{review['sentiment']}</b></small></div>", unsafe_allow_html=True)
                        elif review["sentiment"] == "Neutral":
                            st.markdown(f"<div style='padding:10px; border-left:3px solid orange; margin-bottom:10px;'>{review['text']} <br/><small><b style='color:orange;'>{review['sentiment']}</b></small></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='padding:10px; border-left:3px solid gray; margin-bottom:10px;'>{review['text']} <br/><small><b style='color:gray;'>{review['sentiment']}</b></small></div>", unsafe_allow_html=True)
            
            else:  # Real-time Analysis
                st.subheader("Real-time Review Sentiment Analysis")
                st.write("Analyze sentiment in property reviews by entering text or uploading review data.")
                
                # Text area for manual review entry
                review_text = st.text_area(
                    "Enter review text to analyze:", 
                    "The property in Koramangala is excellent. Great location with good connectivity. The neighborhood is safe and clean with parks nearby. Rental demand is consistently high."
                )
                
                if st.button("Analyze Sentiment"):
                    # Simulate sentiment analysis processing
                    with st.spinner("Analyzing sentiment..."):
                        # For demo purposes, just use a simple keyword-based sentiment scoring
                        positive_words = ["excellent", "great", "good", "best", "safe", "clean", "high", "consistent", "modern"]
                        negative_words = ["issue", "problem", "traffic", "noise", "congestion", "poor", "bad", "worse", "expensive"]
                        
                        # Count positive and negative words
                        positive_count = sum(word.lower() in review_text.lower() for word in positive_words)
                        negative_count = sum(word.lower() in review_text.lower() for word in negative_words)
                        
                        # Calculate basic sentiment score
                        total_count = positive_count + negative_count
                        if total_count == 0:
                            sentiment_percent = 50  # Neutral
                        else:
                            sentiment_percent = int((positive_count / total_count) * 100)
                            
                        # Determine sentiment category
                        if sentiment_percent >= 75:
                            sentiment = "Positive"
                            color = "green"
                        elif sentiment_percent >= 40:
                            sentiment = "Neutral"
                            color = "orange"
                        else:
                            sentiment = "Negative"
                            color = "red"
                            
                        # Display result with progress bar
                        st.subheader("Sentiment Analysis Result")
                        st.markdown(f"<h4 style='color:{color}'>Sentiment: {sentiment}</h4>", unsafe_allow_html=True)
                        
                        # Progress bar visualization
                        st.progress(sentiment_percent/100)
                        st.write(f"Positive sentiment: {sentiment_percent}%")
                        
                        # Display key phrases
                        st.subheader("Key Phrases Detected")
                        
                        # Extract some key phrases (just use positive/negative words found in text for demo)
                        positive_found = [word for word in positive_words if word.lower() in review_text.lower()]
                        negative_found = [word for word in negative_words if word.lower() in review_text.lower()]
                        
                        if positive_found:
                            st.markdown("**Positive mentions:**")
                            for phrase in positive_found:
                                st.markdown(f"- {phrase.title()}")
                                
                        if negative_found:
                            st.markdown("**Negative mentions:**")
                            for phrase in negative_found:
                                st.markdown(f"- {phrase.title()}")
                                
                        # Investment implications based on sentiment
                        st.subheader("Investment Implications")
                        
                        if sentiment == "Positive":
                            st.success("This area appears to have strong positive sentiment, suggesting good investment potential.")
                        elif sentiment == "Neutral":
                            st.warning("This area has mixed reviews. Consider additional research before investing.")
                        else:
                            st.error("The negative sentiment suggests caution is warranted for investments in this area.")
        
        # Tab 4: Tax Optimization
        with tab4:
            st.header("Rental Property Tax Optimization")
            st.write("Analyze tax strategies for your rental property investments.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Property Details")
                tax_property_price = st.number_input("Property Price (₹)", min_value=1000000, max_value=100000000,
                                                 value=7500000, step=500000, format="%d", key="tax_price")
                tax_monthly_rent = st.number_input("Monthly Rent (₹)", min_value=5000, max_value=1000000,
                                               value=35000, step=1000, format="%d", key="tax_rent")
            
            with col2:
                st.subheader("Loan Details")
                tax_interest_rate = st.slider("Loan Interest Rate (%)", min_value=6.0, max_value=12.0, value=8.5, step=0.1)
                tax_loan_percentage = st.slider("Loan Percentage (%)", min_value=0, max_value=90, value=80, step=5)
                tax_loan_term = st.slider("Loan Term (Years)", min_value=5, max_value=30, value=20, step=1)
            
            if st.button("Analyze Tax Optimization"):
                with st.spinner("Calculating tax optimization strategies..."):
                    analysis = self.calculate_tax_optimization(
                        tax_property_price,
                        tax_monthly_rent,
                        interest_rate=tax_interest_rate,
                        loan_percentage=tax_loan_percentage,
                        loan_term=tax_loan_term
                    )
                    
                    # Display results
                    st.subheader("Tax Optimization Results")
                    
                    # Tax savings metrics
                    col_results1, col_results2, col_results3 = st.columns(3)
                    
                    with col_results1:
                        st.metric("Annual Tax Savings", f"₹{analysis['tax_savings']:,.2f}")
                    
                    with col_results2:
                        st.metric("ROI Without Loan", f"{analysis['roi_without_loan']:.2f}%")
                    
                    with col_results3:
                        st.metric("ROI With Loan", f"{analysis['roi_with_loan']:.2f}%")
                    
                    # Visualization of tax differences
                    st.subheader("Tax Impact Comparison")
                    
                    # Create comparison chart
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Data for visualization
                    categories = ['Without Loan', 'With Loan']
                    taxable_incomes = [analysis['taxable_income_without_loan'], analysis['taxable_income_with_loan']]
                    taxes = [analysis['tax_without_loan'], analysis['tax_with_loan']]
                    net_incomes = [analysis['net_income_without_loan'], analysis['net_income_with_loan']]
                    
                    # Plot bars
                    x = np.arange(len(categories))
                    width = 0.35
                    
                    ax.bar(x - width/2, taxable_incomes, width, label='Taxable Income', color='skyblue')
                    ax.bar(x + width/2, taxes, width, label='Tax Amount', color='salmon')
                    
                    # Add values on bars
                    for i, v in enumerate(taxable_incomes):
                        ax.text(i - width/2, v * 1.01, f"₹{v:,.0f}", ha='center')
                    
                    for i, v in enumerate(taxes):
                        ax.text(i + width/2, v * 1.01, f"₹{v:,.0f}", ha='center')
                    
                    # Configure chart
                    ax.set_ylabel('Amount (₹)')
                    ax.set_title('Taxable Income and Tax Amount Comparison')
                    ax.set_xticks(x)
                    ax.set_xticklabels(categories)
                    ax.legend()
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Detailed breakdown
                    st.subheader("Detailed Financial Breakdown")
                    
                    # Income and deductions
                    col_breakdown1, col_breakdown2 = st.columns([1, 1])
                    
                    with col_breakdown1:
                        st.write("**Scenario 1: Without Loan**")
                        data1 = pd.DataFrame({
                            "Item": [
                                "Annual Rental Income",
                                "Standard Deduction (30%)",
                                "Property Tax",
                                "Insurance",
                                "Taxable Income",
                                "Tax Amount (30%)",
                                "Net Income After Tax"
                            ],
                            "Amount": [
                                f"₹{analysis['annual_rent']:,.2f}",
                                f"₹{analysis['standard_deduction']:,.2f}",
                                f"₹{analysis['property_tax']:,.2f}",
                                f"₹{analysis['insurance']:,.2f}",
                                f"₹{analysis['taxable_income_without_loan']:,.2f}",
                                f"₹{analysis['tax_without_loan']:,.2f}",
                                f"₹{analysis['net_income_without_loan']:,.2f}"
                            ]
                        })
                        st.dataframe(data1, hide_index=True, use_container_width=True)
                    
                    with col_breakdown2:
                        st.write("**Scenario 2: With Home Loan**")
                        data2 = pd.DataFrame({
                            "Item": [
                                "Annual Rental Income",
                                "Standard Deduction (30%)",
                                "Property Tax",
                                "Insurance",
                                "Interest Payment",
                                "Taxable Income",
                                "Tax Amount (30%)",
                                "Net Income After Tax"
                            ],
                            "Amount": [
                                f"₹{analysis['annual_rent']:,.2f}",
                                f"₹{analysis['standard_deduction']:,.2f}",
                                f"₹{analysis['property_tax']:,.2f}",
                                f"₹{analysis['insurance']:,.2f}",
                                f"₹{analysis['annual_interest']:,.2f}",
                                f"₹{analysis['taxable_income_with_loan']:,.2f}",
                                f"₹{analysis['tax_with_loan']:,.2f}",
                                f"₹{analysis['net_income_with_loan']:,.2f}"
                            ]
                        })
                        st.dataframe(data2, hide_index=True, use_container_width=True)
                    
                    # Loan details
                    st.subheader("Loan Details")
                    loan_data = pd.DataFrame({
                        "Item": ["Loan Amount", "Monthly EMI", "Annual Interest Payment", "Loan Term"],
                        "Value": [
                            f"₹{analysis['loan_amount']:,.2f}",
                            f"₹{analysis['emi']:,.2f}",
                            f"₹{analysis['annual_interest']:,.2f}",
                            f"{tax_loan_term} years"
                        ]
                    })
                    st.dataframe(loan_data, hide_index=True, use_container_width=True)
                    
                    # ROI comparison
                    st.subheader("ROI Comparison")
                    
                    # Create ROI comparison chart
                    fig2, ax2 = plt.subplots(figsize=(8, 5))
                    
                    roi_data = [analysis['roi_without_loan'], analysis['roi_with_loan']]
                    bars = ax2.bar(categories, roi_data, color=['#5cb85c', '#428bca'])
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height * 1.01,
                               f'{height:.2f}%', ha='center', va='bottom')
                    
                    ax2.set_ylabel('ROI (%)')
                    ax2.set_title('ROI Comparison: Cash Purchase vs. Leveraged Investment')
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                    
                    # Recommendations
                    st.subheader("Tax Optimization Recommendations")
                    
                    if analysis['roi_with_loan'] > analysis['roi_without_loan'] * 1.5:
                        st.success(f"✅ **STRONG RECOMMENDATION**: Using a {tax_loan_percentage}% loan significantly increases your ROI from {analysis['roi_without_loan']:.2f}% to {analysis['roi_with_loan']:.2f}%. The interest deduction provides annual tax savings of ₹{analysis['tax_savings']:,.2f}.")
                    elif analysis['roi_with_loan'] > analysis['roi_without_loan']:
                        st.info(f"ℹ️ **RECOMMENDATION**: Using a {tax_loan_percentage}% loan increases your ROI from {analysis['roi_without_loan']:.2f}% to {analysis['roi_with_loan']:.2f}%. The interest deduction provides annual tax savings of ₹{analysis['tax_savings']:,.2f}.")
                    else:
                        st.warning(f"⚠️ **CAUTION**: While the loan provides tax savings of ₹{analysis['tax_savings']:,.2f}, your ROI is actually higher without a loan ({analysis['roi_without_loan']:.2f}% vs {analysis['roi_with_loan']:.2f}%). Consider a smaller loan or negotiate better interest rates.")
                    
                    # Additional tax tips
                    with st.expander("Additional Tax Optimization Tips for Rental Properties"):
                        st.write("""
                        ### Tax Optimization Strategies
                        
                        1. **Form a Private Limited Company** - Consider forming a company to hold properties for potentially lower tax rates (25% for companies with turnover under ₹400 crores vs 30% individual maximum rate).
                        
                        2. **Home Office Deduction** - If you manage your properties yourself, you may be eligible to deduct home office expenses.
                        
                        3. **Maintenance Timing** - Schedule major maintenance expenses in high-income years to offset higher taxes.
                        
                        4. **Depreciation Benefits** - Claim depreciation at 5% per annum on the building portion of your property value.
                        
                        5. **Joint Ownership** - Consider joint ownership with family members in lower tax brackets to split income.
                        
                        6. **Long-term Capital Gains** - Hold properties for over 2 years to benefit from lower long-term capital gains tax rates and indexation benefits.
                        
                        7. **Municipal Taxes** - Ensure you're claiming deduction for all municipal taxes paid.
                        
                        8. **Interest Timing** - Pre-pay interest when possible in high-income years.
                        
                        9. **Reinvestment under Section 54/54F** - Reinvest capital gains in new residential property to claim tax exemption.
                        
                        > **Disclaimer:** Tax laws change frequently. Consult a tax professional before implementing these strategies.
                        """)
                        