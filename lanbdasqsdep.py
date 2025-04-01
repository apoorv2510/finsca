import boto3
import json
import zipfile
import os

# AWS Configuration
region = 'us-east-1'
role_name = 'LabRole'
lambda_name = 'ProcessKitLambda'
sqs_queue_name = 'SportsKitQueue'
lambda_handler = 'lambda_function.lambda_handler'

# Lambda Function Code as String
lambda_code = '''
import json
import boto3

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            message_body = json.loads(record['body'])
            print(f"Processing kit data: {message_body}")

            # Example Processing: Store to DynamoDB
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('ProcessedKits')
            table.put_item(Item=message_body)
            
            print("Kit processed successfully!")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Processing complete')
        }

    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
'''

# Save the lambda code to a file
lambda_file_name = 'lambda_function.py'
with open(lambda_file_name, 'w') as f:
    f.write(lambda_code)

# Create a zip file containing the lambda function
zip_file_name = 'lambda_function.zip'
with zipfile.ZipFile(zip_file_name, 'w') as zf:
    zf.write(lambda_file_name)

# Clean up the file after zipping
os.remove(lambda_file_name)

# Create SQS Queue
sqs = boto3.client('sqs', region_name=region)
sqs_response = sqs.create_queue(QueueName=sqs_queue_name)
queue_url = sqs_response['QueueUrl']
print(f"SQS Queue Created: {queue_url}")

# Get ARN of the SQS Queue
queue_arn = sqs.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=['QueueArn']
)['Attributes']['QueueArn']

# Create Lambda Function
lambda_client = boto3.client('lambda', region_name=region)
role_arn = f'arn:aws:iam::642051550988:role/{role_name}'

with open(zip_file_name, 'rb') as f:
    zipped_code = f.read()

lambda_response = lambda_client.create_function(
    FunctionName=lambda_name,
    Runtime='python3.9',
    Role=role_arn,
    Handler=lambda_handler,
    Code={'ZipFile': zipped_code},
    Description='Lambda function to process sports kit uploads',
    Timeout=10,
    MemorySize=128
)
lambda_arn = lambda_response['FunctionArn']
print(f"Lambda Function Created: {lambda_arn}")

# Clean up the zip file after uploading
os.remove(zip_file_name)

# Set SQS Trigger for Lambda
event_source_mapping = lambda_client.create_event_source_mapping(
    EventSourceArn=queue_arn,
    FunctionName=lambda_name,
    Enabled=True,
    BatchSize=10
)
print(f"Event Source Mapping Created: {event_source_mapping['UUID']}")

# Add Permission for SQS to Invoke Lambda
lambda_client.add_permission(
    FunctionName=lambda_name,
    StatementId='SQSInvoke',
    Action='lambda:InvokeFunction',
    Principal='sqs.amazonaws.com',
    SourceArn=queue_arn
)

print("✅ Lambda and SQS configured successfully!")
