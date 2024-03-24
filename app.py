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
    data = request.json
    return jsonify({'TO_age': 39, 'TO_time': 14, 'TO_finish': 57, 'TO_liquid': 80315, 'TO_housing': 493412, 'SO_start_age': 25, 'SO_time': 0, 'SO_staircase_finish': 29, 'SO_mortgage_finish': 42, 'SO_liquid': 252525, 'SO_housing': 493412, 'Mortgage_size': 190874, 'age_at_time_data': '[25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67]', 'staircasing_data': '[0.8036418636,0.8572223682,0.9125864651,0.9697293899,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]', 'mortgage_data': '[162000.99,170263.04049,178946.45555499,188072.7247882945,190874.8429292493,183009.3691520661,174200.7193445328,164385.8901958813,153498.3528159803,141467.8722912091,128220.3185072769,113677.4678330444,97756.7952411354,80371.2564220684,61429.0594287377,41390.1961994634,20209.9975211298,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]', 'TO_wealth_data': '[14800.22,19800.8328349515,25006.9195652936,30423.6745097978,36056.4076485421,41774.1401638798,47578.0504495303,53469.3324543801,59449.1958814384,65518.8663892847,71679.5857960349,77932.6122858611,84279.220618094,90720.7023389397,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,6110.649711257,14830.7812940474,23157.951424466,31220.096732828,39018.2854378208,46553.5160002657,53826.7170865566,60838.7475121959,67590.3961653198,74082.3819100993,80315.3534698996]', 'SO_wealth_data': '[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1292.8878298707,15106.3873111249,28711.6232792059,42108.7152593304,55297.7487176976,68278.7747180316,81051.8095686772,93616.8344600898,105724.3907754267,117382.6211064615,128599.412913819,139382.4036030627,149738.9854558988,159676.310419591,169201.2947576001,178320.623564378,187040.7551471685,195367.9252775871,203430.070585949,211228.2592909418,218763.4898533868,226036.6909396776,233048.721365317,239800.3700184409,246292.3557632205,252525.3273230208]', "msg": json.dumps({"house_price": data['housePrice'], "FTB": data['isFirstTimeBuyer'], "gross": data['income'], "consumption": data['monthspending'], "age":data['headOfHouseholdAge'], "savings":data['savings'], "rent":data['currentRent']}, indent=4)})    
    # try:
    #     results = betamodel.get_house_price_data(
    #         data['housePrice'],
    #         data['isFirstTimeBuyer'],
    #         data['income'],
    #         data['monthspending'],
    #         data['headOfHouseholdAge'],
    #         data['savings'],
    #         data['currentRent']
    #     )
    #     return jsonify(results)
    # except Exception as e:
    #     print(e)
    #     traceback.print_exc()
    #     return jsonify({'error': str(e)})

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
