import boto3
import botocore
import json
import configparser


def main(s3Client):
    print('Starting create website function...\n')

    print('Reading configuration file for bucket name...')
    config = readConfig()
    bucket_name = config['bucket_name']

    # Upload html files
    print('Uploading files for the website...')
    uploadWebsiteFiles(s3Client, bucket_name)

    # Enable web hosting
    print('Enabling web hosting on the bucket...')
    enableWebHosting(s3Client, bucket_name)

    # Configure bucket policy
    print('Adding a bucket policy to allow traffic from the internet...')
    allowAccessFromWeb(s3Client, bucket_name)
    
    # Obtain the region from the boto3 session and print url
    session = boto3.session.Session()
    current_region = session.region_name
    print('\nYou can access the website at:\n')
    print('http://' + bucket_name + '.s3-website-' + current_region +'.amazonaws.com')

    print('\nEnd create website function...')




def uploadWebsiteFiles(s3Client, bucket):
    fileNames = getFileList()
    for obj in fileNames:
        key = obj['Name']
        filename =  key
        contentType = obj['Content']
        # Upload html/index.html to the bucket
        s3Client.upload_file(
            Filename=filename,
            Bucket=bucket,
            Key=key,
            ExtraArgs={
                'ContentType': contentType
            }
        )


def enableWebHosting(s3Client, bucket):
    # enable S3 web hosting using the objects you uploaded in the last method as the index and error document for the website.
    s3Client.put_bucket_website(
        Bucket=bucket,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
        }
    )

def allowAccessFromWeb(s3Client, bucket):
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:GetObject'],
            'Resource': "arn:aws:s3:::" + bucket + '/*'
        }]
    }
    bucket_policy = json.dumps(bucket_policy)

    # Apply the provided bucket policy to the website bucket to allow your objects to be accessed from the internet.
    s3Client.put_bucket_policy(
        Bucket=bucket,
        Policy=bucket_policy
    )

def getFileList():
    return [
        {
            "Name": 'index.html',
            "Content": 'text/html'
        },
        {
            "Name": 'styles.css',
            "Content": 'text/css'
        },
        {
            "Name": "image1.jpeg",
            "Content": "image/jpeg"
        },
        {
            "Name": "image2.jpeg",
            "Content": "image/jpeg"
        },
        {
            "Name": "image3.jpeg",
            "Content": "image/jpeg"
        }
    ]


def readConfig():
    config = configparser.ConfigParser()
    config.read('./config.ini')

    return config['S3']


# Create an S3 client to interact with the service and pass it to the main function that will create the buckets
client = boto3.client('s3')
try:
    main(client)
except botocore.exceptions.ClientError as err:
    print(err.response['Error']['Message'])
except botocore.exceptions.ParamValidationError as error:
    print(error)
