import os
import pandas 

def get_house_price_data(df, quarter_year, consumption_percentage, savings, mortgage_rate, mortgage_term):
    # Define the column names based on your Excel file
    quarter_column = 'Quarter'
    price_column = 'LONDON HOUSE PRICES (£)'
    index_column = 'House price index'
    simulated_column = 'Simulated house prices'
    inflation_column = 'Inflation'  # Added inflation column name
    adjusted_inflation_column = 'Adjusted Inflation'
    simulated_income_column = 'Simulated income (quarterly)'
    simulated_rent_column = 'Simulated Rent (Monthly)'
    simulated_rent_column2 = 'Simulated Rent (Quarterly)'
    simulated_savings_column = 'Simulated savings while renting'
    required_deposit_column = 'Required deposit HO' 
    affordability_dummy_column = 'Home Ownership Affordability'

    # Initialize model data frame by column
    df[index_column] = None
    df[adjusted_inflation_column] = None
    df[simulated_column] = None
    df[simulated_income_column] = None
    df[simulated_rent_column] = None
    df[simulated_rent_column2] = None
    df[required_deposit_column] = None
    df[simulated_savings_column] = None
    df[affordability_dummy_column] = 'Not Affordable'  #default
    df['sum dummy'] = 0
    df['home ownership dummy'] = 0

    cumulative_affordable = 0
    for i in range(df.index[0], df.index[-1] + 1):
        if df.at[i, affordability_dummy_column] == 'Affordable':
            cumulative_affordable += 1  

    base_simulated_price = df.at[df.index[0], price_column]
    base_index = df.at[df.index[-1], index_column]
    df.at[df.index[-1], index_column] = 100
    base_simulated_income = 10000

    df.at[df.index[-1], index_column] = 100  # Oldest entry for the house price index
    df.at[df.index[-1], adjusted_inflation_column] = 100  # Oldest entry for the inflation
    df.at[df.index[-1], simulated_column] = base_simulated_price # Oldest entry for the inflation 
    df.at[df.index[-1], simulated_income_column] = base_simulated_income  # Oldest entry for the inflation

    df.at[i, 'sum dummy'] = cumulative_affordable
    df.at[i, 'home ownership dummy'] = int(cumulative_affordable > 0)

    # Update savings based on input
    df.at[df.index[-1], simulated_savings_column] = savings

    # Calculate the House Price Index and Adjusted Inflation for all entries
    for i in range(df.index[-2], df.index[0] - 1, -1):  # Start from the second last row to the top
        # House Price Index Calculation
        current_price = df.at[i, price_column]
        previous_price = df.at[i + 1, price_column]
        previous_index = df.at[i + 1, index_column]
        df.at[i, index_column] = previous_index * (current_price / previous_price)

        # Simulated House Price Calculation
        current_index = df.at[i, index_column]
        df.at[i, simulated_column] = base_simulated_price * (current_index / base_index)
        
        # Adjusted Inflation Calculation
        current_inflation = df.at[i, inflation_column]
        previous_inflation = df.at[i + 1, inflation_column]
        previous_adjusted_inflation = df.at[i + 1, adjusted_inflation_column]
        df.at[i, adjusted_inflation_column] = previous_adjusted_inflation * (current_inflation / previous_inflation)

        # Simulated Income (quarterly) Calculation
        previous_income = df.at[i + 1, simulated_income_column]
        df.at[i, simulated_income_column] = previous_income * ((0.5 * (current_inflation / previous_inflation)) + (0.5 * (current_index / previous_index)))

        # Simulated Rent (monthly) Calculation
        simulated_house_price = df.at[i, simulated_column] 
        rent_factor = 0.045 / 12 
        df.at[i, simulated_rent_column] = simulated_house_price * rent_factor

        # Simulated Rent (quarterly) Calculation
        df.at[i, simulated_rent_column2] = df.at[i, simulated_rent_column] * 3

        # Simulated Savings while Renting Calculation
        previous_savings = df.at[i + 1, simulated_savings_column]
        df.at[i, simulated_savings_column] = previous_savings * (1 - consumption_percentage) + df.at[i, simulated_income_column]

        # Required Deposit Calculation
        df.at[i, required_deposit_column] = 0.05 * df.at[i, simulated_column]

        # Check if savings are enough for deposit
        if df.at[i, simulated_savings_column] >= df.at[i, required_deposit_column]:
            df.at[i, affordability_dummy_column] = 'Affordable'
        else:
            df.at[i, affordability_dummy_column] = 'Not Affordable'

    # Retrieve and return data for the specified quarter/year
    if quarter_year in df[quarter_column].values:
        return {
            'simulated_savings_value': df.loc[df[quarter_column] == quarter_year, simulated_savings_column].iloc[0],
            'simulated_price': df.loc[df[quarter_column] == quarter_year, simulated_column].iloc[0],
            'affordability_status': df.loc[df[quarter_column] == quarter_year, affordability_dummy_column].iloc[0],
        }
    else:
        return {"error": "The specified quarter/year does not exist in the data."}

# 