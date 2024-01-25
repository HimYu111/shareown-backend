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
df[affordability_dummy_column] = 'not affordable'
df[BoE_interest_column] = 0.02
df[simulated_mortgage_rate_column] = 0
df[simulated_mortgage_payment_column] = 0.0
df['cumulative_mortgage_payments'] = 0
df[Accumulated_wealth_column] = 0
df['sum dummy'] = 0
df['home ownership dummy'] = 0
df[simulated_dates_quarter] = df[simulated_date].apply(date_to_quarter)
df['shared_ownership_share'] = 0


def get_house_price_data(consumption_percentage, savings, age, income):

    ################################################################################################
    #inputs
    quarterly_income = 3*income


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

    #savings and deposit
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

            # Check if current savings exceed required deposit
            required_deposit = df.at[i, required_deposit_column]
            if current_savings >= required_deposit:
                mortgage_start_date = df.at[i, 'Simulated date']
                break
        return mortgage_start_date

    mortgage_start_date = find_mortgage_start_date(df)
    mortgage_term_quarters = None

    #mortgage term
    if mortgage_start_date:
        mortgage_start_year = mortgage_start_date.year

        current_year = datetime.now().year
        age_at_start = age + (mortgage_start_year - current_year)

        # Determine the mortgage term
        mortgage_term = 67 - age_at_start
        if mortgage_term > 30:
            mortgage_term = 30
        mortgage_term_quarters = mortgage_term * 4

    print(df[simulated_savings_column])

    #mortgage payment
    # First, find the row index where the user has enough for a deposit
    deposit_affordable_index = None
    for i in range(df.index[-1], df.index[0] - 1, -1):
        if df.at[i, simulated_savings_column] > df.at[i, required_deposit_column]:
            deposit_affordable_index = i
            initial_house_value = df.at[i, simulated_column]
            break



    if deposit_affordable_index is not None and mortgage_term_quarters is not None:
        # Calculate initial loan amount
        loan_amount = initial_house_value * LTV
        total_payments = mortgage_term_quarters * 3

        # Iterate from the deposit affordable point to the start of the DataFrame
        for i in range(deposit_affordable_index, df.index[0] - 1, -1):
            # Update the mortgage rate for the quarter
            annual_interest_rate = df.at[i, simulated_mortgage_rate_column]
            monthly_interest_rate = annual_interest_rate / 12

            # Calculate remaining payments
            payments_made = (deposit_affordable_index - i) * 3  # Convert quarters to months
            remaining_payments = total_payments - payments_made

            # Mortgage payment calculation
            if remaining_payments > 0 and monthly_interest_rate != 0:
                monthly_mortgage_payment = loan_amount * (monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -remaining_payments))
                quarterly_mortgage_payment = monthly_mortgage_payment * 3
            else:
                quarterly_mortgage_payment = 0

            # Update the DataFrame with the quarterly mortgage payment
            df.at[i, simulated_mortgage_payment_column] = quarterly_mortgage_payment

            # Update the loan amount for the next quarter
            if quarterly_mortgage_payment > 0:
                principal_payment = monthly_mortgage_payment - (loan_amount * monthly_interest_rate)
                loan_amount = max(loan_amount - principal_payment * 3, 0)  # Ensure loan amount doesn't go negative
        with pd.option_context('display.max_rows', None):
            print(df[simulated_mortgage_payment_column])
    else:
        print("Deposit affordable index not found or initial house value is zero.")

    #cumalative mortgage payment
    df['cumulative_mortgage_payments'] = 0.0
    for i in range(df.index[-1], df.index[0] - 1, -1):
        if i == df.index[-1]:
            df.at[i, 'cumulative_mortgage_payments'] = df.at[i, simulated_mortgage_payment_column]
        else:
            df.at[i, 'cumulative_mortgage_payments'] = df.at[i, simulated_mortgage_payment_column] + df.at[i + 1, 'cumulative_mortgage_payments']


    pd.set_option('display.max_columns', None)
    print(df['cumulative_mortgage_payments'])

    #mortgage check
    df['mortgage_check'] = 0.0
    for i in range(df.index[-1], df.index[0] - 1, -1):
        # Check if savings are greater than the required deposit
        if df.at[i, simulated_savings_column] > df.at[i, required_deposit_column]:
            deposit_affordable_index = i
            initial_house_value = df.at[i, simulated_column]

        # Set the 'mortgage_check' for the current row
        if 'initial_house_value' in locals():
            df.at[i, 'mortgage_check'] = initial_house_value - df.at[i, 'cumulative_mortgage_payments']
        else:
            df.at[i, 'mortgage_check'] = 0  # Or some other default value if initial_house_value is not set

    ################################################################################################
    #Affordability check
    df['Affordability Status'] = 'not affordable'
    for i in range(df.index[-1], df.index[0] - 1, -1):
        current_savings = df.at[i, simulated_savings_column]
        required_deposit = df.at[i, required_deposit_column]
        simulated_income_quarterly = df.at[i, simulated_income_column]

        potential_loan_amount = 4.5 * 4 * simulated_income_quarterly
        house_value = df.at[i, simulated_column]
        remaining_value = house_value * LTV - required_deposit

        # Check if both savings for deposit and loan amount are sufficient
        if current_savings >= required_deposit and potential_loan_amount >= remaining_value:
            df.at[i, 'Affordability Status'] = 'affordable'
            break  # Stop the loop as we found the point where the us

    ################################################################################################
    #Accumulation
    df['saved_wealth'] = 0.0
    current_year = datetime.now().year
    df['age_at_time'] = age + (df[simulated_date].dt.year - current_year)

    tracked_saved_wealth = 0.0
    for i in range(df.index[-1], df.index[0] - 1, -1):
        mortgage_paid_off = df.at[i, 'mortgage_check'] < 0
        under_retirement_age = df.at[i, 'age_at_time'] < 67

        if mortgage_paid_off and under_retirement_age:
            income = df.at[i, simulated_income_column]
            consumption = income * consumption_percentage
            interest_rate = df.at[i, BoE_interest_column]  # Convert interest rate to a decimal

            # Update tracked saved wealth
            tracked_saved_wealth = tracked_saved_wealth * (1 + interest_rate) + income - consumption

        df.at[i, 'saved_wealth'] = tracked_saved_wealth

    #Wealth accumulated
    for i in range(len(df)):
        house_value_at_67 = df.at[i, simulated_column]
        accumulated_mortgage_payments_at_67 = df.at[i, 'cumulative_mortgage_payments']
        saved_wealth_at_67 = df.at[i, 'saved_wealth']

        df.at[i, Accumulated_wealth_column] = house_value_at_67 - (accumulated_mortgage_payments_at_67 + saved_wealth_at_67)

    ################################################################################################
    #Shared ownership
    import math

    # Ask the user if they want to explore shared ownership options
    explore_shared_ownership = 'yes' #' #input("Do you want to explore shared ownership options? (yes/no): ").lower()

    if explore_shared_ownership == 'yes':
        min_shared_ownership = 0.25  # Minimum share for shared ownership
        rent_percentage = 0.0275  # Rent percentage of property value
        service_charge_ratio = 1 / 3  # Ratio of service charge to rent
        max_LTV_SO = 0.95  # Maximum loan-to-value ratio for shared ownership
        mortgage_term = 67 - age  # Mortgage term ending at age 67

        # Find the starting point for shared ownership
        start_index = None
        for i in range(df.index[-1], -1, -1):
            current_savings = df.at[i, simulated_savings_column]
            home_price = df.at[i, price_column]
            required_deposit_SO = 0.05 * min_shared_ownership * home_price
            if current_savings >= required_deposit_SO:
                start_index = i
                initial_savings = current_savings
                initial_home_price = home_price
                break

        if start_index is None:
            print("You currently do not have enough savings for shared ownership.")
        else:
            cumulative_mortgage_payments = 0
            last_percentage_owned = 0  # Track the last percentage owned to ensure it never decreases
            for i in range(start_index, df.index[0] - 1, -1):
                home_price = df.at[i, price_column]
                current_savings = df.at[i, simulated_savings_column]
                disposable_income = df.at[i, simulated_income_column] - df.at[i, simulated_rent_column]

                previous_share_owned = df.at[i + 1, 'shared_ownership_share'] if i < df.index[-1] else 0

                # Check if we can buy more shares
                if current_savings >= home_price * 0.01:  # Check if savings are enough for at least 1% share
                    share_affordable = current_savings / home_price
                    share_purchased = max(0, math.floor(share_affordable * 100) / 100)
                    share_purchased = min(share_purchased, 1 - previous_share_owned)
                    current_savings -= share_purchased * home_price  # Update savings after purchasing
                else:
                    share_purchased = 0

                total_share_owned = max(last_percentage_owned, previous_share_owned + share_purchased)
                df.at[i, 'shared_ownership_share'] = total_share_owned
                last_percentage_owned = total_share_owned  # Update the last percentage owned

                # Update other financial elements
                SO_Rent = (1 - total_share_owned) * home_price * rent_percentage
                Service_Charge = SO_Rent * service_charge_ratio
                years_left = 67 - age
                mortgage_amount = min((home_price * total_share_owned) - required_deposit_SO, home_price * max_LTV_SO)
                mortgage_payment_SO = mortgage_amount / years_left

                cumulative_mortgage_payments += mortgage_payment_SO

                total_paid_towards_house = required_deposit_SO + cumulative_mortgage_payments
                percentage_owned = min(100, max(math.floor((total_paid_towards_house / home_price) * 100), last_percentage_owned))

                # Cap at 100% ownership
                df.at[i, 'shared_ownership_share'] = percentage_owned
                if percentage_owned >= 100:
                    print(f"At {df.at[i, 'simulated_dates_quarter']}, you have reached 100% ownership of the house.")
                    age_at_SO = int(df.at[i, 'age_at_time'])
                    break

                print(f"At {df.at[i, 'simulated_dates_quarter']}, you own {percentage_owned}% of the house.")

    affordability_status = df['Affordability Status'].iloc[-1]
    accumulated_wealth_at_67 = df[df['age_at_time'] == 67][Accumulated_wealth_column].iloc[0] if not df[df['age_at_time'] == 67].empty else 'not Applicable'
    x = 100 - consumption_percentage
    transformed_wealth_data = int(accumulated_wealth_at_67/((1+0.03)**(67-age)))
    initial_share = math.floor(initial_savings/ initial_home_price )

    age_at_time_data = df['age_at_time'].to_json(orient='records')
    accumulated_wealth_data = df[Accumulated_wealth_column].to_json(orient='records')
    latest_simulated_column_value = df[simulated_column].iloc[-1]
    shared_ownership_share_data = df['shared_ownership_share'].to_json(orient='records')


    results = {
        "affordability_status": df['Affordability Status'].iloc[-1],
        "accumulated_wealth_at_67": df[df['age_at_time'] == 67][Accumulated_wealth_column].iloc[0] if not df[df['age_at_time'] == 67].empty else 'not Applicable',
        "x": 100 - consumption_percentage,
        "house_price": df.at[df.index[-2], simulated_column],
        "full_data": df.to_dict(orient="records"),
        "age_at_SO": age_at_SO,
        "age_at_time": age_at_time_data,
        "accumulated_wealth": accumulated_wealth_data,
        "latest_simulated_value": latest_simulated_column_value,
        "shared_ownership_share": shared_ownership_share_data,
        "transformed_wealth": transformed_wealth_data,
        "initial_share": initial_share

    }
    return results
 