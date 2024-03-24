import os
import sys
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import betamodel

from emailmodel import save_email

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"msg": "POg"})

@app.route('/predict', methods=['POST'])
def predict():
    print(json.dumps({"house_price": data['housePrice'], "FTB": data['isFirstTimeBuyer'], "gross": data['income'], "consumption": data['monthspending'], "age":data['headOfHouseholdAge'], "savings":data['savings'], "rent":data['currentRent']}, indent=4))      
    try:
        data = request.json
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
        return jsonify({'error': str(e)})

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
