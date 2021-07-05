import os
import subprocess
import sys
from datetime import datetime
import base64
import boto3
import gzip
import shutil


def dump_database(db_name, db_user, backups_dir):
    now = datetime.now().strftime("%Y-%m-%d-%H-%M")
    backup_name = "{}-{}.sql".format(now, db_name)
    backup_name = os.path.join(backups_dir, backup_name)
    gzip_name = f"{backup_name}.gz"
    print("Dumping db_name: {}".format(db_name))
    command = "pg_dump {} -U {}".format(
        db_name, db_user
    )
    print("Running: {}".format(command))
    with open(backup_name, "wb") as out:
        subprocess.check_call(command, stdout=out, shell=True)

    if not os.path.exists(backup_name):
        raise Exception(
            "Database dump not saved for: {}".format(backup_name)
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


if __name__ == "__main__":
    try:
        _, db_name, db_user, backups_dir, bucket_name, secret = sys.argv
        main(db_name, db_user, backups_dir, bucket_name, secret)
    except Exception as e:
        print("errored with {}".format(e))
