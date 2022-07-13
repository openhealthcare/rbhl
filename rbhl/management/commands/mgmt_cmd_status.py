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


def raise_alarm():
    """
    If we fail for any reason, get shouty
    """
    BN = settings.OPAL_BRAND_NAME
    logger.error(f'{BN} failed to check management command status')


def send_email(lines, memory_status):
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
        "emails/running_commands.html", {"title": title, "lines": lines, "memory:" memory}
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
    for bline in ps_lines:
        line = bline.decode("utf-8").strip()
        some_dt = " ".join(line.strip().split(" ")[:5])
        cmd = line.replace(some_dt, "").strip()
        if cmd == 'grep manage.py':
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
                    '(this includes this command)'
                ])
            )
            if len(lines) > THRESHOLD:
                logger.info(
                    " ".join([
                        f'Threshold {THRESHOLD} breached, with {[i[0] for i in lines]}',
                        'Sending email'
                    ])
                )
                
                memory_proc = suprocess.Popen(['free', '-h' ], stdout=subprocess.PIPE)
                memory_status = "".join(memory_proc.stdout.readlines())
                
                send_email(lines, memory_status)
        except Exception:
            raise_alarm()
