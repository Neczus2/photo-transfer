from flask import Flask, render_template, request, send_file
from pathlib import Path
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from datetime import datetime
from uuid import uuid4
import socket
import qrcode
from io import BytesIO
import secrets

app = Flask(__name__)
active_session_token = None
active_transfer_folder = None

def get_local_ip():
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        connection.connect(("8.8.8.8", 80))
        ip_address = connection.getsockname()[0]
    finally:
        connection.close()

    return ip_address



UPLOAD_FOLDER = Path(__file__).resolve().parent / "shared_photos"

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

MAX_FILE_SIZE = 15 * 1024 * 1024
MAX_FILES = 20

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


@app.route("/")
def home():
    global active_session_token, active_transfer_folder

    active_session_token = secrets.token_urlsafe(16)

    transfer_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    active_transfer_folder = UPLOAD_FOLDER / transfer_id

    return render_template("index.html", token=active_session_token)

@app.route("/qr")
def generate_qr():
    if not active_session_token:
        return "Brak aktywnej sesji", 404

    address = f"http://{get_local_ip()}:5000/upload/{active_session_token}"

    qr_image = qrcode.make(address)

    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return send_file(image_buffer, mimetype="image/png")

@app.route("/upload/<token>", methods=["GET", "POST"])
def upload(token):
    if not active_session_token or not secrets.compare_digest(token, active_session_token):
        return "Sesja wygasła lub jest nieprawidłowa.", 403

    if request.method == "GET":
        return render_template(
        "index.html",
        token=active_session_token,
        mobile_upload=True
    )

    photos = request.files.getlist("photos")

    if not photos or all(not photo.filename for photo in photos):
        return render_template(
            "index.html",
            token=active_session_token,
            mobile_upload=True,
            error_message="Nie wybrano żadnych zdjęć. Spróbuj ponownie."
        ), 400

    if len(photos) > MAX_FILES:
        return render_template(
            "index.html",
            token=active_session_token,
            mobile_upload=True,
            error_message=f"Możesz przesłać maksymalnie {MAX_FILES} zdjęć jednocześnie."
        ), 400

    saved_count = 0
    rejected_count = 0

    for photo in photos:
        if not photo.filename:
            continue

        try:
            photo.stream.seek(0, 2)
            file_size = photo.stream.tell()
            photo.stream.seek(0)

            if file_size > MAX_FILE_SIZE or file_size == 0:
                rejected_count += 1
                continue

            image = Image.open(photo.stream)

            if image.format not in ALLOWED_FORMATS:
                rejected_count += 1
                continue

            image.verify()
            photo.stream.seek(0)

        except (UnidentifiedImageError, OSError, ValueError):
            rejected_count += 1
            continue

        filename = secure_filename(photo.filename)

        if not filename:
            rejected_count += 1
            continue

        filename = f"{uuid4().hex[:8]}_{filename}"

        active_transfer_folder.mkdir(parents=True, exist_ok=True)
        photo.save(active_transfer_folder / filename)

        saved_count += 1

    return render_template(
        "index.html",
        token=active_session_token,
        mobile_upload=True,
        saved_count=saved_count,
        rejected_count=rejected_count,
        error_message=(
            f"Nie udało się przesłać {rejected_count} plików. "
            "Sprawdź ich format i rozmiar."
            if rejected_count > 0 else None
        )
    )

@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "index.html",
        token=active_session_token,
        mobile_upload=True,
        error_message="Łączny rozmiar przesyłanych plików przekracza limit 100 MB. Wybierz mniej zdjęć."
    ), 413


if __name__ == "__main__":
       print(f"Adres dla telefonu: http://{get_local_ip()}:5000")

       app.run(host="0.0.0.0", port=5000, debug=True)
