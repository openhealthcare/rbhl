import os
import subprocess
import sys
from datetime import datetime
import base64
import boto3


def dump_database(db_name, db_user, backup_name):
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


def upload(bucket_name, local_path, key, secret_file):
    """
    Given a bucket name, key_name and filename will upload the referenced file
    to the given bucket against the provided key_name.
    """
    s3 = boto3.client('s3')
    with open(secret_file, "rb") as sf:
        secret = base64.b64decode(sf.read())
    with open(local_path) as f:
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=f.read(),
            SSECustomerKey=secret,
            SSECustomerAlgorithm='AES256'
        )


def main(db_name, db_user, backups_dir, bucket_name, secret_file):
    now = datetime.now().strftime("%Y-%m-%d-%H-%M")
    backup_name = "{}-{}.sql".format(now, db_name)

    full_backup_name = os.path.join(backups_dir, backup_name)
    dump_database(db_name, db_user, full_backup_name)
    upload(bucket_name, full_backup_name, backup_name, secret_file)
    os.remove(full_backup_name)


if __name__ == "__main__":
    try:
        _, db_name, db_user, backups_dir, bucket_name, secret = sys.argv
        main(db_name, db_user, backups_dir, bucket_name, secret)
    except Exception as e:
        print("errored with {}".format(e))
