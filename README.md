# Flask Image Upload App

Name: Barbu Alexandru Daniel
Class: 314CC

This is a Flask web application that allows users to upload images and modify them using Pillow library.
Users can also view, delete, and modify their account details.

## Features

- User authentication (login/logout)
- Upload multiple images with category selection
- View, delete, and modify uploaded images
    - Modify image attributes such as contrast

## Requirements

- Python 3.x
- Flask
- Pillow

## Installation

1. Unzip the directory:

    ```bash
    unzip photo_app_app.zip
    ```
2. Install dependencies using pip:
    ```bash
    $ cd root_directory_of_my_app
    $ pip install -r requirements.txt # optional (docker should do this by default like the big boy he is)
    ```
## Usage

1. Run the dockerfile:
    ```bash
    $ docker build -t iap1-tema . # or any other neme besides `iap1-tema`
    $ docker run -p 5000:5000 -it iap1-tema
    ```
2. Open a web browser and navigate to `http://localhost:5000` to access the application.

3. You can log in using the following credentials:

    - Username: admin
    - Password: admin
    
    - Username: test
    - Password: test123
    
    >_**NOTE:**_ By default the user is considered as guest, meaning he / she cannot add photos to the library.

## Technology used:

- Flask - for backend
- Pillow - for image processing
- Bootstrap - for frontend
- Docker