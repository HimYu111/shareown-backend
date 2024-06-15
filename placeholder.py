import os
import pandas as pd

def get_house_data(postcode, propertyType, sheet_name='Appreciation Rate'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(script_dir, 'Appreciation Rates 1996 to 2023.xlsx')

    if not os.path.exists(excel_path):
        print("Excel file does not exist.")
        return "Excel file does not exist."

    try:
        # Load the Excel file from a specific sheet
        df = pd.read_excel(excel_path, engine='openpyxl', header=6, sheet_name=sheet_name)
        print(df.columns)  # Debug: Print the DataFrame columns after load
    except Exception as e:
        return f"Failed to load Excel file: {e}"

    propertyType = propertyType.lower()
    propertyType_to_column = {
        'detached': 'Detached',
        'semi-detached': 'Semi-Detached',
        'terraced': 'Terraced',
        'flat': 'Flats',
        'undecided': 'Undecided'
    }

    if propertyType not in propertyType_to_column:
        return "Invalid house type specified"
    column_name = propertyType_to_column[propertyType]

    try:
        df['Local authority name'] = df['Local authority name'].astype(str).str.lower()
        #print("Data in 'Local authority name':", df['Local authority name'])  # Debug: Print values
        house_price_appreciation = df[df['Local authority name'] == postcode.lower()][column_name].values[0]
        return house_price_appreciation
    except IndexError:
        print("Local authority name not found or no data in the specified column")
        return "Local authority name not found"

# Example usage
postcode = 'Sunderland'
propertyType = 'Detached'
house_price_appreciation = get_house_data(postcode, propertyType, sheet_name='Appreciation Rate')
print("Result:", house_price_appreciation)