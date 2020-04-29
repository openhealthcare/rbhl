from datetime import datetime

from django.utils import timezone


def to_bool(s):
    if s.lower() in ["unknown", "not applicable", "0"]:
        return

    boolLUT = {"no": False, "yes": True}
    if s and s.lower() not in boolLUT:
        print("Unable to find a boolean for {}".format(s))
    return boolLUT.get(s.lower(), None)


def to_date(s):
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
