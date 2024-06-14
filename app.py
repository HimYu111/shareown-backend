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
from email.mime.image import MIMEImage
import smtplib
import matplotlib.pyplot as plt
from io import BytesIO
import base64


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import betamodel

from emailmodel import save_email

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})


def create_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS user_data')
    c.execute('DROP TABLE IF EXISTS emails')
    
    c.execute('''
        CREATE TABLE user_data (
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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE emails (
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_db() 

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"msg": "POg"})

@app.route('/export-data')
def export_data():
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_data")
        data = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Session ID', 'Local Authority', 'Property Type', 'Bedrooms', 'Occupation', 'House Price', 'Is First Time Buyer', 'Income', 'Month Spending', 'Age', 'Savings', 'Current Rent', 'Timestamp'])
        for row in data:
            writer.writerow(row)

        output.seek(0)
        conn.close()

        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=user_data.csv"})
    except Exception as e:
        return str(e), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        session_id = data.get('sessionId')

        with sqlite3.connect('data.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO user_data (session_id, local_authority, property_type, bedrooms, occupation, house_price, is_first_time_buyer, income, month_spending, head_of_household_age, savings, current_rent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (session_id, data['local_authority'], data['propertyType'], data['bedrooms'], data['occupation'], data['housePrice'], data['isFirstTimeBuyer'], data['income'], data['monthspending'], data['headOfHouseholdAge'], data['savings'], data['currentRent']))
            conn.commit()

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
        )
        print("Prediction results:", results)
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


def create_email_content(result):
    to_affordability = "You cannot afford full ownership with the current inputs." if result['TO_deposit'] == 0 else "You can afford full ownership."
    so_affordability = "You cannot afford shared ownership with the current inputs." if result['SO_deposit'] == 0 else "You can afford shared ownership."

    html_content = f"""
    <html>
    <body>
        <h1>Your Results</h1>
        <p>Value of home: £{result['house_price']}</p>
        <div>
            <h2>Full Ownership</h2>
            <p>{to_affordability}</p>
            <p>Minimum Deposit: £{result['TO_deposit']}</p>
            <p>Monthly costs: £{result['TO_mortgage']}</p>
            <p>Lifetime wealth: £{result['TO_housing']} in housing wealth, £{result['TO_liquid']} in savings</p>
        </div>
        <div>
            <h2>Shared Ownership</h2>
            <p>{so_affordability}</p>
            <p>Minimum Deposit: £{result['SO_deposit']}</p>
            <p>Monthly costs: £{result['SO_mortgage']}</p>
            <p>Lifetime wealth: £{result['SO_housing']} in housing wealth, £{result['SO_liquid']} in savings</p>
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

        sender_email = os.getenv('SMTP_EMAIL')
        receiver_email = email
        password = os.getenv('SMTP_PASSWORD')

        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Calculated Results"
        message["From"] = sender_email
        message["To"] = receiver_email

        html_content = create_email_content(result)
        part = MIMEText(html_content, "html")
        message.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def download_data():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data")
    data = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Session ID', 'House Price', 'Is First Time Buyer', 'Income', 'Month Spending', 'Age', 'Savings', 'Current Rent', 'Timestamp'])
    writer.writerows(data)

    output.seek(0)
    conn.close()

    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=user_data.csv"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    