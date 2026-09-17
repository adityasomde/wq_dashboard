from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, AlphaResult
import os

def create_app():
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    CORS(app)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alpha_results.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    @app.route('/api/simulate', methods=['POST'])
    def trigger_simulation():
        from generator import generate_expression
        from simulator import simulate_expression
        import jwt
        from auth import SECRET_KEY
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing token'}), 401
        try:
            token = auth_header.split(' ')[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            wq_token = decoded.get('wq_token', '')
        except:
            return jsonify({'error': 'Invalid token'}), 401
            
        settings = request.json.get('settings', {})
        expr = request.json.get('alphaCode', '')
        parent_id = request.json.get('parentId', None)
        
        task = simulate_expression.delay(expr, wq_token, settings, parent_id)
        
        return jsonify({
            "message": "Simulation triggered",
            "task_id": task.id
        }), 202

    @app.route('/api/task/<task_id>', methods=['GET'])
    def task_status(task_id):
        from simulator import celery_app
        task = celery_app.AsyncResult(task_id)
        return jsonify({
            "state": task.state,
            "status": str(task.info)
        })

    @app.route('/api/results', methods=['GET'])
    def get_results():
        results = AlphaResult.query.all()
        data = []
        for r in results:
            data.append({
                "id": r.id,
                "parent_id": r.parent_id,
                "expression_string": r.expression_string,
                "is_sharpe": r.is_sharpe,
                "os_sharpe": r.os_sharpe,
                "fitness": r.fitness,
                "turnover": r.turnover,
                "passed_threshold": r.passed_threshold
            })
        return jsonify(data), 200

    @app.route('/api/me', methods=['GET'])
    def get_me():
        import jwt
        import requests
        from auth import SECRET_KEY
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing token'}), 401
        try:
            token = auth_header.split(' ')[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            wq_token = decoded.get('wq_token', '')
        except:
            return jsonify({'error': 'Invalid token'}), 401
            
        headers = {
            "Cookie": f"t={wq_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        try:
            res = requests.get('https://api.worldquantbrain.com/users/me', headers=headers)
            if res.status_code == 200:
                return jsonify(res.json()), 200
            else:
                return jsonify({'error': 'Failed to fetch from WQ'}), res.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schema', methods=['POST'])
    def get_schema():
        import jwt
        import requests
        from auth import SECRET_KEY
        from wq_schema import resolve_options
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing token'}), 401
        try:
            token = auth_header.split(' ')[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            wq_token = decoded.get('wq_token', '')
        except:
            return jsonify({'error': 'Invalid token'}), 401
            
        settings = request.json or {}
        
        headers = {
            "Cookie": f"t={wq_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json; version=3.0"
        }
        try:
            res = requests.options('https://api.worldquantbrain.com/simulations', headers=headers)
            if res.status_code == 200:
                body = res.json()
                children = body.get("actions", {}).get("POST", {}).get("settings", {}).get("children", {})
                resolved = resolve_options(children, settings)
                return jsonify(resolved), 200
            else:
                return jsonify({'error': 'Failed to fetch schema'}), res.status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ah/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def ah_proxy(path):
        import requests
        from flask import request, Response
        url = f"http://localhost:8000/api/{path}"
        headers = {k: v for k, v in request.headers if k.lower() != 'host'}
        
        try:
            if request.method == 'GET':
                resp = requests.get(url, headers=headers, params=request.args, stream=True)
            elif request.method == 'POST':
                resp = requests.post(url, headers=headers, params=request.args, data=request.get_data(), stream=True)
            elif request.method == 'PUT':
                resp = requests.put(url, headers=headers, params=request.args, data=request.get_data(), stream=True)
            elif request.method == 'DELETE':
                resp = requests.delete(url, headers=headers, params=request.args, stream=True)
            elif request.method == 'PATCH':
                resp = requests.patch(url, headers=headers, params=request.args, data=request.get_data(), stream=True)
                
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            resp_headers = [(name, value) for (name, value) in resp.raw.headers.items()
                            if name.lower() not in excluded_headers]
            
            return Response(resp.iter_content(chunk_size=10*1024), resp.status_code, resp_headers)
        except Exception as e:
            return jsonify({'error': f'Proxy error: {str(e)}'}), 500

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return app.send_static_file(path)
        else:
            return app.send_static_file('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
