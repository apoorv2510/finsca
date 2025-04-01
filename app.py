from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import boto3
import uuid
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import http.client  # ✅ FIX: Import http.client correctly
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# AWS Services Configuration
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# DynamoDB Tables
user_table = dynamodb.Table('Users')  # Store registered users
kit_table = dynamodb.Table('SportsKits')  # Store sports kit designs
preset_table = dynamodb.Table('KitPresets')  # Store kit presets

sns = boto3.client('sns', region_name='us-east-1')
sns_topic_arn = 'arn:aws:sns:us-east-1:642051550988:NewKitDesigns'

s3 = boto3.client('s3', region_name='us-east-1')
s3_bucket_name = 'sportskits-designs'

# SQS Configuration
sqs = boto3.client('sqs', region_name='us-east-1')
sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/642051550988/SportsKitQueue'

def send_to_sqs(message_body):
    try:
        response = sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(message_body)
        )
        print(f"Message sent to SQS: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending message to SQS: {str(e)}")

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # Redirects to login page if user is not authenticated

# Load 3D Jersey Template
JERSEY_TEMPLATE_PATH = "static/3d_jersey_template.png"  # Ensure this exists in 'static/'


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    @classmethod
    def get(cls, user_id):
        response = user_table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            return cls(user_id)
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    next_page = request.args.get('next')  # Capture the original requested URL

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        response = user_table.get_item(Key={'user_id': email})
        user = response.get('Item')

        if user and check_password_hash(user['password'], password):
            user_obj = User(email)
            login_user(user_obj, remember=True)  # Session persistence
            return redirect(next_page) if next_page else redirect(url_for('index'))  # Redirect to original page
        else:
            flash('Invalid email or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        response = user_table.get_item(Key={'user_id': email})
        if 'Item' in response:
            flash("User already exists! Please login.")
            return redirect(url_for('login_page'))

        user_table.put_item(Item={'user_id': email, 'password': password})
        flash("Registration successful! Please log in.")
        return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/gallery')
@login_required
def gallery():
    try:
        # Fetch processed kits from the ProcessedKits table
        processed_kits_table = dynamodb.Table('ProcessedKits')
        response = processed_kits_table.scan()
        processed_kits = response.get('Items', [])

        # Pass the processed kits to the gallery.html template
        return render_template('gallery.html', kits=processed_kits)

    except Exception as e:
        print(f"Error fetching processed kits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/edit-kit-page')
@login_required
def edit_kit_page():
    return render_template('edit_kit.html')


@app.route('/upload-kit-page')
@login_required
def upload_kit_page():
    return render_template('upload_kit.html')


@app.route('/presets')
@login_required
def presets():
    return render_template('presets.html')


@app.route('/customize-jersey-page')
@login_required
def customize_jersey_page():
    return render_template('customize_jersey.html')


@app.route('/create-and-upload-kit', methods=['POST'])
@login_required
def create_and_upload_kit():
    try:
        user_id = current_user.id
        design = request.form['design']
        kit_id = str(uuid.uuid4())
        timestamp = str(datetime.datetime.now())
        file_url = None

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = f"{uuid.uuid4()}_{file.filename}"
            s3.upload_fileobj(file, s3_bucket_name, filename)
            file_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{filename}"

        kit_data = {
            'kit_id': kit_id,
            'user_id': user_id,
            'design': design,
            'timestamp': timestamp,
            'file_url': file_url
        }

        kit_table.put_item(Item=kit_data)

        # Send message to SQS
        send_to_sqs(kit_data)

        sns.publish(TopicArn=sns_topic_arn, Message=f"New kit design created by {user_id} with ID {kit_id}")

        flash("Kit created and image uploaded successfully!")
        return redirect(url_for('index'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/customize-jersey', methods=['GET'])
@login_required
def customize_jersey():
    try:
        try:
            jersey = Image.open(JERSEY_TEMPLATE_PATH).convert("RGBA")
        except FileNotFoundError:
            return jsonify({'error': 'Jersey template not found.'}), 500

        team = request.args.get('team', 'Default Team')
        color = request.args.get('color', '#FFFFFF')
        number = request.args.get('number', '10')
        logo_url = request.args.get('logo', None)

        overlay = Image.new("RGBA", jersey.size, color)
        jersey = Image.blend(jersey, overlay, 0.5)

        draw = ImageDraw.Draw(jersey)
        font = ImageFont.load_default()

        draw.text((150, 60), team, fill="black", font=font)
        draw.text((180, 250), number, fill="black", font=font)

        if logo_url:
            response = requests.get(logo_url)
            if response.status_code == 200:
                logo = Image.open(io.BytesIO(response.content)).convert("RGBA")
                logo = logo.resize((100, 100))
                jersey.paste(logo, (150, 100), mask=logo)

        img_io = io.BytesIO()
        jersey.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get-all-kits', methods=['GET'])
@login_required
def get_all_kits():
    response = kit_table.scan()
    kits = response.get('Items', [])
    return jsonify(kits)

@app.route('/get-football-teams')
@login_required
def get_football_teams():
    """Fetches football teams with IDs from 1 to 30 and renders them in teams.html"""
    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/teams"

        # ✅ Generate team IDs from 1 to 30
        team_ids = [str(i) for i in range(20, 40)]  

        headers = {
            "x-rapidapi-key": "1d47af403cmsh7bf7014d0e91ebap17fb61jsn4e575df1c9d8",
            "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
        }

        teams_data = []

        # Fetch each team separately since API does not support multiple IDs in one request
        for team_id in team_ids:
            querystring = {"id": team_id}
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()

            if "response" in data and len(data["response"]) > 0:
                teams_data.append(data["response"][0])  # Append first entry of response

        if len(teams_data) > 0:
            return render_template("teams.html", teams=teams_data)
        else:
            print("Error: No team data found in API response.")
            return jsonify({"error": "No team data found"}), 500

    except Exception as e:
        print(f"Error fetching teams data: {str(e)}")  # ✅ Debugging print
        return jsonify({"error": str(e)}), 500

@app.route('/get-football-players')
@login_required
def get_football_players():
    """Fetches football players from EC2 API and returns JSON data"""
    try:
        ec2_api_url = "http://playersapi.us-east-1.elasticbeanstalk.com/api/players"
        response = requests.get(ec2_api_url)

        if response.status_code == 200:
            players_data = response.json()
            return render_template("players.html", players=players_data)
        else:
            return jsonify({"error": "Could not fetch data from EC2 API"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get-football-boots')
@login_required
def get_football_boots():
    """Fetches football boots data from local API and renders boots.html"""
    try:
        # Fetch boots data from your local API endpoint
        response = requests.get("https://2fvses73yg.execute-api.us-east-1.amazonaws.com/prod/boots")
        
        if response.status_code == 200:
            boots_data = response.json()
            return render_template("boots.html", boots=boots_data)
        else:
            return jsonify({"error": "Could not fetch boots data"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/boots')
@login_required
def api_boots():
    """Returns JSON data for football boots (mock data or from database)"""
    try:
        # Example boots data - replace with your actual data source
        boots_data = {
            "data": [
                {
                    "BootsBrand": "Nike",
                    "BootsName": "Mercurial Superfly VII",
                    "BootsPosition": "Attack",
                    "BootsTopPlayers": "Cristiano Ronaldo",
                    "RecordID": "63"
                },
                {
                    "BootsBrand": "Adidas",
                    "BootsName": "Predator Edge.1",
                    "BootsPosition": "Midfield",
                    "BootsTopPlayers": "Jude Bellingham",
                    "RecordID": "16"
                },
                # Add more boots data as needed
            ],
            "message": "Fetched boots successfully",
            "status": "success"
        }
        return jsonify(boots_data)

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

