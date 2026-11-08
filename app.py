
from flask import Flask, render_template, request
from pathlib import Path
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from datetime import datetime
from uuid import uuid4
import socket

app = Flask(__name__)
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
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    photos = request.files.getlist("photos")

    if not photos or all(not photo.filename for photo in photos):
        return "Nie wybrano zdjęć.", 400

    if len(photos) > MAX_FILES:
        return f"Możesz przesłać maksymalnie {MAX_FILES} zdjęć.", 400

    saved_count = 0
    rejected_count = 0

    transfer_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    transfer_folder = UPLOAD_FOLDER / transfer_id

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

        transfer_folder.mkdir(parents=True, exist_ok=True)
        photo.save(transfer_folder / filename)

        saved_count += 1

    return (
        f"Przesłano: {saved_count}. Odrzucono: {rejected_count}."
    )


@app.errorhandler(413)
def file_too_large(error):
    return "Przesłane pliki przekraczają limit 100 MB.", 413


if __name__ == "__main__":
       print(f"Adres dla telefonu: http://{get_local_ip()}:5000")

       app.run(host="0.0.0.0", port=5000, debug=True)
