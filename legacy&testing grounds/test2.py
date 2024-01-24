import os
import pandas as pd
from datetime import datetime

def date_to_quarter(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    return f'Q{quarter} {year}'

script_dir = os.path.dirname(os.path.abspath(__file__))

excel_path = os.path.join(script_dir, 'refnew.xlsx')

df = pd.read_excel(excel_path, parse_dates=['Simulated date'])
df['simulated_dates_quarter'] = df['Simulated date'].apply(date_to_quarter)

quarter_column = 'Quarter'
price_column = 'LONDON HOUSE PRICES (£)'
index_column = 'House price index'
simulated_column = 'Simulated house prices'
simulated_date = 'Simulated date'
inflation_column = 'Inflation'
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

# Initialize model data frame by column
df[index_column] = 0
df[adjusted_inflation_column] = None
df[simulated_column] = 0
df[simulated_income_column] = 0
df[simulated_rent_column] = 0
df[simulated_rent_column2] = 0
df[simulated_savings_column] = 0
df[required_deposit_column] = 0
df[affordability_dummy_column] = 'Not Affordable' 
df[BoE_interest_column] = df['BoE interest rates']
df[simulated_mortgage_rate_column] = df[BoE_interest_column] + 0.003
df[simulated_mortgage_payment_column] = 0

df['cumulative_mortgage_payments'] = 0
df[Accumulated_wealth_column] = 0
df['sum dummy'] = 0
df['home ownership dummy'] = 0
df['simulated_dates_quarter'] = df['Simulated date'].apply(date_to_quarter)  
df['shared_ownership_share'] = 0
print(df['Simulated variable mortgage rates'])

#Initial user inputs
consumption_percentage = 0.35
LTV = 0.8

#savings = float(input("Enter your current available savings (£): "))
age = 10 #int(input("What is your age? "))
#income = float(input("Enter your current household income post-Tax (Monthly)"))
#quarterly_income = 3*income

current_year = datetime.now().year
mortgage_term = 67 - age
if mortgage_term > 30:
    mortgage_term = 30

target_year = current_year + mortgage_term
target_quarter_year = f'Q1 {target_year}'

mortgage_term_quarters = mortgage_term * 4
target_row_index = df.index[df['simulated_dates_quarter'] == target_quarter_year][0]
total_mortgage_payments = df.loc[target_row_index:target_row_index + mortgage_term_quarters, simulated_mortgage_payment_column].sum()
#df.at[df.index[-1], 'Simulated Income (quarterly)'] = quarterly_income

base_index = df.at[df.index[-1], index_column]
df.at[df.index[-1], index_column] = 100
base_simulated_income = 100 #quarterly_income

df.at[df.index[-1], index_column] = 100  # Oldest entry for the house price index
df.at[df.index[-1], adjusted_inflation_column] = 100  # Oldest entry for the inflation
base_simulated_price = df.at[df.index[0], price_column]
df.at[df.index[-1], simulated_column] = base_simulated_price # Oldest entry for the inflation 
df.at[df.index[-1], simulated_income_column] = base_simulated_income  # Oldest entry for the inflation
df.at[df.index[-1], simulated_savings_column] = 0 #savings

#House Price Index 
for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
    current_price = df.at[i, price_column]
    previous_price = df.at[i + 1, price_column]
    previous_index = df.at[i + 1, index_column]
    df.at[i, index_column] = previous_index * (current_price / previous_price)

  #Simulated House Price Calculation
    current_index = df.at[i, index_column]
    base_index = 100
    df.at[i, simulated_column] = base_simulated_price * (current_index / base_index)
    
#Deposit
for i in range(df.index[-1], df.index[0] - 1, -1):  
    df.at[i, required_deposit_column] = 0.05 * df.at[i, simulated_column]
    required_deposit = df.at[i, required_deposit_column]

# rent
for i in range(df.index[-1], df.index[0] - 1, -1):  
    simulated_house_price = df.at[i, simulated_column] 
    rent_factor = 0.045/12 
    df.at[i, simulated_rent_column] = simulated_house_price * rent_factor
#convert to quarterly
    df.at[i, simulated_rent_column2] = df.at[i, simulated_rent_column] * 3
    simulated_rent_quarterly = df.at[i, simulated_rent_column2]
    simulated_rent_quarterly = float(simulated_rent_quarterly)

print( df[simulated_rent_column2])