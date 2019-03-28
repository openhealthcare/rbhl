from datetime import datetime

from django.utils import timezone


def to_bool(s):
    boolLUT = {"no": False, "yes": True}
    return boolLUT.get(s, None)


def to_date(s):
    dt = to_datetime(s)

    if not dt:
        return

    return dt.date()


def to_datetime(s):
    if not s:
        return

    try:
        dt = datetime.strptime(s, "%d-%b-%y")
    except ValueError:
        return

    return timezone.make_aware(dt)


def to_float(s):
    if not s:
        return

    return float(s)


def to_int(s):
    if not s:
        return 0

    try:
        return int(s)
    except ValueError:
        return 0


def to_upper(s):
    if not s:
        return

    return s.upper()
