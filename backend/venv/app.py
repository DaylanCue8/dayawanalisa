from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # This allows your Flutter app to access the API without security blocks

@app.route('/api/greet', methods=['GET'])
def greet():
    return jsonify({"message": "Hello from Flask backend!"})

if __name__ == '__main__':
    # '0.0.0.0' makes the server accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)