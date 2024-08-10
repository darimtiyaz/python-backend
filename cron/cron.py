# tasks.py

from flask import Flask, Blueprint
from config import init_db
from datetime import datetime
from flask_apscheduler import APScheduler

app = Flask(__name__)
cron_bp = Blueprint('cron', __name__)
# Initialize Scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Define your scheduled job
@scheduler.task('interval', hours=1)
def scheduled_task():
    print("Scheduled task running every hour")
