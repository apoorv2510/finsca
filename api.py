from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import boto3
import uuid
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 🔹 Load 3D jersey template
JERSEY_TEMPLATE_PATH = "static/3d_jersey_template.png"  # Place a transparent 3D jersey template in 'static/' folder

#  **API: Customize 3D Jersey**
@app.route('/customize-jersey', methods=['GET'])
@login_required
def customize_jersey():
    try:
        # Load 3D jersey template
        jersey = Image.open(JERSEY_TEMPLATE_PATH).convert("RGBA")

        # Get customization parameters
        team = request.args.get('team', 'Default Team')
        color = request.args.get('color', '#FFFFFF')  # Default white
        number = request.args.get('number', '10')
        logo_url = request.args.get('logo', None)

        # Apply color overlay
        overlay = Image.new("RGBA", jersey.size, color)
        jersey = Image.blend(jersey, overlay, 0.6)  # Blend jersey with selected color

        # Draw team name and number
        draw = ImageDraw.Draw(jersey)
        font = ImageFont.load_default()

        # Add team name (positioning near the chest)
        draw.text((150, 60), team, fill="black", font=font)

        # Add number (positioning at the center)
        draw.text((180, 250), number, fill="black", font=font)

        # Add logo if provided
        if logo_url:
            response = requests.get(logo_url)
            if response.status_code == 200:
                logo = Image.open(io.BytesIO(response.content)).convert("RGBA")
                logo = logo.resize((100, 100))  # Resize logo
                jersey.paste(logo, (150, 100), mask=logo)  # Paste logo with transparency

        # Save the image to memory
        img_io = io.BytesIO()
        jersey.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
JERSEY_TEMPLATE_PATH = "static/3d_jersey_template.png"  # Load from static folder

@app.route('/customize-jersey', methods=['GET'])
@login_required
def customize_jersey():
    try:
        # Load 3D jersey template
        jersey = Image.open(JERSEY_TEMPLATE_PATH).convert("RGBA")

        # Get customization parameters
        team = request.args.get('team', 'Default Team')
        color = request.args.get('color', '#FFFFFF')  # Default white
        number = request.args.get('number', '10')
        logo_url = request.args.get('logo', None)

        # Apply color overlay to the jersey
        overlay = Image.new("RGBA", jersey.size, color)
        jersey = Image.blend(jersey, overlay, 0.6)  # Blend color with jersey

        # Add team name and number
        draw = ImageDraw.Draw(jersey)
        font = ImageFont.load_default()

        # Add team name (near chest)
        draw.text((150, 60), team, fill="black", font=font)

        # Add number (near center)
        draw.text((180, 250), number, fill="black", font=font)

        # Add logo if provided
        if logo_url:
            response = requests.get(logo_url)
            if response.status_code == 200:
                logo = Image.open(io.BytesIO(response.content)).convert("RGBA")
                logo = logo.resize((100, 100))  # Resize logo
                jersey.paste(logo, (150, 100), mask=logo)  # Paste logo with transparency

        # Save the customized jersey to memory
        img_io = io.BytesIO()
        jersey.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
