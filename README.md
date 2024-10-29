# aksNdeepEdits - Image Processing Web App

aksndeepEdits is a Flask-based web application that provides various image processing capabilities such as cropping, rotating, blurring, enhancing, and background removal. Users can upload an image and apply these transformations to the image, which is then displayed on the web page.

## Features

1. **Crop Image**: Users can crop the uploaded image by specifying a percentage value.
2. **Rotate Image**: Users can rotate the uploaded image by a specified angle.
3. **Blur Image**: Users can apply Gaussian blur to the uploaded image with a specified blur intensity.
4. **Enhance Image**: The application automatically enhances the color, brightness, and contrast of the uploaded image.
5. **Reduce File Size**: Users can reduce the file size of the uploaded image to a specified value.
6. **Remove Background**: The application uses the Remove.bg API to remove the background from the uploaded image.

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: Pillow, OpenCV, scikit-image
- **Background Removal**: Remove.bg API

## Installation and Setup

1. Clone the repository:
```
git clone https://github.com/your-username/aksNdeepEdits.git
```
2. Create a virtual environment and activate it:
```
python -m venv env
source env/bin/activate
```
3. Install the required dependencies:
```
pip install -r requirements.txt
```
4. Obtain an API key from Remove.bg and update the `REMOVE_BG_API_KEY` variable in the `app.py` file.
5. Run the application:
```
python app.py
```
6. Access the application in your web browser at `http://localhost:5000`.

## Usage

1. Visit the home page and click on the "Start" button to begin.
2. Choose the image you want to process by clicking the "Choose File" button.
3. Select the desired image processing operation from the dropdown menu.
4. Depending on the selected operation, enter the required parameters (e.g., percentage for cropping, angle for rotation, desired file size for reduction).
5. Click the "Process" button to apply the selected transformation to the image.
6. The processed image will be displayed on the "Result" page.

## Contributing

If you find any issues or have suggestions for improvements, please feel free to create a new issue or submit a pull request. Contributions are always welcome!

## License

This project is licensed under the [MIT License](LICENSE).
