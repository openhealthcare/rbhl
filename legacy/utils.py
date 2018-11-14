"""
Utilities for working with legacy data
"""
import datetime

from django.utils import timezone


def str_to_date(s, no_future_dates=False):
    if s == '':
        return
    when = timezone.make_aware(
        datetime.datetime.strptime(s, "%m/%d/%y %H:%M:%S")
    ).date()
    if no_future_dates:
        if when > datetime.date.today():
            when = when.replace(year=when.year - 100)
    return when

def bol(s):
    if s == '':
        return
    return bool(int(s))

def inty(s):
    if s == '':
        return
    return(int(s))
