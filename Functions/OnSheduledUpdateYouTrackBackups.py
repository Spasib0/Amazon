import json
import boto3
import os
import urllib3
import json
import shutil

def lambda_handler(event, context):
    headers = {'Authorization': os.environ['YT_TOKEN'],
                'Accept': 'application/json',
                'Content-Type': 'application/json'}
                
               
    http = urllib3.PoolManager()

    response = http.request("GET", os.environ['YT_URL'], headers=headers)

    if response.status != 200:
        print(response) #отправить письмо какое-то
    
    
    class Backups:
        items = []
    
        def __init__(self, backups_data):
            for backup in backups_data:
                self.items.append(Backup(backup['id']))
    
    
    class Backup:
        def __init__(self, backup_id):
            self.id = backup_id
            self.year, self.month, self.day, self.hours, self.minutes, self.seconds_and_extension = backup_id.split("-")
            self.seconds, self.extension = self.seconds_and_extension.split(".", 1)
    
    jsonData = json.loads(response.data)
    
    backup = Backups(jsonData).items[0]

    buketName = backup.id
    
    backup_fields = http.request("GET", os.environ['YT_BACKUPS_URL']+buketName+os.environ["FIELDS_ARGS"], headers=headers)
    
    backupLink = json.loads(backup_fields.data)['link']

    s3 = boto3.client('s3')
    
    key = f"{backup.year}/{backup.month}/{backup.day}{backup.month}{backup.year}.{backup.extension}"

    print("key", key)
    
    path = '/tmp/' + buketName
    
    with http.request('GET', os.environ['YT_API_URL']+backupLink, preload_content=False) as r, open(path, 'wb') as out_file:       
       shutil.copyfileobj(r, out_file)

    yt_bucket_obj = s3.upload_file(path, os.environ['YT_BUCKET'], key )
    
    print("ytobj", yt_bucket_obj)
    
    SesClient = boto3.client('ses', region_name='eu-west-1')
    response = SesClient.send_email(
        Destination={
            'ToAddresses': os.environ['YT_EMAILS'].split(',')
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': 'Youtrack backup - https://s3.console.aws.amazon.com/s3/object/youtrackbackups?region=eu-central-1&prefix=' + key,
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Youtrack buckup complite',
            },
        },
    Source= os.environ['YT_EMAIL_SOURCE']
    )
    
    print(response)