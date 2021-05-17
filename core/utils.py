from datetime import datetime, timedelta


def get_due_date():
    """ Assuming due date is 20 days after issue date"""
    return datetime.today().date() + timedelta(days=20)
