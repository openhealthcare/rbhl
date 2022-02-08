import gzip
import os
import subprocess
import sys
import base64
import boto3


def get_backup(bucket_name, key, file_name, secret_file):
    s3 = boto3.client('s3')
    with open(secret_file, "rb") as sf:
        secret = base64.b64decode(sf.read())
    response = s3.get_object(
        Bucket=bucket_name,
        Key=key,
        SSECustomerKey=secret,
        SSECustomerAlgorithm='AES256'
    )
    with gzip.GzipFile(fileobj=response["Body"]) as gzipfile:
        content = gzipfile.read()

    with open(file_name, "wb") as f:
        f.write(content)


def load_file(db_name, db_user, file_name):
    command = "psql -d {} -U {} -f {}".format(
        db_name, db_user, file_name
    )
    subprocess.check_call(command, shell=True)


def main(db_name, db_user, bucket_name, key, secret_file):
    file_name = "db_dump.sql"
    get_backup(bucket_name, key, file_name, secret_file)
    load_file(db_name, db_user, file_name)
    os.remove(file_name)


if __name__ == "__main__":
    _, db_name, db_user, bucket_name, key, secret_file = sys.argv
    main(db_name, db_user, bucket_name, key, secret_file)
