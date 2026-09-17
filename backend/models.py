from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AlphaResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('alpha_result.id'), nullable=True)
    expression_string = db.Column(db.String(500), nullable=False)
    is_sharpe = db.Column(db.Float, nullable=True)
    os_sharpe = db.Column(db.Float, nullable=True)
    fitness = db.Column(db.Float, nullable=True)
    turnover = db.Column(db.Float, nullable=True)
    passed_threshold = db.Column(db.Boolean, default=False)
