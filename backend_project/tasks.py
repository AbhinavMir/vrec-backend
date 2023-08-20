from celery import shared_task

@shared_task
def weekly_task():
    # Your weekly task code here
    pass

@shared_task
def monthly_task():
    # Your monthly task code here
    pass
