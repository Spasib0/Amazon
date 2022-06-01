import json
import urllib.parse
import boto3
import os

#print('Loading function')

s3 = boto3.client('s3')

s3ya = boto3.client(
    service_name='s3',
    endpoint_url=os.environ['YA_URL'],
    aws_access_key_id=os.environ['YA_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['YA_SECRET_ACCESS_KEY']
    )


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        #print("res:" + bucket + " / " + key)
        s3ya.put_object(Bucket=bucket, Key=key, Body=response['Body'].read())
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
