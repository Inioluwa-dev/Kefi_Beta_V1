import boto3
import os

def generate_b2_signed_url(key, expires_in=3600):
    s3 = boto3.client(
        's3',
        endpoint_url='https://s3.us-west-004.backblazeb2.com',
        aws_access_key_id=os.environ['B2_KEY_ID'],
        aws_secret_access_key=os.environ['B2_APP_KEY'],
        region_name='us-west-004',
    )
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.environ['B2_BUCKET_NAME'], 'Key': key},
        ExpiresIn=expires_in,
    )
    return url
