import datetime

start_date = None


def get_today():
    return datetime.datetime.now()


def set_start_date(date_time_str):
    global start_date
    start_date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')


def get_start_date():
    return start_date
