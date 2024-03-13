# Define tax rates and thresholds
basic_rate = 0.20
higher_rate = 0.40
additional_rate = 0.45
basic_threshold = 37700
higher_threshold = 125140

# Example gross income
gross_income = 42000  # Change this to the gross income you want to calculate net for

# Calculate tax
if gross_income <= basic_threshold:
    # All income taxed at basic rate
    tax = gross_income * basic_rate
elif gross_income <= higher_threshold:
    # Part of the income is taxed at the basic rate, and the rest at the higher rate
    tax = basic_threshold * basic_rate + (gross_income - basic_threshold) * higher_rate
else:
    # Income is taxed at basic, higher, and additional rates
    tax = basic_threshold * basic_rate + (higher_threshold - basic_threshold) * higher_rate + (gross_income - higher_threshold) * additional_rate

# Calculate net income
net_income = gross_income - tax

print(f"Gross income: £{gross_income}")
print(f"Tax paid: £{tax:.2f}")
print(f"Net income: £{net_income:.2f}")
