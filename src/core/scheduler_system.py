
import schedule
import time

class SchedulerSystem:
    def __init__(self):
        pass

    def add_job(self, cron_string, task_function):
        # This is a simplified representation. 
        # A real cron implementation would parse the cron_string.
        # For now, we'll assume cron_string is something like "daily" or "hourly"
        if cron_string == "daily":
            schedule.every().day.at("00:00").do(task_function)
        elif cron_string == "hourly":
            schedule.every().hour.do(task_function)
        elif cron_string == "every_minute":
            schedule.every().minute.do(task_function)
        else:
            print(f"Unsupported cron string: {cron_string}")

    def run_pending_jobs(self):
        while True:
            schedule.run_pending()
            time.sleep(1) # wait one second

