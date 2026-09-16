from celery import Celery
import time
import requests
import os
from models import db, AlphaResult

celery_app = Celery('wq_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery_app.task(bind=True)
def simulate_expression(self, expression_string, wq_token=''):
    """
    Submits a generated expression to the BRAIN /simulate endpoint.
    Strict simulation variables: Equity, USA, TOP3000, Delay 1, Truncation 0.01.
    """
    # Note: Flask app context is required for database operations.
    from app import create_app
    flask_app = create_app()
    
    with flask_app.app_context():
        result_record = AlphaResult(expression_string=expression_string)
        db.session.add(result_record)
        db.session.commit()
        record_id = result_record.id

    simulation_payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "NONE",
            "truncation": 0.01,
            "pasteurization": "ON",
            "testPeriod": "P2Y",
            "language": "PYTHON"
        },
        "regular": expression_string
    }

    wq_token = wq_token or os.getenv('WQ_TOKEN', '')
    headers = {
        "Cookie": f"t={wq_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    url = 'https://api.worldquantbrain.com/simulations'
    
    sim_url = None
    while True:
        try:
            response = requests.post(url, json=simulation_payload, headers=headers)
            if response.status_code == 201:
                location = response.headers.get('Location')
                sim_url = f"https://api.worldquantbrain.com{location}" if location.startswith('/') else location
                break
            elif 'Retry-After' in response.headers:
                time.sleep(int(response.headers.get('Retry-After')))
            else:
                break
        except:
            break

    if sim_url:
        while True:
            res = requests.get(sim_url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                status = data.get('status')
                if status == 'COMPLETE':
                    alpha_id = data.get('alpha')
                    if alpha_id:
                        alpha_res = requests.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}", headers=headers)
                        if alpha_res.status_code == 200:
                            adata = alpha_res.json()
                            is_sharpe = adata.get('is', {}).get('sharpe', 0)
                            os_sharpe = adata.get('os', {}).get('sharpe', 0)
                            fitness = adata.get('is', {}).get('fitness', 0)
                            turnover = adata.get('is', {}).get('turnover', 0)
                            
                            with flask_app.app_context():
                                rec = AlphaResult.query.get(record_id)
                                if rec:
                                    rec.is_sharpe = is_sharpe
                                    rec.os_sharpe = os_sharpe
                                    rec.fitness = fitness
                                    rec.turnover = turnover
                                    rec.passed_threshold = (os_sharpe > 1.0)
                                    db.session.commit()
                    break
                elif status in ['ERROR', 'FAIL', 'TIMEOUT', 'CANCELLED']:
                    break
            elif 'Retry-After' in res.headers:
                time.sleep(int(res.headers.get('Retry-After')))
            else:
                break
