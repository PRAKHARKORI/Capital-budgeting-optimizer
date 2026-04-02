# Capital Budgeting & Portfolio Optimizer

A Python web application that bridges **Finance** and **Project Management**. 

This tool helps FP&A teams and Project Managers determine the optimal combination of projects to fund given a strict capital budget constraint. It calculates the Net Present Value (NPV) of proposed projects based on 5-year cash flow projections and utilizes Linear Programming (the Knapsack algorithm via PuLP) to maximize ROI.

## Tech Stack
* Python
* Streamlit (UI Framework)
* Pandas (Data manipulation)
* NumPy-Financial (Discounted Cash Flow / NPV calculations)
* PuLP (Linear Programming & Optimization)
* Plotly (Data Visualization)

## How to Run Locally
1. Clone this repository.
2. Install the requirements: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`
