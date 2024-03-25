from flask import Flask, render_template, request, redirect
import os
from PIL import Image,ImageEnhance
import cv2
import numpy as np
from skimage import exposure
from rembg import remove

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def crop_image(image_path, percentage):
    # Open the image
    img = Image.open(image_path)
    # Get original image dimensions
    width, height = img.size
    # Calculate cropping dimensions based on percentage
    crop_width = int(width * (percentage / 100))
    crop_height = int(height * (percentage / 100))
    # Calculate cropping boundaries
    left = crop_width
    upper = crop_height
    right = width - crop_width
    lower = height - crop_height
    # Crop the image
    cropped_img = img.crop((left, upper, right, lower))
    # Save the cropped image back to the same path
    cropped_img.save(image_path)
        
def rotate_image(image_path, angle):
    img = Image.open(image_path)
    rotated_img = img.rotate(angle, expand=True)
    rotated_img.save(image_path)


def add_blur(image_path, blur_intensity):
    img = cv2.imread(image_path)
    # Ensure blur_intensity is an odd number (required by GaussianBlur)
    blur_intensity = max(1, blur_intensity)  # Ensure blur_intensity is at least 1
    if blur_intensity % 2 == 0:  # If even, make it odd by adding 1
        blur_intensity += 1
    
    blurred_img = cv2.GaussianBlur(img, (blur_intensity, blur_intensity), 0)
    cv2.imwrite(image_path, blurred_img)


def enhance_image(image_path):
    # Read image using OpenCV
    img = cv2.imread(image_path)
    # Convert image from BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Convert image to PIL format
    pil_img = Image.fromarray(img)
    # Enhance colors
    enhanced_img = ImageEnhance.Color(pil_img).enhance(1.2)
    # Enhance brightness
    enhanced_img = ImageEnhance.Brightness(enhanced_img).enhance(1.1)
    # Enhance contrast
    enhanced_img = ImageEnhance.Contrast(enhanced_img).enhance(1.0)
    # Adjust exposure using scikit-image
    enhanced_img = exposure.adjust_gamma(np.array(enhanced_img), gamma=1.3)
    # Convert back to numpy array
    enhanced_img = np.array(enhanced_img)
    # Convert image from RGB to BGR
    enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(image_path, enhanced_img)

def reduce_file_size(image_path, desired_size):
    img = Image.open(image_path)
    quality = 95  # Initial quality setting
    img_temp_path = "temp_image.jpg"  # Temporary path to save resized image

    while True:
        # Save the image with current quality setting
        img.save(img_temp_path, optimize=True, quality=quality)
        # Check the file size of the temporary image
        file_size_kb = os.path.getsize(img_temp_path) / 1024  # Convert bytes to kilobytes
        # If file size meets desired size or quality becomes too low, break the loop
        if file_size_kb <= desired_size or quality <= 10:
            break
        # Adjust quality for the next iteration
        quality -= 5
    # Save the final image with the adjusted quality
    img.save(image_path, optimize=True, quality=quality)
    # Remove the temporary image file
    os.remove(img_temp_path)

def remove_background(image_path):
    input_image = Image.open(image_path)
    output = remove(input_image)
    output.save(image_path, "PNG")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['GET', 'POST'])
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
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            try:
                if process == 'crop':
                    percentage=int(percentage)
                    crop_image(file_path, percentage) 

                elif process == 'rotate':
                    angle=int(value)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    rotate_image(image_path, angle)

                elif process == 'blur':
                
                    blur_intensity=int(value1)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    add_blur(image_path, blur_intensity)
                
                elif process == 'enhance':
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    enhance_image(image_path)
                
                elif process == 'reduce_size':
                
                    desired_size=int(value2)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    reduce_file_size(image_path, desired_size)
                
                elif process == 'remove_bg':
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    remove_background(image_path)
                    
                else:
                    return render_template('start.html')
            except:
                return render_template('start.html')
        return render_template('result.html', filename=filename)
    return render_template('start.html')

@app.route('/delete')
def download_file():
    folder_path=UPLOAD_FOLDER
    # List all files in the folder
    files = os.listdir(folder_path)
    
    # Iterate over each file
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path):
            # Delete the file
            os.remove(file_path)
    return render_template('index.html')
@app.route('/developers')
def about():
    return render_template('developers.html')
        

if __name__ == '__main__':
    app.run(debug=True)
