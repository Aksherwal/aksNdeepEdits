from flask import Flask, render_template, request, redirect, send_file
from io import BytesIO
import base64
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from skimage import exposure
import requests

# Initialize Flask application

app = Flask(__name__)

# API Key for Remove.bg service

REMOVE_BG_API_KEY = 'WjuyCBRb4yJ2Ce9WSLDUGadc'

# Set of allowed file extensions

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if file extension is allowed

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to crop image based on percentage

def crop_image(image, percentage):
     # Open image using PIL

    img = Image.open(BytesIO(image))

    # Get image dimensions
    width, height = img.size
    
     # Calculate crop dimensions
    crop_width = int(width * (percentage / 100))
    crop_height = int(height * (percentage / 100))

    # Define crop box coordinates
    left = crop_width
    upper = crop_height
    right = width - crop_width
    lower = height - crop_height

    # Crop image

    cropped_img = img.crop((left, upper, right, lower))

    # Convert cropped image to bytes

    output = BytesIO()
    cropped_img.save(output, format='PNG')
    return output.getvalue()

# Function to rotate image by given angle

def rotate_image(image, angle):
    # Open image using PIL

    img = Image.open(BytesIO(image))
    # Rotate image
    rotated_img = img.rotate(angle, expand=True)
    output = BytesIO()
    # Convert rotated image to bytes

    rotated_img.save(output, format='JPEG')
    return output.getvalue()

# Function to add blur to the image

def add_blur(image, blur_intensity):
    # Decode image using OpenCV
    img = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
    # Ensure blur intensity is odd
    blur_intensity = max(1, blur_intensity)
    if blur_intensity % 2 == 0:
        blur_intensity += 1
   
    # Apply Gaussian blur
    blurred_img = cv2.GaussianBlur(img, (blur_intensity, blur_intensity), 0)
    # Encode blurred image to bytes

    success, encoded_img = cv2.imencode('.jpg', blurred_img)
    return encoded_img.tobytes()

# Function to enhance image quality

def enhance_image(image):
    # Decode image using OpenCV and convert to RGB

    img = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Convert image to PIL format
    pil_img = Image.fromarray(img)
    # Apply color, brightness, contrast enhancements
    enhanced_img = ImageEnhance.Color(pil_img).enhance(1.2)
    enhanced_img = ImageEnhance.Brightness(enhanced_img).enhance(1.1)
    enhanced_img = ImageEnhance.Contrast(enhanced_img).enhance(1.0)
    # Apply gamma correction
    enhanced_img = exposure.adjust_gamma(np.array(enhanced_img), gamma=1.3)
    
    # Convert enhanced image to OpenCV format
    enhanced_img = np.array(enhanced_img)
    enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR)
    
    # Encode enhanced image to bytes
    success, encoded_img = cv2.imencode('.jpg', enhanced_img)
    return encoded_img.tobytes()

# Function to reduce file size of the image

def reduce_file_size(image, desired_size):
    
    # Open image using PIL
    img = Image.open(BytesIO(image))

    # Initialize quality parameter
    quality = 95
    img_temp = BytesIO()

    # Iterate until desired file size or minimum quality reached

    while True:
        img.save(img_temp, format='JPEG', optimize=True, quality=quality)
        file_size_kb = img_temp.tell() / 1024
        if file_size_kb <= desired_size or quality <= 10:
            break
        img_temp.seek(0)
        img_temp.truncate(0)
        quality -= 5
    img_temp.seek(0)
    return img_temp.getvalue()

# Function to remove background using Remove.bg service

def remove_background(image_data):
    url = 'https://api.remove.bg/v1.0/removebg'
    files = {'image_file': image_data}
    headers = {'X-Api-Key': REMOVE_BG_API_KEY}

    try:

        # send POST request to Remove.bg API
        response = requests.post(url, files=files, headers=headers)
        if response.status_code == 200:
            # Return the processed image data
            return response.content
        else:
            # Handle API errors
            print("Error processing image: ", response.text)
            return None
    except Exception as e:
        # Handle exceptions
        print("Error processing image: ", e)
        return None

# Route for the home page

@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image processing

@app.route('/start', methods=['POST','GET'])
def start():
    if request.method == 'POST':

        # Check if file is uploaded

        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        process = request.form['process']
        value=request.form['value']
        value1=request.form['value1']
        value2=request.form['value2']
        percentage=request.form['percentage']

        # Check if file is selected

        if file.filename == '':
            return redirect(request.url)

        # Read image data

        if file and allowed_file(file.filename):
            image = file.read()
        try:
            # Apply selected processing method

            if process == 'crop':
                result = crop_image(image, int(percentage))

            elif process == 'rotate':
                result = rotate_image(image, int(value))

            elif process == 'blur':
                result = add_blur(image, int(value1))

            elif process == 'enhance':
                result = enhance_image(image)

            elif process == 'reduce_size':
                result = reduce_file_size(image, int(value2))

            elif process == 'remove_bg':
                result = remove_background(image)

            else:
                return render_template('start.html')

            # Encode processed image to base64 for display

            encoded_image = base64.b64encode(result).decode('utf-8')

        # Handle exceptions
        except Exception as e:
            print(e)
            return render_template('start.html')
            
        # Render result template with processed image

        return render_template('result.html', processed_image=encoded_image, filename=file.filename)
    return render_template('start.html')

# Route for the about page

@app.route('/developers')
def about():
    return render_template('developers.html')

# Run the Flask app

if __name__ == '__main__':
    app.run(debug=True)

