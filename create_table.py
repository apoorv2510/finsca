import boto3

# AWS Configuration
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def create_users_table():
    table_name = "Users"

    # Check if table already exists
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    if table_name in existing_tables:
        print(f"Table '{table_name}' already exists.")
        return

    # Create DynamoDB table
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'user_id', 'KeyType': 'HASH'}  # Primary Key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table is created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

    print(f"Table '{table_name}' created successfully!")

if __name__ == "__main__":
    create_users_table()
