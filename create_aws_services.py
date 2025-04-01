import boto3

# Create DynamoDB table
def create_dynamodb_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName='SportsKits',
        KeySchema=[
            {'AttributeName': 'kit_id', 'KeyType': 'HASH'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'kit_id', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )
    return table

# Create SNS topic
def create_sns_topic():
    sns = boto3.client('sns')
    topic = sns.create_topic(Name='NewKitDesigns')
    return topic

# Create S3 bucket
def create_s3_bucket():
    s3 = boto3.client('s3')
    bucket = s3.create_bucket(Bucket='sportskits-designs')
    return bucket

if __name__ == '__main__':
    print("Creating DynamoDB table...")
    dynamo_table = create_dynamodb_table()
    print("Table created:", dynamo_table.table_status)

    print("Creating SNS topic...")
    sns_topic = create_sns_topic()
    print("Topic ARN:", sns_topic['TopicArn'])

    print("Creating S3 bucket...")
    s3_bucket = create_s3_bucket()
    print("Bucket created successfully")
