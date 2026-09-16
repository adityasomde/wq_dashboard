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
            
        settings = request.json or {}
        expr = generate_expression()
        task = simulate_expression.delay(expr, wq_token, settings)
        
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
