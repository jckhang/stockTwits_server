from apscheduler.schedulers.blocking import BlockingScheduler
from app import updateTwits, updateInfos
sched = BlockingScheduler()


# @sched.scheduled_job('interval', minutes=10)
# def timed_job1():
#     updateDBstock()
#     print('stock price is updated every 10 minutes.')


# @sched.scheduled_job('interval', minutes=30)
# def timed_job2():
#     updateDBtwits()
#     print('stock twits is updated every 30 minutes.')
def scheduled_job():
    updateInfos()
    updateTwits()
    print('This job is run every weekday at 9 to 16.')


sched.add_job(scheduled_job, 'cron', day_of_week='mon-fri', hour='9-16')


sched.start()
