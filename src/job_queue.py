from datetime import datetime
from croniter import croniter
import pytz


class JobQueue():
    '''
    A queue of jobs to be run at regular intervals.
    '''

    def __init__(self, jobdict=None):
        if jobdict is None:
            jobdict = {}
        self.jobdict = jobdict

    def add_job(self, job_name, job_func, job_cron, day_or=True):
        '''
        Add a new job to the queue.

        :param job_name: a name for the job
        :param job_func: a callable to be executed when the job is run
        :param job_cron: a string in cron-format indicating when to run the job
        '''
        if job_name in self.jobdict:
            raise ValueError(f'Job name {job_name} already exists.')
        # Convert the current time to UTC so the math works.
        current_time = datetime.now().astimezone(pytz.utc)
        # Create a croniter object for the job.
        job_iter = croniter(job_cron, current_time, day_or=day_or)
        # Build a dictionary of one key, which we can use to update the master
        # jobdict.
        job = {job_name: {'func': job_func,
                          'cron': job_cron,
                          'iter': job_iter,
                          'day_or': day_or,
                          'next': job_iter.get_next(datetime)
                          }
              }
        self.jobdict.update(job)

    def run_pending(self):
        '''
        Run all jobs whose next run is due to be kicked off.
        '''
        for name, job in self.jobdict.items():
            # Execute any jobs that are due.
            if job['next'] < datetime.now().astimezone(pytz.utc):
                # Update the next time.
                job['next'] = job['iter'].get_next(datetime)
                # Then run the function.
                job['func']()

    def __str__(self):
        s = '<JobQueue with {} jobs>'
        s = s.format(len(self.jobdict))
        return s

    def __repr__(self):
        return f'JobQueue({repr(self.jobdict)})'