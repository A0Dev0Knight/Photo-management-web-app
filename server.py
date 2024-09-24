from flask import Flask, request, render_template, redirect, session, url_for, flash, jsonify, send_file
import os
from PIL import Image, ImageEnhance
import io

app = Flask(__name__, static_folder="public")
app.secret_key = "supersecretkey"

THUMBNAIL_SIZE = (200, 200)

ALLOWED_USERS = {
    "test": "test123",
    "admin": "admin",
    "guest": "guest"
}

THUMBNAIL_FOLDER = "static/images/profile/thumbnails"
DATABASE_FILE = os.path.join(app.static_folder, "database.txt")
PROFILE_IMAGE_FOLDER = os.path.join(app.static_folder, "images", "profile")

CATEGORIES = ["Work", "Family", "Travel"]
CATEGORY_FOLDERS = {cat: os.path.join(PROFILE_IMAGE_FOLDER, cat) for cat in CATEGORIES}

# Ensure necessary directories exist
for folder in [THUMBNAIL_FOLDER, PROFILE_IMAGE_FOLDER] + list(CATEGORY_FOLDERS.values()):
    if not os.path.exists(folder):
        os.makedirs(folder)

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_")).rstrip()

def create_thumbnail(image_path, thumbnail_path, size=(200, 200)):
    with Image.open(image_path) as img:
        img.thumbnail(size)
        img.save(thumbnail_path)

@app.route("/", methods=["GET"])
def index():
    if 'username' not in session:
        session['username'] = 'guest'
    image_files = []
    for category in CATEGORIES:
        category_folder = CATEGORY_FOLDERS[category]
        image_filenames = [f"{category}/{f}" for f in os.listdir(category_folder) if os.path.isfile(os.path.join(category_folder, f))]
        image_files.extend(image_filenames)
    return render_template('index.html', images=image_files)

@app.route("/second")
def second():
    return render_template('index02.html')

@app.route("/third")
def third():
    return render_template('index03.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    error_msg = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
            session["authenticated"] = True
            session["username"] = username
            return redirect(url_for("index"))
        else:
            error_msg = "Invalid username or password"
    return render_template("login.html", error_msg=error_msg)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.context_processor
def inject_template_vars():
    return {
        "authenticated": session.get("authenticated", False),
        "username": session.get("username", "")
    }

def read_database(filename):
    if not os.path.exists(filename):
        return {"first_name": "", "last_name": "", "age": "", "profile_images": [], "title": "", "description": ""}
    with open(filename, "rt") as f:
        lines = f.read().splitlines()
        profile_images = lines[3].split(",") if len(lines) > 3 and lines[3] else []
        return {
            "first_name": lines[0] if len(lines) > 0 else '',
            "last_name": lines[1] if len(lines) > 1 else '',
            "age": lines[2] if len(lines) > 2 else '',
            "profile_images": profile_images,
            "title": lines[4] if len(lines) > 4 else '',
            "description": lines[5] if len(lines) > 5 else ''
        }

def write_database(data):
    with open(DATABASE_FILE, 'w') as file:
        file.write('\n'.join([
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('age', ''),
            ','.join(data.get('profile_images', [])),
            data.get('title', ''),
            data.get('description', '')
        ]))

@app.route("/account-details", methods=["GET", "POST"])
def save_account():
    if session.get('username', '') == 'guest':
        flash("Guest users cannot modify account details.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name', ''),
            'last_name': request.form.get('last_name', ''),
            'age': request.form.get('age', ''),
            'profile_images': [],
            'title': request.form.get('title', ''),
            'description': request.form.get('description', '')
        }

        category = request.form.get('category', 'Work')  # Default to 'Work' if no category is selected
        if category not in CATEGORIES:
            category = 'Work'

        if 'profile_images' in request.files:
            files = request.files.getlist('profile_images')
            for file in files:
                if file.filename != '':
                    sanitized_filename = sanitize_filename(file.filename)
                    profile_image_filename = f"{session.get('username', 'default')}_{sanitized_filename}"
                    file_path = os.path.join(CATEGORY_FOLDERS[category], profile_image_filename)
                    file.save(file_path)
                    data['profile_images'].append(f"{category}/{profile_image_filename}")
                    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, profile_image_filename)
                    create_thumbnail(file_path, thumbnail_path)

        write_database(data)
        flash("Account details updated successfully.", "success")
        return redirect(url_for('save_account'))

    data = read_database(DATABASE_FILE)
    return render_template('account-details.html', **data)

@app.route("/delete-image", methods=["POST"])
def delete_image():
    if session.get('username') != 'admin':
        flash("Only admins can delete images.", "danger")
        return redirect(url_for('index'))
    
    image_filename = request.form.get('image_filename')
    image_path = os.path.join(PROFILE_IMAGE_FOLDER, image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)
        flash(f"Image {image_filename} deleted successfully.", "success")
    else:
        flash(f"Image {image_filename} not found.", "danger")
    
    return redirect(url_for('index'))

@app.route("/modify-image", methods=["POST"])
def modify_image():
    image_filename = request.form.get('image_filename')
    return render_template('modify_image.html', image_filename=image_filename)

@app.route("/modify-image-preview/<image_filename>")
def modify_image_preview(image_filename):
    contrast_value = request.args.get('contrast', 100, type=int)
    
    image_path = os.path.join(app.static_folder, 'images', 'profile', image_filename)
    image = Image.open(image_path)
    
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(contrast_value / 100)
    
    img_io = io.BytesIO()
    enhanced_image.save(img_io, 'JPEG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/jpeg')

@app.route("/save-modified-image/<image_filename>", methods=["POST"])
def save_modified_image(image_filename):
    contrast_value = request.json.get('contrast', 100)
    
    image_path = os.path.join(app.static_folder, 'images', 'profile', image_filename)
    image = Image.open(image_path)
    
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(contrast_value / 100)
    
    enhanced_image.save(image_path)
    
    return jsonify(success=True)

@app.route("/upload", methods=["POST"])
def upload():
    if 'username' not in session or session['username'] == 'guest':
        return jsonify({"message": "Unauthorized"}), 401

    if 'image' not in request.files or 'name' not in request.form or 'category' not in request.form:
        return jsonify({"message": "Missing required fields"}), 400

    file = request.files['image']
    name = request.form['name']
    category = request.form['category']

    if category not in CATEGORY_FOLDERS:
        return jsonify({"message": "Invalid category"}), 400

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    sanitized_name = sanitize_filename(name)
    file_ext = os.path.splitext(file.filename)[1]
    profile_image_filename = f"{session.get('username', 'default')}_{sanitized_name}{file_ext}"
    file_path = os.path.join(CATEGORY_FOLDERS[category], profile_image_filename)
    file.save(file_path)

    # Create thumbnail
    thumbnail_filename = f"{session.get('username', 'default')}_{sanitized_name}.thumb{file_ext}"
    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename)
    create_thumbnail(file_path, thumbnail_path)

    return jsonify({"message": "File uploaded successfully"}), 200

@app.errorhandler(404)
def error404(code):
    return "HTTP Error 404 - Page Not Found"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
