import os
import sys
import traceback
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import betamodel
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({
        "msg": "POg"
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # Extract parameters from the request data
        consumption_percentage = data['expensePercentage']
        savings = data['savings']
        age = data['headOfHouseholdAge']
        income = data['monthlyIncome']
        results = betamodel.get_house_price_data(consumption_percentage, savings, age, income)
        return jsonify(results)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="10000", debug=True)
