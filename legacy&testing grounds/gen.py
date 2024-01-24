import numpy_financial as npf
import pandas as pd
import os
from datetime import datetime


def date_to_quarter(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    return f'Q{quarter} {year}'

script_dir = os.path.dirname(os.path.abspath(__file__))

excel_path = os.path.join(script_dir, 'refnew.xlsx')

df = pd.read_excel(excel_path, parse_dates=['Simulated date'])

# Function to convert dates to quarters
def date_to_quarter(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    return f'Q{quarter} {year}'

# Revised function to calculate mortgage and update DataFrame
def revised_calculate_mortgage(df, age, savings, income):
    # Constants and user inputs
    LTV = 0.8  # Loan-to-value ratio
    retirement_age = 67
    mortgage_term_limit = 30  # Maximum mortgage term in years
    consumption_percentage = 0.35
    rent_factor = 0.045 / 12  # Monthly rent factor
    quarterly_income = 3 * income
    mortgage_term = min(retirement_age - age, mortgage_term_limit)
    mortgage_term_quarters = mortgage_term * 4

    # Calculate target quarter year
    current_year = datetime.now().year
    target_year = current_year + mortgage_term
    target_quarter_year = f'Q1 {target_year}'

    # Initialize model data frame by column
    required_deposit_column = 'Required deposit HO' 
    affordability_dummy_column = 'Home Ownership Affordability'
    simulated_mortgage_payment_column = 'Simulated mortgage payments'
    price_column = 'LONDON HOUSE PRICES (£)'
    index_column = 'House price index'
    simulated_column = 'Simulated house prices'
    inflation_column = 'Inflation'
    adjusted_inflation_column = 'Adjusted inflation'
    simulated_income_column = 'Simulated income (quarterly)'
    simulated_rent_column = 'Simulated Rent (Quarterly)'
    BoE_interest_column = 'BoE interest rates'
    Accumulated_wealth_column = 'Accumulated Wealth'
    simulated_savings_column = 'Simulated savings while renting'
    simulated_mortgage_rate_column = 'Simulated variable mortgage rates'

    last_row_index = df.index[-1]
    base_simulated_price = df.at[last_row_index, price_column]
    base_index = 100  # Assuming base index value
    last_row_index = len(df) - 1
    df.at[last_row_index, index_column] = 100  # Base index
    df.at[last_row_index, simulated_column] = base_simulated_price
    df.at[last_row_index, adjusted_inflation_column] = 100
    df.at[last_row_index, simulated_income_column] = quarterly_income

    # Loop through the DataFrame and perform calculations
    for i in range(len(df) - 1, -1, 1):
        # Base case for the earliest date (last row)
        if i == len(df) - 1:
            df.at[i, index_column] = 100  # Set base index for the earliest date
        else:
            current_price = df.at[i, price_column]
            next_price = df.at[i + 1, price_column]
            next_index = df.at[i + 1, index_column]
            df.at[i, index_column] = next_index * (current_price / next_price)

         # Simulated House Price Calculation
        current_index = df.at[i, index_column]
        df.at[i, simulated_column] = base_simulated_price * (current_index / base_index)

        # Adjusted Inflation Calculation
        if i == len(df) - 1:
            df.at[i, adjusted_inflation_column] = 100
        else:    
            current_inflation = df.at[i, inflation_column]
            previous_inflation = df.at[i + 1, inflation_column] if i > 0 else current_inflation
            previous_adjusted_inflation = df.at[i + 1, adjusted_inflation_column]
            df.at[i, adjusted_inflation_column] = previous_adjusted_inflation * (current_inflation / previous_inflation)

        # Simulated Income Calculation
        if i == len(df) -1:
            df.at[i, simulated_income_column] = quarterly_income
        else:
            growth = df.at[i, adjusted_inflation_column]/df.at[i + 1, adjusted_inflation_column]
            if growth < 1.03:
                previous_income = df.at[i + 1, simulated_income_column] 
                simulated_income = growth*previous_income
                simulated_income = df.at[i, simulated_income_column]
            else:
                if i > 0:
                    previous_income = df.at[i + 1, simulated_income_column]
                    inflation_ratio = df.at[i, adjusted_inflation_column] / df.at[i - 1, adjusted_inflation_column]
                    growth_factor = min(1.03, inflation_ratio)
                    df.at[i, simulated_income_column] = previous_income * growth_factor
                else:
                    df.at[i, simulated_income_column] = df.at[i + 1, simulated_income_column]

        # Simulated Rent Calculation
        simulated_house_price = df.at[i, simulated_column] 
        df.at[i, simulated_rent_column] = simulated_house_price * rent_factor

        # Simulated Savings while Renting Calculation
        previous_savings = df.at[i - 1, simulated_savings_column] if i > 0 else savings
        df.at[i, simulated_savings_column] = (quarterly_income - (quarterly_income * consumption_percentage) - df.at[i, simulated_rent_column] * 3 + (previous_savings * (df.at[i, BoE_interest_column] / 4)))

        # Mortgage rate and payment calculation
        df.at[i, simulated_mortgage_rate_column] = df.at[i, BoE_interest_column] + 0.003
        pv = df.at[i, simulated_column]
        mortgage_rate = df.at[i, simulated_mortgage_rate_column] / 12
        
        mortgage_payment = -npf.pmt(mortgage_rate, mortgage_term_quarters * 3, (pv * LTV), 0)
        df.at[i, simulated_mortgage_payment_column] = mortgage_payment*3 

        # Required deposit and affordability check
        df.at[i, required_deposit_column] = 0.05 * df.at[i, simulated_column]
        if df.at[i, simulated_savings_column] >= df.at[i, required_deposit_column]:
            df.at[i, affordability_dummy_column] = 'Affordable'
    return df
user_age = 30
user_savings = 50000  # £
user_income = 2000  # Monthly, £

# Running the revised function with the same user inputs
df_revised = revised_calculate_mortgage(df, user_age, user_savings, user_income)

pd.set_option('display.max_columns', None)
print(df_revised.head())
