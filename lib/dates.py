import datetime
import businesstimedelta

start_date = None


def get_today():
    return datetime.datetime.now()


def set_start_date(date_time_str):
    global start_date
    start_date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')


def get_start_date():
    return start_date


def get_business_hours_rules():
    # Define a working day/week
    workday = businesstimedelta.WorkDayRule(
        start_time=datetime.time(9),
        end_time=datetime.time(18),
        working_days=[0, 1, 2, 3, 4])

    return businesstimedelta.Rules([workday])
