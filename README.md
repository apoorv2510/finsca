# Sports Kits Application

The **Sports Kits Application** is a web-based platform for managing and processing sports kit data using AWS services such as Lambda, SQS, and DynamoDB. It provides a Flask-based API with cloud deployment support via Elastic Beanstalk and Azure App Services. The app supports automated data handling through CI/CD pipelines.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [AWS Deployment](#aws-deployment)
- [Azure Deployment](#azure-deployment)
- [Contributing](#contributing)

## Overview

This application helps in managing a list of sports kits and processes them using AWS services. Incoming data is queued with Amazon SQS, processed with a Lambda function, and stored in DynamoDB. It also features a Flask API to serve and manage the data locally or in production environments.

## Features

- Kit data management using Flask API
- AWS integration: SQS, Lambda, and DynamoDB
- Asynchronous message-based processing
- Simple web server with Flask
- CI/CD using GitHub Actions
- Supports both local (JSON file) and cloud (DynamoDB) storage

## Architecture

```
User
 ↓
[Flask App] ←→ [players_large.json or DynamoDB]
 ↓
[SQS Queue] → [Lambda Function] → [DynamoDB Table]
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/apoorv2510/finsca.git
   cd finsca
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Create and populate local SQLite DB:
   ```bash
   python create_table.py
   python populateTable.py
   ```

## Usage

To run the application locally:
```bash
python app.py
```

Visit: `http://localhost:5000`

## AWS Deployment

1. Create required AWS services:
   ```bash
   python create_aws_services.py
   python lanbdasqsdep.py
   ```

   This will:
   - Create a DynamoDB table: `ProcessedKits`
   - Set up an SQS queue: `SportsKitQueue`
   - Deploy a Lambda function: `ProcessKitLambda`

2. Deploy to Elastic Beanstalk via GitHub Actions:
   Ensure the following GitHub secrets are configured:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN`
   - `AWS_REGION`
   - `EB_APP_NAME`
   - `EB_ENV_NAME`

   On push to the `main` branch, the app will be zipped, versioned using the commit SHA or timestamp, and deployed automatically.

**EC2 Deployment**

Ensure you're authenticated with the Azure CLI and the required services are configured.

## Contributing

Feel free to submit issues or pull requests to improve the functionality or add new features.
