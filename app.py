from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app) 

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({'error': 'Code ethum anuppala!'}), 400
    
    user_code = data['code']
    # 💥 Pudhusu: Frontend-la irundhu varra Custom Input-ah edukkurom
    user_input = data.get('input', '') 
    
    engine_path = os.path.join(os.path.dirname(__file__), 'compiler_engine', 'qpp_engine')
    
    try:
        result = subprocess.run(
            [engine_path, user_code],
            input=user_input,     # 💥 Pudhusu: C++ Engine-oda cin-ku idhai feed pandrom!
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return jsonify({
                'status': 'error', 
                'error': result.stderr or 'C++ Engine execution failed'
            }), 500
            
        output = result.stdout
        
        return jsonify({
            'status': 'success',
            'output': output,
            'your_code': user_code
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'Q++ Backend API & C++ Engine are linked and running perfectly!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
