import os
import sys
import traceback
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sqlite3
import json
import csv
import io
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Import betamodel and emailmodel
import betamodel
from emailmodel import save_email

# Initialize Flask
app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

# Function to create the initial database schema
import sqlite3

# Function to create the database and ensure schema is correct
def create_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Drop the existing table if it exists (optional)
    c.execute('DROP TABLE IF EXISTS user_data')
    
    # Create the user_data table with the correct schema, including local_authority
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            session_id TEXT,
            local_authority TEXT,
            property_type TEXT,
            bedrooms TEXT,
            occupation TEXT,
            house_price REAL,
            is_first_time_buyer INTEGER,
            income REAL,
            month_spending REAL,
            head_of_household_age INTEGER,
            savings REAL,
            current_rent REAL,
            loan_repayment REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create the emails table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            email TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Call the function to create the database
create_db()


@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"msg": "Hello, world!"})

@app.route('/export-data')
def export_data():
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_data")
        data = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Session ID', 'Local Authority', 'Property Type', 'Bedrooms', 'Occupation', 'House Price', 
                         'Is First Time Buyer', 'Income', 'Month Spending', 'Age', 'Savings', 
                         'Current Rent', 'Loan Repayment', 'Timestamp'])

        for row in data:
            writer.writerow(row)

        output.seek(0)
        conn.close()

        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=user_data.csv"})
    except Exception as e:
        return str(e), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        session_id = data.get('sessionId')

        # Save input data to the database
        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO user_data (session_id, local_authority, property_type, bedrooms, occupation, house_price, is_first_time_buyer, income, month_spending, head_of_household_age, savings, current_rent, loan_repayment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (session_id, data['postcode'], data['propertyType'], data['bedrooms'], data['occupation'], data['housePrice'], data['isFirstTimeBuyer'], data['income'], data['monthspending'], data['headOfHouseholdAge'], data['savings'], data['currentRent'], data['loan_repayment']))
            conn.commit()

        # Get prediction results
        results = betamodel.get_house_price_data(
            data['postcode'],
            data['propertyType'],
            data['bedrooms'],
            data['occupation'],
            data['housePrice'],
            data['isFirstTimeBuyer'],
            data['income'],
            data['monthspending'],
            data['headOfHouseholdAge'],
            data['savings'],
            data['currentRent'],
            data['loan_repayment']
        )
        print("Prediction results:", results)

        # Create email content with both result and input data
        email_content = create_email_content(results, data)

        # You can add code here to send the email using the email_content
        
        return jsonify(results)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/submit-email', methods=['POST'])
def submit_email():
    try:
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({'error': 'No email provided'}), 400
        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO emails (email) VALUES (?)", (email,))
            conn.commit()
        return jsonify({'message': 'Email saved successfully'})
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/submit-contact-form', methods=['POST'])
def submit_contact_form():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        # You can further process the contact form data here
        return jsonify({'message': 'Contact form submitted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        sender_email = os.getenv('SMTP_EMAIL')  
        receiver_email = "s.milcheva@ucl.ac.uk"
        password = os.getenv('SMTP_PASSWORD')

        message = MIMEMultipart("alternative")
        message["Subject"] = "New Contact Form Submission"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = f"""\ 
        Hi,
        You have received a new submission from your contact form.
        Name: {data['name']}
        Email: {data['email']}
        Message: {data['message']}
        """
        part = MIMEText(text, "plain")
        message.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-emails', methods=['GET'])
def get_emails():
    try:
        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("SELECT email FROM emails")
            emails = c.fetchall()
        return jsonify({'emails': [email[0] for email in emails]})
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def create_email_content(result, inputs):
    # Safely retrieve values from the result using .get() to avoid errors
    to_deposit = result.get('TO_deposit', 0)
    so_deposit = result.get('SO_deposit', 0)

    # Affordability messages
    to_affordability = "You cannot afford full ownership with the current inputs." if to_deposit == 0 else "You can afford full ownership."
    so_affordability = "You cannot afford shared ownership with the current inputs." if so_deposit == 0 else "You can afford shared ownership."

    # Input data string with comma-separated values, formatted for readability
    input_data = f"""
        Postcode: {inputs.get('postcode', 'N/A')},
        Property Type: {inputs.get('propertyType', 'N/A')},
        Bedrooms: {inputs.get('bedrooms', 'N/A')},
        Occupation: {inputs.get('occupation', 'N/A')},
        House Price: £{int(inputs.get('housePrice', 0)):,},
        First Time Buyer: {'Yes' if inputs.get('isFirstTimeBuyer', False) else 'No'},
        Income: £{int(inputs.get('income', 0)):,},
        Monthly Spending: £{int(inputs.get('monthspending', 0)):,},
        Age: {inputs.get('headOfHouseholdAge', 'N/A')},
        Savings: £{int(inputs.get('savings', 0)):,},
        Current Rent: £{int(inputs.get('currentRent', 0)):,},
        Loan Repayment: £{int(inputs.get('loan_repayment', 0)):,}
    """

    # HTML email content with both inputs and result data
    html_content = f"""
    <html>
    <body>
        <h1>Your Results</h1>
        <p><strong>Input Data:</strong></p>
        <p>{input_data}</p>

        <div>
            <h2>Full Ownership</h2>
            <p>{to_affordability}</p>
            {f'''
            <p>Minimum Deposit: £{int(to_deposit):,}</p>
            <p>Monthly costs: £{int(result.get('TO_mortgage', 0)):,}</p>
            <p>Lifetime wealth: £{int(result.get('TO_housing', 0)):,} in housing wealth, £{int(result.get('TO_liquid', 0)):,} in savings</p>
            ''' if to_deposit > 0 else ''}
        </div>

        <div>
            <h2>Shared Ownership</h2>
            <p>{so_affordability}</p>
            {f'''
            <p>Share Percentage: {result.get('SO_share', 'N/A')}%</p>
            <p>Staircase Finish: £{int(result.get('SO_staircase_finish', 0)):,}</p>
            <p>Minimum Deposit: £{int(so_deposit):,}</p>
            <p>Monthly costs: £{int(result.get('SO_mortgage', 0)):,}</p>
            <p>Lifetime wealth: £{int(result.get('SO_housing', 0)):,} in housing wealth, £{int(result.get('SO_liquid', 0)):,} in savings</p>
            ''' if so_deposit > 0 else ''}
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/submit-results-email', methods=['POST'])
def submit_results_email():
    try:
        data = request.json
        email = data.get('email')
        result = data.get('result')
        inputs = data.get('inputs')  # Assuming the inputs are passed in the request body as 'inputs'

        sender_email = os.getenv('SMTP_EMAIL')
        receiver_email = email
        password = os.getenv('SMTP_PASSWORD')

        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Calculated Results"
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create the email content with both inputs and result
        html_content = create_email_content(result, inputs)
        part = MIMEText(html_content, "html")
        message.attach(part)

        # Send the email via SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Run the app on the specified port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)