import streamlit as st
import pandas as pd
import numpy_financial as npf
import plotly.express as px
import itertools

# Set Page Configuration
st.set_page_config(page_title="Capital Budgeting & Forecasting Optimizer", layout="wide")

st.title("💼 Capital Budgeting & Multi-Year Forecasting Optimizer")
st.markdown("""
This tool helps Project Managers and FP&A teams select the optimal mix of projects to maximize **Net Present Value (NPV)** and **Profit**, while forecasting multi-year returns based on dynamic growth assumptions.
""")

# Sidebar inputs
st.sidebar.header("1. Financial Constraints")
budget = st.sidebar.number_input("Total Capital Budget ($)", min_value=100000, max_value=5000000, value=1000000, step=50000)
discount_rate = st.sidebar.slider("Discount Rate / WACC (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.5) / 100

st.sidebar.header("2. Forecasting Parameters")
st.sidebar.markdown("Forecast cash flows beyond the initial 5 years:")
forecast_years = st.sidebar.slider("Total Years to Forecast", min_value=5, max_value=20, value=5, step=1)
growth_rate = st.sidebar.slider("Annual Cash Flow Growth Rate (%)", min_value=-10.0, max_value=50.0, value=5.0, step=1.0) / 100

# Load Data
st.subheader("1. Proposed Projects Data")
uploaded_file = st.file_uploader("Upload your project CSV data", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("sample_projects.csv")
    except FileNotFoundError:
        st.error("sample_projects.csv not found! Please make sure it is in the same folder.")
        st.stop()

# Function to forecast cash flows and calculate NPV & Profit
def calculate_metrics(row, rate, years, growth):
    # Base 5 years of cash flows
    cf =[-row['Initial_Cost'], row['Year_1_CF'], row['Year_2_CF'], row['Year_3_CF'], row['Year_4_CF'], row['Year_5_CF']]
    
    # Forecast additional years based on the user's growth rate assumption
    last_cf = row['Year_5_CF']
    for _ in range(6, years + 1):
        next_cf = last_cf * (1 + growth)
        cf.append(next_cf)
        last_cf = next_cf
        
    npv = npf.npv(rate, cf)
    total_profit = sum(cf[1:]) - row['Initial_Cost'] # Total inflows minus initial cost
    return pd.Series([npv, total_profit])

# Apply calculations dynamically
df[['Predicted_NPV', 'Predicted_Profit']] = df.apply(calculate_metrics, axis=1, rate=discount_rate, years=forecast_years, growth=growth_rate)

# Display updated dataframe
st.dataframe(df[['Project_Name', 'Initial_Cost', 'Predicted_NPV', 'Predicted_Profit']].style.format({
    "Initial_Cost": "${:,.0f}", "Predicted_NPV": "${:,.0f}", "Predicted_Profit": "${:,.0f}"
}))

# Custom 0/1 Knapsack Optimization Algorithm (Pure Python)
st.subheader("2. Portfolio Optimization Results")
if st.button("Run Multi-Year Portfolio Optimizer"):
    
    projects = df.to_dict('records')
    best_npv = 0
    best_combination =[]
    
    # Evaluate all possible combinations to find absolute maximum Predicted NPV
    for r in range(1, len(projects) + 1):
        for combo in itertools.combinations(projects, r):
            current_cost = sum(item['Initial_Cost'] for item in combo)
            
            if current_cost <= budget:
                current_npv = sum(item['Predicted_NPV'] for item in combo)
                
                if current_npv > best_npv:
                    best_npv = current_npv
                    best_combination = combo
                    
    # Display Results
    if best_combination:
        result_df = pd.DataFrame(best_combination)
        total_cost = result_df['Initial_Cost'].sum()
        total_npv = result_df['Predicted_NPV'].sum()
        total_profit = result_df['Predicted_Profit'].sum()
        
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Budget Utilized", f"${total_cost:,.0f}", f"{((total_cost/budget)*100):.1f}%")
        col2.metric("Predicted NPV", f"${total_npv:,.0f}")
        col3.metric("Predicted Total Profit", f"${total_profit:,.0f}")
        col4.metric("Projects Funded", f"{len(result_df)} / {len(df)}")
        
        st.success(f"Optimization Complete! Here are the best projects for a {forecast_years}-year horizon:")
        st.dataframe(result_df[['Project_Name', 'Initial_Cost', 'Predicted_NPV', 'Predicted_Profit']].style.format({
            "Initial_Cost": "${:,.0f}", "Predicted_NPV": "${:,.0f}", "Predicted_Profit": "${:,.0f}"
        }))
        
        # Visualizations
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig1 = px.bar(result_df, x='Project_Name', y='Predicted_Profit', color='Initial_Cost', 
                         title=f"Predicted Profit per Project ({forecast_years} Years)",
                         labels={'Project_Name': 'Project', 'Predicted_Profit': 'Total Profit ($)', 'Initial_Cost':'Cost ($)'})
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_chart2:
            # Generate Cumulative Cash Flow array for the line chart
            total_cf_array = [0] * (forecast_years + 1)
            for _, row in result_df.iterrows():
                cf = [-row['Initial_Cost'], row['Year_1_CF'], row['Year_2_CF'], row['Year_3_CF'], row['Year_4_CF'], row['Year_5_CF']]
                last_cf = row['Year_5_CF']
                for _ in range(6, forecast_years + 1):
                    next_cf = last_cf * (1 + growth_rate)
                    cf.append(next_cf)
                    last_cf = next_cf
                for i in range(len(cf)):
                    total_cf_array[i] += cf[i]
            
            # Calculate cumulative sum
            cum_cf =[]
            curr = 0
            for val in total_cf_array:
                curr += val
                cum_cf.append(curr)
                
            chart_df = pd.DataFrame({'Year':[f"Yr {i}" for i in range(0, forecast_years + 1)], 'Cumulative Cash Flow': cum_cf})
            fig2 = px.line(chart_df, x='Year', y='Cumulative Cash Flow', title='Portfolio Cumulative Cash Flow Over Time', markers=True)
            fig2.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break Even Point")
            st.plotly_chart(fig2, use_container_width=True)
            
    else:
        st.warning("Budget is too low to fund any of these projects.")
