import os
import sys
import traceback
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sqlite3
import json
import csv
import io

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
        email = data['email']
        # Call save_email and check if the email was saved successfully
        if save_email(email):
            return jsonify({'message': 'Email saved successfully'})
        else:
            return jsonify({'error': 'Failed to save email'}), 500
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
