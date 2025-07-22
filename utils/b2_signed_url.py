import boto3
import os
from botocore.client import Config
from functools import lru_cache

@lru_cache(maxsize=1)
def get_b2_client():
    return boto3.client(
        's3',
        endpoint_url='https://s3.us-west-004.backblazeb2.com',
        aws_access_key_id=os.environ['B2_KEY_ID'],
        aws_secret_access_key=os.environ['B2_APP_KEY'],
        region_name='us-west-004',
        config=Config(signature_version='s3v4'),  # Force SigV4
    )

def generate_b2_signed_url(key, expires_in=3600):
    try:
        s3 = get_b2_client()
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': os.environ['B2_BUCKET_NAME'], 'Key': key},
            ExpiresIn=expires_in,
        )
        return url
    except Exception as e:
        # Optionally log the error
        return None
