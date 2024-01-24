import os
import numpy as np 
import pandas as pd
from datetime import datetime

def date_to_quarter(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    return f'Q{quarter} {year}'

script_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(script_dir, 'refnew.xlsx')

# Specify the columns to read from the Excel file
columns_to_read = ['Quarter', 'LONDON HOUSE PRICES (£)', 'Date', 'Simulated date', 'Inflation', 'BoE interest rates']

# Read only the specified columns from the Excel file
df = pd.read_excel(excel_path, usecols=columns_to_read, parse_dates=True, nrows=199)

# Define your column names here
simulated_date = 'Simulated date'
price_column = 'LONDON HOUSE PRICES (£)'
inflation_column = 'Inflation'
simulated_dates_quarter = 'simulated_dates_quarter'
index_column = 'House price index'
simulated_column = 'Simulated house prices'
adjusted_inflation_column = 'Adjusted Inflation'
simulated_income_column = 'Simulated income (quarterly)'
simulated_rent_column = 'Simulated Rent (Monthly)'
simulated_rent_column2 = 'Simulated Rent (Quarterly)'
simulated_savings_column = 'Simulated savings while renting'
required_deposit_column = 'Required deposit HO'
affordability_dummy_column = 'Home Ownership Affordability'
BoE_interest_column = 'BoE interest rates'
simulated_mortgage_rate_column = 'Simulated variable mortgage rates'
simulated_mortgage_payment_column = 'Simulated mortgage payments'
Accumulated_wealth_column = 'Accumulated Wealth'

# Initialize other columns to 0 or appropriate default values
df[index_column] = 0
df[adjusted_inflation_column] = 0
df[simulated_column] = 0
df[simulated_income_column] = 0
df[simulated_rent_column] = 0
df[simulated_rent_column2] = 0
df[simulated_savings_column] = 0
df[required_deposit_column] = 0
df[affordability_dummy_column] = 'Not Affordable'
#df[BoE_interest_column] = 0
df[simulated_mortgage_rate_column] = 0
df[simulated_mortgage_payment_column] = 0.0
df['cumulative_mortgage_payments'] = 0
df[Accumulated_wealth_column] = 0
df['sum dummy'] = 0
df['home ownership dummy'] = 0
df[simulated_dates_quarter] = df[simulated_date].apply(date_to_quarter)
df['shared_ownership_share'] = 0


#def get_house_price_data(consumption_percentage, savings, age, income):

################################################################################################
#inputs 
income = 3000 #float(input('What is your monthly income post-tax? '))
quarterly_income = 3*income
consumption_percentage = 0.35 #float(input('How much of your income post-tax is spent on expenses? '))
savings = 200000 #float(input('Please enter your current savings: '))
age = 20 #int(input('please enter your age: '))


################################################################################################
#base values and free variables 
#House price index
df.at[df.index[-1], index_column] = 100
for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    current_price = df.at[i, price_column]
    previous_price = df.at[i + 1, price_column]
    previous_index = df.at[i + 1, index_column]
    df.at[i, index_column] = previous_index * (current_price / previous_price)

#Simulated house prices 
base_simulated_price = df.at[df.index[0], price_column]
df.at[df.index[-1], simulated_column] = base_simulated_price
for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    current_index = df.at[i, index_column]
    base_index = df.at[df.index[-1], index_column]
    df.at[i, simulated_column] = base_simulated_price * (current_index / base_index)

#Adjusted inflation
df.at[df.index[-1], adjusted_inflation_column] = 100  # Oldest entry for the inflation
for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    current_inflation = df.at[i, inflation_column]
    previous_inflation = df.at[i + 1, inflation_column]
    previous_adjusted_inflation = df.at[i + 1, adjusted_inflation_column]
    df.at[i, adjusted_inflation_column] = previous_adjusted_inflation * (current_inflation / previous_inflation)
    adjusted_inflation = df.at[i, adjusted_inflation_column]

#Simulated rent monthly 
for i in range(df.index[-1], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    simulated_house_price = df.at[i, simulated_column] 
    rent_factor = 0.045/12 
    df.at[i, simulated_rent_column] = simulated_house_price * rent_factor

#Simulated rent quarterly
for i in range(df.index[-1], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    df.at[i, simulated_rent_column2] = df.at[i, simulated_rent_column] * 3

#required deposit 
for i in range(df.index[-1], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    df.at[i, required_deposit_column] = df.at[i, simulated_column] * 0.05 


#Simulated variable mortgage rate
for i in range(df.index[-1], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    df.at[i, simulated_mortgage_rate_column] =  df.at[i, BoE_interest_column] + 0.003


#Simulated income  
df.at[df.index[-1], simulated_income_column] = quarterly_income

for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    current_price = df.at[i, price_column]
    previous_price = df.at[i + 1, price_column]
    previous_income = df.at[i + 1, simulated_income_column]
    running_inflation = df.at[i, adjusted_inflation_column]/df.at[i + 1 , adjusted_inflation_column]

    alpha = 0
    growth_factor = ((1 - alpha) * (running_inflation))    +     (alpha * (current_price / previous_price))
    if growth_factor > 1.03:
        growth_factor = 1.03

    df.at[i, simulated_income_column] = previous_income * growth_factor
                        


################################################################################################
#Mortgage dependent variables 
#Basic inputs 
LTV = 0.80
def find_mortgage_start_date(df):
    savings = 200000
    mortgage_start_date = None  # Initialize mortgage_start_date

    # Set the value for the first row
    df.at[df.index[-1], simulated_savings_column] = (
        df.at[df.index[-1], simulated_income_column] * (1 - consumption_percentage)
        - df.at[df.index[-1], simulated_rent_column2]
        + (savings * (1 + df.at[df.index[-1], BoE_interest_column]))
    )

    for i in range(df.index[-2], df.index[0], -1):  # Iterate from the second last row to the top
        if i > df.index[0]:
            previous_savings = df.at[i + 1, simulated_savings_column]
        else:
            previous_savings = savings

        simulated_income_quarterly = df.at[i, simulated_income_column]
        simulated_rent_quarterly = df.at[i, simulated_rent_column2]
        interest = df.at[i, BoE_interest_column]

        # Calculate savings for the current quarter
        df.at[i, simulated_savings_column] = (
            simulated_income_quarterly * (1 - consumption_percentage)
            - simulated_rent_quarterly
            + (previous_savings * (1 + interest))
        )
        current_savings = df.at[i, simulated_savings_column]

        # Check if current savings exceed required deposit
        required_deposit = df.at[i, required_deposit_column]
        if current_savings >= required_deposit:
            mortgage_start_date = df.at[i, 'Simulated date']  # Update mortgage_start_date if savings is sufficient
            break

    return mortgage_start_date

print(df[simulated_savings_column])