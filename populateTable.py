import boto3
import uuid

# AWS Configurations
AWS_REGION = "us-west-2"
DYNAMO_ORDERS_TABLE = "SportsKitCustomizations"

# Initialize DynamoDB Client
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMO_ORDERS_TABLE)

# Sample Order Data
sample_orders = [
    {"id": str(uuid.uuid4()), "design": "Red Jersey", "status": "Processing"},
    {"id": str(uuid.uuid4()), "design": "Blue Shorts", "status": "Completed"},
    {"id": str(uuid.uuid4()), "design": "Green Socks", "status": "Processing"},
    {"id": str(uuid.uuid4()), "design": "Yellow Jersey", "status": "Shipped"},
    {"id": str(uuid.uuid4()), "design": "Black Cap", "status": "Processing"},
]

# Insert Data into DynamoDB
for order in sample_orders:
    table.put_item(Item=order)
    print(f"Inserted Order: {order}")

print("✅ Sample orders added successfully!")
