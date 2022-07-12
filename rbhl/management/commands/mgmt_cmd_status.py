"""
A management command that checks running cron jobs
and emails the admin team with the count and description
"""
from django.core.management.base import BaseCommand
import subprocess
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
import logging

logger = logging.getLogger('commands')


# the number of management commands that if we have more than
# we should email
THRESHOLD = 1

# we ignore the first one of these commands that we hit
# as they are caused by this managment command
# subsequent references we keep as these would be stale
# hangovers of previous run of this command
IGNORE_FIRST = (
    " ".join([
        "/bin/sh -c /home/ubuntu/.virtualenvs/rbhl/bin/python",
        "/usr/lib/ohc/rbhl/manage.py mgmt_cmd_status >>",
        "/usr/lib/ohc/log/cron.log 2>&1",
    ]),
    " ".join([
        "/home/ubuntu/.virtualenvs/rbhl/bin/python",
        "/usr/lib/ohc/rbhl/manage.py mgmt_cmd_status",
    ]),
    "grep manage.py"
)


def raise_alarm():
    """
    If we fail for any reason, get shouty
    """
    BN = settings.OPAL_BRAND_NAME
    logger.error(f'{BN} failed to check management command status')


def send_email(lines):
    """
    Email with the admins the details of the currently running
    management commands
    """
    name = settings.OPAL_BRAND_NAME
    if len(lines) == 1:
        title = f"There is 1 running command on {name}"
    else:
        title = f"There are {len(lines)} running commands on {name}"
    html_message = render_to_string(
        "emails/running_commands.html", {"title": title, "lines": lines}
    )
    plain_message = strip_tags(html_message)
    send_mail(
        title,
        plain_message,
        settings.ADMINS[0][1],
        [i[1] for i in settings.ADMINS],
        html_message=html_message,
    )


def get_managepy_processes():
    """
    Returns a list of management commands currently running
    in the form [(the command, the date the command started)]
    """
    p1 = subprocess.Popen(
        ["ps", "--sort=-lstart", "-eo", "lstart,cmd"], stdout=subprocess.PIPE
    )
    p2 = subprocess.Popen(
        ["grep", "manage.py"], stdin=p1.stdout, stdout=subprocess.PIPE
    )
    ps_lines = p2.stdout.readlines()
    cmd_and_date = []
    ignore_first = list(IGNORE_FIRST)
    for bline in ps_lines:
        line = bline.decode("utf-8").strip()
        some_dt = line[:25].strip()
        cmd = line[25:].strip()
        if cmd in ignore_first:
            ignore_first.remove(cmd)
            continue
        cmd_and_date.append((cmd, some_dt,))

    return cmd_and_date


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            lines = get_managepy_processes()
            logger.info(
                " ".join([
                    f'Found {len(lines)} running management commands',
                ])
            )
            if len(lines) > THRESHOLD:
                logger.info(
                    " ".join([
                        f'Threshold {THRESHOLD} breached, with {[i[0] for i in lines]}',
                        'Sending email'
                    ])
                )
                send_email(lines)
        except Exception:
            raise_alarm()
