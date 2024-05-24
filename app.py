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
        receiver_email = 'zcechsy@ucl.ac.uk' #"s.milcheva@ucl.ac.uk"
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

@app.route('/submit-results-email', methods=['POST'])
def submit_results_email():
    try:
        data = request.json
        email = data.get('email')
        results = data.get('result')
        
        # sender_email = 'shareown8@gmail.com'  # Use your configured sender email
        sender_email = os.getenv('SMTP_EMAIL')
        receiver_email = email  # The user's email address
        # password = 'paperbutterfly1'  # Your email password
        password = os.getenv('SMTP_PASSWORD')

        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Calculated Results"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = f"Here are your results:\n{results}"
        part = MIMEText(text, "plain")
        message.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)

    
