import os
import subprocess
from datetime import datetime
import base64
import boto3
import gzip
import shutil
from django.core.management import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


def raise_alarm():
    BN = settings.OPAL_BRAND_NAME
    send_mail(
        f'{BN} failed to backup',
        f'We have been unable to do the nightly back up for {BN}',
        settings.ADMINS[0][1],
        [i[1] for i in settings.ADMINS],
        fail_silently=False,
    )


def dump_database(db_name, db_user, backups_dir):
    now = datetime.now().strftime("%Y-%m-%d-%H-%M")
    bn = settings.OPAL_BRAND_NAME.lower().replace(" ", "-")
    backup_name = f"{bn}-{now}-{db_name}.sql"
    backup_name = os.path.join(backups_dir, backup_name)
    gzip_name = f"{backup_name}.gz"
    print(f"Dumping db_name: {db_name}")
    command = f"pg_dump {db_name} -U {db_user}"
    print(f"Running: {command}")
    with open(backup_name, "wb") as out:
        subprocess.check_call(command, stdout=out, shell=True)

    if not os.path.exists(backup_name):
        raise Exception(
            f"Database dump not saved for: {backup_name}"
        )
    # create a gzipped version of the backup
    with open(backup_name, 'rb') as backup:
        with gzip.open(gzip_name, 'wb') as gzipped_backup:
            shutil.copyfileobj(backup, gzipped_backup)
    # delete the non gzipped version
    os.remove(backup_name)
    return gzip_name


def upload(bucket_name, backup_with_path, secret_file):
    """
    Given a bucket name, key_name and filename will upload the referenced file
    to the given bucket against the provided key_name.
    """
    s3 = boto3.client('s3')
    with open(secret_file, "rb") as sf:
        secret = base64.b64decode(sf.read())
    with open(backup_with_path) as f:
        s3.put_object(
            Bucket=bucket_name,
            Key=os.path.basename(backup_with_path),
            Body=f.read(),
            ContentType='text/plain',
            ContentEncoding='gzip',
            SSECustomerKey=secret,
            SSECustomerAlgorithm='AES256'
        )


def main(db_name, db_user, backups_dir, bucket_name, secret_file):
    gzip_name = dump_database(db_name, db_user, backups_dir)
    upload(bucket_name, gzip_name, secret_file)
    os.remove(gzip_name)


class Command(BaseCommand):
    def add_arguments(self , parser):
        parser.add_argument('backups_dir')
        parser.add_argument('bucket_name')
        parser.add_argument('secret')

    def handle(self, *args, **kwargs):
        db_name = settings.DATABASES["default"]["NAME"]
        db_user = settings.DATABASES["default"]["USER"]
        backups_dir = kwargs["backups_dir"]
        bucket_name = kwargs["bucket_name"]
        secret = kwargs["secret"]
        try:
            main(db_name, db_user, backups_dir, bucket_name, secret)
        except Exception:
            raise_alarm()
