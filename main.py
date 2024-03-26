from flask import Flask, render_template, request, redirect, send_file
from io import BytesIO
import base64
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from skimage import exposure
import requests

app = Flask(__name__)

REMOVE_BG_API_KEY = 'WjuyCBRb4yJ2Ce9WSLDUGadc'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def crop_image(image, percentage):
    img = Image.open(BytesIO(image))
    width, height = img.size
    crop_width = int(width * (percentage / 100))
    crop_height = int(height * (percentage / 100))
    left = crop_width
    upper = crop_height
    right = width - crop_width
    lower = height - crop_height
    cropped_img = img.crop((left, upper, right, lower))
    output = BytesIO()
    cropped_img.save(output, format='PNG')
    return output.getvalue()
        
def rotate_image(image, angle):
    img = Image.open(BytesIO(image))
    rotated_img = img.rotate(angle, expand=True)
    output = BytesIO()
    rotated_img.save(output, format='JPEG')
    return output.getvalue()

def add_blur(image, blur_intensity):
    img = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
    blur_intensity = max(1, blur_intensity)
    if blur_intensity % 2 == 0:
        blur_intensity += 1
    blurred_img = cv2.GaussianBlur(img, (blur_intensity, blur_intensity), 0)
    success, encoded_img = cv2.imencode('.jpg', blurred_img)
    return encoded_img.tobytes()

def enhance_image(image):
    img = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img)
    enhanced_img = ImageEnhance.Color(pil_img).enhance(1.2)
    enhanced_img = ImageEnhance.Brightness(enhanced_img).enhance(1.1)
    enhanced_img = ImageEnhance.Contrast(enhanced_img).enhance(1.0)
    enhanced_img = exposure.adjust_gamma(np.array(enhanced_img), gamma=1.3)
    enhanced_img = np.array(enhanced_img)
    enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR)
    success, encoded_img = cv2.imencode('.jpg', enhanced_img)
    return encoded_img.tobytes()

def reduce_file_size(image, desired_size):
    img = Image.open(BytesIO(image))
    quality = 95
    img_temp = BytesIO()
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

def remove_background(image_data):
    url = 'https://api.remove.bg/v1.0/removebg'
    files = {'image_file': image_data}
    headers = {'X-Api-Key': REMOVE_BG_API_KEY}

    try:
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
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST','GET'])
def start():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        process = request.form['process']
        value=request.form['value']
        value1=request.form['value1']
        value2=request.form['value2']
        percentage=request.form['percentage']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            image = file.read()
        try:
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
            encoded_image = base64.b64encode(result).decode('utf-8')
        except Exception as e:
            print(e)
            return render_template('start.html')
        return render_template('result.html', processed_image=encoded_image, filename=file.filename)
    return render_template('start.html')

@app.route('/developers')
def about():
    return render_template('developers.html')

if __name__ == '__main__':
    app.run(debug=True)
