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
    c.execute('''CREATE TABLE IF NOT EXISTS user_data
                 (session_id TEXT, house_price REAL, is_first_time_buyer INTEGER, 
                 income REAL, month_spending REAL, head_of_household_age INTEGER, 
                 savings REAL, current_rent REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (email TEXT)''')
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
        writer.writerow(['Session ID', 'House Price', 'Is First Time Buyer', 'Income', 'Month Spending', 'Age', 'Savings', 'Current Rent', 'Timestamp'])
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
            c.execute("INSERT INTO user_data (session_id, house_price, is_first_time_buyer, income, month_spending, head_of_household_age, savings, current_rent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (session_id, data['housePrice'], data['isFirstTimeBuyer'], data['income'], data['monthspending'], data['headOfHouseholdAge'], data['savings'], data['currentRent']))
            conn.commit()

        results = betamodel.get_house_price_data(
            data['housePrice'],
            data['isFirstTimeBuyer'],
            data['income'],
            data['monthspending'],
            data['headOfHouseholdAge'],
            data['savings'],
            data['currentRent']
        )
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

def generate_chart_image(chart_data, title, x_label, y_label):
    plt.figure()
    plt.plot(chart_data)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img_base64

@app.route('/submit-contact-form', methods=['POST'])
def submit_contact_form():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        # Logic to handle the data goes here
        # For example, saving to a database or sending an email

        return jsonify({'message': 'Contact form submitted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        sender_email = os.getenv('SMTP_EMAIL')  # Get environment variable
        receiver_email = "s.milcheva@ucl.ac.uk"
        password = os.getenv('SMTP_PASSWORD')  # Get environment variable

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
    # Generate chart images
    staircasing_data = result['staircasing_data']
    mortgage_data = result['mortgage_data']
    mortgage_data2 = result['mortgage_data2']
    TO_wealth_data = result['TO_wealth_data']
    SO_wealth_data = result['SO_wealth_data']

    staircasing_img = generate_chart_image(staircasing_data, 'Staircasing', 'Age', 'Share (%)')
    loan_img = generate_chart_image(mortgage_data, 'Outstanding Loan Balance', 'Age', 'Mortgage Debt (£)')
    wealth_img = generate_chart_image(TO_wealth_data, 'Wealth Comparison', 'Age', 'Wealth (£)')

    # Create HTML content
    html_content = f"""
    <html>
    <body>
        <h1>Your Results</h1>
        <p>Value of home: £{result['house_price']}</p>
        <div>
            <h2>Full Ownership</h2>
            <p>Minimum Deposit: £{result['TO_deposit']}</p>
            <p>Monthly costs: £{result['TO_mortgage']}</p>
            <p>Lifetime wealth: £{result['TO_housing']} in housing wealth, £{result['TO_liquid']} in savings</p>
            <img src="data:image/png;base64,{loan_img}" alt="Loan Chart">
            <img src="data:image/png;base64,{wealth_img}" alt="Wealth Chart">
        </div>
        <div>
            <h2>Shared Ownership</h2>
            <p>Minimum Deposit: £{result['SO_deposit']}</p>
            <p>Monthly costs: £{result['SO_mortgage']}</p>
            <p>Lifetime wealth: £{result['SO_housing']} in housing wealth, £{result['SO_liquid']} in savings</p>
            <img src="data:image/png;base64,{staircasing_img}" alt="Staircasing Chart">
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)

    
