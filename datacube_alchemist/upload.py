import os
import tempfile
from distutils.dir_util import copy_tree
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from datacube_alchemist.assume_role_helper import get_autorefresh_session

from urllib.parse import urlparse


def create_s3_connection():
    # Set up s3 connection
    if 'AWS_ROLE_ARN' in os.environ and 'AWS_WEB_IDENTITY_TOKEN_FILE' in os.environ:
        role_with_web_identity_params = {
            "DurationSeconds": os.getenv('SESSION_DURATION', 3600),
            "RoleArn": os.getenv('AWS_ROLE_ARN'),
            "RoleSessionName": os.getenv('AWS_SESSION_NAME', 'test_session'),
            "WebIdentityToken": open(os.getenv('AWS_WEB_IDENTITY_TOKEN_FILE')).read(),
        }
        autorefresh_session = get_autorefresh_session(**role_with_web_identity_params)
        s3_client = autorefresh_session.client('s3')
    else:
        s3_client = boto3.client('s3')
    return s3_client


def _files_to_copy(src_base, dst_base):
    src_base = Path(src_base)
    src_base = src_base.absolute()
    n_skip = len(str(src_base))

    for base, _, files in os.walk(src_base):
        b = Path(base)
        for f in files:
            src = b / f
            dst = str(src)[n_skip:]
            yield (src, dst_base + dst)


class S3Upload(object):
    def __init__(self, location):
        if location[0:2] == 's3':
            self.upload = True
            self.tmp_results = tempfile.mkdtemp()
            self._location = self.tmp_results
            self.s3location = location
        else:
            self._location = location
            self.upload = False

    @property
    def location(self):
        return self._location

    def upload_if_needed(self):
        """
        If the data needs to be moved from a tmp location to s3 do the move.
        """
        if self.upload is True:
            self.upload_now_change_control()

    def upload_now_change_control(self):
        s3_client = create_s3_connection()

        for f_src, f_dst in _files_to_copy(self._location, self.s3location):
            o = urlparse(str(f_dst), allow_fragments=False)
            bucket = o.netloc
            key = o.path.lstrip('/')
            try:
                s3_client.upload_file(
                    str(f_src),  # I don't know why this isn't a string already
                    bucket,
                    key,
                    ExtraArgs={'ACL': 'bucket-owner-full-control'}
                )
            except ClientError as e:
                print("Failed to upload with error {}".format(e))


def main():
    """
    Very hacky test.
    :return:
    """
    location = 's3://dea-public-data-dev/alchemist/tests'

    s3ul = S3Upload(location)
    location = s3ul.location
    local = "/tmp/test"
    copy_tree(local, location)

    s3ul.upload_if_needed()


if __name__ == '__main__':
    main()
