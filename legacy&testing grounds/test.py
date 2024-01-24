import os
import numpy_financial as np
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


# Define your column names here
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

#Initial user inputs
consumption_percentage = 0.35
savings = float(input("Enter your current available savings (£): "))
age = int(input("What is your age? "))
income = float(input("Enter your current household income post-Tax (Monthly)"))
quarterly_income = 3*income
LTV = 0.8


current_year = datetime.now().year
mortgage_term = 67 - age
if mortgage_term > 30:
    mortgage_term = 30

target_year = current_year + mortgage_term
target_quarter_year = f'Q1 {target_year}'

mortgage_term_quarters = mortgage_term * 4
target_row_index = df.index[df['simulated_dates_quarter'] == target_quarter_year][0]
total_mortgage_payments = df.loc[target_row_index:target_row_index + mortgage_term_quarters, simulated_mortgage_payment_column].sum()
df.at[df.index[-1], simulated_income_column] = quarterly_income

cumulative_affordable = 0
for i in range(df.index[0], df.index[-1] + 1):
    if df.at[i, affordability_dummy_column] == 'Affordable':
        cumulative_affordable += 1  

base_simulated_price = df.at[df.index[0], price_column]
base_index = df.at[df.index[-1], index_column]
df.at[df.index[-1], index_column] = 100
base_simulated_income = quarterly_income

df.at[df.index[-1], index_column] = 100  # Oldest entry for the house price index
df.at[df.index[-1], adjusted_inflation_column] = 100  # Oldest entry for the inflation
df.at[df.index[-1], simulated_column] = base_simulated_price # Oldest entry for the inflation 
df.at[df.index[-1], simulated_income_column] = base_simulated_income  # Oldest entry for the inflation
df.at[df.index[-1], simulated_savings_column] = savings

#First mortgage payment
pv = df.at[df.index[-1], simulated_column]
outstanding_principal = pv * LTV

first_mortgage_rate = (df.at[df.index[-1], simulated_mortgage_rate_column])/12  # First mortgage rate
first_mortgage_payment = (pv *LTV * first_mortgage_rate)/(1-(1 + first_mortgage_rate)**(-mortgage_term_quarters*3))
first_mortgage_payment = first_mortgage_payment * 3
df.at[df.index[-1], simulated_mortgage_payment_column] = first_mortgage_payment


print("First Mortgage Payment Calculation:")
print("PV:", pv, "First Mortgage Rate:", first_mortgage_rate, "First Payment:", first_mortgage_payment)

df.at[i, 'sum dummy'] = cumulative_affordable
df.at[i, 'home ownership dummy'] = int(cumulative_affordable > 0)

