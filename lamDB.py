import boto3
import time

# AWS Configuration
region_name = 'us-east-1'
table_name = 'ProcessedKits'

# Create a DynamoDB client
dynamodb = boto3.client('dynamodb', region_name=region_name)

def create_table():
    try:
        # Create the DynamoDB table
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'kit_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'kit_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        print(f"Creating table {table_name}...")

        # Wait until the table exists
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)

        print(f"✅ Table '{table_name}' created successfully!")

    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table '{table_name}' already exists. No need to create it again.")
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")

if __name__ == "__main__":
    create_table()
