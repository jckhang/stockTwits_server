import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from app import updateTwits, updateInfos
logging.basicConfig()
sched = BlockingScheduler()


def scheduled_job():
    updateInfos()
    updateTwits()
    print('This job is run every weekday at 9 to 16.')


sched.add_job(scheduled_job, 'interval', minutes=10)

sched.start()