def date_to_quarter(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    return f'Q{quarter} {year}'

df['simulated_dates_quarter'] = df['Simulated date'].apply(date_to_quarter)  # Replace 'Column_G' with your actual column name

#print(df.count())

# Calculate the House Price Index and Adjusted Inflation for all entries
for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
    if i >= df.shape[0]:
        break
    # House Price Index Calculation
    current_price = df.at[i, price_column]
    previous_price = df.at[i + 1, price_column]
    previous_index = df.at[i + 1, index_column]
    df.at[i, index_column] = previous_index * (current_price / previous_price)

    #Simulated House Price Calculation
    current_index = df.at[i, index_column]
    base_index = 100
    df.at[i, simulated_column] = base_simulated_price * (current_index / base_index)
    
    # Adjusted Inflation Calculation
    current_inflation = df.at[i, inflation_column]
    previous_inflation = df.at[i + 1, inflation_column]
    previous_adjusted_inflation = df.at[i + 1, adjusted_inflation_column]
    df.at[i, adjusted_inflation_column] = previous_adjusted_inflation * (current_inflation / previous_inflation)
    adjusted_inflation = df.at[i, adjusted_inflation_column]

    #Simulated Income (quarterly) Calculation
    previous_income = df.at[i + 1, simulated_income_column]

    current_inflation = df.at[i, adjusted_inflation_column]
    previous_inflation = df.at[i + 1, adjusted_inflation_column]

    alpha = 0
    growth_factor = ((1 - alpha) * (adjusted_inflation/100)) + (alpha * (current_price / previous_price))
    growthfactor = float(growth_factor)
    if growth_factor > 1.03:
        growth_factor = 1.03

    df.at[i, simulated_income_column] = previous_income * growth_factor
    #df.at[i, simulated_income_column] = previous_income * (current_inflation/previous_inflation)

    #print('growth factor: ', growth_factor)

    #Simulated Rent (monthly) Calculation
    simulated_house_price = df.at[i, simulated_column] 
    rent_factor = 0.045/12 
    df.at[i, simulated_rent_column] = simulated_house_price * rent_factor

    #Simluated Rent (quarterly) Calculation
    df.at[i, simulated_rent_column2] = df.at[i, simulated_rent_column] * 3
    simulated_rent_quarterly = df.at[i, simulated_rent_column2]
    simulated_rent_quarterly = float(simulated_rent_quarterly)

    #Simulated Savings while Renting Calculation
    previous_savings = df.at[i + 1, simulated_savings_column]
    previous_savings = float(previous_savings)
    simulated_income_quarterly = df.at[i, simulated_income_column]
    simulated_income_quarterly = float(simulated_income_quarterly)
    interest = df.at[i, BoE_interest_column]
    interest = float(interest)

    df.at[i, simulated_savings_column] = (simulated_income_quarterly - (simulated_income_quarterly * consumption_percentage) - simulated_rent_quarterly + (previous_savings * interest))
    
    #Mortgage rate
    current_mortgage_rate = df.at[i, simulated_mortgage_rate_column] / 12  # Monthly rate
    remaining_term = mortgage_term_quarters * 3 - ((df.index[-2] - i) * 3)

    #Wt
    Wt = (1- consumption_percentage) * simulated_income_quarterly

    #Mortgage payment
    if outstanding_principal > 0 and remaining_term > 0:
        mortgage_payment = np.pmt(current_mortgage_rate, remaining_term, -outstanding_principal)
    else:
        mortgage_payment = 0
    
    df.at[i, simulated_mortgage_payment_column] = mortgage_payment

    interest_payment = outstanding_principal * current_mortgage_rate
    principal_payment = mortgage_payment - interest_payment
    outstanding_principal = max(outstanding_principal - principal_payment, 0)

    
    df.at[i, required_deposit_column] = 0.05 * df.at[i, simulated_column]
    required_deposit = df.at[i, required_deposit_column]

    #Mortgage affordable
    home_value = df.at[i, simulated_column]
    potential_loan_amount = 4.5 * 4 * simulated_income_quarterly

df.at[df.index[-1], simulated_rent_column2] = df.at[df.index[-1], simulated_column] * rent_factor * 3

#End of work wealth parameters 
retirement_age = 67
current_quarter = (datetime.now().month - 1) // 3 + 1
years_until_retirement = retirement_age - age
retirement_year = current_year + years_until_retirement
retirement_quarter = 'Q' + str(current_quarter) + ' ' + str(retirement_year)
retirement_row_index = df[df['simulated_dates_quarter'] == retirement_quarter].index.min()


initial_house_price = df.at[df.index[-1], 'Simulated house prices']  # Adjust the column name as needed
cumulative_mortgage_payments = 0

for i in range(len(df) - 1, -1, -1):
    current_mortgage_payment = df.at[i, simulated_mortgage_payment_column]
    BoE_interest = df.at[i, BoE_interest_column]
    quarterly_income = df.at[i, simulated_income_column]

    cumulative_mortgage_payments += current_mortgage_payment

    df.at[i, 'cumulative_mortgage_payments'] = cumulative_mortgage_payments

    # Check if mortgage is considered paid off
    if i == len(df) - 1 or cumulative_mortgage_payments >= initial_house_price:
        previous_wealth = 0
    else:
        previous_wealth = df.at[i + 1, Accumulated_wealth_column]

    df.at[i, Accumulated_wealth_column] = previous_wealth * (1 + BoE_interest) + Wt

print(df['cumulative_mortgage_payments'])

#Total equity retirement
if pd.isna(retirement_row_index):
    print("No matching retirement quarter/year found in the data.")
else:
    house_value_at_retirement = df.at[retirement_row_index, simulated_column]
    house_value_at_retirement = float(house_value_at_retirement)
    total_mortgage_payments_until_retirement = df.loc[target_row_index:retirement_row_index, simulated_mortgage_payment_column].sum()
    total_mortgage_payments_until_retirement = float(total_mortgage_payments_until_retirement)
    savings_accumulation_at_retirement = df.at[retirement_row_index, Accumulated_wealth_column]
    savings_accumulation_at_retirement = float(savings_accumulation_at_retirement)

    final = house_value_at_retirement - total_mortgage_payments_until_retirement + savings_accumulation_at_retirement
    #print(f"User's equity at the time of retirement (age 67): £{final}")

#Check section
for i in range(df.index[-2], df.index[0] - 1, -1):    
    df.at[i, 'Required deposit'] = required_deposit  # Adding this line to store the required deposit

    # Compare Savings to Required Deposit
    if df.at[i, simulated_savings_column] >= required_deposit:
        df.at[i, affordability_dummy_column] = 'Affordable'
    else:
        df.at[i, affordability_dummy_column] = 'Not Affordable'

def get_house_price_data(df, target_quarter_year):
    if target_quarter_year in df['simulated_dates_quarter'].values:
        matching_rows = df[df['simulated_dates_quarter'] == target_quarter_year]
        if not matching_rows.empty:
            affordability_status = matching_rows[affordability_dummy_column].iloc[0]
            print(f"By {target_quarter_year}, at the end of your mortgage term, home ownership is {affordability_status}.")
            print(f"User's equity at the time of retirement (age 67): £{final}")

        else:
            print(f"No data available for {target_quarter_year}.")
            
    else:
        print("The specified quarter/year does not exist in the data.")

get_house_price_data(df, target_quarter_year)


# Loop through the DataFrame and check values 
#for i in range(len(df)):
#   print(f"Row {i}: Rent = {df.at[i, simulated_rent_column2]}")

explore_shared_ownership = input("Do you want to explore shared ownership options? (yes/no): ").lower()

if explore_shared_ownership == 'yes':
    min_shared_ownership = 0.10  # Minimum required stake in the property
    rent_percentage = 0.0275  # Rent paid on the share owned by the housing association
    service_charge_ratio = 1/3  # Service charge as a fraction of the rent
    max_LTV_SO = 0.95  # Maximum LTV for Shared Ownership
    mortgage_term = 67 - age  # Assuming 'age' is defined

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
