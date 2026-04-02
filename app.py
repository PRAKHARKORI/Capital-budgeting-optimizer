import streamlit as st
import pandas as pd
import numpy_financial as npf
import plotly.express as px
import itertools

# Set Page Configuration
st.set_page_config(page_title="Capital Budgeting Optimizer", layout="wide")

st.title("💼 Capital Budgeting & Portfolio Optimizer")
st.markdown("""
This tool helps Project Managers and FP&A teams select the optimal mix of projects to maximize **Net Present Value (NPV)** without exceeding the **Capital Budget**.
""")

# Sidebar inputs
st.sidebar.header("Financial Parameters")
budget = st.sidebar.number_input("Total Capital Budget ($)", min_value=100000, max_value=5000000, value=1000000, step=50000)
discount_rate = st.sidebar.slider("Discount Rate / WACC (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.5) / 100

# Load Data
st.subheader("1. Proposed Projects Data")
uploaded_file = st.file_uploader("Upload your project CSV data", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Using sample data. Upload a CSV to use your own data.")
    try:
        df = pd.read_csv("sample_projects.csv")
    except FileNotFoundError:
        st.error("sample_projects.csv not found! Please make sure it is in the same folder.")
        st.stop()

st.dataframe(df.style.format({"Initial_Cost": "${:,.0f}"}))

# Calculate NPV for each project
def calculate_npv(row, rate):
    cash_flows =[-row['Initial_Cost'], row['Year_1_CF'], row['Year_2_CF'], row['Year_3_CF'], row['Year_4_CF'], row['Year_5_CF']]
    return npf.npv(rate, cash_flows)

df['NPV'] = df.apply(calculate_npv, axis=1, rate=discount_rate)

# Custom 0/1 Knapsack Optimization Algorithm (Pure Python)
st.subheader("2. Optimization Results")
if st.button("Run Portfolio Optimizer"):
    
    # Convert dataframe to a list of dictionaries for faster processing
    projects = df.to_dict('records')
    
    best_npv = 0
    best_combination =[]
    
    # Evaluate all possible combinations of projects to find the absolute maximum NPV
    for r in range(1, len(projects) + 1):
        for combo in itertools.combinations(projects, r):
            current_cost = sum(item['Initial_Cost'] for item in combo)
            
            # Check if this combination of projects is within our budget
            if current_cost <= budget:
                current_npv = sum(item['NPV'] for item in combo)
                
                # If it's within budget and has a higher NPV, save it as our new best
                if current_npv > best_npv:
                    best_npv = current_npv
                    best_combination = combo
                    
    # Display Results
    if best_combination:
        result_df = pd.DataFrame(best_combination)
        total_cost = result_df['Initial_Cost'].sum()
        total_npv = result_df['NPV'].sum()
        
        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Budget Utilized", f"${total_cost:,.0f}", f"{((total_cost/budget)*100):.1f}% of Budget")
        col2.metric("Total Value Created (NPV)", f"${total_npv:,.0f}")
        col3.metric("Projects Funded", f"{len(result_df)} / {len(df)}")
        
        st.success("Optimization Complete! Here are the recommended projects to fund:")
        st.dataframe(result_df[['Project_Name', 'Initial_Cost', 'NPV']].style.format({"Initial_Cost": "${:,.0f}", "NPV": "${:,.0f}"}))
        
        # Visualization
        fig = px.bar(result_df, x='Project_Name', y='NPV', color='Initial_Cost', 
                     title="Selected Projects by NPV and Initial Cost",
                     labels={'Project_Name': 'Project', 'NPV': 'Net Present Value ($)', 'Initial_Cost':'Cost ($)'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Budget is too low to fund any of these projects.")