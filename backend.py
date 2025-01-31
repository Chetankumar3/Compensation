from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os
import logging
import urllib.parse

# Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG to capture debug messages
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

# Enable Flask's own debugging logs
app.logger.setLevel(logging.DEBUG)

'''
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': 3306
}
'''
# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Luckyomer10@',
    'database': 'compensationapp'
}

def create_connection():
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        if connection.is_connected():
            print("Connected to the database")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Routes
@app.route('/')
def home():
    return "Welcome to the Compensation App!"

@app.route('/guards', methods=['GET'])
def get_guards():
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM guards")
        result = cursor.fetchall()
        return jsonify(result)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
@app.route('/aguards', methods=['POST'])
def add_guard():
    data = request.json
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO guards (emp_id, name, mobile_number, division, range_, beat) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
        cursor.execute(query, (
            data['emp_id'], 
            data['name'], 
            data['mobile_number'], 
            data['division'], 
            data['range_'], 
            data['beat']
        ))
        connection.commit()
        return jsonify({"message": "Guard added successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
@app.route('/verify_guard', methods=['POST'])
def verify_guard():
    data = request.json
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM guards WHERE emp_id = %s AND mobile_number = %s"
        cursor.execute(query, (data['emp_id'], data['mobile_number']))
        result = cursor.fetchone()
        if result:
            return jsonify({"message": "Verified", "employee": result}), 200
        else:
            return jsonify({"message": "Employee not found"}), 404
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



@app.route('/compensationform', methods=['POST'])
def insert_compensation_form():
    data = request.json
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        document_url = data.get('documentURL')
        logging.debug(f"Document URL: {document_url}")
        
        if not document_url:
            return jsonify({"error": "Document URL is missing"}), 400

        # Ensure the document URL is encoded before storing in MySQL
        encoded_url = urllib.parse.quote(document_url, safe=':/?=&')

        cursor = connection.cursor()
        query = """
        INSERT INTO compensationform (
            ForestGuardID, ApplicantName, Age, FatherSpouseName, Mobile, AnimalName, IncidentDate, 
            AdditionalDetails, Address, CropType, CerealCrop, CropDamageArea, FullHouseDamage, 
            PartialHouseDamage, NumberOfCattlesDied, EstimatedCattleAge, HumanDeathVictimName, 
            NumberOfDeaths, TemporaryInjuryDetails, PermanentInjuryDetails, BankName, IFSCCode, 
            BranchName, AccountHolderName, AccountNumber, PANNumber, AadhaarNumber, Status, 
            documentURL, VerifiedBy, PaymentProcessedBy
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['forestGuardID'], data['applicantName'], data['age'], data['fatherSpouseName'],
            data['mobile'], data['animalName'], data['incidentDate'], data['additionalDetails'],
            data['address'], data['cropType'], data['cerealCrop'], data['cropDamageArea'],
            data['fullHouseDamage'], data['partialHouseDamage'], data['numberOfCattlesDied'],
            data['estimatedCattleAge'], data['humanDeathVictimName'], data['numberOfDeaths'],
            data['temporaryInjuryDetails'], data['permanentInjuryDetails'], data['bankName'],
            data['ifscCode'], data['branchName'], data['accountHolderName'], data['accountNumber'],
            data['panNumber'], data['aadhaarNumber'], data['status'], encoded_url,
            data['verifiedBy'], data['paymentProcessedBy']
        ))

        connection.commit()
        return jsonify({"message": f"Compensation form submitted successfully {encoded_url}"}), 201
    except Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/guards/<mobile_number>', methods=['GET'])
def get_guard_by_mobile_number(mobile_number):
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM guards WHERE mobile_number = %s"
        cursor.execute(query, (mobile_number,))
        result = cursor.fetchone()
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "Guard not found"}), 404
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/compensationform/<string:forest_guard_id>', methods=['GET'])
def get_compensation_forms(forest_guard_id):
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT * FROM compensationform
        WHERE ForestGuardID = %s
        """
        cursor.execute(query, (forest_guard_id,))
        compensation_forms = cursor.fetchall()

        if not compensation_forms:
            return jsonify({"message": "No compensation forms found for this ForestGuardID"}), 404

        # Convert each form into a dictionary and decode the documentURL
        result = []
        for form in compensation_forms:
            form_data = {
                "formID": form["FormID"],
                "submissionDateTime": form["SubmissionDateTime"],
                "forestGuardID": form["ForestGuardID"],
                "applicantName": form["ApplicantName"],
                "age": form["Age"],
                "fatherSpouseName": form["FatherSpouseName"],
                "mobile": form["Mobile"],
                "animalName": form["AnimalName"],
                "incidentDate": form["IncidentDate"],
                "additionalDetails": form["AdditionalDetails"],
                "address": form["Address"],
                "cropType": form["CropType"],
                "cerealCrop": form["CerealCrop"],
                "cropDamageArea": form["CropDamageArea"],
                "fullHouseDamage": form["FullHouseDamage"],
                "partialHouseDamage": form["PartialHouseDamage"],
                "numberOfCattlesDied": form["NumberOfCattlesDied"],
                "estimatedCattleAge": form["EstimatedCattleAge"],
                "humanDeathVictimName": form["HumanDeathVictimName"],
                "numberOfDeaths": form["NumberOfDeaths"],
                "temporaryInjuryDetails": form["TemporaryInjuryDetails"],
                "permanentInjuryDetails": form["PermanentInjuryDetails"],
                "bankName": form["BankName"],
                "ifscCode": form["IFSCCode"],
                "branchName": form["BranchName"],
                "accountHolderName": form["AccountHolderName"],
                "accountNumber": form["AccountNumber"],
                "panNumber": form["PANNumber"],
                "aadhaarNumber": form["AadhaarNumber"],
                "status": form["Status"],
                # Decode the document URL
                "documentURL": urllib.parse.unquote(form["documentURL"]),
                "verifiedBy": form["VerifiedBy"],
                "paymentProcessedBy": form["PaymentProcessedBy"]
            }
            result.append(form_data)

        return jsonify(result), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
