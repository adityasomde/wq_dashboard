from celery.schedules import crontab
from simulator import celery_app, simulate_expression
from generator import generate_expression

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        run_daily_generation.s(),
    )

@celery_app.task
def run_daily_generation():
    for _ in range(50):
        expr = generate_expression()
        simulate_expression.delay(expr)
