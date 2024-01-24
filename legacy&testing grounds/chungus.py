import os
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
df = pd.read_excel(excel_path, usecols=columns_to_read, parse_dates=['Simulated date'])

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
df['shared_ownership_share'] = 0

explore_shared_ownership = input("Do you want to explore shared ownership options? (yes/no): ").lower()

age = 20

savings = 100000 #float(input("Enter your current available savings (£): "))
df.at[df.index[-1], simulated_savings_column] = savings
def find_mortgage_start_date(df):
    mortgage_start_date = None  # Initialize mortgage_start_date
    for i in range(df.index[-2], df.index[0] - 1, -1):  # Iterate from the second last row to the top
        previous_savings = df.at[i + 1, simulated_savings_column]
        simulated_income_quarterly = df.at[i, simulated_income_column]
        simulated_rent_quarterly = df.at[i, simulated_rent_column2]
        interest = df.at[i, BoE_interest_column]
        
        # Calculate savings for the current quarter
        df.at[i, simulated_savings_column] = (simulated_income_quarterly - (simulated_income_quarterly * consumption_percentage) - simulated_rent_quarterly + (previous_savings * interest))
        current_savings = df.at[i, simulated_savings_column]

quarterly_income = 10000
df.at[df.index[-1], simulated_income_column] = quarterly_income

for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    current_price = df.at[i, price_column]
    previous_price = df.at[i + 1, price_column]
    previous_income = df.at[i + 1, simulated_income_column]
    running_inflation = df.at[i, adjusted_inflation_column]/df.at[i + 1 , adjusted_inflation_column]

    alpha = 0
    growth_factor = ((1 - alpha) * (running_inflation))      +      (alpha * (current_price / previous_price))
    if growth_factor > 1.03:
        growth_factor = 1.03

    df.at[i, simulated_income_column] = previous_income * growth_factor

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


#########################################################################################################################################################################################
if explore_shared_ownership == 'yes':
    min_shared_ownership = 0.10  
    rent_percentage = 0.0275  
    service_charge_ratio = 1/3  
    max_LTV_SO = 0.95  
    mortgage_term = 67 - age  

    start_index = None
    for i in range(df.index[-1], -1, -1):  # Loop from the latest entry backwards
        current_savings = df.at[i, simulated_savings_column]
        home_price = df.at[i, price_column]
        required_deposit_SO = 0.05 * min_shared_ownership * home_price  # Deposit calculation

        if current_savings >= required_deposit_SO:
            start_index = i
            break

    if start_index is None:
        print("You currently do not have enough savings for shared ownership.")
    else:
        cumulative_mortgage_payments = 0
        for i in range(start_index, df.index[0] - 1, -1):
            home_price = df.at[i, price_column]
            current_savings = df.at[i, simulated_savings_column]
            disposable_income = df.at[i, simulated_income_column] - df.at[i, simulated_rent_column]

            required_deposit_SO = 0.05 * min_shared_ownership * home_price

            if current_savings >= required_deposit_SO:
                previous_share_owned = df.at[i + 1, 'shared_ownership_share'] if i < len(df) - 1 else 0
                affordable_mortgage = (disposable_income - (home_price * rent_percentage * (1 - previous_share_owned))) * 12 / (max_LTV_SO / mortgage_term)

                total_affordable_purchase = current_savings + affordable_mortgage - required_deposit_SO
                share_affordable = total_affordable_purchase / home_price
                share_purchased = min(share_affordable, 1 - previous_share_owned)
                total_share_owned = previous_share_owned + share_purchased
                df.at[i, 'shared_ownership_share'] = total_share_owned

                SO_Rent = (1 - total_share_owned) * home_price * rent_percentage
                Service_Charge = SO_Rent * service_charge_ratio

                years_left = 67 - age
                mortgage_amount = min((home_price * total_share_owned) - required_deposit_SO, home_price * max_LTV_SO)
                mortgage_payment_SO = mortgage_amount / years_left

                # Update cumulative mortgage payments
                cumulative_mortgage_payments += mortgage_payment_SO

                # Calculate the total amount paid towards the house (deposit + mortgage payments)
                total_paid_towards_house = required_deposit_SO + cumulative_mortgage_payments

                # Calculate the percentage of the house owned
                percentage_owned = (total_paid_towards_house / home_price) * 100
                df.at[i, 'shared_ownership_share'] = percentage_owned

                # Display the percentage of the house owned
                if percentage_owned < 100:
                    print(f"At {df.at[i, 'simulated_dates_quarter']}, you own {percentage_owned:.2f}% of the house.")
                else:
                    print(f"At {df.at[i, 'simulated_dates_quarter']}, you have reached 100% ownership of the house.")
                    break  # Stop the loop once 100% ownership is reached

        # Calculate final wealth at age 67
        final_wealth_shared_ownership = df.at[df.index[0], simulated_savings_column]
        print(f"Final Wealth at age 67 with Shared Ownership: £{final_wealth_shared_ownership}")
