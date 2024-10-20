# tasks.py
from config import db, settings
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def scheduled_task():
    print("Scheduled task running every hour")

# Define your scheduled job
scheduler.add_job(scheduled_task, 'interval', hours=1)
