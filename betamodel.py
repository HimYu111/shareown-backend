import os as os
import pandas as pd
import math
import json

inflation_adjustment = 0.5

###############

savings_rate = 0.03
inflation = 0.03
mortgage_rate = 0.04
#house_price_appreciation = 0.05
house_maintainance_cost = 0.01
mortgage_term = 30
transaction_cost = 0

############ TO
LTV = 0.95
loan_ratio = 4.5

############ SO1
max_inc_to_exp = 0.4
rent_appreciation = 0.035
minimum_initial_share = 0.25
initial_rent_percent = 0.0275
staircase_admin = 1000
service_charge = 0.01
affordability_cons = 0.4

#house_price = 300000
#FTB = 0
#gross = 50000
#consumption = 1500
#age = 18
#savings = 10000
#rent = 1300

def get_house_data(postcode, propertyType, sheet_name='Appreciation Rate'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(script_dir, 'Appreciation Rates 1996 to 2023.xlsx')

    if not os.path.exists(excel_path):
        print("Excel file does not exist.")
        return "Excel file does not exist."

    try:
        df = pd.read_excel(excel_path, engine='openpyxl', header=6, sheet_name=sheet_name)
        print(df.columns)  # Debug: Print the DataFrame columns after load
    except Exception as e:
        return f"Failed to load Excel file: {e}"

    propertyType = propertyType.lower()
    propertyType_to_column = {
        'detached': 'Detached',
        'semi-detached': 'Semi-Detached',
        'terraced': 'Terraced',
        'apartment': 'Apartment',
        'undecided': 'Undecided'
    }

    if propertyType not in propertyType_to_column:
        return "Invalid house type specified"
    column_name = propertyType_to_column[propertyType]

    try:
        # Ensure case-insensitive matching for local authorities
        df['Local authority name'] = df['Local authority name'].astype(str).str.lower()
        # Try to get the house price appreciation value
        house_price_appreciation = df[df['Local authority name'] == postcode.lower()][column_name].values[0]
        return house_price_appreciation
    except IndexError:
        return "Local authority name not found or no data in the specified column"

#
def get_house_price_data(postcode, propertyType, bedrooms, occupation, house_price, FTB, gross, consumption, age, savings, rent, loan_repayment):
    #Basic###################################################################
    print(postcode)
    print(propertyType)
    print(bedrooms)
    print(occupation)
    house_price = int(house_price)
    gross = int(gross)
    consumption = int(consumption)
    age = int(age)
    savings = int(savings)
    rent = int(rent)
    house_price_appreciation = get_house_data(postcode, propertyType)
    house_price_appreciation = float(house_price_appreciation)
    print(house_price_appreciation)
    loan_repayment = float(loan_repayment)
    loan_repayment = loan_repayment*12


    num_rows = 68 - age
    retirement_age = 67
    df = pd.DataFrame({'D': range(age, 68)}, index=range(num_rows))

    additional_columns = ['E', 'F', 'G', 'H', 'I', 'J', 'N0', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'N1', 'N2', 'W', 'X', 
    'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 
    'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 
    'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ', 'CA', 'CB', 'CC', 'CD',  'N3', 'N4', 'N5', 'N6', 'N7', 'N8']


    for col in additional_columns:
        df[col] = 0  # Initialize other columns here

    annual_rent = rent * 12 
    
    basic_rate = 0.20
    higher_rate = 0.40
    additional_rate = 0.45
    allowance = 12570
    basic_threshold = 50270
    higher_threshold = 125140
    if gross <= allowance:
        tax = 0 
    elif gross <= basic_threshold:
        tax = (gross - allowance)  * basic_rate
    elif gross <= higher_threshold:
        tax = ((basic_threshold - allowance)  * basic_rate) + (gross - basic_threshold) * higher_rate
    else:
        tax = ((basic_threshold- allowance)  * basic_rate) + (higher_threshold - basic_threshold) * higher_rate + (gross - higher_threshold) * additional_rate
    income = gross - tax
    non_housing_exp = (consumption*12)/income

    for i in range(len(df)):
        # Period
        df.at[i, 'E'] = df.at[i, 'D'] - age
        
    #Calculate house price appreciation for each year and set in 'F'
        df.at[i, 'F'] = house_price * ((1 + house_price_appreciation) ** df.at[i, 'E'])
                    
    #income growth 
        if 22 <= df.at[i, 'D'] <= 29:
            growth = 0.036
        elif 30 <= df.at[i, 'D'] <= 39:
            growth = 0.027
        elif 40 <= df.at[i, 'D'] <= 49:
            growth = 0.006
        elif 50 <= df.at[i, 'D'] <= 59:
            growth = -0.01
        elif df.at[i, 'D'] >= 60:
            growth = 0.0
        else:
            growth = 0  # For ages outside the specified ranges 
        df.at[i, 'G'] = growth
    
    #income growth inflation adjustment
        df.at[i, 'H'] = df.at[i, 'G'] + (inflation_adjustment*inflation)

    #income and non housing consumption
        df.at[0, 'I'] = income
        df.at[0, 'J'] = df.at[0, 'I'] * non_housing_exp
        for i in range(1, len(df)):
            if df.at[i-1, 'I'] is not None and df.at[i, 'H'] is not None:
                df.at[i, 'I'] = df.at[i-1, 'I'] * (1 + df.at[i, 'H'])
            else:
                df.at[i, 'I'] = None

            df.at[i, 'J'] = df.at[i, 'I'] * non_housing_exp
            
    #non housing consumption + repayment
    df.at[0, 'N0'] = df.at[0, 'J'] + loan_repayment
    for i in range (1, len(df)): 
        df.at[i, 'N0'] = df.at[i, 'J'] + loan_repayment


    #private rent and savings 
        df.at[0, 'K'] = annual_rent
        df.at[0, 'L'] = df.at[0, 'I'] - df.at[0, 'N0'] - df.at[0, 'K'] 

        for i in range(1, len(df)):
            if df.at[i-1, 'K'] is not None:
                df.at[i, 'K'] = df.at[i-1, 'K'] * (1 + ((0.5*inflation)+(0.5*house_price_appreciation)))
            else:
                df.at[i, 'K'] = None
        
        #Annual Savings 
            df.at[i, 'L'] = df.at[i, 'I'] - df.at[i, 'N0'] - df.at[i, 'K'] 

     #Total Savings 
        df.at[0, 'M'] = (savings)
        for i in range(1, len(df)):
            if df.at[i-1, 'M'] is not None:
                df.at[i, 'M'] = df.at[i-1, 'M']*(1 + savings_rate) + df.at[i, 'L']
            else:
                df.at[i, 'M'] = None

################################################################ 
#SDLT 
    for i in range(len(df)):
        # SDLT FTB
        if df.at[i, 'F'] >= 425000:
            df.at[i, 'N'] = 0.05 * (df.at[i, 'F'] - 425000)
        else: 
                df.at[i, 'N'] = 0 
        # SDLT STB     
        if df.at[i, 'F'] >= 250000:
            df.at[i, 'O'] = 0.05 * (df.at[i, 'F'] - 250000)
        else: 
                df.at[i, 'O'] = 0 
        df.at[i, 'P'] = (FTB * df.at[i, 'N']) + ((1 - FTB)*df.at[i, 'O']) 

        #Total savings net of SDLT and transaction cost = deposit
        df.at[i, 'Q'] = df.at[i, 'M']  - df.at[i, 'P'] - transaction_cost

        #deposit constraints
        if df.at[i, 'Q'] >= ((1 - LTV)*df.at[i, 'F']) - 0.001:
            df.at[i, 'R'] = 1 
        else:
            df.at[i, 'R'] = 0 

        df['S'] = df['R'].cumsum()
        df['S'] = (df['S'] >= 1).astype(int)
        #income constraint
        if df.at[i, 'I']* loan_ratio >= df.at[i, 'F'] - df.at[i, 'Q']:
            df.at[i, 'T'] = 1 
        else:
            df.at[i, 'T'] = 0 
        #income constraint 1 
        df['U'] = df['T'].cumsum()
        df['U'] = (df['U'] >= 1).astype(int)

        #DSCR constraint
    for i in range(len(df)):
        # Calculate df['N1']
        if pd.isna(df.at[i, 'D']):
            df.at[i, 'N1'] = None
        else:
            max_term = max(retirement_age - age, 30)
            numerator = mortgage_rate * (1 + mortgage_rate) ** max_term
            denominator = (1 + mortgage_rate) ** max_term - 1
            mortgage_payment = (df.at[i, 'F'] - df.at[i, 'Q']) * numerator / denominator
            if 0.4 * df.at[i, 'I'] >= mortgage_payment:
                df.at[i, 'N1'] = 1
            else:
                df.at[i, 'N1'] = 0
    
        #DSCR adjusted
        if pd.isna(df.at[i, 'D']):
            df.at[i, 'N2'] = None
        else:
            if df.loc[:i, 'N1'].sum() >= 1:
                df.at[i, 'N2'] = 1
            else:
                df.at[i, 'N2'] = 0

        #home buying decision
        df.at[i, 'V'] = df.at[i, 'S']*df.at[i, 'U']*df.at[i, 'N2']

    #home buying indicator  
    df.at[0, 'W'] = 1 if df.at[0, 'V'] != 0 else 0
    for i in range(1, len(df)):
        if df.at[i, 'V'] == df.at[i-1, 'V']:
            df.at[i, 'W'] = 0
        else:
            df.at[i, 'W'] = 1

    for i in range(len(df)):
        # Mortgage loan
        if i == 0 or (df.at[i, 'V'] == 1 and df.at[i-1, 'V'] == 0):
            df.at[i, 'X'] = df.at[i, 'V'] * (df.at[i, 'F'] - df.at[i, 'Q'])
        else:
            df.at[i, 'X'] = 0
        
        # Homeowner Savings
        if df.at[i, 'W'] == 1:
            df.at[i, 'Y'] = 0
        else:
            df.at[i, 'Y'] = df.at[i, 'V'] * (df.at[i, 'I'] - df.at[i, 'N0'] - df.at[i, 'F'] * house_maintainance_cost)
        
        # Outstanding Loan
        if i == 0:
            if df.at[i, 'W'] == 1: 
                df.at[i, 'Z'] = df.at[i, 'X']
            else: 
                df.at[i, 'Z'] = 0 - df.at[i, 'Y']  # Adjusted to handle the case for the first row
        else:
            if df.at[i, 'W'] == 1:
                df.at[i, 'Z'] = df.at[i, 'X']
            else:
                df.at[i, 'Z'] = df.at[i-1, 'Z'] * (1 + mortgage_rate) - df.at[i, 'Y']
        
    # Outstanding Loan adjusted
    for i in range(len(df)):
        df.at[i, 'AA'] = max(df.at[i, 'Z'], 0)
        
        # Savings indicator
        if i > 0 and df.at[i, 'Z'] <= 0 < df.at[i-1, 'Z']:
            df.at[i, 'AB'] = -df.at[i, 'Z'] * ((1 + savings_rate) / (1 + mortgage_rate))
        else:
            df.at[i, 'AB'] = 0
    
    # Repayment indicator
    df.at[0, 'AC'] = 0
    df.at[0, 'AD'] = 0
    df.at[0, 'AE'] = df.at[0, 'AC'] * df.at[0, 'Y']
    for i in range(1, len(df)):
        df.at[i, 'AC'] = 1 if df.at[i, 'AB'] > 0 or df.at[i-1, 'AC'] > 0 else 0
        
        # Repayment dummy
        df.at[i, 'AD'] = 1 if df.at[i, 'AC'] != df.at[i-1, 'AC'] else 0
    
    # Period Savings
    for i in range(len(df)):
        if df.at[i, 'AD'] == 1:
            df.at[i, 'AE'] = df.at[i, 'AB']
        else:
            df.at[i, 'AE'] = df.at[i, 'AC'] * df.at[i, 'Y']
    #Liquid wealth
    df.at[0, 'AF'] = df.at[0, 'AE'] 
    df.at[0, 'AG'] = (1 - df.at[0, 'V']) * df.at[0, 'M'] + df.at[0, 'V'] * df.at[0, 'AF']
    for i in range(1, len(df)):
        df.at[i, 'AF'] = df.at[i-1, 'AF'] * (1 + savings_rate) + df.at[i, 'AE']
        df.at[i, 'AG'] = (1 - df.at[i, 'V']) * df.at[i, 'M'] + df.at[i, 'V'] * df.at[i, 'AF']

    for i in range(len(df)):
    #Housing wealth
        df.at[i, 'AH'] = df.at[i, 'V']*(df.at[i, 'F'] - df.at[i, 'AA'] ) 
    #inflation index
        df.at[i, 'AI'] = (1 + inflation)**df.at[i, 'E']
    #Age
        df.at[i, 'AJ'] = df.at[i, 'D']
    #Discounted liquid wealth 
        df.at[i, 'AK'] = df.at[i, 'AG']/df.at[i, 'AI']
    #Discounted housing wealth 
        df.at[i, 'AL'] = df.at[i, 'AH']/df.at[i, 'AI']
    #Outstanding LTV
        df.at[i, 'AM'] = 100*df.at[i, 'AH']/df.at[i, 'F']

##################################
    #Min Deposit 
    for i in range(len(df)):
        df.at[i, 'AN'] = df.at[i, 'F']*minimum_initial_share*(1-LTV)
        if (df.at[i, 'M'] - staircase_admin) > df.at[i, 'AN']:
            df.at[i, 'AO'] = 1
        else:
            df.at[i, 'AO'] = 0
    #deposit constraint adjusted
        df['AP'] = df['AO'].cumsum()
        df['AP'] = (df['AP'] >= 1).astype(int)
    #potential mortgage payment 
        df.at[i,'AQ'] = (df.at[i, 'F'] * minimum_initial_share * LTV) * mortgage_rate / (mortgage_rate if df.at[i, 'D'] == retirement_age else (1 - 1 / ((1 + mortgage_rate) ** min(mortgage_term, retirement_age- df.at[i, 'D']))))
    #Potential rental payment 
        df.at[i,'AR'] = df.at[i, 'F']*initial_rent_percent*(1-minimum_initial_share)
    
    #Affordability constraint and adjusted 
        if (affordability_cons*df.at[i,'I']) >= ((df.at[i,'F']*service_charge) + df.at[i,'AQ'] + df.at[i, 'AR']):
            df.at[i,'AS'] = 1
        else:
            df.at[i,'AS'] = 0
        df['AT'] = (df['AS'].cumsum() >= 1).astype(int)
    #Affordability constraint bank and adjusted 
        if (df.at[i,'I']*(gross/income)*loan_ratio) >= minimum_initial_share*df.at[i,'F']-(df.at[i,'M']-staircase_admin):
            df.at[i,'AU'] = 1
        else: 
            df.at[i,'AU'] = 0 
        df['AV'] = (df['AU'].cumsum() >= 1).astype(int)
    #Affordability constraint staircasing and adjusted 
        if ((df.at[i, 'M'] + min((LTV / (1 - LTV)) * df.at[i, 'M'], df.at[i, 'I'] * loan_ratio)) / df.at[i, 'F']) >= minimum_initial_share:
            df.at[i, 'AW'] = 1
        else:
            df.at[i, 'AW'] = 0
        df['AX'] = (df['AW'].cumsum() >= 1).astype(int)

    #AC1 McCabe
        if pd.isna(df.at[i, 'D']):
            df.at[i, 'N3'] = None
        else:
            df.at[i, 'N3'] = 1 - (0.9 * df.at[i, 'I'] - loan_repayment - service_charge * df.at[i, 'F']) / (df.at[i, 'F'] * initial_rent_percent * (1 + inflation) ** 5)
    #AC2 numerator
        if pd.isna(df.at[i, 'D']):
            df.at[i, 'N4'] = None
        else:
            df.at[i, 'N4'] = df.at[i, 'I'] - loan_repayment- service_charge * df.at[i, 'F'] - df.at[i, 'F'] * initial_rent_percent * (1 + inflation) ** 5
    #AC2 denominator
        if pd.isna(df.at[i, 'D']):
            df.at[i, 'N5'] = None
        else:
            df.at[i, 'N5'] = df.at[i, 'F'] * (
            (1 / 0.3) * LTV * mortgage_rate /
            (1 - (1 / (1 + mortgage_rate) ** max(retirement_age - df.at[i, 'D'], mortgage_term))) -
            initial_rent_percent * (1 + inflation) ** 5)
    
    #AC2 McCabe
        if pd.isna(df.at[i, 'D']):
            df.at[i, 'N6'] = None
        else:
            df.at[i, 'N6'] = df.at[i, 'N4'] / df.at[i, 'N5']
    #AC indicator
        if pd.isna(df.at[i, 'D']):
            df.at[i, 'N7'] = None
        else:
            df.at[i, 'N7'] = 1 if (df.at[i, 'N3'] < df.at[i, 'N6']) and (df.at[i, 'N6'] >= 0.25) else 0
    #AC adjusted
        df['cumulative_sum_n7'] = df['N7'].cumsum()

        # Set 'N8' to 1 if the cumulative sum is >= 1, otherwise set it to 0
        df['N8'] = df['cumulative_sum_n7'].apply(lambda x: 1 if x >= 1 else 0)

    #Home buying decision
        df.at[i, 'AY'] = df.at[i, 'AP']*df.at[i, 'AT']*df.at[i, 'AV']*df.at[i, 'AX']*df.at[i, 'N8']

    #Home buying decision
        df.at[i, 'AY'] = df.at[i, 'AP']*df.at[i, 'AT']*df.at[i, 'AV']*df.at[i, 'AX']
    #SO indicator 
        if df.at[0, 'AY'] > 0: 
            df.at[0, 'AZ'] = 1 
        else: 
            df.at[0, 'AZ'] = 0
        for i in range(1, len(df)):
            if df.at[i, 'AY'] > df.at[i-1, 'AY']: 
                df.at[i, 'AZ'] = 1 
            else: 
                df.at[i, 'AZ'] = 0
    #Home buying decision (non-reversible)
        df['BA'] = (df['AZ'].cumsum() >= 1).astype(int)
    #rent factor
        if df.at[0, 'AZ'] == 1 and df.at[0, 'BA'] == 1:
            df.at[0, 'BB'] = 1
        else:
            df.at[0, 'BB'] = 0  # This line seems redundant given your description; adjust as needed
        for i in range(1, len(df)):
            if df.at[i, 'AZ'] == 1 and df.at[i, 'BA'] == 1:
                df.at[i, 'BB'] = 1
            else:
                df.at[i, 'BB'] = df.at[i-1, 'BB'] * (1 + rent_appreciation)

        #Purchase price and adjusted 
    for i in range(len(df)):
        df.at[i, 'BC'] =  df.at[i, 'AZ']*df.at[i, 'F']
        df['BD'] = (df['BC'].cumsum()).astype(int)
        #Full rent 
        df.at[i, 'BE'] = df.at[i, 'BD'] * df.at[i, 'BB'] * initial_rent_percent
        #Home buying decision 
        df.at[i, 'BF'] = df.at[i, 'BA'] 

#############################################
    df.at[0, 'BG'] = df.at[0, 'M'] if df.at[0, 'AZ'] == 1 else df.at[0, 'BF'] * (df.at[0, 'I'] - df.at[0, 'N0'] - df.at[0, 'F'] * service_charge - staircase_admin - (0 * mortgage_rate))
    df.at[0, 'BJ'] = min([df.at[0, 'BF'] * loan_ratio * df.at[0, 'I'], (1 - 0) * df.at[0, 'F'] - df.at[0, 'BG']])
    df.at[0, 'BK'] = (LTV / (1 - LTV)) * (df.at[0, 'BG'] + 0 - 0)
    df.at[0, 'BL'] = min([df.at[0, 'BJ'], df.at[0, 'BK']])
    df.at[0, 'BH'] = 1 if df.at[0, 'BH'] == 1 else min((df.at[0, 'BG'] + df.at[0, 'BL']) / df.at[0, 'F'], 0.75 if df.at[0, 'BH'] == 0 else 1)
    df.at[0, 'BM'] = df.at[0, 'BL'] * df.at[0, 'BF'] if df.at[0, 'BH'] < 1 else min([df.at[0, 'BL'], df.at[0, 'F'] - df.at[0, 'BG']])


    for i in range(1, len(df)):
        if df.at[i, 'AZ'] == 1:
            df.at[i, 'BG'] = df.at[i, 'M']  
        else: 
            df.at[i, 'BG'] = df.at[i, 'BF'] * ((df.at[i, 'I'] - df.at[i, 'N0'] - df.at[i, 'F'] * service_charge - staircase_admin - df.at[i, 'BE']*(1 - df.at[i-1, 'BH']) - df.at[i-1, 'BM']* mortgage_rate))
        
        df.at[i, 'BJ'] = min([df.at[i, 'BF'] * loan_ratio * df.at[i, 'I'] - df.at[i-1, 'BM'], (1 - df.at[i-1, 'BH']) * df.at[i, 'F'] - df.at[i, 'BG']]) if (1 - df.at[i-1, 'BH']) > 0 else (df.at[i, 'BF'] * loan_ratio * df.at[i, 'I'] - df.at[i-1, 'BM'])
        
        df.at[i, 'BK'] = (LTV/(1-LTV))*(df.at[i,'BG']+ (df.at[i-1,'BH']*df.at[i,'F']) - df.at[i-1,'BM'])
        
        df.at[i, 'BL'] = df.at[i, 'BF']*(min(df.at[i, 'BJ'], df.at[i, 'BK']))
        
        df.at[i, 'BH'] = 1 if df.at[i-1, 'BH'] == 1 else (
            min(df.at[i-1, 'BH'] + (df.at[i, 'BG'] + df.at[i, 'BL']) / df.at[i, 'F'], 0.75)
            if df.at[i-1, 'BH'] == 0 else
            min(df.at[i-1, 'BH'] + (df.at[i, 'BG'] + df.at[i, 'BL']) / df.at[i, 'F'], 1)
        )        
        
        if df.at[i, 'BH'] < 1:
            df.at[i, 'BM'] = (df.at[i-1, 'BM'] + df.at[i, 'BL']*df.at[i, 'BF'])  
        elif df.at[i, 'BH'] == 1 and df.at[i-1, 'BH'] < 1:
            df.at[i, 'BM'] = df.at[i-1, 'BM'] + min(df.at[i, 'BL'], (df.at[i, 'F']-df.at[i, 'BG']))
        else: 
            df.at[i, 'BM'] = df.at[i-1, 'BM']


    for i in range(len(df)):
        if df.at[i, 'BH'] == 1:
            df.at[i, 'BI'] = 1 
        else:
            df.at[i, 'BI'] = 0
    
######################################
    if df.at[0, 'BI'] > 0:
        df.at[0, 'BN'] = 1
    else:
        df.at[0, 'BN'] = 0
    for i in range(1, len(df)):
        if df.at[i, 'BI'] > df.at[i-1, 'BI']:
            df.at[i, 'BN'] = 1
        else:
            df.at[i, 'BN'] = 0

    #Loan adjusted + STLT
    for i in range(len(df)):
        df.at[i, 'BO'] = (df.at[i, 'BM'] + df.at[i, 'P'])* df.at[i, 'BN']
        
        #Savings after full staircasing indicator
        df['BP'] = df['BN'].cumsum().shift(fill_value=0).astype(int)
        #Savings 
        df.at[i, 'BQ'] = df.at[i, 'BP']*(df.at[i, 'I']-df.at[i, 'N0'] - (service_charge*df.at[i, 'F']))
    df.at[0, 'BR'] = df.at[0, 'BO'] - df.at[0, 'BQ']
    for i in range(1, len(df)):
        df.at[i, 'BR'] = (df.at[i-1, 'BR']* (1 + mortgage_rate)) + df.at[i, 'BO'] - df.at[i, 'BQ']
    
    #mortgage loan indicator 
    for i in range(len(df)):
        df.at[i, 'BS']=  df.at[i, 'BN'] +  df.at[i, 'BP']
    #mortgage loan
        df.at[i, 'BT'] = (1 - df.at[i, 'BS']) * df.at[i, 'BM'] + (1 if df.at[i, 'BR'] > 0 else 0) * df.at[i, 'BR']
    #mortgage repayment
    df.at[0, 'BU'] = 0
     
    for i in range(1, len(df)):
        if df.at[i, 'BR'] <= 0 and df.at[i-1, 'BR'] > 0:
           df.at[i, 'BU'] = 1
        else: 
            df.at[i, 'BU'] = 0 

    #savings indicator
    for i in range(len(df)):
        df['BV'] = df['BU'].cumsum().shift(fill_value=0).astype(int)
    #first savings
        df.at[i, 'BW'] = -df.at[i, 'BU']*df.at[i, 'BR']*((1+savings_rate)/(1+mortgage_rate))
    #savings 
    df.at[0, 'BX'] = df.at[0, 'BU']*df.at[0, 'BW']+df.at[0, 'BV']*df.at[0, 'BQ']
    for i in range(1, len(df)):
        df.at[i, 'BX'] = (df.at[i-1, 'BX']*(1+savings_rate))+df.at[i, 'BU']*df.at[i, 'BW']+df.at[i, 'BV']*df.at[i, 'BQ']
    #Liquid wealth 
    for i in range(len(df)):
        df.at[i, 'BY'] = df.at[i, 'M']*(1-df.at[i, 'BF']) + df.at[i, 'BX']
    #Housing wealth 
        df.at[i, 'BZ'] = df.at[i, 'BH']*df.at[i, 'F'] - df.at[i, 'BT']

        df.at[i, 'CA'] = df.at[i, 'AI'] 
        df.at[i, 'CB'] = df.at[i, 'D']
        df.at[i, 'CC'] = df.at[i, 'BY']/df.at[i, 'CA'] 
        df.at[i, 'CD'] = df.at[i, 'BZ']/df.at[i, 'CA']


#########################
# Initialize all your output variables with defaults or None
    # Check and assign values only if the filtered DataFrames are not empty
    
    try:
        TO_age = int(df.loc[df[df['W'] == 1].index[0], 'D'])
    except (ValueError, IndexError) as e:
        TO_age = 0 

    try: 
        TO_time = int(df.loc[df[df['W'] == 1].index[0], 'E'])
    except (ValueError, IndexError) as e:
        TO_time = 0

    try: 
        TO_finish = int(df.loc[df[df['AD'] == 1].index[0], 'D'])
    except (ValueError, IndexError) as e:       
        TO_finish =0 
      
    try:
        TO_liquid = int(df.loc[df['D'] == retirement_age, 'AK'].iloc[0])
    except (ValueError, IndexError) as e:
        TO_liquid = 0 

    try:
        TO_housing = int(df.loc[df['D'] == retirement_age, 'AL'].iloc[0])
    except (ValueError, IndexError) as e:
        TO_housing = 0 

##################
    try:
        TO_deposit = int((df.loc[df['X'] != 0, 'F'].iloc[0]) * 0.05)
    except (ValueError, IndexError) as e:
        TO_deposit = 0 
    try:
        TO_mortgage = int(df.loc[df['X'] != 0, 'X'].iloc[0] * (mortgage_rate / 12) / (1 - (1 + (mortgage_rate / 12)) ** (-12 * mortgage_term)))
    except (ValueError, IndexError) as e:
        TO_mortgage = 0

    #print(TO_housing)
    #print(TO_mortgage)

##################
    try:
        SO_start_age = int(df.loc[df[df['AZ'] == 1].index[0], 'D'])
    except (ValueError, IndexError) as e:
        SO_start_age = 0 

    try:
        SO_time = int(df.loc[df[df['AZ'] == 1].index[0], 'E'])
    except (ValueError, IndexError) as e:
        SO_time = 0 

    try:
        SO_staircase_finish = int(df.loc[df[df['BN'] == 1].index[0], 'D'])
    except (ValueError, IndexError) as e:
        SO_staircase_finish = 0

    try:
        SO_mortgage_finish = int(df.loc[df[df['BU'] == 1].index[0], 'D'])
    except (ValueError, IndexError) as e:
        SO_mortgage_finish = 0 

    try:
        SO_liquid = int(df.loc[df['D'] == retirement_age, 'CC'].iloc[0])
    except (ValueError, IndexError) as e:
        SO_liquid = 0      

    higher_income_postcodes = [
        "City of London", "London", "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley", "Camden", "Croydon", 
        "Ealing", "Enfield", "Greenwich", "Hackney", "Hammersmith and Fulham", "Haringey", "Harrow", "Havering", 
        "Hillingdon", "Hounslow", "Islington", "Kensington and Chelsea", "Kingston upon Thames", "Lambeth", "Lewisham", 
        "Merton", "Newham", "Redbridge", "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets", "Waltham Forest", 
        "Wandsworth", "Westminster"
    ]

    # Modify the try block
    try:
        if (postcode in higher_income_postcodes and income >= 90000) or (postcode not in higher_income_postcodes and income >= 80000):
            SO_housing = int(1)
        else:
            SO_housing = int(df.loc[df['D'] == retirement_age, 'CD'].iloc[0])
    except (ValueError, IndexError) as e:
        SO_housing = 0

    try:
        SO_mortgage = int((((0.25 * df.loc[df['AO'] != 0, 'F'].iloc[0]) - (0.0125 * df.loc[df['AO'] != 0, 'F'].iloc[0] ))*
                          ((mortgage_rate/12) / (1 - (1 + (mortgage_rate/12))**(-12*mortgage_term)))) 
                            + (0.75 * 0.0275 * df.loc[df['AO'] != 0, 'F'].iloc[0]/12) + (service_charge * df.loc[df['AO'] != 0, 'F'].iloc[0]/12))
    except (ValueError, IndexError) as e:
        SO_mortgage = 0      
        
    print(SO_mortgage)

    try:
        SO_deposit = int((df.loc[df['AO'] != 0, 'F'].iloc[0]) * 0.05 * 0.25)
    except (ValueError, IndexError) as e:
        SO_deposit = 0 

    gross = int(gross)
    try:
        SO_share = float(df.loc[df['BH']  != 0, 'BH'].iloc[0])*100
    except (ValueError, IndexError) as e:
        SO_share = 0 

    SO_liquid = round(SO_liquid / 1000) * 1000
    TO_liquid = round(TO_liquid / 1000) * 1000
    TO_housing = round(TO_housing / 1000) * 1000
    SO_housing = round(SO_housing / 1000) * 1000
    
    print(SO_share)

    age_ranges = ["20", "30", "40", "50", "60", "67"]
    age_ranges_dict = {
        "20": 20,
        "30": 30,
        "40": 40,
        "50": 50,
        "60": 60,
        "67": 67
    }

    # Initialize dictionaries to store the values at the last age of each range
    net_wealth_cd_values = {key: 0 for key in age_ranges}
    net_wealth_ak_values = {key: 0 for key in age_ranges}
    net_wealth_cc_values = {key: 0 for key in age_ranges}
    net_wealth_al_values = {key: 0 for key in age_ranges}
    net_wealth_bt_values = {key: 0 for key in age_ranges}
    net_wealth_aa_values = {key: 0 for key in age_ranges}

    # Iterate over the DataFrame and update the values when the age matches the end of the range
    for i in range(len(df)):
        age_value = df.at[i, 'D']
        for age_range_key, last_age in age_ranges_dict.items():
            if age_value == last_age:
                net_wealth_cd_values[age_range_key] = float(df.at[i, 'CD'])
                net_wealth_ak_values[age_range_key] = float(df.at[i, 'AK'])
                net_wealth_cc_values[age_range_key] = float(df.at[i, 'CC'])
                net_wealth_al_values[age_range_key] = float(df.at[i, 'AL'])
                net_wealth_bt_values[age_range_key] = float(df.at[i, 'BT'])
                net_wealth_aa_values[age_range_key] = float(df.at[i, 'AA'])
                break

    # Convert the net wealth values dictionaries to lists (optional)
    net_wealth_cd_list = [net_wealth_cd_values[age_range] for age_range in age_ranges]
    net_wealth_ak_list = [net_wealth_ak_values[age_range] for age_range in age_ranges]
    net_wealth_cc_list = [net_wealth_cc_values[age_range] for age_range in age_ranges]
    net_wealth_al_list = [net_wealth_al_values[age_range] for age_range in age_ranges]
    net_wealth_bt_list = [net_wealth_bt_values[age_range] for age_range in age_ranges]
    net_wealth_aa_list = [net_wealth_aa_values[age_range] for age_range in age_ranges]
    
    print(age_ranges)
    print(net_wealth_cd_list)
    print(net_wealth_ak_list)
    print(net_wealth_cc_list)
    print(net_wealth_al_list)
    print(net_wealth_bt_list)
    print(net_wealth_aa_list)
    
    age_ranges = json.dumps(age_ranges)
    net_wealth_cd_list = json.dumps(net_wealth_cd_list)
    net_wealth_ak_list = json.dumps(net_wealth_ak_list)
    net_wealth_cc_list = json.dumps(net_wealth_cc_list)
    net_wealth_al_list = json.dumps(net_wealth_al_list)
    net_wealth_bt_list = json.dumps(net_wealth_bt_list)
    net_wealth_aa_list = json.dumps(net_wealth_aa_list)

    def find_max_index(df):
        cumulative_sum = 0
        max_index = 0

        for i in range(len(df)):
            if float(df.at[i, 'BH']) >= 1:
                max_index = i + 1
                break

        return max_index

    max_index = find_max_index(df)
    age_stairgraph = df['D'].iloc[:max_index].tolist()
    share_stairgraph = df['BH'].iloc[:max_index].tolist()
    print(share_stairgraph)

    # Convert to JSON-exportable formats (floats for BH values)
    age_stairgraph = json.dumps(age_stairgraph)
    share_stairgraph = json.dumps([float(BH) for BH in share_stairgraph])

    #Graphs 
    age_at_time_data = df['D'].to_json(orient='records')
    staircasing_data = df['BH'].to_json(orient='records')
    mortgage_data = df['BT'].to_json(orient='records')
    mortgage_data2 = df['AA'].to_json(orient='records')
    TO_wealth_data = df['AK'].to_json(orient='records')
    SO_wealth_data = df['CC'].to_json(orient='records')
    TO_house_data = df['AL'].to_json(orient='records')
    SO_house_data = df['CD'].to_json(orient='records')

    results = {
        "TO_age": TO_age,
        "TO_time": TO_time,
        "TO_finish": TO_finish,
        "TO_liquid": TO_liquid,
        "TO_housing": TO_housing, 
        "TO_deposit": TO_deposit,
        "TO_mortgage": TO_mortgage,

        "SO_start_age": SO_start_age, 
        "SO_time": SO_time,
        "SO_staircase_finish": SO_staircase_finish,
        "SO_mortgage_finish": SO_mortgage_finish,
        "SO_liquid": SO_liquid,
        "SO_housing": SO_housing,
        "SO_deposit": SO_deposit,
        "SO_mortgage": SO_mortgage,
        "SO_share": SO_share,

        "age_at_time_data": age_at_time_data,
        "staircasing_data": staircasing_data,
        "mortgage_data": mortgage_data,
        "mortgage_data2": mortgage_data2,
        "TO_wealth_data": TO_wealth_data, 
        "SO_wealth_data": SO_wealth_data,
        "TO_house_data": TO_house_data,
        "SO_house_data": SO_house_data,
        "house_price": house_price,
        "income": gross,
        "full_data": df.to_dict(orient="records"),

        "age_ranges": age_ranges,
        "net_wealth_cd_by_age_range": net_wealth_cd_list,
        "net_wealth_ak_by_age_range": net_wealth_ak_list,
        "net_wealth_cc_by_age_range": net_wealth_cc_list,
        "net_wealth_al_by_age_range": net_wealth_al_list,
        "net_wealth_bt_by_age_range": net_wealth_bt_list,
        "net_wealth_aa_by_age_range": net_wealth_aa_list,
    
        "age_stairgraph": age_stairgraph,
        "share_stairgraph": share_stairgraph,
    }

    return results