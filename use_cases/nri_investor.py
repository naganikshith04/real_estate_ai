"""
NRI (Non-Resident Indian) investor module for Real Estate AI.
Focuses on currency conversion, RERA compliance, and regulatory requirements.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from data_providers.location_analyzer import LocationAnalyzer

class NRIInvestorAnalysis:
    """NRI investor specialized analysis and dashboard components."""
    
    def __init__(self, data, processed):
        """Initialize with loaded data."""
        self.data = data
        self.processed = processed
        self.location_analyzer = LocationAnalyzer()
        
        # Currency exchange rates (as of March 2025)
        self.exchange_rates = {
            "USD": 83.50,  # US Dollar to INR
            "EUR": 90.25,  # Euro to INR
            "GBP": 105.75, # British Pound to INR
            "AED": 22.75,  # UAE Dirham to INR
            "SGD": 61.50,  # Singapore Dollar to INR
            "AUD": 54.25,  # Australian Dollar to INR
            "CAD": 60.80,  # Canadian Dollar to INR
        }
    
    def convert_currency(self, amount_inr, target_currency="USD"):
        """Convert INR to target currency."""
        if target_currency not in self.exchange_rates:
            return None
        
        return amount_inr / self.exchange_rates[target_currency]
    
    def analyze_rera_compliance(self, city, area, property_type="Residential"):
        """Check RERA compliance status for the area."""
        compliance_data = {
            "city": city,
            "area": area,
            "property_type": property_type,
            "rera_authority": "",
            "rera_website": "",
            "rera_coverage": 0,
            "compliance_score": 0
        }
        
        # RERA authorities by state
        rera_authorities = {
            "Maharashtra": {
                "name": "MahaRERA",
                "website": "https://maharera.mahaonline.gov.in",
                "coverage": 95
            },
            "Karnataka": {
                "name": "K-RERA",
                "website": "https://rera.karnataka.gov.in",
                "coverage": 90
            },
            "Delhi": {
                "name": "Delhi RERA",
                "website": "https://rera.delhi.gov.in",
                "coverage": 85
            },
            "Haryana": {
                "name": "HRERA",
                "website": "https://haryanarera.gov.in",
                "coverage": 80
            },
            "Telangana": {
                "name": "Telangana RERA",
                "website": "https://rera.telangana.gov.in",
                "coverage": 85
            },
            "Tamil Nadu": {
                "name": "TNRERA",
                "website": "https://tnrera.in",
                "coverage": 85
            }
        }
        
        # Map cities to states
        city_to_state = {
            "Mumbai": "Maharashtra",
            "Pune": "Maharashtra",
            "Bangalore": "Karnataka",
            "Delhi-NCR": "Delhi",  # Simplified mapping
            "Hyderabad": "Telangana",
            "Chennai": "Tamil Nadu"
        }
        
        # Look up state for the city
        state = city_to_state.get(city, "")
        
        if state in rera_authorities:
            authority_data = rera_authorities[state]
            compliance_data["rera_authority"] = authority_data["name"]
            compliance_data["rera_website"] = authority_data["website"]
            compliance_data["rera_coverage"] = authority_data["coverage"]
            
            # Calculate compliance score (0-100)
            # Starting with state's base coverage
            compliance_score = authority_data["coverage"]
            
            # Adjust based on property type (commercial tends to have higher compliance)
            if property_type == "Commercial":
                compliance_score += 5
            
            # Cap at 100
            compliance_data["compliance_score"] = min(100, compliance_score)
        else:
            # Default values for unknown states
            compliance_data["rera_authority"] = "State RERA"
            compliance_data["rera_website"] = "https://rera.gov.in"
            compliance_data["rera_coverage"] = 70
            compliance_data["compliance_score"] = 70
        
        return compliance_data
    
    def calculate_nri_tax_implications(self, property_price, expected_rent=0, 
                                     expected_appreciation=5, holding_period=5):
        """Calculate tax implications for NRI real estate investment."""
        tax_data = {
            "property_price": property_price,
            "annual_rental_income": expected_rent * 12,
            "estimated_value_after_holding": 0,
            "capital_gains": 0,
            "rental_income_tax": 0,
            "capital_gains_tax": 0,
            "tds_on_sale": 0,
            "total_tax_liability": 0
        }
        
        # Calculate future value based on expected appreciation
        future_value = property_price * ((1 + (expected_appreciation/100)) ** holding_period)
        tax_data["estimated_value_after_holding"] = future_value
        
        # Calculate capital gains
        capital_gains = future_value - property_price
        tax_data["capital_gains"] = capital_gains
        
        # Long-term capital gains tax rate for NRIs
        # 20% with indexation benefit after 2 years
        if holding_period >= 2:
            # Apply indexation benefit (simplified calculation)
            # Assuming 5% average inflation for indexation
            inflation_factor = ((1 + 0.05) ** holding_period)
            indexed_cost = property_price * inflation_factor
            indexed_capital_gains = max(0, future_value - indexed_cost)
            tax_data["capital_gains_tax"] = indexed_capital_gains * 0.20
        else:
            # Short-term capital gains taxed at income tax slab rates
            # Assuming highest slab rate of 30% for NRIs
            tax_data["capital_gains_tax"] = capital_gains * 0.30
        
        # Calculate rental income tax
        # 30% standard deduction on rental income
        taxable_rental_income = (tax_data["annual_rental_income"] * 0.7)
        # Flat 30% tax rate for NRIs
        tax_data["rental_income_tax"] = taxable_rental_income * 0.30
        
        # TDS on sale (1% for property value > 50 lakhs)
        if future_value > 5000000:
            tax_data["tds_on_sale"] = future_value * 0.01
        
        # Total tax liability over the holding period
        tax_data["total_tax_liability"] = (
            tax_data["rental_income_tax"] * holding_period + 
            tax_data["capital_gains_tax"] + 
            tax_data["tds_on_sale"]
        )
        
        return tax_data
    
    def generate_regulatory_checklist(self, property_type="Residential"):
        """Generate a regulatory checklist for NRI real estate investment."""
        checklist = {}
        
        # Common documents for all property types
        common_documents = [
            {"requirement": "PAN Card", "mandatory": True, "description": "Permanent Account Number is required for all financial transactions in India."},
            {"requirement": "NRI Status Proof", "mandatory": True, "description": "Passport, visa, or overseas employment letter to establish NRI status."},
            {"requirement": "OCI/PIO Card", "mandatory": False, "description": "Overseas Citizen of India or Person of Indian Origin card if applicable."},
            {"requirement": "NRO Account", "mandatory": True, "description": "Non-Resident Ordinary Rupee Account for transactions in India."}
        ]
        
        # Property Purchase Requirements
        purchase_requirements = [
            {"requirement": "RERA Registration Verification", "mandatory": True, "description": "Check if the property is registered under the Real Estate Regulatory Authority."},
            {"requirement": "FEMA Compliance", "mandatory": True, "description": "Foreign Exchange Management Act compliance for property purchase by NRIs."},
            {"requirement": "Power of Attorney", "mandatory": False, "description": "If not personally present for transactions, a registered PoA is needed."},
            {"requirement": "RBI Permission", "mandatory": False, "description": "Required only for agricultural land, plantation property, or farmhouse purchase."}
        ]
        
        # Tax Requirements
        tax_requirements = [
            {"requirement": "Foreign Bank Account Reporting", "mandatory": True, "description": "Reporting foreign bank accounts in Indian tax returns if applicable."},
            {"requirement": "TDS on Rental Income", "mandatory": True, "description": "TDS of 30% on rental income for NRIs."},
            {"requirement": "TDS on Property Sale", "mandatory": True, "description": "TDS of 20% on capital gains when selling property."},
            {"requirement": "DTAA Benefits", "mandatory": False, "description": "Double Taxation Avoidance Agreement benefits may be available based on country of residence."}
        ]
        
        # Property-specific requirements
        if property_type == "Residential":
            property_specific = [
                {"requirement": "No RBI Permission for Residential", "mandatory": False, "description": "No special RBI permission needed for residential property."},
                {"requirement": "Income Proof for Home Loan", "mandatory": True, "description": "Bank statements, tax returns from foreign country if applying for home loan."}
            ]
        elif property_type == "Commercial":
            property_specific = [
                {"requirement": "Business Plan", "mandatory": False, "description": "Business plan if property is for setting up business operations."},
                {"requirement": "GST Registration", "mandatory": True, "description": "GST registration if commercial property will be leased out."}
            ]
        else:
            property_specific = []
        
        # Repatriation Requirements
        repatriation_requirements = [
            {"requirement": "Tax Clearance Certificate", "mandatory": True, "description": "Required for repatriation of sale proceeds."},
            {"requirement": "CA Certificate", "mandatory": True, "description": "Chartered Accountant certificate confirming taxes paid."},
            {"requirement": "Form 15CA/CB", "mandatory": True, "description": "Required for remittance of funds outside India."},
            {"requirement": "Original Purchase Documents", "mandatory": True, "description": "Required to prove the source of funds for the initial investment."}
        ]
        
        # Compile all requirements
        checklist["documents"] = common_documents
        checklist["purchase"] = purchase_requirements
        checklist["property_specific"] = property_specific
        checklist["tax"] = tax_requirements
        checklist["repatriation"] = repatriation_requirements
        
        return checklist
    
    def render_dashboard(self):
        """Render the NRI investor dashboard."""
        st.title("🌏 NRI Real Estate Investment Portal")
        st.write("Specialized tools for non-resident Indians investing in the Indian real estate market.")
        
        tab1, tab2, tab3 = st.tabs(["💱 Currency & Investment Calculator", "📋 RERA & Regulatory Compliance", "💰 Tax Planning"])
        
        # Tab 1: Currency & Investment Calculator
        with tab1:
            st.header("Currency Conversion & Investment Calculator")
            st.write("Calculate investment amounts and project returns in your preferred currency.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Property Details (INR)")
                property_price = st.number_input("Property Price (₹)", min_value=1000000, max_value=500000000, 
                                             value=7500000, step=500000, format="%d")
                
                monthly_rent = st.number_input("Expected Monthly Rent (₹)", min_value=0, max_value=2000000, 
                                           value=35000, step=1000, format="%d")
                
                # Other investment parameters
                annual_appreciation = st.slider("Expected Annual Appreciation (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.5)
                holding_period = st.slider("Investment Horizon (Years)", min_value=1, max_value=20, value=5)
            
            with col2:
                st.subheader("Currency Settings")
                base_currency = st.selectbox(
                    "Your Base Currency", 
                    ["USD", "EUR", "GBP", "AED", "SGD", "AUD", "CAD"],
                    index=0
                )
                
                # Display current exchange rate
                exchange_rate = self.exchange_rates.get(base_currency, 83.50)
                st.write(f"Current Exchange Rate: 1 {base_currency} = ₹{exchange_rate:.2f}")
                
                # Custom exchange rate option
                use_custom_rate = st.checkbox("Use Custom Exchange Rate")
                if use_custom_rate:
                    custom_rate = st.number_input(f"Custom Exchange Rate (₹ per {base_currency})", 
                                              min_value=1.0, max_value=200.0, value=exchange_rate, step=0.1)
                    exchange_rate = custom_rate
            
            # Calculate and display results
            if st.button("Calculate Investment Analysis"):
                with st.spinner("Calculating investment projections..."):
                    # Convert main values to foreign currency
                    price_foreign = property_price / exchange_rate
                    monthly_rent_foreign = monthly_rent / exchange_rate
                    
                    # Calculate future value
                    future_value_inr = property_price * ((1 + (annual_appreciation/100)) ** holding_period)
                    future_value_foreign = future_value_inr / exchange_rate
                    
                    # Calculate total rental income
                    total_rent_inr = monthly_rent * 12 * holding_period
                    total_rent_foreign = total_rent_inr / exchange_rate
                    
                    # Calculate ROI
                    total_return_inr = future_value_inr - property_price + total_rent_inr
                    roi_percentage = (total_return_inr / property_price) * 100
                    annual_roi = roi_percentage / holding_period
                    
                    # Display results
                    st.subheader("Investment Analysis")
                    
                    # Display currency conversion table
                    st.write("**Currency Conversion**")
                    conversion_data = pd.DataFrame({
                        "Metric": ["Property Price", "Monthly Rental", "Projected Future Value"],
                        "INR (₹)": [f"₹{property_price:,.0f}", f"₹{monthly_rent:,.0f}", f"₹{future_value_inr:,.0f}"],
                        f"{base_currency}": [f"{base_currency} {price_foreign:,.0f}", 
                                           f"{base_currency} {monthly_rent_foreign:,.0f}", 
                                           f"{base_currency} {future_value_foreign:,.0f}"]
                    })
                    st.dataframe(conversion_data, hide_index=True, use_container_width=True)
                    
                    # Display ROI metrics
                    col_roi1, col_roi2, col_roi3 = st.columns(3)
                    
                    with col_roi1:
                        st.metric("Total Appreciation", f"₹{future_value_inr - property_price:,.0f}")
                    
                    with col_roi2:
                        st.metric("Total Rental Income", f"₹{total_rent_inr:,.0f}")
                    
                    with col_roi3:
                        st.metric(f"{holding_period}-Year ROI", f"{roi_percentage:.1f}%")
                    
                    # Create visualization of investment growth
                    st.subheader("Investment Growth Projection")
                    
                    years = list(range(holding_period + 1))  # Include year 0
                    property_values = [property_price * ((1 + (annual_appreciation/100)) ** year) for year in years]
                    cumulative_rental = [monthly_rent * 12 * year for year in years]
                    total_returns = [property_values[i] - property_price + cumulative_rental[i] for i in years]
                    
                    # Create plot
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    ax.plot(years, property_values, marker='o', label='Property Value', color='#1f77b4')
                    ax.plot(years, [property_price + rent for rent in cumulative_rental], marker='s', 
                          label='Initial Investment + Rental Income', color='#ff7f0e')
                    ax.plot(years, [property_price + ret for ret in total_returns], marker='^', 
                          label='Total Return (Value + Rental)', color='#2ca02c')
                    ax.axhline(y=property_price, color='gray', linestyle='--', label='Initial Investment')
                    
                    ax.set_xlabel('Years')
                    ax.set_ylabel('Value (₹)')
                    ax.set_title('Investment Growth Over Time')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
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
                    
                    # Foreign currency equivalent growth
                    st.subheader(f"Equivalent Growth in {base_currency}")
                    
                    # Convert all values to foreign currency
                    property_values_foreign = [val / exchange_rate for val in property_values]
                    cumulative_rental_foreign = [val / exchange_rate for val in cumulative_rental]
                    total_returns_foreign = [val / exchange_rate for val in total_returns]
                    initial_price_foreign = property_price / exchange_rate
                    
                    # Create plot
                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                    
                    ax2.plot(years, property_values_foreign, marker='o', label='Property Value', color='#1f77b4')
                    ax2.plot(years, [initial_price_foreign + rent for rent in cumulative_rental_foreign], marker='s', 
                           label='Initial Investment + Rental Income', color='#ff7f0e')
                    ax2.plot(years, [initial_price_foreign + ret for ret in total_returns_foreign], marker='^', 
                           label='Total Return (Value + Rental)', color='#2ca02c')
                    ax2.axhline(y=initial_price_foreign, color='gray', linestyle='--', label='Initial Investment')
                    
                    ax2.set_xlabel('Years')
                    ax2.set_ylabel(f'Value ({base_currency})')
                    ax2.set_title(f'Investment Growth Over Time in {base_currency}')
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                    
                    # NRI-specific investment guidelines
                    with st.expander("NRI Investment Guidelines"):
                        st.write("""
                        ### Key Points for NRI Investors
                        
                        1. **Eligible Properties**: NRIs can purchase residential and commercial properties in India but not agricultural land, plantation properties, or farmhouses without RBI permission.
                        
                        2. **Payment Methods**: Funds must come through proper banking channels, either through an NRE/NRO account or direct remittance from a foreign account.
                        
                        3. **Repatriation Rules**:
                           - For properties purchased with funds remitted from abroad, up to two residential properties can have their sale proceeds repatriated.
                           - For properties purchased out of rupee resources, sale proceeds can't be repatriated beyond the initial investment.
                        
                        4. **Documentation**: Keep proper documentation of all fund transfers for future repatriation needs.
                        
                        5. **Exchange Rate Risk**: Consider hedging options if concerned about rupee depreciation affecting returns when converting back to your base currency.
                        """)
        
        # Tab 2: RERA & Regulatory Compliance
        with tab2:
            st.header("RERA Compliance & Regulatory Requirements")
            st.write("Verify RERA status and understand the regulatory requirements for NRI real estate investment.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # City selection
                cities = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR", "Chennai"]
                selected_city = st.selectbox("Select City", cities, key="nri_city_select")
            
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
                        "Delhi-NCR": ["Gurgaon", "Noida", "Greater Noida", "Dwarka", "Faridabad"],
                        "Chennai": ["Adyar", "Anna Nagar", "T Nagar", "Velachery", "OMR"]
                    }
                    areas = default_areas.get(selected_city, [])
                
                selected_area = st.selectbox("Select Area", areas, key="nri_area_select") if areas else None
            
            # Property type selection
            property_type = st.radio("Property Type", ["Residential", "Commercial"], horizontal=True)
            
            if selected_city and selected_area:
                if st.button("Check RERA Compliance"):
                    with st.spinner(f"Checking RERA compliance for {selected_area}, {selected_city}..."):
                        rera_data = self.analyze_rera_compliance(selected_city, selected_area, property_type)
                        
                        # Display RERA authority information
                        st.subheader("RERA Authority")
                        
                        col_rera1, col_rera2 = st.columns([1, 2])
                        
                        with col_rera1:
                            st.write(f"**Authority**: {rera_data['rera_authority']}")
                            st.write(f"**Website**: [{rera_data['rera_website']}]({rera_data['rera_website']})")
                        
                        with col_rera2:
                            # Display compliance score gauge
                            score = rera_data["compliance_score"]
                            fig, ax = plt.subplots(figsize=(8, 2))
                            
                            # Configure gauge colors
                            gauge_colors = ['#FF6B6B', '#FFD166', '#06D6A0']
                            score_color = gauge_colors[0] if score < 70 else gauge_colors[1] if score < 85 else gauge_colors[2]
                            
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
                            
                            plt.title("RERA Compliance Score", pad=10)
                            st.pyplot(fig)
                            
                            # Interpretation
                            st.write(f"Approximately **{rera_data['rera_coverage']}%** of projects in this area are RERA registered.")
                            
                            if score >= 85:
                                st.success("✅ High RERA compliance in this area. Most projects should be properly registered.")
                            elif score >= 70:
                                st.info("ℹ️ Good RERA compliance in this area, but verify registration for specific projects.")
                            else:
                                st.warning("⚠️ Mixed RERA compliance. Extra due diligence recommended.")
                        
                        # RERA compliance tips
                        st.subheader("RERA Verification Tips for NRIs")
                        
                        col_tips1, col_tips2 = st.columns([1, 1])
                        
                        with col_tips1:
                            st.write("""
                            **How to Verify RERA Registration:**
                            1. Visit the state RERA website
                            2. Enter the RERA registration number of the project
                            3. Check if the registration is valid and not expired
                            4. Verify project details match with what's advertised
                            """)
                        
                        with col_tips2:
                            st.write("""
                            **Red Flags to Watch For:**
                            1. Builder reluctant to share RERA registration number
                            2. Advertisement missing RERA number
                            3. Project details on RERA website different from marketing materials
                            4. Registration expiring before expected completion date
                            """)
                        
                        # NRI-specific regulatory checklist
                        st.subheader("NRI Investment Regulatory Checklist")
                        
                        checklist = self.generate_regulatory_checklist(property_type)
                        
                        # Document requirements
                        with st.expander("Document Requirements", expanded=True):
                            doc_data = []
                            for item in checklist["documents"]:
                                doc_data.append({
                                    "Requirement": item["requirement"],
                                    "Mandatory": "Yes" if item["mandatory"] else "No",
                                    "Description": item["description"]
                                })
                            
                            st.dataframe(pd.DataFrame(doc_data), hide_index=True, use_container_width=True)
                        
                        # Purchase requirements
                        with st.expander("Purchase Procedure Requirements"):
                            purchase_data = []
                            for item in checklist["purchase"]:
                                purchase_data.append({
                                    "Requirement": item["requirement"],
                                    "Mandatory": "Yes" if item["mandatory"] else "No",
                                    "Description": item["description"]
                                })
                            
                            st.dataframe(pd.DataFrame(purchase_data), hide_index=True, use_container_width=True)
                        
                        # Property-specific requirements
                        with st.expander(f"{property_type}-specific Requirements"):
                            prop_data = []
                            for item in checklist["property_specific"]:
                                prop_data.append({
                                    "Requirement": item["requirement"],
                                    "Mandatory": "Yes" if item["mandatory"] else "No",
                                    "Description": item["description"]
                                })
                            
                            st.dataframe(pd.DataFrame(prop_data), hide_index=True, use_container_width=True)
                        
                        # Repatriation requirements
                        with st.expander("Fund Repatriation Requirements"):
                            rep_data = []
                            for item in checklist["repatriation"]:
                                rep_data.append({
                                    "Requirement": item["requirement"],
                                    "Mandatory": "Yes" if item["mandatory"] else "No",
                                    "Description": item["description"]
                                })
                            
                            st.dataframe(pd.DataFrame(rep_data), hide_index=True, use_container_width=True)
                        
                        # FEMA guidelines for NRIs
                        with st.expander("FEMA Guidelines for NRIs"):
                            st.write("""
                            ### Foreign Exchange Management Act (FEMA) Guidelines
                            
                            1. **Property Types Allowed**: NRIs can purchase residential and commercial properties without RBI permission. Agricultural land, plantation properties, and farmhouses require special RBI approval.
                            
                            2. **Payment Methods**: All payments must be made through banking channels by remittance from abroad, from an NRE/NRO/FCNR account, or other methods allowed by RBI.
                            
                            3. **Repatriation of Sale Proceeds**:
                               - For properties acquired through foreign inward remittance, sale proceeds of up to two residential properties can be repatriated.
                               - For properties acquired through rupee accounts, principal investment can be repatriated subject to conditions.
                               - Capital gains must remain in India unless there's specific permission.
                            
                            4. **Loans**:
                               - NRIs can obtain home loans from authorized banks in India.
                               - Maximum loan amount is 75-80% of property value.
                               - Repayment must be through NRE/NRO accounts or direct remittances.
                            
                            5. **Rental Income**: Can be received in NRO account and partially repatriable after tax payment.
                            
                            > **Note**: FEMA regulations can change. Consult with a legal expert familiar with NRI investments.
                            """)
            else:
                st.info("Please select a city and area to check RERA compliance.")
        
        # Tab 3: Tax Planning
        with tab3:
            st.header("NRI Tax Planning for Real Estate")
            st.write("Understand the tax implications of your real estate investment in India.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Property Details")
                tax_property_price = st.number_input("Property Value (₹)", min_value=1000000, max_value=500000000, 
                                                 value=7500000, step=500000, format="%d", key="tax_property_price")
                
                tax_monthly_rent = st.number_input("Expected Monthly Rent (₹)", min_value=0, max_value=2000000, 
                                              value=35000, step=1000, format="%d", key="tax_monthly_rent")
            
            with col2:
                st.subheader("Investment Parameters")
                tax_appreciation = st.slider("Expected Annual Appreciation (%)", min_value=0.0, max_value=15.0, 
                                        value=5.0, step=0.5, key="tax_appreciation")
                
                tax_holding_period = st.slider("Investment Horizon (Years)", min_value=1, max_value=20, 
                                           value=5, key="tax_holding_period")
            
            if st.button("Calculate Tax Implications"):
                with st.spinner("Calculating tax implications..."):
                    tax_data = self.calculate_nri_tax_implications(
                        property_price=tax_property_price,
                        expected_rent=tax_monthly_rent,
                        expected_appreciation=tax_appreciation,
                        holding_period=tax_holding_period
                    )
                    
                    # Display summary metrics
                    st.subheader("Tax Liability Summary")
                    
                    col_summary1, col_summary2, col_summary3 = st.columns(3)
                    
                    with col_summary1:
                        annual_rental_tax = tax_data["rental_income_tax"]
                        st.metric("Annual Rental Income Tax", f"₹{annual_rental_tax:,.0f}")
                    
                    with col_summary2:
                        capital_gains_tax = tax_data["capital_gains_tax"]
                        st.metric("Capital Gains Tax", f"₹{capital_gains_tax:,.0f}")
                    
                    with col_summary3:
                        total_tax = tax_data["total_tax_liability"]
                        st.metric(f"Total Tax ({tax_holding_period} years)", f"₹{total_tax:,.0f}")
                    
                    # Display detailed breakdown
                    st.subheader("Detailed Tax Breakdown")
                    
                    # Future value and capital gains
                    col_details1, col_details2 = st.columns([1, 1])
                    
                    with col_details1:
                        st.write("**Property Value Projection**")
                        value_data = pd.DataFrame({
                            "Item": ["Initial Purchase Price", "Projected Sale Value", "Capital Gains"],
                            "Amount (₹)": [
                                f"₹{tax_property_price:,.0f}",
                                f"₹{tax_data['estimated_value_after_holding']:,.0f}",
                                f"₹{tax_data['capital_gains']:,.0f}"
                            ]
                        })
                        st.dataframe(value_data, hide_index=True, use_container_width=True)
                    
                    with col_details2:
                        st.write("**Rental Income Taxation**")
                        rent_data = pd.DataFrame({
                            "Item": ["Annual Gross Rental Income", "Standard Deduction (30%)", 
                                  "Taxable Rental Income", "Tax on Rental Income (30%)"],
                            "Amount (₹)": [
                                f"₹{tax_data['annual_rental_income']:,.0f}",
                                f"₹{tax_data['annual_rental_income'] * 0.3:,.0f}",
                                f"₹{tax_data['annual_rental_income'] * 0.7:,.0f}",
                                f"₹{tax_data['rental_income_tax']:,.0f}"
                            ]
                        })
                        st.dataframe(rent_data, hide_index=True, use_container_width=True)
                    
                    # TDS and Total Tax
                    st.write("**Capital Gains & Total Tax Liability**")
                    tax_table = pd.DataFrame({
                        "Item": ["Capital Gains Tax", "TDS on Property Sale (1%)", 
                               "Rental Income Tax (Total)", "Total Tax Liability"],
                        "Amount (₹)": [
                            f"₹{tax_data['capital_gains_tax']:,.0f}",
                            f"₹{tax_data['tds_on_sale']:,.0f}",
                            f"₹{tax_data['rental_income_tax'] * tax_holding_period:,.0f}",
                            f"₹{tax_data['total_tax_liability']:,.0f}"
                        ]
                    })
                    st.dataframe(tax_table, hide_index=True, use_container_width=True)
                    
                    # Tax visualization
                    st.subheader("Tax Distribution")
                    
                    # Prepare data for pie chart
                    tax_components = {
                        "Capital Gains Tax": tax_data["capital_gains_tax"],
                        "Rental Income Tax": tax_data["rental_income_tax"] * tax_holding_period,
                        "TDS on Sale": tax_data["tds_on_sale"]
                    }
                    
                    # Create pie chart
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.pie(tax_components.values(), labels=tax_components.keys(), autopct='%1.1f%%',
                         startangle=90, colors=plt.cm.Set2(range(len(tax_components))))
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                    ax.set_title('Distribution of Tax Liability')
                    
                    st.pyplot(fig)
                    
                    # Tax optimization tips
                    st.subheader("Tax Optimization Strategies for NRIs")
                    
                    with st.expander("Double Taxation Avoidance", expanded=True):
                        st.write("""
                        ### Double Taxation Avoidance Agreement (DTAA) Benefits
                        
                        India has DTAA with more than 85 countries to prevent taxation of the same income in both India and your country of residence.
                        
                        **How to Claim DTAA Benefits:**
                        1. Obtain Tax Residency Certificate (TRC) from your country of residence
                        2. Submit Form 10F along with TRC when filing tax returns
                        3. Provide PAN details with all relevant documents
                        
                        **Common DTAA Benefits:**
                        - Reduced tax rates on rental income
                        - Offsetting taxes paid in India against tax liability in your country
                        - Possible exemptions on capital gains based on specific DTAA provisions
                        
                        > Note: DTAA benefits vary by country. Consult with a tax professional familiar with both Indian tax laws and the tax laws of your country of residence.
                        """)
                    
                    with st.expander("Indexation Benefits"):
                        st.write("""
                        ### Indexation Benefits for Long-Term Capital Gains
                        
                        For properties held for more than 2 years, indexation benefits can significantly reduce your capital gains tax liability.
                        
                        **How Indexation Works:**
                        1. Purchase price is adjusted for inflation using the Cost Inflation Index (CII)
                        2. Indexed cost = Original Cost × (CII for year of sale ÷ CII for year of purchase)
                        3. Capital gains = Sale price - Indexed cost
                        4. Tax is calculated at 20% on the indexed capital gains
                        
                        **Example:**
                        - Property purchased in 2015 for ₹50 lakhs with CII of 254
                        - Property sold in 2025 for ₹1 crore with CII of 389 (projected)
                        - Indexed cost = ₹50 lakhs × (389 ÷ 254) = ₹76.67 lakhs
                        - Indexed capital gains = ₹1 crore - ₹76.67 lakhs = ₹23.33 lakhs
                        - Tax liability = 20% of ₹23.33 lakhs = ₹4.67 lakhs
                        
                        Without indexation, the tax would be on the full ₹50 lakhs gain, resulting in ₹10 lakhs tax.
                        """)
                    
                    with st.expander("Section 54/54F Benefits"):
                        st.write("""
                        ### Tax Exemption under Sections 54 & 54F
                        
                        NRIs can claim exemption from capital gains tax by reinvesting in residential property.
                        
                        **Section 54 (For residential property):**
                        - Applicable when selling a residential property after 2+ years of ownership
                        - Reinvest capital gains in up to two residential properties in India
                        - Purchase must be 1 year before or 2 years after sale, or construction within 3 years
                        - Maximum exemption of ₹2 crores
                        
                        **Section 54F (For any long-term capital asset):**
                        - Applicable when selling any long-term capital asset (except residential house)
                        - Entire sale proceeds (not just capital gains) must be invested in a residential house
                        - Same timeline requirements as Section 54
                        - NRI should not own more than one residential house in India (except the new one)
                        
                        **Capital Gains Account Scheme:**
                        - If not immediately reinvesting, deposit gains in a Capital Gains Account Scheme (CGAS)
                        - Must utilize funds within the prescribed time limit
                        - Available with authorized banks in India
                        """)
                    
                    with st.expander("TDS Refund Process"):
                        st.write("""
                        ### TDS Refund Process for NRIs
                        
                        When selling property, buyers are required to deduct TDS at a higher rate for NRIs. You can claim refunds if actual tax liability is lower.
                        
                        **TDS Rates for NRIs:**
                        - 20% for long-term capital gains (property held >2 years)
                        - 30% for short-term capital gains (property held ≤2 years)
                        
                        **Steps to Claim TDS Refund:**
                        1. Obtain Form 16A from the buyer (TDS certificate)
                        2. File income tax return in India declaring the capital gains
                        3. Calculate actual tax liability after all deductions and exemptions
                        4. If TDS exceeds final tax liability, claim refund in the tax return
                        
                        **Required Documents:**
                        - PAN Card
                        - Form 16A for TDS deducted
                        - Sale deed and purchase agreement
                        - Bank account details for refund credit
                        
                        > Note: Processing time for refunds is typically 3-6 months after filing returns.
                        """)
                    