import os
import subprocess

# Set Azure details
APP_NAME = "flask-api-app"  # Change this to a unique app name
RESOURCE_GROUP = "flask-api-group"
LOCATION = "eastus"

# Commands for Azure App Service deployment
commands = [
    f"az group create --name {RESOURCE_GROUP} --location {LOCATION}",
    f"az appservice plan create --name {APP_NAME}-plan --resource-group {RESOURCE_GROUP} --sku FREE",
    f"az webapp create --resource-group {RESOURCE_GROUP} --plan {APP_NAME}-plan --name {APP_NAME} --runtime 'PYTHON:3.8'",
    "zip -r flask-api.zip . -x '*.git*'",
    f"az webapp deployment source config-zip --resource-group {RESOURCE_GROUP} --name {APP_NAME} --src flask-api.zip",
    f"az webapp config set --resource-group {RESOURCE_GROUP} --name {APP_NAME} --startup-file 'gunicorn -w 4 -b 0.0.0.0:8000 app:app'",
    f"az webapp restart --resource-group {RESOURCE_GROUP} --name {APP_NAME}",
]

# Execute deployment commands
for cmd in commands:
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)

print(f"✅ Deployment Complete! Access your API at: https://{APP_NAME}.azurewebsites.net")
