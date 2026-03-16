from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    mode = request.form.get('mode', 'Default')
    
    # 💡 This is where you would call your Baybayin AI model!
    print(f"Translating image using mode: {mode}")
    
    return jsonify({
        "translated_text": "Kamusta (Translated from Baybayin)",
        "status": "success"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)